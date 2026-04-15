# AntiRot

![CI](https://github.com/zack-dev-cm/antirot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-0b5fff)
![License](https://img.shields.io/badge/license-MIT-111111)
![Output](https://img.shields.io/badge/output-text%20%7C%20json%20%7C%20markdown%20%7C%20sarif-0a7f5a)
![Runtime](https://img.shields.io/badge/runtime-local--first-6f42c1)

**Catch unsupported claims before Markdown drafts ship.**

AntiRot is a local-first CLI for AI-assisted papers, proposals, reports, and design docs.
It flags claim-heavy sentences with no nearby evidence anchor, broken citations, numeric claims
without support, overclaim language, and leftover draft markers before the text gets shipped.

Style linters focus on wording. AntiRot focuses on evidence hygiene.

## Install

Install directly from GitHub:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install "antirot @ git+https://github.com/zack-dev-cm/antirot.git"
```

## Quick Start

```bash
antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format markdown
```

If you want a project config:

```bash
antirot init
# edit .antirot.toml for your draft_glob and optional references path
antirot lint
```

## Example

Input draft:

```md
We present a breakthrough system that outperforms frontier scientific agents by 37% on molecular reasoning.

The system reduces hallucinations to 0.0% while producing world-class papers in minutes TODO add benchmark table.

We show a 2.7x improvement in experiment throughput compared with prior work [@ghost2026].
```

Report:

```text
AntiRot report for examples/sloppy_paper.md
score=0/100 claims=5 coverage=0.0% citation_validity=0.0% issues=17
- ERROR unsupported-claim line 3: Claim-like sentence has no nearby evidence anchor in the sentence or paragraph.
- WARNING absolute-claim line 5: Absolute or universal wording should be narrowed, scoped, or backed by unusually strong evidence.
- WARNING draft-marker line 7: Draft marker present. Remove TODO/TBD/FIXME before release.
- ERROR citation-not-found line 9: Citation `ghost2026` is not defined in the references file or document references section.
```

## What It Checks

- unsupported claims without nearby evidence anchors
- numeric claims without nearby support
- citations that do not resolve in the references file
- citation-like markers that cannot be verified because no references source was loaded
- footnote citations and references sections inside the same Markdown draft
- inline Markdown links, DOIs, arXiv ids, and raw URLs as evidence anchors
- paragraph-level evidence carry for wrapped Markdown prose
- hype language without evidence
- comparative claims without benchmark grounding
- absolute or universal claim language that should be narrowed
- TODO, TBD, FIXME, XXX, and HACK markers
- fenced code blocks and non-prose Markdown are ignored instead of treated as claims

## Typical Uses

- AI-generated research drafts before submission or internal review
- benchmark summaries written by agents or analysts
- proposals and memos with lots of numeric claims
- Markdown docs that need a cheap evidence gate in CI

## Output Formats

- `text` for local review
- `json` for scripts and pipelines
- `markdown` for human-readable reports
- `sarif` for GitHub code scanning and CI flows

## GitHub Actions

AntiRot can feed GitHub code scanning with SARIF output:

```yaml
name: antirot

on:
  pull_request:
    paths:
      - "docs/**/*.md"

jobs:
  lint-drafts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install "antirot @ git+https://github.com/zack-dev-cm/antirot.git"
      - run: |
          antirot lint docs/paper.md \
            --references docs/references.bib \
            --format sarif \
            --output antirot.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: antirot.sarif
```

## Why Use It Alongside Vale or textlint

AntiRot is not a general prose or style linter. It is a narrow check for claim grounding,
citation hygiene, and draft leftovers in Markdown artifacts. Use Vale or textlint for style;
use AntiRot when the main failure mode is "this sounds publishable, but the evidence is weak."

## Configuration

`antirot init` writes a starter `.antirot.toml`:

```toml
# draft_glob = "docs/**/*.md"
# references = "docs/references.md"
strict = true
min_score = 80
```

Set `draft_glob` to the Markdown drafts you want to lint. The `references` path is optional. If
you set it, point it at a real `.bib`, Markdown references file, or numbered reference list before
linting. Citation markers only count as evidence when AntiRot can resolve them from that file or
from a `References` section or footnote definition inside the draft.

## Current Boundaries

- the linter is still Markdown-first; it does not parse DOCX, LaTeX, or PDFs
- evidence detection is local and structural, not semantic fact verification
- score thresholds are best used as review gates, not as publication truth guarantees
- config parsing supports scalar values only

## Docs

- [Release notes](docs/releases/v0.2.0.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Development

```bash
pip install -e '.[dev]'
python3 -m pytest -q
python3 -m antirot.cli lint examples/sloppy_paper.md --references examples/references.md --strict
```

## License

MIT
