from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from codex_harness.system_audit import audit_local_codex_environment


def _write_plugin_manifest(
    codex_home: Path,
    *,
    marketplace: str = "openai-curated",
    name: str = "github",
    version: str = "abc123",
) -> None:
    plugin_root = (
        codex_home
        / "plugins"
        / "cache"
        / marketplace
        / name
        / version
    )
    (plugin_root / ".codex-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_root / "skills").mkdir(parents=True, exist_ok=True)
    (plugin_root / ".app.json").write_text("{}", encoding="utf-8")
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        """
        {
          "name": "github",
          "version": "0.1.0",
          "skills": "./skills",
          "apps": "./.app.json"
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )


def _write_session_file(session_root: Path, cwd: Path, *, agent_role: str = "reviewer") -> None:
    today = datetime.now(timezone.utc).date()
    day_dir = session_root / f"{today.year:04d}" / f"{today.month:02d}" / f"{today.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    session_path = day_dir / "rollout-test.jsonl"
    session_path.write_text(
        "\n".join(
            [
                (
                    '{"timestamp":"2026-04-17T00:00:00Z","type":"session_meta","payload":'
                    f'{{"cwd":"{cwd}","source":{{}},"agent_role":"{agent_role}"}}'
                    "}"
                ),
                '{"timestamp":"2026-04-17T00:00:01Z","type":"turn_context","payload":{"model":"gpt-5.4"}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_system_audit_reports_available_assets(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    skills_root = codex_home / "skills" / "demo-skill"
    skills_root.mkdir(parents=True)
    (skills_root / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
    (codex_home / "config.toml").write_text(
        '\n'.join(
            [
                '[plugins."github@openai-curated"]',
                "enabled = true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_plugin_manifest(codex_home)

    repo_root = tmp_path / "repos" / "acme"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "skills" / "local-demo").mkdir(parents=True)
    (repo_root / "skills" / "local-demo" / "SKILL.md").write_text(
        "# Local Demo\n",
        encoding="utf-8",
    )
    (repo_root / "docs").mkdir(parents=True)
    (repo_root / "docs" / "notes.md").write_text(
        f"See `{skills_root / 'SKILL.md'}` for the shared playbook.\n",
        encoding="utf-8",
    )

    _write_session_file(codex_home / "sessions", repo_root)

    report = audit_local_codex_environment(
        codex_home,
        scan_roots=[tmp_path / "repos"],
        recent_usage_days=30,
    )

    assert report.score == 100
    assert not report.issues
    assert len(report.local_skills) == 1
    assert report.local_skills[0].skill_id == "demo-skill"
    assert len(report.cached_plugins) == 1
    assert report.cached_plugins[0].enabled
    assert len(report.projects) == 1
    assert report.projects[0].local_skill_files == ["skills/local-demo/SKILL.md"]
    assert report.external_skill_reference_count == 1
    assert report.recent_session_count == 1
    assert report.recent_project_usage[0].name == "acme"
    assert report.recent_models == {"gpt-5.4": 1}
    assert report.recent_agent_roles == {"reviewer": 1}


def test_system_audit_flags_broken_external_skill_reference(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    (codex_home / "skills" / "demo-skill").mkdir(parents=True)
    (codex_home / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# Demo\n",
        encoding="utf-8",
    )

    repo_root = tmp_path / "repos" / "broken"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "docs").mkdir(parents=True)
    (repo_root / "docs" / "bad.md").write_text(
        "Use `/Users/zack/.codex/skills/missing-skill/SKILL.md` when this run lands.\n",
        encoding="utf-8",
    )

    report = audit_local_codex_environment(
        codex_home,
        scan_roots=[tmp_path / "repos"],
        recent_usage_days=1,
    )

    assert report.has_errors
    assert any(
        issue.code == "broken-external-skill-reference" for issue in report.issues
    )
    assert report.score < 100


def test_system_audit_accepts_string_session_source(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    (codex_home / "skills" / "demo-skill").mkdir(parents=True)
    (codex_home / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# Demo\n",
        encoding="utf-8",
    )

    repo_root = tmp_path / "repos" / "string-source"
    (repo_root / ".git").mkdir(parents=True)

    today = datetime.now(timezone.utc).date()
    day_dir = codex_home / "sessions" / f"{today.year:04d}" / f"{today.month:02d}" / f"{today.day:02d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    (day_dir / "rollout-string-source.jsonl").write_text(
        "\n".join(
            [
                (
                    '{"timestamp":"2026-04-17T00:00:00Z","type":"session_meta","payload":'
                    f'{{"cwd":"{repo_root}","source":"desktop"}}'
                    "}"
                ),
                '{"timestamp":"2026-04-17T00:00:01Z","type":"turn_context","payload":{"model":"gpt-5.4"}}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = audit_local_codex_environment(
        codex_home,
        scan_roots=[tmp_path / "repos"],
        recent_usage_days=7,
    )

    assert report.recent_session_count == 1
    assert report.recent_project_usage[0].name == "string-source"


def test_system_audit_marker_discovery_finds_only_codex_repos(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    (codex_home / "skills" / "demo-skill").mkdir(parents=True)
    (codex_home / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# Demo\n",
        encoding="utf-8",
    )

    codex_repo = tmp_path / "workspace" / "codex-repo"
    (codex_repo / ".git").mkdir(parents=True)
    (codex_repo / "skills" / "demo").mkdir(parents=True)
    (codex_repo / "skills" / "demo" / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    plain_repo = tmp_path / "workspace" / "plain-repo"
    (plain_repo / ".git").mkdir(parents=True)
    (plain_repo / "README.md").write_text("# Plain\n", encoding="utf-8")

    report = audit_local_codex_environment(
        codex_home,
        scan_roots=[tmp_path / "workspace"],
        marker_discovery=True,
    )

    assert [Path(project.root).name for project in report.projects] == ["codex-repo"]


def test_system_audit_flags_repo_plugin_placeholder_metadata(tmp_path: Path) -> None:
    codex_home = tmp_path / ".codex"
    (codex_home / "skills" / "demo-skill").mkdir(parents=True)
    (codex_home / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# Demo\n",
        encoding="utf-8",
    )

    repo_root = tmp_path / "repos" / "plugin-repo"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / ".agents" / "plugins").mkdir(parents=True)
    (repo_root / ".agents" / "plugins" / "marketplace.json").write_text(
        """
        {
          "name": "local-market",
          "plugins": [
            {
              "name": "demo-plugin",
              "source": {
                "source": "local",
                "path": "./plugins/demo-plugin"
              }
            }
          ]
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )
    plugin_root = repo_root / "plugins" / "demo-plugin"
    (plugin_root / ".codex-plugin").mkdir(parents=True)
    (plugin_root / "skills").mkdir(parents=True)
    (plugin_root / ".codex-plugin" / "plugin.json").write_text(
        """
        {
          "name": "demo-plugin",
          "author": {
            "name": "[TODO: Author Name]"
          },
          "homepage": "[TODO: https://example.com/demo-plugin]",
          "skills": "./skills"
        }
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    report = audit_local_codex_environment(
        codex_home,
        scan_roots=[tmp_path / "repos"],
    )

    assert any(
        issue.code == "repo-plugin-placeholder-metadata" for issue in report.issues
    )
    assert not any(
        issue.code == "marketplace-plugin-outside-repo" for issue in report.issues
    )
    assert not any(
        issue.code == "repo-plugin-not-in-marketplace" for issue in report.issues
    )
