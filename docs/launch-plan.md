# Launch Plan

This plan is optimized for stars, not only for code quality.

## Positioning

Primary hook:

> AntiRot catches the exact sentences your research agent should not be allowed to publish.

Secondary hook:

> Harness engineering for AI-written papers, proposals, and lab notes.

## Before first public push

1. Record a 20-40 second terminal demo of `antirot lint examples/sloppy_paper.md`.
2. Add that GIF or MP4 to the top of the README.
3. Create a repo social preview image with the line:
   - "Stop research-agent slop before it ships."
4. Set GitHub topics:
   - `llm`
   - `ai-agents`
   - `research`
   - `scientific-writing`
   - `hallucination-detection`
   - `markdown`
   - `citations`
   - `harness-engineering`
5. Publish a minimal release tag: `v0.1.0`.

## Distribution sequence

### Day 0

- Push the repo public.
- Post a short demo clip on X.
- Post the repo to Hacker News with a title focused on the pain, not the stack.
- Share in agent/dev tooling communities where research slop is already a known complaint.

### Day 1-3

- Add one more concrete example:
  - grant proposal draft
  - paper abstract
  - benchmark summary
- Publish a follow-up thread showing a real draft AntiRot would reject.

### Week 1

- Add GitHub issue templates for:
  - new lint rule
  - citation format support
  - integration request
- Add one integration example for Codex or Claude Code in CI.

## Content angles that can pull stars

- "AI agents can generate scientific text faster than we can verify it."
- "Most paper slop looks professional until you inspect the evidence anchors."
- "Subagents need a final artifact gate, not only better prompts."
- "This is `ruff`, but for research-agent evidence hygiene."

## Hard constraints

- Keep the README under control.
- Keep the first demo local and zero-key.
- Do not turn version `0.1.0` into a framework.
- Do not add browser automation, paper scraping, or external APIs until the core linting story is obvious.

## First three follow-up releases

### `v0.2.0`

- section-aware policies
- richer citation parsing
- GitHub Actions annotation output

Delivered early in `v0.1.0`:

- SARIF export for machine-readable CI and code-scanning workflows

### `v0.3.0`

- claim ledger export
- machine-readable JSON schema for agent pipelines

### `v0.4.0`

- subagent review packet templates
- evidence bundle mode for proposal and paper workflows
