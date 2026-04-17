from __future__ import annotations

from pathlib import Path

from codex_harness.audit import audit_repository
from codex_harness.templates import derive_project_name, scaffold_files


def _write_scaffold(root: Path, project_name: str = "Demo Repo") -> None:
    for item in scaffold_files(project_name):
        target = root / item.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item.content, encoding="utf-8")


def _write_publishable_repo(root: Path) -> None:
    _write_scaffold(root, project_name="Acme")
    (root / "README.md").write_text(
        "\n".join(
            [
                "# Acme",
                "",
                "Security issues should be reported through SECURITY.md.",
                "",
                "## Quick Start",
                "",
                "Run `python -m acme --help`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (root / "SECURITY.md").write_text("# Security\n", encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text("# Contributing\n", encoding="utf-8")
    (root / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    tests_dir = root / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "test_smoke.py").write_text("def test_smoke():\n    assert True\n", encoding="utf-8")
    workflows_dir = root / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    (workflows_dir / "ci.yml").write_text(
        "\n".join(
            [
                "name: ci",
                "on:",
                "  pull_request:",
                "jobs:",
                "  audit:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - run: python -m codex_harness audit . --strict --min-score 90",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    pr_template = root / ".github" / "pull_request_template.md"
    pr_template.write_text(
        "\n".join(
            [
                "## Validation",
                "",
                "- [ ] `python -m codex_harness audit . --strict --min-score 90`",
                "- [ ] Security and leak review completed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_derive_project_name_normalizes_path() -> None:
    assert derive_project_name(Path("codex-harness-kit")) == "Codex Harness Kit"
    assert derive_project_name(Path("codex_harness")) == "Codex Harness"


def test_scaffold_files_include_expected_paths() -> None:
    paths = {item.path for item in scaffold_files("Acme")}
    assert "AGENTS.md" in paths
    assert ".codex/agents/architect.toml" in paths
    assert ".codex/agents/reviewer.toml" in paths
    assert "docs/codex/evals.md" in paths


def test_audit_repository_flags_missing_harness(tmp_path: Path) -> None:
    report = audit_repository(tmp_path)

    assert report.score < 100
    assert report.has_errors
    codes = {issue.code for issue in report.issues}
    assert "missing-agents-md" in codes
    assert "missing-custom-agents" in codes


def test_audit_repository_accepts_generated_scaffold(tmp_path: Path) -> None:
    _write_scaffold(tmp_path, project_name="Acme")

    report = audit_repository(tmp_path)

    assert report.score == 100
    assert not report.issues


def test_audit_repository_flags_publishable_repo_gaps(tmp_path: Path) -> None:
    _write_scaffold(tmp_path, project_name="Acme")
    (tmp_path / "README.md").write_text("# Acme\n", encoding="utf-8")

    report = audit_repository(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert "missing-license" in codes
    assert "missing-security-policy" in codes
    assert "missing-ci-workflow" in codes


def test_audit_repository_detects_secret_and_bleed_markers(tmp_path: Path) -> None:
    _write_publishable_repo(tmp_path)
    (tmp_path / ".env").write_text("TOKEN=1\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text(
        "\n".join(
            [
                "Token: ghp_abcdefghijklmnopqrstuvwxyz123456",  # codex-harness: allow-secret
                "Path: /Users/zack/private/report.md",  # codex-harness: allow-bleed
                "URL: http://localhost:3000/dashboard",  # codex-harness: allow-bleed
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = audit_repository(tmp_path)

    codes = {issue.code for issue in report.issues}
    assert "tracked-env-file" in codes
    assert "github-token" in codes
    assert "private-path" in codes
    assert "private-url" in codes


def test_audit_repository_allows_inline_secret_and_bleed_markers(tmp_path: Path) -> None:
    _write_publishable_repo(tmp_path)
    (tmp_path / "notes.txt").write_text(
        "\n".join(
            [
                "Token: ghp_abcdefghijklmnopqrstuvwxyz123456  # codex-harness: allow-secret",  # codex-harness: allow-secret
                "URL: http://localhost:3000/dashboard  # codex-harness: allow-bleed",  # codex-harness: allow-bleed
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = audit_repository(tmp_path)

    assert report.score == 100
    assert not report.issues


def test_audit_repository_accepts_hardened_publishable_repo(tmp_path: Path) -> None:
    _write_publishable_repo(tmp_path)

    report = audit_repository(tmp_path)

    assert report.score == 100
    assert not report.issues
