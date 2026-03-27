# Demo Script

This is the shortest high-signal terminal demo for `AntiRot`.

## Goal

Show a bad draft, run `antirot`, and make the problem legible in under 40 seconds.

## Terminal script

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format markdown
```

## What to narrate

1. "Research agents can write polished text faster than we can verify it."
2. "AntiRot is a local-first evidence-hygiene linter for the final artifact."
3. "Here is a deliberately sloppy draft."
4. "One command gives me unsupported claims, citation drift, and draft markers."
5. "This is meant to be the review harness after the agent writes."

## Demo framing

- Keep the terminal font large.
- Start at the repo root with the examples visible.
- Scroll just enough for the audience to see issue codes and line numbers.
- End on the GitHub URL after the command output.

## Backup version

If you want a shorter clip, use:

```bash
antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format text
```
