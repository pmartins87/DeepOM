#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV="${VENV:-.venv}"

if [ ! -x "$VENV/bin/python" ]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --disable-pip-version-check -q -r requirements-dev.txt

mkdir -p runs

echo "=== DeepOM OM6 finite local benchmark ==="
echo "This is an engineering benchmark, not a production training run."

"$VENV/bin/python" tools/benchmark_dense_solver.py   --mode 4w   --iterations 2   --deals 100   --seed 123   --fortune-multiplier 1.0   --jackpot-multiplier 1.0   --output runs/om6_dense_4w_econ_i2_d100_seed123.json

"$VENV/bin/python" tools/benchmark_dense_solver.py   --mode 4w   --iterations 2   --deals 100   --seed 123   --gross   --output runs/om6_dense_4w_gross_i2_d100_seed123.json

echo
echo "OM6_LOCAL_BENCHMARK=COMPLETE"
echo "Outputs:"
echo "  runs/om6_dense_4w_econ_i2_d100_seed123.json"
echo "  runs/om6_dense_4w_gross_i2_d100_seed123.json"
