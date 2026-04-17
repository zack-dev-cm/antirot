from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ScaffoldFile:
    path: str
    content: str


def derive_project_name(path: Path) -> str:
    raw_name = path.name or "project"
    normalized = raw_name.replace("_", " ").replace("-", " ").strip()
    words = [word for word in normalized.split() if word]
    if not words:
        return "Project"
    return " ".join(word.capitalize() for word in words)


def scaffold_files(project_name: str) -> list[ScaffoldFile]:
    title = project_name.strip() or "Project"
    return [
        ScaffoldFile("AGENTS.md", _render_agents_md(title)),
        ScaffoldFile(".codex/agents/architect.toml", _render_architect_toml()),
        ScaffoldFile(".codex/agents/implementer.toml", _render_implementer_toml()),
        ScaffoldFile(".codex/agents/reviewer.toml", _render_reviewer_toml()),
        ScaffoldFile(".codex/agents/evolver.toml", _render_evolver_toml()),
        ScaffoldFile(".codex/agents/cleanup.toml", _render_cleanup_toml()),
        ScaffoldFile("docs/codex/overview.md", _render_overview_md(title)),
        ScaffoldFile("docs/codex/architecture.md", _render_architecture_md(title)),
        ScaffoldFile("docs/codex/workflow.md", _render_workflow_md()),
        ScaffoldFile("docs/codex/evals.md", _render_evals_md()),
        ScaffoldFile("docs/codex/cleanup.md", _render_cleanup_md()),
    ]


def _render_agents_md(project_name: str) -> str:
    return f"""# AGENTS.md

This repository uses a small-file Codex harness for {project_name}. Read this file first, then open only the docs that matter for the task.

## Operating rules

- Restate the goal and name the verification step before making changes.
- Prefer the smallest change that solves the request.
- Keep diffs surgical. Do not refactor adjacent code unless the task requires it.
- Treat this file as an index. Put durable knowledge in versioned docs under `docs/codex/`.
- Use the custom agents in `.codex/agents/` when the user explicitly asks for delegation or parallel agent work.

## Repo map

- [Overview](docs/codex/overview.md)
- [Architecture](docs/codex/architecture.md)
- [Workflow](docs/codex/workflow.md)
- [Evals](docs/codex/evals.md)
- [Cleanup](docs/codex/cleanup.md)

## Default loop

1. Clarify the task and state success checks.
2. Open the smallest relevant docs from the repo map.
3. Implement or revise code with tests or other verification.
4. Run the documented checks.
5. Update docs when the change introduces a durable rule, invariant, or workflow.

## Custom agents

- `architect`: scope, tradeoffs, acceptance criteria, and boundary decisions.
- `implementer`: minimal code and tests.
- `reviewer`: correctness, regressions, and missing checks.
- `evolver`: controlled search over alternatives when the task benefits from measured iteration.
- `cleanup`: entropy reduction, doc refresh, and follow-up cleanup.
"""


def _render_architect_toml() -> str:
    return '''name = "architect"
description = "Use for scope clarification, architecture tradeoffs, and acceptance criteria before implementation."
developer_instructions = """
You are the architecture and scope guard.

- Surface ambiguity explicitly instead of silently picking an interpretation.
- Offer 2-3 options when tradeoffs are real, then recommend the smallest sound path.
- Translate vague asks into concrete acceptance criteria and verification steps.
- Preserve existing boundaries unless the task explicitly requires changing them.
- Do not start coding when the main value is sharper framing.
"""
nickname_candidates = ["Northstar", "Frame", "Scope"]
'''


def _render_implementer_toml() -> str:
    return '''name = "implementer"
description = "Use for focused implementation work with minimal diffs and concrete verification."
developer_instructions = """
You are the implementation specialist.

- Write the minimum code needed to satisfy the task.
- Prefer existing patterns and utilities over new abstractions.
- Add or update tests when the task changes behavior.
- Keep changes localized and remove only the unused code your edit created.
- Report exactly what you changed and how you verified it.
"""
nickname_candidates = ["Forge", "Patch", "Relay"]
'''


def _render_reviewer_toml() -> str:
    return '''name = "reviewer"
description = "Use for bug-focused review of correctness, regressions, security, and missing tests."
developer_instructions = """
You are the final reviewer.

- Review like an owner, not a stylist.
- Prioritize correctness, security, behavior regressions, and missing test coverage.
- Call out brittle assumptions, edge cases, and risky migrations.
- Keep summaries brief; findings come first and should include file references.
- If there are no findings, say so explicitly and mention residual risk.
"""
nickname_candidates = ["Atlas", "Delta", "Echo"]
'''


def _render_evolver_toml() -> str:
    return '''name = "evolver"
description = "Use for controlled iteration loops when the task benefits from measured experimentation."
developer_instructions = """
You are the measured-search specialist.

- Start from a baseline and name the primary metric before trying alternatives.
- Change one meaningful lever at a time when possible.
- Prefer fast, reproducible experiments over broad speculative churn.
- Keep a short log of attempts, metrics, and whether the change was kept or reverted.
- Stop when the search stops producing signal or the budget is exhausted.
"""
nickname_candidates = ["Vector", "Sprint", "Pilot"]
'''


def _render_cleanup_toml() -> str:
    return '''name = "cleanup"
description = "Use for entropy reduction, doc drift cleanup, and small follow-up refactors after tasks land."
developer_instructions = """
You are the garbage-collection specialist.

- Hunt for duplication, stale docs, and small inconsistencies created by recent work.
- Prefer narrow cleanup diffs that improve legibility for future agent runs.
- Do not broaden into opportunistic rewrites.
- When you see a repeated mistake, propose a durable rule or check instead of a one-off edit.
- Verify that cleanup preserves behavior.
"""
nickname_candidates = ["Broom", "Polish", "Tidy"]
'''


def _render_overview_md(project_name: str) -> str:
    return f"""# Overview

This file explains what {project_name} is, who it serves, and what success looks like.

## Product

- Primary user: [describe the main user]
- Core job: [describe the main job to be done]
- Non-goals: [name the work this repo should not grow into]

## Repo landmarks

- App or package code: [replace with the main source paths]
- Tests: [replace with test paths]
- Scripts and tooling: [replace with ops or automation paths]
- Docs worth reading first: [list high-signal docs]

## Standard checks

- Build: [replace with the build command]
- Tests: [replace with the test command]
- Lint or typecheck: [replace with the lint command]
- Smoke test: [replace with the fastest high-signal validation]
"""


def _render_architecture_md(project_name: str) -> str:
    return f"""# Architecture

Use this file to document the boundaries Codex should preserve in {project_name}.

## Domains

- Domain: [name] | Owners: [team or role] | Entry points: [paths or modules]
- Domain: [name] | Allowed dependencies: [what it can talk to]

## Guardrails

- Parse and validate data at boundaries.
- Prefer boring, inspectable dependencies over opaque magic.
- Keep modules small enough that an agent can reason about them locally.
- Write down invariants here before they spread only through chat or tribal memory.

## Do-not-break list

- Public APIs or CLIs: [list them]
- Migrations or schemas: [list them]
- Long-running jobs or background loops: [list them]
- External integrations and credentials: [list them]
"""


def _render_workflow_md() -> str:
    return """# Workflow

This starter uses a role-based sprint loop for Codex.

## Default loop

1. Clarify: restate the goal, assumptions, and verification.
2. Plan: choose the smallest architecture that can work.
3. Implement: write the change and the checks.
4. Review: inspect for correctness, regressions, security, and missing tests.
5. Verify: run the highest-signal local validation plus the public-surface gate.
6. Ship: summarize outcome and residual risk.
7. Cleanup: remove entropy or write a durable rule for the next run.

## When to use which agent

- `architect` when the problem is ambiguous or the main work is decision-making.
- `implementer` when the path is known and the goal is a focused code change.
- `reviewer` after implementation or when you need a bug-focused second pass.
- `evolver` when several candidate approaches can be compared with a clear metric.
- `cleanup` after a landing, a refactor wave, or visible doc drift.

## Parallel work

Only spawn subagents when the user explicitly asks for delegation or parallel agent work. Keep tasks disjoint and concrete.
"""


def _render_evals_md() -> str:
    return """# Evals

Use this file to define the ratchet that keeps Codex runs honest.

## Rules

- Every meaningful task should name one primary success check.
- Keep a baseline before you change behavior.
- Prefer fast, deterministic checks before expensive end-to-end runs.
- Record when a change improves quality, speed, reliability, or cost.
- Public repos need a leak gate for secrets, private paths, and local URLs before merge.

## Required checks

- Unit: [replace with the command or suite]
- Integration: [replace with the command or suite]
- Smoke: [replace with the fastest realistic user-path check]
- Open-source gate: `python -m codex_harness audit . --strict --min-score 90`
- Manual: [describe any manual verification that still matters]

## Experiment log

| Date | Change | Metric | Result | Kept |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | baseline | [metric] | [value] | yes |
"""


def _render_cleanup_md() -> str:
    return """# Cleanup

Codex can amplify entropy if you never clean the repo. This file defines the garbage-collection loop.

## Weekly sweep

- Collapse duplicated helpers that recent tasks introduced.
- Refresh docs that no longer match the code.
- Remove dead tests, scripts, and examples created by reverted work.
- Tighten recurring review comments into lint rules, checks, or reusable docs.
- Re-scan the public surface for secrets, local paths, copied dashboards, and stale release artifacts.

## Promote a rule when

- The same issue appears in two or more tasks.
- Review comments keep repeating the same guidance.
- A missing invariant caused wasted time or broken behavior.

## Do not do

- Huge opportunistic rewrites under the label of cleanup.
- Formatting-only churn across unrelated files.
- "Helpful" abstractions with no repeated use yet.
"""
