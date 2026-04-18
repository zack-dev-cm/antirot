# Codex Harness

`codex-harness` is a small CLI that scaffolds and audits a Codex-native engineering harness plus open-source release gates.

It packages one opinionated starter:

- a short `AGENTS.md` that acts as a repo map instead of a giant instruction blob
- project-scoped custom agents under `.codex/agents/*.toml`
- durable repo docs under `docs/codex/`
- an audit command that scores whether a repo is actually legible to Codex and safe to publish
- a system audit command that inventories local Codex skills, packaged plugins, project-level Codex assets, and recent usage

## Why this exists

The design is a synthesis of the sources below:

- [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills): small behavioral rules, simple code, surgical diffs, and verification-first execution
- [Codex subagents docs](https://developers.openai.com/codex/subagents) and [Codex subagents concepts](https://developers.openai.com/codex/concepts/subagents): project-scoped custom agents in `.codex/agents/` and explicit, user-requested delegation
- [OpenAI harness engineering](https://openai.com/index/harness-engineering/), published February 11, 2026: `AGENTS.md` as a table of contents, repo knowledge as the system of record, and recurring cleanup
- [algorithmicsuperintelligence/openevolve](https://github.com/algorithmicsuperintelligence/openevolve), [karpathy/autoresearch](https://github.com/karpathy/autoresearch), and [algorithmicsuperintelligence/optillm](https://github.com/algorithmicsuperintelligence/optillm): measured iteration loops, ratchets, and explicit metrics
- [openai/symphony](https://github.com/openai/symphony), [paperclipai/paperclip](https://github.com/paperclipai/paperclip), [garrytan/gstack](https://github.com/garrytan/gstack), and [openclaw/openclaw](https://github.com/openclaw/openclaw): role-based agent workflows, local-first execution, and managing work instead of micromanaging prompts

## Commands

Initialize a repo:

```bash
python3 -m codex_harness init path/to/repo
```

Audit a repo:

```bash
python3 -m codex_harness audit path/to/repo --format markdown
```

Audit the local Codex environment:

```bash
python3 -m codex_harness system-audit \
  --codex-home ~/.codex \
  --scan-root ~/Documents/GitHub/github_stars_optimizer \
  --format markdown
```

Audit the wider workspace without hand-maintaining a repo list:

```bash
python3 -m codex_harness system-audit \
  --codex-home ~/.codex \
  --scan-root ~/Documents/GitHub \
  --marker-discovery \
  --format markdown
```

Fail closed for open-source prep:

```bash
python3 -m codex_harness audit path/to/repo --strict --min-score 90
```

## Generated files

`codex-harness init` writes:

- `AGENTS.md`
- `.codex/agents/architect.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`
- `.codex/agents/evolver.toml`
- `.codex/agents/cleanup.toml`
- `docs/codex/overview.md`
- `docs/codex/architecture.md`
- `docs/codex/workflow.md`
- `docs/codex/evals.md`
- `docs/codex/cleanup.md`

## Audit coverage

For repos that already look publishable, `codex-harness audit` also checks:

- `README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, tests, CI workflows, and PR template presence
- whether the README includes a first-run path and a security pointer
- whether CI enforces an open-source gate such as `codex-harness audit`, CodeQL, or secret scanning
- high-confidence secret-like strings such as GitHub tokens, AWS keys, OpenAI-style keys, and private key blocks
- public-surface bleed such as `/Users/...` paths, `localhost` links, and internal hostnames

If a fixture intentionally needs one of those patterns, add an inline comment on the same line:

- `codex-harness: allow-secret`
- `codex-harness: allow-bleed`
