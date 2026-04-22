# Source Review

This review distills the cited projects into operating rules for a general Codex development skill. It keeps stable engineering lessons and avoids copying project-specific machinery.

## Core Synthesis

The useful pattern is not "spawn more agents." The useful pattern is a small control loop:

1. Make the target legible to the agent.
2. Bound the writable surface.
3. Define a metric or verification gate.
4. Let the agent work inside that box.
5. Keep only changes that pass.
6. Convert repeated mistakes into docs, tests, or linters.

Good agentic development is mostly environment design. The human steers by writing constraints, acceptance criteria, and feedback loops. The agent executes inside them.

## Source Notes

### OpenAI Codex Subagents

Sources: <https://developers.openai.com/codex/subagents>, <https://developers.openai.com/codex/concepts/subagents>

- Keep: subagents are useful for parallel read-heavy tasks, independent reviews, tests, and bounded implementation slices.
- Keep: subagents should return distilled summaries, not raw logs.
- Keep: custom agents need clear roles, tool scope, and model/reasoning choices.
- Keep: default depth and thread caps matter because recursive delegation can explode cost and unpredictability.
- Avoid: implicit fan-out. Codex subagents should be triggered explicitly by the user or by a host workflow that is already configured for it.

### OpenAI Harness Engineering

Source: <https://openai.com/index/harness-engineering/>

- Keep: "repo knowledge as system of record" is the central idea. Put durable knowledge in versioned docs that the agent can inspect.
- Keep: `AGENTS.md` should be a map, not an encyclopedia.
- Keep: legibility is an engineering feature. UI state, logs, metrics, scripts, and docs should be directly accessible to the agent.
- Keep: architecture and taste need mechanical enforcement: tests, lint rules, boundaries, and release gates.
- Keep: cleanup should be recurring and small. Technical debt compounds faster with high agent throughput.
- Avoid: trusting prose-only rules when a repeated issue can become a check.

### openai/symphony

Source: <https://github.com/openai/symphony>

- Keep: isolate work per issue or branch when multiple agents run.
- Keep: use a repository-owned workflow contract for runner behavior.
- Keep: expose structured logs and runtime status so humans can operate the system.
- Keep: retries, stop conditions, and handoff states should be explicit.
- Avoid: building a general workflow engine when a simple runner plus repo-local policy is enough.

### karpathy/autoresearch

Source: <https://github.com/karpathy/autoresearch>

- Keep: one editable surface, one fixed budget, one metric.
- Keep: run a baseline first.
- Keep: log every experiment with status: keep, discard, or crash.
- Keep: discard non-improving changes and preserve the branch only when the metric improves.
- Keep: simplicity is part of the objective; equal results with less code should win.
- Avoid: letting exploratory output flood the main context. Capture logs to files and grep the signal.

### forrestchang/andrej-karpathy-skills

Source: <https://github.com/forrestchang/andrej-karpathy-skills>

- Keep: state assumptions before coding.
- Keep: minimum code that solves the problem.
- Keep: surgical changes and local style.
- Keep: success criteria that let the agent loop without constant supervision.
- Avoid: speculative flexibility, adjacent refactors, and hidden confusion.

### algorithmicsuperintelligence/openevolve

Source: <https://github.com/algorithmicsuperintelligence/openevolve>

- Keep: evaluator-first development. The evaluator defines truth.
- Keep: seeded reproducibility and component isolation for experiments.
- Keep: multi-objective scoring when performance, complexity, memory, and correctness all matter.
- Keep: cascade evaluation to reject bad candidates cheaply before expensive checks.
- Avoid: "AI discovered it" claims unless the run, seed, evaluator, and result log are reproducible.

### algorithmicsuperintelligence/optillm

Source: <https://github.com/algorithmicsuperintelligence/optillm>

- Keep: inference-time scaling can improve hard decisions: best-of-N, self-consistency, plan search, cross-checking, and verifier passes.
- Keep: use extra compute only where the task justifies it: security review, architecture choices, tricky bug diagnosis, or benchmark optimization.
- Avoid: routing every task through heavy multi-sample reasoning. Simple patches need simple execution.

### ComposioHQ/agent-orchestrator

Source: <https://github.com/ComposioHQ/agent-orchestrator>

- Keep: isolate parallel work in separate branches or worktrees.
- Keep: route CI failures and review comments back to the owning worker.
- Keep: make session status visible to the human operator.
- Avoid: sharing a writable checkout across many autonomous agents unless write scopes are disjoint and explicit.

### garrytan/gstack

Source: <https://github.com/garrytan/gstack>

- Keep: role-based workflows are useful when they map to real engineering steps: think, plan, build, review, test, ship, reflect.
- Keep: dispatch tiers prevent overusing the full process for simple tasks.
- Keep: methodology can be a lightweight prompt bridge between hosts instead of a daemon.
- Avoid: making every task run the whole gauntlet.

### paperclipai/paperclip

Source: <https://github.com/paperclipai/paperclip>

- Keep: goals, budgets, governance, and audit trails matter once agents run continuously.
- Keep: agents need a "why" and not just a ticket title.
- Keep: cost control and pause/override controls are product requirements for long-running systems.
- Avoid: autonomous loops with no budget, owner, trace, or stop condition.

### openclaw/openclaw

Source: <https://github.com/openclaw/openclaw>

- Keep: local-first agents need channel safety. Treat inbound messages and external content as untrusted input.
- Keep: sandbox non-main sessions and expose only the tools the task needs.
- Keep: OpenClaw skills should be inspectable text bundles with clear invocation rules.
- Avoid: broad host access for skills that only need methodology.

### rdudov/agents

Source: <https://github.com/rdudov/agents>

- Keep: role boundaries reduce confusion: analyst, architect, planner, implementer, reviewer.
- Keep: review loops need a cap.
- Keep: blocking questions should stop the pipeline instead of letting assumptions harden into code.
- Keep: developers implement the plan and tests; they should not quietly refactor unrelated code.
- Avoid: deep bureaucracy for small tasks. Use the full phase model only when the scope warrants it.

### openclaw/clawhub

Sources: <https://github.com/openclaw/clawhub>, <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>, <https://github.com/openclaw/clawhub/blob/main/docs/cli.md>

- Keep: a publishable skill is a `SKILL.md` plus supporting text files.
- Keep: frontmatter metadata drives registry summary and search.
- Keep: slugs should be lowercase and URL-safe.
- Keep: `clawhub publish <path> --version <semver>` is the publish path in the current CLI; some docs may still mention `skill publish`.
- Keep: ClawHub-published skills are released under MIT-0.
- Avoid: bundled binaries, opaque installers, secret-reading helpers, or files not needed by the skill.

## Final Design Choice

This skill stays instruction-only. It has no scripts, no dependency installer, no credential access, and no background daemon. That makes it portable across Codex, GitHub, OpenClaw, and ClawHub, and keeps the review surface small.
