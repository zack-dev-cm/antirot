# Social Posts

Prepared on **March 27, 2026** for the `AntiRot` launch.

Use these after the repository contents are live at `https://github.com/zack-dev-cm/antirot`.

## X post

### Primary

I open-sourced AntiRot: a local-first linter for AI-written research drafts.

It catches:
- unsupported claims
- numbers without citations
- citation drift
- hype language without evidence
- TODOs left in publishable text

If agents can write papers, they need a final artifact gate too.

GitHub: https://github.com/zack-dev-cm/antirot

### Shorter variant

I open-sourced AntiRot.

It is a local-first linter for AI-written research drafts: unsupported claims, citation drift, hype language, and draft markers.

If agents can write papers, they need a final artifact gate.

https://github.com/zack-dev-cm/antirot

### X thread opener

I think one of the biggest AI-for-science failure modes is not just hallucination.

It is polished-looking research text with weak or missing evidence anchors.

So I built and open-sourced AntiRot: https://github.com/zack-dev-cm/antirot

## LinkedIn post

I just open-sourced **AntiRot**, a local-first evidence-hygiene linter for AI-written research drafts.

The problem it targets is simple: research agents can now generate polished text faster than most teams can verify it. The result is often not obvious hallucination, but something worse for decision-making: credible-looking claims with weak evidence behind them.

AntiRot is a narrow guardrail for that last mile. It flags:

- unsupported claims
- numeric claims without citations
- citation drift
- hype language without evidence
- comparative claims without benchmark grounding
- TODO and draft markers left in publishable text

I designed it to be easy to run locally and easy to drop into CI, with text, JSON, Markdown, and SARIF outputs.

This is the GitHub repo:
https://github.com/zack-dev-cm/antirot

If you work on agentic research systems, scientific tooling, or AI writing workflows, I’d be interested in the false positives and failure modes you want this kind of tool to catch next.

## Comment reply

Thanks. The main idea is that better prompting is not enough for research agents. You also need a review harness around the artifact they produce.

## Hashtag pack

`#opensource #aiagents #research #llm #scientificwriting #github`
