#!/bin/sh
set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  "$PYTHON_BIN" -m venv "$PROJECT_ROOT/.venv"
  "$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/01_source/requirements.txt"
elif [ "${REFRESH_DEPENDENCIES:-false}" = "true" ]; then
  "$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/01_source/requirements.txt"
fi

cd "$PROJECT_ROOT"
"$VENV_PYTHON" 04_tests/tests/run_tests.py
exec "$VENV_PYTHON" 04_tests/tests/run_service_tests.py
