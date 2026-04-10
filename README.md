# AntiRot

![Python](https://img.shields.io/badge/python-3.10%2B-0b5fff)
![License](https://img.shields.io/badge/license-MIT-111111)
![Output](https://img.shields.io/badge/output-text%20%7C%20json%20%7C%20markdown%20%7C%20sarif-0a7f5a)
![Runtime](https://img.shields.io/badge/runtime-local--first-6f42c1)

**Lint Markdown drafts for unsupported claims, broken citations, and draft markers.**

AntiRot is a local-first CLI for papers, proposals, reports, and other Markdown drafts. It flags
claim-heavy sentences with no visible citation, citations that do not resolve, numeric claims
without evidence, hype language, and leftover TODOs before the text gets shipped.

## Quick Start

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

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
score=0/100 claims=5 coverage=20.0% citation_validity=0.0% issues=12
- ERROR unsupported-claim line 3: Claim-like sentence has no visible citation anchor.
- WARNING draft-marker line 7: Draft marker present. Remove TODO/TBD/FIXME before release.
- ERROR citation-not-found line 9: Citation `ghost2026` is not defined in the references file.
```

## What It Checks

- unsupported claims without visible evidence anchors
- numeric claims without citations
- citations that do not resolve in the references file
- hype language without evidence
- comparative claims without benchmark grounding
- TODO, TBD, FIXME, XXX, and HACK markers

## Output Formats

- `text` for local review
- `json` for scripts and pipelines
- `markdown` for human-readable reports
- `sarif` for GitHub code scanning and CI flows

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
linting.

## CI Example

```bash
antirot lint docs/paper.md \
  --references docs/references.bib \
  --format sarif \
  --output antirot.sarif
```

## Current Limits

- heuristics are intentionally simple in `v0.1.0`
- claim detection is conservative and Markdown-focused
- config parsing supports scalar values only

## Docs

- [Release notes](docs/releases/v0.1.0.md)
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
