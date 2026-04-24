# Evals

## Rules

- Every task should name the primary check before editing.
- Public-surface changes need a leak and bleed review, not just passing tests.
- Prefer deterministic local checks before expensive end-to-end runs.
- If the repo is being prepared for open source, the release gate is mandatory.

## Required checks

- Unit and regression: `python3 -m pytest -q`
- Open-source gate: `python3 -m codex_harness audit . --strict --min-score 90`
- ClawHub skill gate: `python3 skills/clawhub-skills-security/scripts/audit_clawhub_skill.py /path/to/skill`
- AntiRot smoke: `python3 -m antirot.cli lint examples/sloppy_paper.md --references examples/references.md --format json --output /tmp/antirot-report.json`
- Release tooling: `python3 -m pip install -e '.[dev,release]'`
- Packaging: `python3 -m build && python3 -m twine check dist/*`
- Packaged optimizer smoke: `github-stars-optimizer --demo --format json`

## Quality bar

- Score regression in `codex-harness audit` is a failure unless the task explicitly changes the gate.
- Secret-like strings, tracked credential files, private paths, and local URLs are release blockers.
- Public examples should prefer placeholders such as `/path/to/repo`, `/path/to/workspace`, and `your-user` unless a real public artifact is the point of the example.
- README and PR template drift are part of the product surface, not optional polish.
