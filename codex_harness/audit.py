from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re


EXPECTED_AGENT_FILES = {
    "architect.toml",
    "cleanup.toml",
    "evolver.toml",
    "implementer.toml",
    "reviewer.toml",
}
EXPECTED_DOC_FILES = {
    "architecture.md",
    "cleanup.md",
    "evals.md",
    "overview.md",
    "workflow.md",
}
SEVERITY_RANK = {"ERROR": 0, "WARNING": 1}
PUBLISHABLE_MARKER_PATHS = (
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
    ".github/workflows",
)
SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".venv310",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
TEXT_FILE_SUFFIXES = {
    ".cfg",
    ".cff",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".lock",
    ".md",
    ".py",
    ".pyi",
    ".sh",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
TRACKED_CREDENTIAL_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
TRACKED_CREDENTIAL_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
TRACKED_RUNTIME_SUFFIXES = {".db", ".log", ".sqlite"}
ALLOW_SECRET_MARKER = "codex-harness: allow-secret"
ALLOW_BLEED_MARKER = "codex-harness: allow-bleed"
README_QUICKSTART_TOKENS = ("quick start", "quickstart", "install", "usage")
SECURITY_DISCLOSURE_TOKENS = ("security", "responsible disclosure", "vulnerability")
CI_GATE_TOKENS = (
    "codex-harness audit",
    "codex_harness audit",
    "codeql",
    "gitleaks",
    "secret",
    "security",
)

SECRET_PATTERNS: tuple[tuple[str, str, re.Pattern[str], str, int], ...] = (
    (
        "private-key-block",
        "ERROR",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "Private key material is committed.",
        30,
    ),
    (
        "github-token",
        "ERROR",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
        "A GitHub token-like string is committed.",
        25,
    ),
    (
        "github-pat",
        "ERROR",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
        "A GitHub fine-grained token-like string is committed.",
        25,
    ),
    (
        "openai-key",
        "ERROR",
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        "An API key-like string is committed.",
        25,
    ),
    (
        "aws-access-key",
        "ERROR",
        re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
        "An AWS access key-like string is committed.",
        25,
    ),
)

BLEED_PATTERNS: tuple[tuple[str, str, re.Pattern[str], str, int], ...] = (
    (
        "private-path",
        "WARNING",
        re.compile(
            r"(?:(?:/Users|/home)/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._ -]+\\)"
        ),
        "A private workstation path leaked into the public surface.",
        8,
    ),
    (
        "private-url",
        "WARNING",
        re.compile(
            r"\bhttps?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|"
            r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"192\.168\.\d{1,3}\.\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})"
            r"[^\s)\]}]*"
        ),
        "A local or private URL leaked into the public surface.",
        8,
    ),
    (
        "internal-host",
        "WARNING",
        re.compile(r"\bhttps?://[A-Za-z0-9.-]+\.(?:local|internal|corp|lan)\b"),
        "An internal hostname leaked into the public surface.",
        8,
    ),
)


@dataclass(slots=True)
class AuditIssue:
    severity: str
    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class AuditReport:
    root: str
    score: int
    issues: list[AuditIssue]

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "ERROR" for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "score": self.score,
            "issue_count": self.issue_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_text(self) -> str:
        lines = [
            f"Codex Harness audit for {self.root}",
            f"score={self.score}/100 issues={self.issue_count}",
        ]
        for issue in self.issues:
            lines.append(
                f"- {issue.severity} {issue.code} {issue.path}: {issue.message}"
            )
        return "\n".join(lines)

    def to_markdown(self) -> str:
        lines = [
            f"# Codex Harness audit for `{self.root}`",
            "",
            f"- score: **{self.score}/100**",
            f"- issues: **{self.issue_count}**",
            "",
        ]
        if not self.issues:
            lines.append("No issues found.")
            return "\n".join(lines)

        for issue in self.issues:
            lines.append(
                f"- **{issue.severity} `{issue.code}`** `{issue.path}`: {issue.message}"
            )
        return "\n".join(lines)


def audit_repository(root: Path) -> AuditReport:
    root = root.resolve()
    issues: list[AuditIssue] = []
    score = 100

    def add_issue(
        severity: str,
        code: str,
        path: str,
        message: str,
        penalty: int,
    ) -> None:
        nonlocal score
        score -= penalty
        issues.append(
            AuditIssue(
                severity=severity,
                code=code,
                path=path,
                message=message,
            )
        )

    agents_path = root / ".codex" / "agents"
    docs_path = root / "docs" / "codex"
    agents_md_path = root / "AGENTS.md"

    if not agents_md_path.exists():
        add_issue(
            severity="ERROR",
            code="missing-agents-md",
            path="AGENTS.md",
            message="Missing AGENTS.md index. Start with a repo map, not a hidden prompt blob.",
            penalty=30,
        )
    else:
        agents_md_text = agents_md_path.read_text(encoding="utf-8")
        agent_lines = len(agents_md_text.splitlines())
        if "docs/codex/" not in agents_md_text:
            add_issue(
                severity="WARNING",
                code="agents-md-missing-map",
                path="AGENTS.md",
                message="AGENTS.md should link to durable docs under docs/codex/.",
                penalty=10,
            )
        if ".codex/agents/" not in agents_md_text:
            add_issue(
                severity="WARNING",
                code="agents-md-missing-custom-agents",
                path="AGENTS.md",
                message="AGENTS.md should mention the project-scoped custom agents.",
                penalty=5,
            )
        if "verif" not in agents_md_text.lower():
            add_issue(
                severity="WARNING",
                code="agents-md-missing-verification",
                path="AGENTS.md",
                message="AGENTS.md should make verification part of the default loop.",
                penalty=5,
            )
        if agent_lines > 180:
            add_issue(
                severity="WARNING",
                code="agents-md-too-large",
                path="AGENTS.md",
                message="AGENTS.md is getting large. Use it as a table of contents, not the full manual.",
                penalty=10,
            )

    if not agents_path.exists():
        add_issue(
            severity="ERROR",
            code="missing-custom-agents",
            path=".codex/agents",
            message="No project-scoped custom agents were found.",
            penalty=30,
        )
    else:
        agent_files = {path.name for path in agents_path.glob("*.toml")}
        if not agent_files:
            add_issue(
                severity="ERROR",
                code="empty-custom-agents",
                path=".codex/agents",
                message="The .codex/agents directory exists but contains no TOML agent files.",
                penalty=30,
            )
        elif len(agent_files) < 3:
            add_issue(
                severity="WARNING",
                code="few-custom-agents",
                path=".codex/agents",
                message="Add a few focused agents instead of routing everything through one generic role.",
                penalty=10,
            )

        missing_agents = sorted(EXPECTED_AGENT_FILES - agent_files)
        if missing_agents:
            add_issue(
                severity="WARNING",
                code="missing-opinionated-agents",
                path=".codex/agents",
                message="Missing starter roles: " + ", ".join(missing_agents),
                penalty=min(15, len(missing_agents) * 3),
            )

    if not docs_path.exists():
        add_issue(
            severity="WARNING",
            code="missing-codex-docs",
            path="docs/codex",
            message="Missing docs/codex/. Durable repo knowledge should be versioned and discoverable.",
            penalty=20,
        )
    else:
        doc_files = {path.name for path in docs_path.glob("*.md")}
        missing_docs = sorted(EXPECTED_DOC_FILES - doc_files)
        if missing_docs:
            add_issue(
                severity="WARNING",
                code="missing-codex-docs",
                path="docs/codex",
                message="Missing starter docs: " + ", ".join(missing_docs),
                penalty=min(20, len(missing_docs) * 4),
            )

        evals_path = docs_path / "evals.md"
        if evals_path.exists():
            evals_text = evals_path.read_text(encoding="utf-8").lower()
            if "metric" not in evals_text and "check" not in evals_text:
                add_issue(
                    severity="WARNING",
                    code="weak-evals-doc",
                    path="docs/codex/evals.md",
                    message="The evals doc should name metrics or concrete checks.",
                    penalty=5,
                )

        cleanup_path = docs_path / "cleanup.md"
        if cleanup_path.exists():
            cleanup_text = cleanup_path.read_text(encoding="utf-8").lower()
            if "weekly" not in cleanup_text and "cadence" not in cleanup_text:
                add_issue(
                    severity="WARNING",
                    code="weak-cleanup-doc",
                    path="docs/codex/cleanup.md",
                    message="The cleanup doc should define a cadence for entropy reduction.",
                    penalty=5,
                )

    if _is_publishable_repo(root):
        _audit_publishable_surface(root, add_issue)

    _scan_tracked_surface(root, add_issue)

    issues.sort(key=lambda issue: (SEVERITY_RANK[issue.severity], issue.code, issue.path))
    return AuditReport(root=str(root), score=max(score, 0), issues=issues)


def _is_publishable_repo(root: Path) -> bool:
    return any((root / marker).exists() for marker in PUBLISHABLE_MARKER_PATHS)


def _audit_publishable_surface(
    root: Path,
    add_issue,
) -> None:
    readme_path = root / "README.md"
    if not readme_path.exists():
        add_issue(
            severity="ERROR",
            code="missing-readme",
            path="README.md",
            message="Open-source repos need a README with the user-facing story and first-run path.",
            penalty=20,
        )
    else:
        _audit_readme(readme_path, add_issue)

    if not (root / "LICENSE").exists():
        add_issue(
            severity="ERROR",
            code="missing-license",
            path="LICENSE",
            message="Open-source repos need an explicit license before they go public.",
            penalty=20,
        )

    if not (root / ".gitignore").exists():
        add_issue(
            severity="WARNING",
            code="missing-gitignore",
            path=".gitignore",
            message="Missing .gitignore. Release repos need guardrails against committing runtime junk.",
            penalty=8,
        )

    if not (root / "SECURITY.md").exists():
        add_issue(
            severity="WARNING",
            code="missing-security-policy",
            path="SECURITY.md",
            message="Add a security policy before publishing the repository.",
            penalty=8,
        )

    if not (root / "CONTRIBUTING.md").exists():
        add_issue(
            severity="WARNING",
            code="missing-contributing",
            path="CONTRIBUTING.md",
            message="Open-source repos should explain contribution expectations and local validation.",
            penalty=5,
        )

    if not _has_tests(root):
        add_issue(
            severity="WARNING",
            code="missing-tests",
            path="tests",
            message="No obvious test suite was found. Strict review gates need at least one regression ratchet.",
            penalty=10,
        )

    workflow_paths = sorted((root / ".github" / "workflows").glob("*.y*ml"))
    if not workflow_paths:
        add_issue(
            severity="WARNING",
            code="missing-ci-workflow",
            path=".github/workflows",
            message="Add a CI workflow so review and release gates run on pull requests.",
            penalty=10,
        )
    else:
        _audit_workflows(root, workflow_paths, add_issue)

    pr_template_path = root / ".github" / "pull_request_template.md"
    if not pr_template_path.exists():
        add_issue(
            severity="WARNING",
            code="missing-pr-template",
            path=".github/pull_request_template.md",
            message="Add a pull request template that forces validation and security review notes.",
            penalty=5,
        )
    else:
        _audit_pr_template(pr_template_path, add_issue)


def _audit_readme(readme_path: Path, add_issue) -> None:
    readme_text = readme_path.read_text(encoding="utf-8").lower()
    if not any(token in readme_text for token in README_QUICKSTART_TOKENS):
        add_issue(
            severity="WARNING",
            code="readme-missing-quickstart",
            path="README.md",
            message="README.md should include install or quick-start instructions.",
            penalty=5,
        )
    if not any(token in readme_text for token in SECURITY_DISCLOSURE_TOKENS):
        add_issue(
            severity="WARNING",
            code="readme-missing-security-link",
            path="README.md",
            message="README.md should point readers at the security policy or responsible disclosure path.",
            penalty=3,
        )


def _audit_workflows(root: Path, workflow_paths: list[Path], add_issue) -> None:
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8") for path in workflow_paths if path.exists()
    ).lower()
    if "pull_request" not in workflow_text:
        add_issue(
            severity="WARNING",
            code="ci-missing-pr-trigger",
            path=".github/workflows",
            message="CI workflows should run on pull requests, not only after merge.",
            penalty=5,
        )
    if not any(token in workflow_text for token in CI_GATE_TOKENS):
        rel_path = workflow_paths[0].relative_to(root).as_posix()
        add_issue(
            severity="WARNING",
            code="ci-missing-publish-gate",
            path=rel_path,
            message="CI should enforce a release gate such as codex-harness audit, CodeQL, or secret scanning.",
            penalty=8,
        )


def _audit_pr_template(pr_template_path: Path, add_issue) -> None:
    template_text = pr_template_path.read_text(encoding="utf-8").lower()
    if "security" not in template_text or "leak" not in template_text:
        add_issue(
            severity="WARNING",
            code="pr-template-missing-security-checks",
            path=".github/pull_request_template.md",
            message="The PR template should force authors to confirm security, leak, and public-surface review.",
            penalty=5,
        )
    if "codex-harness audit" not in template_text and "codex_harness audit" not in template_text:
        add_issue(
            severity="WARNING",
            code="pr-template-missing-audit-check",
            path=".github/pull_request_template.md",
            message="The PR template should name the release gate command explicitly.",
            penalty=4,
        )


def _has_tests(root: Path) -> bool:
    for candidate in ("tests", "test", "spec"):
        candidate_path = root / candidate
        if candidate_path.exists():
            return True
    return any(root.rglob("test_*.py"))


def _scan_tracked_surface(root: Path, add_issue) -> None:
    for path in _iter_repo_files(root):
        rel_path = path.relative_to(root).as_posix()
        _audit_filename(path, rel_path, add_issue)
        text = _read_text_if_textual(path)
        if text is None:
            continue
        _audit_text(path=path, rel_path=rel_path, text=text, add_issue=add_issue)


def _iter_repo_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def _audit_filename(path: Path, rel_path: str, add_issue) -> None:
    suffix = path.suffix.lower()
    name = path.name

    if name.startswith(".env") and name not in {".env.example", ".env.sample", ".env.template"}:
        add_issue(
            severity="ERROR",
            code="tracked-env-file",
            path=rel_path,
            message="Tracked .env files should stay out of public repositories.",
            penalty=20,
        )
        return

    if name in TRACKED_CREDENTIAL_NAMES or suffix in TRACKED_CREDENTIAL_SUFFIXES:
        add_issue(
            severity="ERROR",
            code="tracked-credential-file",
            path=rel_path,
            message="Credential or key material appears to be committed.",
            penalty=20,
        )
        return

    if suffix in TRACKED_RUNTIME_SUFFIXES:
        add_issue(
            severity="WARNING",
            code="tracked-runtime-artifact",
            path=rel_path,
            message="Runtime artifacts such as logs and local databases should not ship in the public repo.",
            penalty=5,
        )


def _read_text_if_textual(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_FILE_SUFFIXES and path.name not in {
        ".gitignore",
        "LICENSE",
        "AGENTS.md",
    }:
        return None
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _audit_text(path: Path, rel_path: str, text: str, add_issue) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_SECRET_MARKER not in line:
            for code, severity, pattern, message, penalty in SECRET_PATTERNS:
                match = pattern.search(line)
                if match and not _looks_placeholder(match.group(0)):
                    add_issue(
                        severity=severity,
                        code=code,
                        path=rel_path,
                        message=f"{message} Line {line_number}.",
                        penalty=penalty,
                    )
                    break
        if ALLOW_BLEED_MARKER not in line:
            for code, severity, pattern, message, penalty in BLEED_PATTERNS:
                if pattern.search(line):
                    add_issue(
                        severity=severity,
                        code=code,
                        path=rel_path,
                        message=f"{message} Line {line_number}.",
                        penalty=penalty,
                    )
                    break


def _looks_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(
        marker in lowered
        for marker in ("example", "placeholder", "replace-me", "your_", "dummy", "test")
    )
