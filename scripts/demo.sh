#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -x ".venv310/bin/antirot" ]; then
  echo "Expected .venv310 with AntiRot installed. Run:"
  echo "  python3.10 -m venv .venv310"
  echo "  .venv310/bin/python -m pip install --upgrade pip setuptools wheel"
  echo "  .venv310/bin/python -m pip install -e '.[dev]'"
  exit 1
fi

.venv310/bin/antirot lint examples/sloppy_paper.md \
  --references examples/references.md \
  --format markdown
