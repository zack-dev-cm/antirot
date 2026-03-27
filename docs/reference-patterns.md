# Reference Patterns

This file records the best-practice patterns pulled from the repos and docs that informed `AntiRot`.

## Current traction snapshot

Checked on **March 27, 2026**:

| Project | Stars | Created | Why it matters |
| --- | ---: | --- | --- |
| `karpathy/autoresearch` | 57,497 | 2026-03-06 | Viral because the premise is instantly legible and the README reads like a story, not a spec. |
| `paperclipai/paperclip` | 33,962 | 2026-03-02 | Wins with a strong narrative, visual brand, and problem/solution table that maps directly to operator pain. |
| `openai/symphony` | 14,088 | 2026-02-26 | Small surface area, clean demo video, clear positioning around autonomous implementation runs. |
| `algorithmicsuperintelligence/openevolve` | 5,773 | 2025-05-15 | Succeeds on quick start, visible benchmarks, and examples that prove the thesis. |
| `algorithmicsuperintelligence/optillm` | 3,395 | 2024-08-22 | Succeeds on drop-in value proposition, benchmark table, and "works with your existing stack" messaging. |

## README patterns worth copying

### `optillm`

- One-line value proposition immediately under the title.
- Quick start in three simple steps.
- Benchmark table near the top.
- Multiple distribution paths: PyPI, Docker, source.
- Strong "drop-in replacement" framing.

### `openevolve`

- Strong product identity and visual logo.
- "Why" section before implementation detail.
- Examples gallery and concrete achievements.
- Reproducibility called out as a feature, not a footnote.

### `autoresearch`

- Narrative hook first, then the mechanics.
- Very small conceptual model: one file the agent edits, one file the human edits.
- Concrete overnight loop anyone can imagine running.
- The README is opinionated and memorable.

### `symphony`

- Short README.
- Demo video near the top.
- Clear statement of requirements and current maturity.
- Points readers toward a spec so contributors can reimplement the system.

### `paperclip`

- Big thesis statement.
- Problem/solution table that makes pain obvious.
- Features framed in business language, not only systems language.
- Brand and UI make the project feel like a movement instead of a utility.

## Official OpenAI guidance that matters

From OpenAI’s Codex docs, the main design pattern is to keep the main thread focused on the core problem and offload bounded work such as exploration, tests, or triage to subagents. The "Best practices" page also emphasizes that long-running work should stay organized by thread and only branch when the work truly diverges.

Why this matters for `AntiRot`:

- Drafting should stay in the main author thread.
- Evidence review should be isolated into bounded reviewer lanes.
- The final artifact needs a harness and gate, not only a prompt.

Relevant sources:

- https://developers.openai.com/codex/learn/best-practices/
- https://developers.openai.com/codex/subagents/
- https://openai.com/index/harness-engineering/

## Product-level conclusions

The next star-worthy project should satisfy five constraints:

1. The hook must fit in one sentence.
2. The first run must work in under a minute.
3. The demo must show failure becoming legible.
4. The scope must be broad enough to matter but narrow enough to explain.
5. The README must read like a thesis with proof, not a dumping ground.

`AntiRot` was selected because it fits all five better than a generic "agent framework" does.
