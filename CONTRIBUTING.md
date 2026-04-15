# Contributing

AntiRot is intentionally narrow in `v0.2.0`. That is a feature, not an accident.

The bar for contributions is simple:

- the rule must catch a real evidence-hygiene failure mode
- the failure mode must be easy to explain in one sentence
- the check must be cheap enough to run locally and in CI
- the output must help an author fix the issue, not just shame them

## Local setup

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e '.[dev]'
pytest -q
```

## Typical contribution types

- new lint rules for unsupported claims, evidence drift, or citation hygiene
- new citation formats that are common in research markdown
- CLI output improvements
- CI integration examples
- better sample drafts and reference fixtures

## Contribution guidelines

1. Keep the change small and legible.
2. Add or update tests for every rule change.
3. Prefer standard-library implementations unless there is a strong reason not to.
4. Avoid turning AntiRot into a full paper-writing framework.
5. If a rule is heuristic, make that explicit in the wording.

## Rule design notes

- False positives matter. A noisy evidence linter will be ignored.
- Citations should be treated as anchors, not truth by themselves.
- Warnings should preserve author agency. Errors should represent stronger evidence gaps.
- The README demo should stay aligned with actual CLI output.
