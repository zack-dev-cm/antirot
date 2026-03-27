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
