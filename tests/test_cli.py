from __future__ import annotations

from pathlib import Path

from antirot.cli import build_sarif, load_config, resolve_drafts
from antirot.linting import lint_markdown


def test_load_config_parses_basic_scalars(tmp_path: Path) -> None:
    config_path = tmp_path / ".antirot.toml"
    config_path.write_text(
        "\n".join(
            [
                'draft_glob = "docs/**/*.md"',
                'references = "docs/references.md"',
                "strict = true",
                "min_score = 85",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    config = load_config(str(config_path))
    assert config == {
        "draft_glob": "docs/**/*.md",
        "references": "docs/references.md",
        "strict": True,
        "min_score": 85,
    }


def test_resolve_drafts_uses_config_glob(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "a.md").write_text("# A\n", encoding="utf-8")
    (docs_dir / "b.md").write_text("# B\n", encoding="utf-8")

    cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        drafts = resolve_drafts(None, {"draft_glob": "docs/*.md"})
    finally:
        os.chdir(cwd)

    assert drafts == ["docs/a.md", "docs/b.md"]


def test_resolve_drafts_excludes_references_file(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.md").write_text("# Draft\n", encoding="utf-8")
    (docs_dir / "references.md").write_text("# References\n", encoding="utf-8")

    cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        drafts = resolve_drafts(
            None,
            {"draft_glob": "docs/*.md"},
            "docs/references.md",
        )
    finally:
        os.chdir(cwd)

    assert drafts == ["docs/draft.md"]


def test_build_sarif_emits_results_and_rules() -> None:
    report = lint_markdown("examples/sloppy_paper.md", "examples/references.md")
    sarif = build_sarif([report])
    run = sarif["runs"][0]
    assert sarif["version"] == "2.1.0"
    assert len(run["results"]) == report.issue_count
    rule_ids = {rule["id"] for rule in run["tool"]["driver"]["rules"]}
    assert "unsupported-claim" in rule_ids
