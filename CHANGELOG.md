# Changelog

All notable changes to this project will be documented in this file.

## v0.2.0 - 2026-04-15

### Changed

- upgraded the linter from line-by-line matching to paragraph-aware Markdown parsing
- added support for inline links, DOIs, arXiv ids, and footnote references as evidence anchors
- added in-document references section parsing, so numbered references can resolve without a separate file
- stopped counting unresolved citations as evidence when no references source is loaded
- reduced false positives from identifiers like `Section 3`, `GPT-4`, and numeric arrays
- added `absolute-claim` warnings for universal or zero-risk language
- stopped scanning fenced code blocks and other non-prose Markdown as claims

## v0.1.1 - 2026-04-10

### Changed

- rewrote the public README around the actual CLI job instead of internal launch notes
- made `antirot init` generate a safer starter config with commented example paths
- added a clean CLI error when a configured references file does not exist
- trimmed internal launch and star-planning docs from the public repo surface

## v0.1.0 - 2026-03-27

Initial public release.

### Added

- `antirot lint` CLI for Markdown draft review
- evidence-hygiene checks for unsupported claims, numeric claims without citations, hype language, comparative claims, and draft markers
- references parsing for citekeys, numbered references, and BibTeX keys
- config-driven linting via `.antirot.toml`
- JSON, Markdown, text, and SARIF output modes
- GitHub Actions CI with SARIF artifact and code-scanning upload
- example clean and sloppy drafts
- contributor docs, issue templates, and release materials

### Known limits

- heuristics are intentionally simple in `v0.1.0`
- config parsing supports simple scalar values only
- claim detection is optimized for Markdown papers and notes, not full manuscript formats
