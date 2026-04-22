# Agentic Codex Dev Skill

`skills/agentic-codex-dev/` is a publish-ready text skill for Codex, GitHub, OpenClaw, and ClawHub agentic software development.

## Purpose

The skill packages a simple operating loop:

- restate the goal and verification step
- read the repo map before editing
- keep diffs small
- verify locally
- review for correctness, tests, security, and public-surface bleed
- publish only after GitHub and ClawHub metadata are clean

It is intentionally instruction-only. There are no scripts, installers, background daemons, or credential readers.

## Files

- `skills/agentic-codex-dev/SKILL.md`: runtime instructions and ClawHub metadata.
- `skills/agentic-codex-dev/agents/openai.yaml`: Codex UI metadata.
- `skills/agentic-codex-dev/references/source-review.md`: source analysis from the requested projects and OpenAI docs.
- `skills/agentic-codex-dev/references/publish-checklist.md`: GitHub and ClawHub release checklist.

## Verification

Run the default repo gate after edits:

```bash
python3 -m pytest -q
python3 -m codex_harness audit . --strict --min-score 90
```

If publishing to ClawHub, also inspect the installed or published bundle:

```bash
clawhub inspect agentic-codex-dev --files
```
