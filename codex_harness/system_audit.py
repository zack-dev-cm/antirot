from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .audit import AuditIssue


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".dart_tool",
    ".idea",
    ".next",
    ".turbo",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "Pods",
    "artifacts",
    "data",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "out",
    "outputs",
    "target",
    "tmp",
}
TEXT_FILE_SUFFIXES = {
    ".json",
    ".md",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
MAX_TEXT_SCAN_BYTES = 512_000
RG_FILE_GLOBS = (
    "*.json",
    "*.md",
    "*.toml",
    "*.txt",
    "*.yaml",
    "*.yml",
    "SKILL.md",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
)
SEVERITY_RANK = {"ERROR": 0, "WARNING": 1}
SKILL_PATH_PATTERN = re.compile(
    r'(?P<path>(?:~|/(?:[^/\s"\'`<>]+/)*[^/\s"\'`<>]+)/\.codex/skills/[^\s"\'`<>]+/SKILL\.md)'
)
PLUGIN_SECTION_PATTERN = re.compile(r'^\[plugins\."(?P<name>[^"]+)"\]\s*$')
ENABLED_PATTERN = re.compile(r"^\s*enabled\s*=\s*(?P<value>true|false)\s*$", re.IGNORECASE)
TODO_PATTERN = re.compile(r"\[TODO:[^]]+\]|TODO:", re.IGNORECASE)


@dataclass(slots=True)
class LocalSkill:
    skill_id: str
    path: str
    source: str
    symlink: bool = False
    resolved_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class CachedPlugin:
    name: str
    key: str
    version: str
    marketplace: str
    path: str
    enabled: bool
    has_skills: bool
    has_apps: bool
    has_mcp_servers: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ProjectFootprint:
    root: str
    local_skill_files: list[str]
    plugin_manifest_files: list[str]
    marketplace_files: list[str]
    external_skill_references: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ProjectUsage:
    name: str
    root: str
    sessions: int
    subagent_sessions: int
    last_session: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class SystemAuditReport:
    codex_home: str
    scan_roots: list[str]
    score: int
    enabled_plugins: list[str]
    issues: list[AuditIssue]
    local_skills: list[LocalSkill]
    cached_plugins: list[CachedPlugin]
    projects: list[ProjectFootprint]
    recent_usage_days: int
    recent_project_usage: list[ProjectUsage]
    recent_session_count: int
    recent_subagent_session_count: int
    recent_models: dict[str, int]
    recent_agent_roles: dict[str, int]

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def repo_local_skill_count(self) -> int:
        return sum(len(project.local_skill_files) for project in self.projects)

    @property
    def repo_local_plugin_count(self) -> int:
        return sum(len(project.plugin_manifest_files) for project in self.projects)

    @property
    def external_skill_reference_count(self) -> int:
        return sum(len(project.external_skill_references) for project in self.projects)

    @property
    def recent_project_count(self) -> int:
        return len(self.recent_project_usage)

    def to_dict(self) -> dict[str, object]:
        return {
            "codex_home": self.codex_home,
            "scan_roots": self.scan_roots,
            "score": self.score,
            "issue_count": self.issue_count,
            "enabled_plugins": self.enabled_plugins,
            "summary": {
                "local_skill_count": len(self.local_skills),
                "cached_plugin_count": len(self.cached_plugins),
                "project_count": len(self.projects),
                "repo_local_skill_count": self.repo_local_skill_count,
                "repo_local_plugin_count": self.repo_local_plugin_count,
                "external_skill_reference_count": self.external_skill_reference_count,
                "recent_usage_days": self.recent_usage_days,
                "recent_session_count": self.recent_session_count,
                "recent_subagent_session_count": self.recent_subagent_session_count,
                "recent_project_count": self.recent_project_count,
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "local_skills": [skill.to_dict() for skill in self.local_skills],
            "cached_plugins": [plugin.to_dict() for plugin in self.cached_plugins],
            "projects": [project.to_dict() for project in self.projects],
            "recent_usage": {
                "days": self.recent_usage_days,
                "session_count": self.recent_session_count,
                "subagent_session_count": self.recent_subagent_session_count,
                "project_count": self.recent_project_count,
                "models": self.recent_models,
                "agent_roles": self.recent_agent_roles,
                "projects": [project.to_dict() for project in self.recent_project_usage],
            },
        }

    def to_text(self) -> str:
        lines = [
            f"Codex system audit for {self.codex_home}",
            f"score={self.score}/100 issues={self.issue_count}",
            f"local_skills={len(self.local_skills)} cached_plugins={len(self.cached_plugins)} enabled_plugins={len(self.enabled_plugins)}",
            f"projects={len(self.projects)} repo_local_skills={self.repo_local_skill_count} repo_local_plugins={self.repo_local_plugin_count} external_skill_refs={self.external_skill_reference_count}",
            f"recent_sessions={self.recent_session_count} recent_projects={self.recent_project_count} subagent_sessions={self.recent_subagent_session_count} window_days={self.recent_usage_days}",
        ]
        for issue in self.issues:
            lines.append(
                f"- {issue.severity} {issue.code} {issue.path}: {issue.message}"
            )
        if self.recent_project_usage:
            lines.append("top_recent_projects:")
            for project in self.recent_project_usage[:5]:
                lines.append(
                    f"- {project.name} sessions={project.sessions} subagents={project.subagent_sessions} root={project.root}"
                )
        return "\n".join(lines)

    def to_markdown(self) -> str:
        lines = [
            f"# Codex system audit for `{self.codex_home}`",
            "",
            f"- score: **{self.score}/100**",
            f"- issues: **{self.issue_count}**",
            f"- local skills: **{len(self.local_skills)}**",
            f"- cached plugins: **{len(self.cached_plugins)}**",
            f"- enabled plugins in config: **{len(self.enabled_plugins)}**",
            f"- repos with Codex assets: **{len(self.projects)}**",
            f"- repo-local skills: **{self.repo_local_skill_count}**",
            f"- repo-local plugin manifests: **{self.repo_local_plugin_count}**",
            f"- external skill references: **{self.external_skill_reference_count}**",
            f"- recent sessions ({self.recent_usage_days}d): **{self.recent_session_count}**",
            f"- recent projects ({self.recent_usage_days}d): **{self.recent_project_count}**",
            f"- recent subagent sessions ({self.recent_usage_days}d): **{self.recent_subagent_session_count}**",
        ]
        if self.enabled_plugins:
            lines.append(
                "- enabled plugin keys: "
                + ", ".join(f"`{plugin}`" for plugin in self.enabled_plugins)
            )

        lines.extend(["", "## Issues"])
        if not self.issues:
            lines.append("No issues found.")
        else:
            for issue in self.issues[:20]:
                lines.append(
                    f"- **{issue.severity} `{issue.code}`** `{issue.path}`: {issue.message}"
                )
            if len(self.issues) > 20:
                lines.append(f"- ... and {len(self.issues) - 20} more issues")

        if self.cached_plugins:
            lines.extend(["", "## Cached Plugins"])
            for plugin in self.cached_plugins:
                flags = []
                if plugin.enabled:
                    flags.append("enabled")
                if plugin.has_skills:
                    flags.append("skills")
                if plugin.has_apps:
                    flags.append("apps")
                if plugin.has_mcp_servers:
                    flags.append("mcp")
                lines.append(
                    f"- `{plugin.key}` v{plugin.version}: {', '.join(flags) if flags else 'metadata only'}"
                )

        if self.projects:
            lines.extend(["", "## Project Footprint"])
            ranked_projects = sorted(
                self.projects,
                key=lambda project: (
                    -(len(project.local_skill_files) + len(project.plugin_manifest_files) + len(project.external_skill_references)),
                    project.root,
                ),
            )
            for project in ranked_projects[:10]:
                lines.append(
                    f"- `{project.root}`: skills={len(project.local_skill_files)}, plugins={len(project.plugin_manifest_files)}, marketplace_files={len(project.marketplace_files)}, external_skill_refs={len(project.external_skill_references)}"
                )

        if self.recent_project_usage:
            lines.extend(["", "## Recent Usage"])
            for project in self.recent_project_usage[:10]:
                lines.append(
                    f"- `{project.name}`: {project.sessions} sessions, {project.subagent_sessions} subagent sessions, root `{project.root}`"
                )
            if self.recent_models:
                model_summary = ", ".join(
                    f"`{model}` {count}" for model, count in self.recent_models.items()
                )
                lines.append(f"- models: {model_summary}")
            if self.recent_agent_roles:
                role_summary = ", ".join(
                    f"`{role}` {count}" for role, count in self.recent_agent_roles.items()
                )
                lines.append(f"- agent roles: {role_summary}")

        return "\n".join(lines)


def audit_local_codex_environment(
    codex_home: Path,
    *,
    scan_roots: list[Path] | None = None,
    recent_usage_days: int = 14,
    max_depth: int = 3,
    marker_discovery: bool = False,
) -> SystemAuditReport:
    codex_home = codex_home.expanduser()
    normalized_roots = [
        root.expanduser().resolve()
        for root in (
            scan_roots
            if scan_roots
            else _default_scan_roots()
        )
    ]

    issues: list[AuditIssue] = []
    if not codex_home.exists():
        issues.append(
            AuditIssue(
                severity="ERROR",
                code="missing-codex-home",
                path=str(codex_home),
                message="The supplied Codex home directory does not exist.",
            )
        )

    enabled_plugins = _load_enabled_plugins(codex_home / "config.toml", issues)
    local_skills = _collect_local_skills(codex_home, issues)
    cached_plugins = _collect_cached_plugins(codex_home, enabled_plugins, issues)
    repo_roots = _discover_repo_roots(
        normalized_roots,
        max_depth=max_depth,
        issues=issues,
        marker_discovery=marker_discovery,
    )
    projects = _collect_project_footprints(repo_roots, issues)
    recent_project_usage, recent_session_count, recent_subagent_session_count, recent_models, recent_agent_roles = _collect_recent_usage(
        codex_home / "sessions",
        recent_usage_days=recent_usage_days,
        issues=issues,
    )

    issues.sort(key=lambda issue: (SEVERITY_RANK[issue.severity], issue.code, issue.path))
    score = _score_issues(issues)
    return SystemAuditReport(
        codex_home=str(codex_home.resolve()) if codex_home.exists() else str(codex_home),
        scan_roots=[str(root) for root in normalized_roots],
        score=score,
        enabled_plugins=enabled_plugins,
        issues=issues,
        local_skills=local_skills,
        cached_plugins=cached_plugins,
        projects=projects,
        recent_usage_days=recent_usage_days,
        recent_project_usage=recent_project_usage,
        recent_session_count=recent_session_count,
        recent_subagent_session_count=recent_subagent_session_count,
        recent_models=recent_models,
        recent_agent_roles=recent_agent_roles,
    )


def _default_scan_roots() -> list[Path]:
    github_root = Path.home() / "Documents" / "GitHub"
    if github_root.exists():
        return [github_root]
    return [Path.cwd()]


def _load_enabled_plugins(config_path: Path, issues: list[AuditIssue]) -> list[str]:
    if not config_path.exists():
        issues.append(
            AuditIssue(
                severity="WARNING",
                code="missing-config",
                path=str(config_path),
                message="No Codex config.toml was found, so enabled plugin keys could not be verified.",
            )
        )
        return []

    enabled: list[str] = []
    current_plugin: str | None = None
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        section_match = PLUGIN_SECTION_PATTERN.match(raw_line)
        if section_match:
            current_plugin = section_match.group("name")
            continue
        if raw_line.startswith("["):
            current_plugin = None
            continue
        if current_plugin is None:
            continue
        enabled_match = ENABLED_PATTERN.match(raw_line)
        if enabled_match and enabled_match.group("value").lower() == "true":
            enabled.append(current_plugin)
    return sorted(set(enabled))


def _collect_local_skills(codex_home: Path, issues: list[AuditIssue]) -> list[LocalSkill]:
    skills_root = codex_home / "skills"
    if not skills_root.exists():
        issues.append(
            AuditIssue(
                severity="ERROR",
                code="missing-skills-root",
                path=str(skills_root),
                message="No ~/.codex/skills directory was found.",
            )
        )
        return []

    local_skills: list[LocalSkill] = []
    seen_ids: set[str] = set()
    for child in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if child.is_symlink() and not child.exists():
            issues.append(
                AuditIssue(
                    severity="ERROR",
                    code="broken-skill-symlink",
                    path=str(child),
                    message="Top-level Codex skill symlink is broken.",
                )
            )

    for current_root, dirnames, filenames in os.walk(skills_root, followlinks=True):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIRS
        ]
        if "SKILL.md" not in filenames:
            continue
        skill_root = Path(current_root)
        relative_parts = skill_root.relative_to(skills_root).parts
        skill_id = "/".join(relative_parts)
        if not skill_id:
            continue
        if skill_id in seen_ids:
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="duplicate-skill-id",
                    path=str(skill_root / "SKILL.md"),
                    message=f"Duplicate skill id `{skill_id}` was discovered while scanning ~/.codex/skills.",
                )
            )
            continue
        seen_ids.add(skill_id)
        top_level = skills_root / relative_parts[0]
        is_symlink = top_level.is_symlink()
        local_skills.append(
            LocalSkill(
                skill_id=skill_id,
                path=str((skill_root / "SKILL.md").resolve()),
                source="codex-home",
                symlink=is_symlink,
                resolved_path=str(skill_root.resolve()) if is_symlink else None,
            )
        )

    if not local_skills:
        issues.append(
            AuditIssue(
                severity="ERROR",
                code="no-local-skills",
                path=str(skills_root),
                message="The ~/.codex/skills directory exists but no SKILL.md files were found.",
            )
        )

    return sorted(local_skills, key=lambda skill: skill.skill_id)


def _collect_cached_plugins(
    codex_home: Path,
    enabled_plugins: list[str],
    issues: list[AuditIssue],
) -> list[CachedPlugin]:
    cache_root = codex_home / "plugins" / "cache"
    if not cache_root.exists():
        issues.append(
            AuditIssue(
                severity="WARNING",
                code="missing-plugin-cache",
                path=str(cache_root),
                message="No plugin cache directory was found under ~/.codex/plugins/cache.",
            )
        )
        return []

    cached_plugins: list[CachedPlugin] = []
    available_keys: set[str] = set()
    for manifest_path in sorted(cache_root.glob("*/*/*/.codex-plugin/plugin.json")):
        relative = manifest_path.relative_to(cache_root)
        marketplace, cache_name, version = relative.parts[:3]
        manifest_root = manifest_path.parent.parent
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(
                AuditIssue(
                    severity="ERROR",
                    code="invalid-plugin-manifest",
                    path=str(manifest_path),
                    message=f"Failed to parse plugin manifest JSON: {exc}",
                )
            )
            continue

        name = str(payload.get("name") or cache_name)
        key = f"{name}@{marketplace}"
        available_keys.add(key)
        available_keys.add(f"{cache_name}@{marketplace}")
        skills_path = payload.get("skills")
        apps_path = payload.get("apps")
        mcp_servers = payload.get("mcpServers")
        has_skills = isinstance(skills_path, str) and (manifest_root / skills_path).exists()
        has_apps = isinstance(apps_path, str) and (manifest_root / apps_path).exists()
        has_mcp_servers = isinstance(mcp_servers, str) and (manifest_root / mcp_servers).exists()

        if skills_path and not has_skills:
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="missing-plugin-skills-path",
                    path=str(manifest_path),
                    message=f"Plugin `{key}` declares a skills directory that was not found.",
                )
            )
        if apps_path and not has_apps:
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="missing-plugin-apps-path",
                    path=str(manifest_path),
                    message=f"Plugin `{key}` declares an app manifest that was not found.",
                )
            )
        if mcp_servers and not has_mcp_servers:
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="missing-plugin-mcp-path",
                    path=str(manifest_path),
                    message=f"Plugin `{key}` declares MCP servers that were not found.",
                )
            )

        cached_plugins.append(
            CachedPlugin(
                name=name,
                key=key,
                version=version,
                marketplace=marketplace,
                path=str(manifest_path),
                enabled=key in enabled_plugins or f"{cache_name}@{marketplace}" in enabled_plugins,
                has_skills=has_skills,
                has_apps=has_apps,
                has_mcp_servers=has_mcp_servers,
            )
        )

    for plugin_key in enabled_plugins:
        if plugin_key not in available_keys:
            issues.append(
                AuditIssue(
                    severity="ERROR",
                    code="missing-enabled-plugin",
                    path=str(cache_root),
                    message=f"Plugin `{plugin_key}` is enabled in config.toml but no cached manifest was found.",
                )
            )

    return cached_plugins


def _discover_repo_roots(
    scan_roots: list[Path],
    *,
    max_depth: int,
    issues: list[AuditIssue],
    marker_discovery: bool,
) -> list[Path]:
    if marker_discovery:
        discovered = _discover_repo_roots_by_markers(scan_roots, issues=issues)
        if discovered:
            return discovered

    discovered: set[Path] = set()
    visited: set[Path] = set()

    for scan_root in scan_roots:
        if not scan_root.exists():
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="missing-scan-root",
                    path=str(scan_root),
                    message="Scan root does not exist and was skipped.",
                )
            )
            continue

        queue: list[tuple[Path, int]] = [(scan_root, 0)]
        while queue:
            current, depth = queue.pop()
            current = current.resolve()
            if current in visited:
                continue
            visited.add(current)

            if (current / ".git").exists():
                discovered.add(current)
                continue
            if depth >= max_depth:
                continue

            try:
                children = sorted(
                    (
                        Path(entry.path)
                        for entry in os.scandir(current)
                        if entry.is_dir(follow_symlinks=False)
                        and entry.name not in SKIP_DIRS
                    ),
                    key=lambda child: child.name,
                    reverse=True,
                )
            except OSError:
                continue

            for child in children:
                queue.append((child, depth + 1))

    return sorted(discovered)


def _discover_repo_roots_by_markers(
    scan_roots: list[Path],
    *,
    issues: list[AuditIssue],
) -> list[Path]:
    discovered: set[Path] = set()

    for scan_root in scan_roots:
        if not scan_root.exists():
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="missing-scan-root",
                    path=str(scan_root),
                    message="Scan root does not exist and was skipped.",
                )
            )
            continue

        for current_root, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = [dirname for dirname in dirnames if dirname not in SKIP_DIRS]
            root_path = Path(current_root)
            marker_hit = False
            if "SKILL.md" in filenames:
                marker_hit = True
            elif root_path.as_posix().endswith("/.codex-plugin") and "plugin.json" in filenames:
                marker_hit = True
            elif root_path.as_posix().endswith("/.agents/plugins") and "marketplace.json" in filenames:
                marker_hit = True
            if not marker_hit:
                continue
            repo_root = _find_git_root(root_path)
            if repo_root:
                discovered.add(repo_root)

    return sorted(discovered)


def _collect_project_footprints(
    repo_roots: list[Path],
    issues: list[AuditIssue],
) -> list[ProjectFootprint]:
    projects: list[ProjectFootprint] = []

    for repo_root in repo_roots:
        local_skill_files: list[str] = []
        plugin_manifest_files: list[str] = []
        marketplace_files: list[str] = []
        external_skill_references: dict[str, set[str]] = {}

        for relative_path in _repo_files(repo_root):
            file_path = repo_root / relative_path
            relative_text = relative_path.as_posix()

            if file_path.name == "SKILL.md":
                local_skill_files.append(relative_text)
            if relative_text == ".codex-plugin/plugin.json" or relative_text.endswith(
                "/.codex-plugin/plugin.json"
            ):
                plugin_manifest_files.append(relative_text)
            if relative_text == ".agents/plugins/marketplace.json" or relative_text.endswith(
                "/.agents/plugins/marketplace.json"
            ):
                marketplace_files.append(relative_text)

            if not _should_scan_text_file(file_path):
                continue

            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for target_path in _extract_skill_references(text):
                external_skill_references.setdefault(target_path, set()).add(relative_text)

        for target_path, source_files in sorted(external_skill_references.items()):
            if not Path(target_path).exists():
                first_source = sorted(source_files)[0]
                issues.append(
                    AuditIssue(
                        severity="ERROR",
                        code="broken-external-skill-reference",
                        path=f"{repo_root}:{first_source}",
                        message=(
                            f"Referenced local skill path does not exist: `{target_path}` "
                            f"(seen in {len(source_files)} file(s))."
                        ),
                    )
                )

        _validate_repo_local_plugins(
            repo_root,
            plugin_manifest_files=plugin_manifest_files,
            marketplace_files=marketplace_files,
            issues=issues,
        )

        if (
            local_skill_files
            or plugin_manifest_files
            or marketplace_files
            or external_skill_references
        ):
            projects.append(
                ProjectFootprint(
                    root=str(repo_root),
                    local_skill_files=sorted(local_skill_files),
                    plugin_manifest_files=sorted(plugin_manifest_files),
                    marketplace_files=sorted(marketplace_files),
                    external_skill_references=sorted(external_skill_references),
                )
            )

    return sorted(projects, key=lambda project: project.root)


def _should_scan_text_file(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_FILE_SUFFIXES:
        return False
    try:
        return path.stat().st_size <= MAX_TEXT_SCAN_BYTES
    except OSError:
        return False


def _repo_files(repo_root: Path) -> list[Path]:
    if shutil.which("rg"):
        try:
            result = subprocess.run(
                [
                    "rg",
                    "--files",
                    "--hidden",
                    *[item for glob in RG_FILE_GLOBS for item in ("-g", glob)],
                    ".",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )
        except (OSError, subprocess.CalledProcessError):
            pass
        else:
            return [
                Path(line)
                for line in result.stdout.splitlines()
                if line
                and _allow_relative_repo_path(Path(line))
            ]

    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in SKIP_DIRS
        ]
        root_path = Path(current_root)
        for filename in filenames:
            relative_path = (root_path / filename).relative_to(repo_root)
            if _allow_relative_repo_path(relative_path) and _relevant_repo_file(relative_path):
                files.append(relative_path)
    return files


def _allow_relative_repo_path(relative_path: Path) -> bool:
    return not any(part in SKIP_DIRS for part in relative_path.parts)


def _relevant_repo_file(relative_path: Path) -> bool:
    relative_text = relative_path.as_posix()
    return (
        relative_path.name == "SKILL.md"
        or relative_text.endswith("/.codex-plugin/plugin.json")
        or relative_text.endswith("/.agents/plugins/marketplace.json")
        or relative_path.suffix.lower() in TEXT_FILE_SUFFIXES
    )


def _extract_skill_references(text: str) -> set[str]:
    references: set[str] = set()
    for match in SKILL_PATH_PATTERN.finditer(text):
        raw_path = match.group("path").rstrip("),.:;]")
        references.add(str(Path(raw_path).expanduser()))
    return references


def _validate_repo_local_plugins(
    repo_root: Path,
    *,
    plugin_manifest_files: list[str],
    marketplace_files: list[str],
    issues: list[AuditIssue],
) -> None:
    if not plugin_manifest_files:
        return

    manifest_names_by_root: dict[str, str] = {}
    for manifest_relative in plugin_manifest_files:
        manifest_path = repo_root / manifest_relative
        try:
            raw_text = manifest_path.read_text(encoding="utf-8")
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            issues.append(
                AuditIssue(
                    severity="ERROR",
                    code="invalid-repo-plugin-manifest",
                    path=f"{repo_root}:{manifest_relative}",
                    message=f"Failed to parse repo-local plugin manifest JSON: {exc}",
                )
            )
            continue

        plugin_root_relative = Path(manifest_relative).parent.parent.as_posix()
        plugin_name = str(payload.get("name") or Path(plugin_root_relative).name)
        manifest_names_by_root[plugin_root_relative] = plugin_name

        _validate_plugin_manifest_payload(
            repo_root,
            manifest_relative,
            plugin_root_relative,
            payload,
            raw_text,
            issues,
        )

    registered_plugin_roots: set[str] = set()
    for marketplace_relative in marketplace_files:
        marketplace_path = repo_root / marketplace_relative
        try:
            payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(
                AuditIssue(
                    severity="ERROR",
                    code="invalid-marketplace-manifest",
                    path=f"{repo_root}:{marketplace_relative}",
                    message=f"Failed to parse marketplace.json: {exc}",
                )
            )
            continue

        for plugin in payload.get("plugins") or []:
            if not isinstance(plugin, dict):
                continue
            source = plugin.get("source") or {}
            source_path = source.get("path")
            if not isinstance(source_path, str):
                continue
            resolved_root = (repo_root / source_path).resolve()
            plugin_root_relative = _safe_relative_to_repo(repo_root, resolved_root)
            if plugin_root_relative is None:
                issues.append(
                    AuditIssue(
                        severity="WARNING",
                        code="marketplace-plugin-outside-repo",
                        path=f"{repo_root}:{marketplace_relative}",
                        message=f"Marketplace entry points outside the repo: `{source_path}`.",
                    )
                )
                continue
            registered_plugin_roots.add(plugin_root_relative)
            if not resolved_root.exists():
                issues.append(
                    AuditIssue(
                        severity="ERROR",
                        code="missing-marketplace-plugin-path",
                        path=f"{repo_root}:{marketplace_relative}",
                        message=f"Marketplace entry points at a missing plugin path: `{source_path}`.",
                    )
                )
                continue
            manifest_name = manifest_names_by_root.get(plugin_root_relative)
            marketplace_name = plugin.get("name")
            if manifest_name and marketplace_name and manifest_name != marketplace_name:
                issues.append(
                    AuditIssue(
                        severity="WARNING",
                        code="marketplace-plugin-name-mismatch",
                        path=f"{repo_root}:{marketplace_relative}",
                        message=(
                            f"Marketplace entry `{marketplace_name}` does not match plugin manifest name "
                            f"`{manifest_name}` for `{plugin_root_relative}`."
                        ),
                    )
                )

    if not marketplace_files:
        issues.append(
            AuditIssue(
                severity="WARNING",
                code="repo-plugin-no-marketplace",
                path=str(repo_root),
                message="Repo contains plugin manifests but no `.agents/plugins/marketplace.json` file.",
            )
        )
        return

    for plugin_root_relative, plugin_name in sorted(manifest_names_by_root.items()):
        if plugin_root_relative not in registered_plugin_roots:
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code="repo-plugin-not-in-marketplace",
                    path=f"{repo_root}:{plugin_root_relative}/.codex-plugin/plugin.json",
                    message=f"Repo-local plugin `{plugin_name}` is not registered in the repo marketplace file.",
                )
            )


def _validate_plugin_manifest_payload(
    repo_root: Path,
    manifest_relative: str,
    plugin_root_relative: str,
    payload: dict[str, object],
    raw_text: str,
    issues: list[AuditIssue],
) -> None:
    plugin_root = repo_root / plugin_root_relative
    plugin_name = str(payload.get("name") or Path(plugin_root_relative).name)
    manifest_path = f"{repo_root}:{manifest_relative}"

    if TODO_PATTERN.search(raw_text):
        issues.append(
            AuditIssue(
                severity="WARNING",
                code="repo-plugin-placeholder-metadata",
                path=manifest_path,
                message=f"Repo-local plugin `{plugin_name}` still contains placeholder TODO metadata.",
            )
        )

    for field_name, code in (
        ("skills", "missing-repo-plugin-skills-path"),
        ("apps", "missing-repo-plugin-apps-path"),
        ("hooks", "missing-repo-plugin-hooks-path"),
        ("mcpServers", "missing-repo-plugin-mcp-path"),
    ):
        field_value = payload.get(field_name)
        if not isinstance(field_value, str):
            continue
        if not (plugin_root / field_value).exists():
            issues.append(
                AuditIssue(
                    severity="WARNING",
                    code=code,
                    path=manifest_path,
                    message=f"Repo-local plugin `{plugin_name}` declares `{field_name}` at `{field_value}`, but that path was not found.",
                )
            )


def _safe_relative_to_repo(repo_root: Path, path: Path) -> str | None:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None


def _collect_recent_usage(
    session_root: Path,
    *,
    recent_usage_days: int,
    issues: list[AuditIssue],
) -> tuple[list[ProjectUsage], int, int, dict[str, int], dict[str, int]]:
    if not session_root.exists():
        issues.append(
            AuditIssue(
                severity="WARNING",
                code="missing-session-root",
                path=str(session_root),
                message="No ~/.codex/sessions directory was found, so recent usage could not be summarized.",
            )
        )
        return [], 0, 0, {}, {}

    today = datetime.now(timezone.utc).date()
    start_day = today - timedelta(days=max(recent_usage_days - 1, 0))
    usage_by_root: dict[str, ProjectUsage] = {}
    model_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    session_count = 0
    subagent_session_count = 0

    for session_path in _recent_session_files(session_root, start_day, today):
        cwd, is_subagent, agent_role, model = _read_session_details(session_path)
        if not cwd:
            continue

        session_count += 1
        if is_subagent:
            subagent_session_count += 1

        resolved_cwd = Path(cwd).expanduser()
        repo_root = _find_git_root(resolved_cwd) or resolved_cwd
        project_key = str(repo_root)
        project_name = repo_root.name or project_key
        usage = usage_by_root.get(project_key)
        session_day = _date_from_session_path(session_path)
        last_session = session_day.isoformat() if session_day else ""
        if usage is None:
            usage = ProjectUsage(
                name=project_name,
                root=project_key,
                sessions=0,
                subagent_sessions=0,
                last_session=last_session,
            )
            usage_by_root[project_key] = usage
        usage.sessions += 1
        if is_subagent:
            usage.subagent_sessions += 1
        if last_session and last_session > usage.last_session:
            usage.last_session = last_session

        role_counts[agent_role or "default"] += 1
        if model:
            model_counts[model] += 1

    ranked_projects = sorted(
        usage_by_root.values(),
        key=lambda project: (-project.sessions, project.name, project.root),
    )
    return (
        ranked_projects,
        session_count,
        subagent_session_count,
        dict(model_counts.most_common()),
        dict(role_counts.most_common()),
    )


def _recent_session_files(session_root: Path, start_day: date, end_day: date) -> list[Path]:
    session_files: list[Path] = []
    current = start_day
    while current <= end_day:
        day_dir = session_root / f"{current.year:04d}" / f"{current.month:02d}" / f"{current.day:02d}"
        if day_dir.exists():
            session_files.extend(sorted(day_dir.glob("*.jsonl")))
        current += timedelta(days=1)
    return session_files


def _read_session_details(path: Path) -> tuple[str | None, bool, str | None, str | None]:
    cwd: str | None = None
    is_subagent = False
    agent_role: str | None = None
    model: str | None = None

    try:
        with path.open("r", encoding="utf-8") as handle:
            for index, raw_line in enumerate(handle):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                item_type = payload.get("type")
                data = payload.get("payload") or {}
                if item_type == "session_meta" and isinstance(data, dict):
                    cwd = data.get("cwd")
                    source = data.get("source")
                    source_payload = source if isinstance(source, dict) else {}
                    is_subagent = bool(source_payload.get("subagent"))
                    agent_role = data.get("agent_role")
                elif item_type == "turn_context" and isinstance(data, dict):
                    model = data.get("model")
                    if cwd:
                        break
                if index >= 40 and cwd:
                    break
    except OSError:
        return None, False, None, None

    return cwd, is_subagent, agent_role, model


def _find_git_root(path: Path) -> Path | None:
    current = path if path.is_dir() else path.parent
    current = current.expanduser()
    while True:
        if (current / ".git").exists():
            return current.resolve()
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _date_from_session_path(path: Path) -> date | None:
    parts = path.parts
    if len(parts) < 4:
        return None
    try:
        return date(int(parts[-4]), int(parts[-3]), int(parts[-2]))
    except ValueError:
        return None


def _score_issues(issues: list[AuditIssue]) -> int:
    score = 100
    penalties = {
        "missing-codex-home": (40, 40),
        "missing-skills-root": (30, 30),
        "no-local-skills": (20, 20),
        "broken-skill-symlink": (10, 20),
        "invalid-plugin-manifest": (10, 20),
        "missing-enabled-plugin": (10, 30),
        "missing-plugin-cache": (15, 15),
        "missing-plugin-skills-path": (4, 12),
        "missing-plugin-apps-path": (4, 12),
        "missing-plugin-mcp-path": (4, 12),
        "invalid-repo-plugin-manifest": (10, 20),
        "invalid-marketplace-manifest": (10, 20),
        "missing-repo-plugin-skills-path": (4, 12),
        "missing-repo-plugin-apps-path": (4, 12),
        "missing-repo-plugin-hooks-path": (4, 12),
        "missing-repo-plugin-mcp-path": (4, 12),
        "repo-plugin-placeholder-metadata": (5, 15),
        "repo-plugin-no-marketplace": (5, 10),
        "repo-plugin-not-in-marketplace": (5, 15),
        "missing-marketplace-plugin-path": (6, 18),
        "marketplace-plugin-name-mismatch": (3, 9),
        "marketplace-plugin-outside-repo": (3, 9),
        "broken-external-skill-reference": (4, 24),
        "missing-config": (5, 5),
        "missing-scan-root": (3, 9),
        "missing-session-root": (5, 5),
        "duplicate-skill-id": (3, 12),
    }
    counts = Counter(issue.code for issue in issues)
    for code, count in counts.items():
        amount, cap = penalties.get(code, (2, 10))
        score -= min(amount * count, cap)
    return max(score, 0)
