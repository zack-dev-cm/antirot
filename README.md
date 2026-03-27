# AntiRot

![Python](https://img.shields.io/badge/python-3.10%2B-0b5fff)
![License](https://img.shields.io/badge/license-MIT-111111)
![Focus](https://img.shields.io/badge/focus-research%20agents-0a7f5a)
![Scope](https://img.shields.io/badge/zero%20deps-runtime-6f42c1)

**Harness engineering for research agents.**

AntiRot catches unsupported claims, citation drift, hype language, and draft markers in Markdown papers before your agent ships slop to arXiv, a proposal, or a lab note.

The pitch is simple:

- `optillm` is a pill for inference.
- `openevolve` is a harness for code search.
- `autoresearch` turns overnight training loops into agentic science.
- `symphony` and OpenAI’s Codex docs push toward bounded subagent workflows and harness engineering.
- **AntiRot is the missing review harness for the final artifact.**

If your agent can write a paper, it also needs a gate that asks: "Which exact claims are actually supported?"

## Why This Exists

The current failure mode in AI-for-science is not only hallucinated facts. It is **credible-looking nonsense**:

- benchmark numbers with no citations
- "state-of-the-art" language attached to vague comparisons
- references that do not exist in the bibliography
- TODOs and draft markers left in release artifacts
- overconfident claims that read better than the evidence behind them

AntiRot makes those failure modes visible with one command.

## Quick Start

```bash
python3.10 -m venv .venv  # or any Python 3.10+ interpreter
source .venv/bin/activate
pip install -e '.[dev]'

antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format markdown

antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format sarif \
  --output antirot.sarif
```

You can also create a starter config:

```bash
antirot init
antirot lint
```

If `.antirot.toml` exists, `antirot lint` will use its `draft_glob`, `references`, `strict`, and `min_score` settings automatically.

## Example

Input draft:

```md
We present a breakthrough system that outperforms frontier scientific agents by 37% on molecular reasoning.

The system reduces hallucinations to 0.0% while producing world-class papers in minutes TODO add benchmark table.

We show a 2.7x improvement in experiment throughput compared with prior work [@ghost2026].
```

AntiRot report:

```text
AntiRot report for examples/sloppy_paper.md
score=0/100 claims=5 coverage=20.0% citation_validity=0.0% issues=12
- ERROR unsupported-claim line 3: Claim-like sentence has no visible citation anchor.
- WARNING draft-marker line 7: Draft marker present. Remove TODO/TBD/FIXME before release.
- ERROR citation-not-found line 9: Citation `ghost2026` is not defined in the references file.
```

## What AntiRot Checks

- unsupported claims without visible evidence anchors
- numeric claims without citations
- citations that do not resolve in the references file
- hype language without evidence
- comparative claims without benchmark grounding
- TODO, TBD, FIXME, XXX, and HACK markers
- SARIF output for GitHub-native code scanning and CI review flows
- GitHub code-scanning upload via `github/codeql-action/upload-sarif`

## Why This Project Has Star Potential

This repo is designed around the patterns that are working in the current agent wave:

- **Sharp one-line thesis.** People understand the failure mode instantly.
- **Low-friction first run.** No API key, no cloud dependency, no browser profile.
- **Demonstrable before/after.** A bad draft goes in, a precise report comes out.
- **Agent-compatible.** You can drop it into Codex, Claude Code, or CI as a hard gate.
- **Extensible.** The first release is a markdown linter; the roadmap grows into claim ledgers, citation fetchers, and subagent review lanes.

## Design Principles

- **Bounded review beats agent sprawl.** Borrowed from the Codex multi-agent and subagent guidance: keep noisy verification work out of the main drafting thread.
- **Harness over vibes.** Borrowed from OpenAI’s harness-engineering framing: the system is the benchmark, gates, logs, and review surface, not just the prompt.
- **Show the proof.** Borrowed from the best README patterns in `optillm`, `openevolve`, `autoresearch`, `symphony`, and `paperclip`: strong narrative, quick start, and a concrete demo.

## Roadmap

- claim ledger generation for every numeric or superlative sentence
- citation fetch hooks for DOI/arXiv/URL resolution
- section-specific policies for abstract, results, and conclusion
- CI-friendly SARIF or GitHub annotation output
- subagent review packs for literature review and benchmark audit lanes
- paper submission checklist mode for arXiv and workshop pipelines

## Repository Layout

```text
antirot/                 CLI and lint engine
examples/                bad draft + references
tests/                   smoke coverage for the first checks
docs/reference-patterns.md
docs/github-star-audit.md
docs/launch-plan.md
```

## Docs

- [Reference patterns](docs/reference-patterns.md)
- [GitHub star audit](docs/github-star-audit.md)
- [Launch plan](docs/launch-plan.md)
- [Publish checklist](docs/publish-checklist.md)
- [Release notes](docs/releases/v0.1.0.md)
- [Social posts](docs/social-posts.md)
- [Demo script](docs/demo-script.md)
- [Contributing](CONTRIBUTING.md)

## Development

```bash
pip install -e '.[dev]'
pytest -q
antirot lint examples/sloppy_paper.md --references examples/references.md --strict
```

## License

MIT
