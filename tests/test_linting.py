from pathlib import Path

from antirot.linting import extract_citation_ids, lint_markdown


def test_extracts_multiple_citation_styles() -> None:
    sentence = "This beats baselines [@smith2025; @lee2024] and prior work [1-2]."
    assert extract_citation_ids(sentence) == [
        "smith2025",
        "lee2024",
        "1",
        "2",
    ]


def test_extracts_comma_separated_citekeys() -> None:
    sentence = "This is grounded in prior work [@smith2025, @lee2024]."
    assert extract_citation_ids(sentence) == ["smith2025", "lee2024"]


def test_lints_example_draft() -> None:
    report = lint_markdown("examples/sloppy_paper.md", "examples/references.md")
    codes = {issue.code for issue in report.issues}
    assert report.score < 80
    assert "unsupported-claim" in codes
    assert "citation-not-found" in codes
    assert "draft-marker" in codes


def test_clean_example_passes_strict_gate() -> None:
    report = lint_markdown("examples/clean_paper.md", "examples/references.md")
    assert report.issue_count == 0
    assert report.score >= 90


def test_report_renders_text_and_markdown() -> None:
    report = lint_markdown("examples/sloppy_paper.md", "examples/references.md")
    markdown = report.to_markdown()
    text = report.to_text()
    assert "# AntiRot Report" in markdown
    assert "| Severity | Code | Line | Detail |" in markdown
    assert "AntiRot report for examples/sloppy_paper.md" in text
    assert "unsupported-claim" in text


def test_paragraph_level_citation_supports_wrapped_claim(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "\n".join(
            [
                "# Draft",
                "",
                "We improve review throughput in the tested workflow",
                "while preserving the same approval gates [1].",
                "",
                "## References",
                "",
                "1. Internal benchmark report.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    codes = {issue.code for issue in report.issues}
    assert "unsupported-claim" not in codes
    assert "citation-not-found" not in codes


def test_ignores_fenced_code_blocks(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "\n".join(
            [
                "# Draft",
                "",
                "```python",
                'print("TODO: state-of-the-art breakthrough")',
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    assert report.issue_count == 0


def test_inline_link_counts_as_evidence_anchor(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "We improve throughput by 14% according to [the benchmark report](https://example.com/report).\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    codes = {issue.code for issue in report.issues}
    assert "unsupported-claim" not in codes
    assert "number-without-citation" not in codes


def test_absolute_claim_warning_is_emitted() -> None:
    report = lint_markdown("examples/sloppy_paper.md", "examples/references.md")
    codes = {issue.code for issue in report.issues}
    assert "absolute-claim" in codes


def test_invalid_citation_does_not_count_as_evidence() -> None:
    report = lint_markdown("examples/sloppy_paper.md", "examples/references.md")
    ghost_issue = next(issue for issue in report.issues if issue.code == "citation-not-found")
    unsupported_lines = {
        issue.line for issue in report.issues if issue.code == "unsupported-claim"
    }
    assert ghost_issue.line in unsupported_lines
    assert report.evidence_coverage < 0.5


def test_unverified_citation_does_not_count_as_evidence_without_references(
    tmp_path: Path,
) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "We show a 37% gain on the task [@ghost2026].\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    codes = {issue.code for issue in report.issues}
    assert "citation-unverified" in codes
    assert "unsupported-claim" in codes
    assert "number-without-citation" in codes
    assert report.evidence_coverage == 0.0


def test_numeric_arrays_are_not_treated_as_citations(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "The hidden sizes are [32, 64] and the pipeline is described in Section 3.\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    codes = {issue.code for issue in report.issues}
    assert "citation-not-found" not in codes
    assert report.issue_count == 0


def test_model_and_section_identifiers_do_not_trigger_numeric_claims(
    tmp_path: Path,
) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "Section 3 summarizes the GPT-4 baseline and Appendix 2 lists prompts.\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    assert report.issue_count == 0


def test_ignores_frontmatter(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "\n".join(
            [
                "---",
                "title: state-of-the-art benchmark",
                "score: 37",
                "---",
                "",
                "Plain overview only.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = lint_markdown(draft)
    assert report.issue_count == 0
