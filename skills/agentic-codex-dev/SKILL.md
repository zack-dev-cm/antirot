---
name: agentic-codex-dev
description: Use when planning, implementing, reviewing, or publishing agentic software development work with Codex, GitHub, and OpenClaw/ClawHub. This skill turns vague coding-agent requests into small verified loops, repo-local instructions, subagent-safe decomposition, and open-source release checks without overengineering.
version: 0.1.0
metadata:
  openclaw:
    homepage: https://github.com/zack-dev-cm/antirot/tree/codex/agentic-codex-dev-skill/skills/agentic-codex-dev
    tags:
      - codex
      - github
      - clawhub
      - agentic-development
---

# Agentic Codex Dev

Build like a small, sharp engineering team: one clear goal, one narrow diff, one verification loop.

## When to Use

Use this skill for:

- coding tasks where Codex should inspect, modify, test, and report on a GitHub repo
- turning a rough product or bug request into scoped implementation work
- setting up repo-local `AGENTS.md`, `.codex/agents/`, or lightweight skills
- reviewing agent-generated code for correctness, tests, security, and public-surface leaks
- preparing a GitHub repo or ClawHub skill for open-source publication
- coordinating explicit parallel/subagent work without losing control of the main thread

Do not use it for one-line answers, pure brainstorming, or tasks that only need a command output.

## Core Loop

1. Restate the goal and name the verification step before editing.
2. Read the repo map: `AGENTS.md`, README, package config, tests, and the files closest to the task.
3. Define the smallest success criteria that would let a reviewer say "done".
4. Make the smallest defensible change. Match local style. Avoid speculative abstractions.
5. Run the highest-signal local check. Add a focused smoke test when behavior changed.
6. Review the diff for bugs, regressions, secrets, private paths, and public-surface bleed.
7. Report what changed, how it was verified, and any residual risk.

If the task is unclear, stop early and name the ambiguity. Prefer one precise question over guessing.

## Operating Rules

- Treat repository files as the source of truth. If knowledge matters later, put it in repo docs.
- Keep `AGENTS.md` short. Use it as an index to durable docs, not a giant prompt.
- Prefer boring, inspectable code over opaque magic. Agents compound what they can read.
- Touch only files required for the goal. Mention unrelated problems; do not fix them unless asked.
- Use structured APIs, tests, and parsers where available. Avoid fragile string tricks.
- Convert repeated review feedback into checks, docs, or templates.
- Keep logs and long command output out of the main narrative; summarize the signal.
- Avoid asking an agent to read undeclared secret files or sync credentials as part of a skill.

## Scope Modes

Pick the smallest mode that fits:

- **Patch**: one bug or one small feature. Read close code, edit, test, review.
- **Plan**: ambiguous or multi-file work. Write a short acceptance plan before editing.
- **Review**: findings first, with emphasis on correctness, regressions, security, tests, and leaks as summarized in [source review](references/source-review.md).
- **Harness**: improve repo legibility: docs, CI, local scripts, custom agents, or audit gates.
- **Evolve**: metric-driven optimization. One variable per experiment, fixed budget, log keep/discard.
- **Publish**: GitHub/ClawHub release readiness, metadata, license, docs, and verification.

Prefer Patch unless the task shows it needs more structure.

## Subagents

Only use subagents when the user explicitly asks for subagents, delegation, or parallel agent work.

Good delegation targets:

- read-heavy codebase mapping
- independent test or CI-log analysis
- independent review categories such as security, test gaps, or docs correctness
- disjoint implementation slices with clearly separate file ownership

Bad delegation targets:

- the immediate blocker for your next local step
- tightly coupled edits in the same files
- vague "go improve the code" work
- recursive fan-out with no cap

When delegating, give each agent a bounded task, a clear output shape, and explicit ownership. Keep the main thread focused on requirements, decisions, integration, and final review.

## Implementation Discipline

Before editing:

- inspect the existing patterns
- identify the likely tests or smoke command
- check dirty git state and avoid touching unrelated user changes
- state the planned edit in one or two sentences

While editing:

- keep the diff surgical
- add tests when behavior, contracts, or public output changes
- avoid new dependencies unless they clearly reduce risk or complexity
- keep comments rare and useful

After editing:

- run the named verification
- inspect the diff, not just test output
- update docs only when user-facing behavior or workflow changed
- do not call work published until the public surface is clean

## Review Checklist

Review every non-trivial result for:

- Does every changed line trace to the stated goal?
- Are edge cases covered by tests or a clear smoke path?
- Did the change preserve existing public APIs and CLI behavior?
- Did docs/examples drift from actual behavior?
- Did any secret-like string, local path, private URL, copied dashboard, or stale release note enter the repo?
- Did the final diff remove avoidable complexity from the first draft, as recommended in [source review](references/source-review.md)?

## GitHub and ClawHub Publish Gate

Before publishing:

- README or skill summary says what it does, when to use it, and what it does not do.
- License is compatible with the target surface. ClawHub publishes skills under MIT-0.
- `SKILL.md` has frontmatter `name`, `description`, and `version`.
- The skill folder contains only text-based files needed at runtime.
- No hidden install scripts, credential readers, service restarts, or local machine assumptions.
- Public repo has security, contribution, support, CI, and release/audit checks when applicable.
- Run the repo's public-surface gate before pushing or publishing to a registry.

For this skill's source analysis, read `references/source-review.md`.
For release commands and manual checks, read `references/publish-checklist.md`.
