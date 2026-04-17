from __future__ import annotations

import json
from pathlib import Path

from codex_harness import cli


def test_main_init_writes_scaffold(monkeypatch, tmp_path: Path, capsys) -> None:
    target = tmp_path / "acme-repo"

    monkeypatch.setattr("sys.argv", ["codex-harness", "init", str(target)])

    assert cli.main() == 0
    assert (target / "AGENTS.md").exists()
    assert (target / ".codex" / "agents" / "reviewer.toml").exists()
    assert (target / "docs" / "codex" / "overview.md").exists()

    output = capsys.readouterr().out
    assert "Initialized Codex harness" in output


def test_main_init_refuses_to_overwrite_without_force(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    target = tmp_path / "acme-repo"
    target.mkdir()
    (target / "AGENTS.md").write_text("existing\n", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["codex-harness", "init", str(target)])

    assert cli.main() == 1

    output = capsys.readouterr().out
    assert "Refusing to overwrite existing Codex harness files" in output


def test_main_audit_emits_json(monkeypatch, tmp_path: Path, capsys) -> None:
    target = tmp_path / "acme-repo"

    monkeypatch.setattr("sys.argv", ["codex-harness", "init", str(target)])
    assert cli.main() == 0
    capsys.readouterr()

    monkeypatch.setattr(
        "sys.argv",
        ["codex-harness", "audit", str(target), "--format", "json"],
    )

    assert cli.main() == 0

    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["score"] == 100
    assert payload["issue_count"] == 0


def test_main_audit_strict_fails_when_errors_exist(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["codex-harness", "audit", str(tmp_path), "--strict"],
    )

    assert cli.main() == 1

    output = capsys.readouterr().out
    assert "missing-agents-md" in output


def test_main_system_audit_emits_json(monkeypatch, tmp_path: Path, capsys) -> None:
    codex_home = tmp_path / ".codex"
    skill_root = codex_home / "skills" / "demo"
    skill_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text("# Demo\n", encoding="utf-8")

    repo_root = tmp_path / "repos" / "acme"
    (repo_root / ".git").mkdir(parents=True)

    monkeypatch.setattr(
        "sys.argv",
        [
            "codex-harness",
            "system-audit",
            "--codex-home",
            str(codex_home),
            "--scan-root",
            str(tmp_path / "repos"),
            "--format",
            "json",
        ],
    )

    assert cli.main() == 0

    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["summary"]["local_skill_count"] == 1
    assert payload["summary"]["project_count"] == 0


def test_main_audit_min_score_fails_when_repo_is_not_publish_ready(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    (tmp_path / "README.md").write_text("# Draft Repo\n", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["codex-harness", "audit", str(tmp_path), "--min-score", "90"],
    )

    assert cli.main() == 1

    output = capsys.readouterr().out
    assert "missing-license" in output
