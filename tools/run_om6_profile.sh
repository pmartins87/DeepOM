#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"

if [ ! -x "$VENV/bin/python" ]; then
  echo "ERROR: $VENV is missing. Run tools/run_om6_local_benchmark.sh once to create it."
  exit 1
fi

mkdir -p runs

echo "=== DeepOM OM6 hot-path profiling gate ==="
echo "Gross-payoff mode is intentional: prior benchmark showed only ~1.38% economic overhead."
echo "Class-index build is measured but excluded from the hot-path profile."
echo

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --output-json runs/om6_profile_4w_gross_d500_seed123.json   --output-text runs/om6_profile_4w_gross_d500_seed123.txt   --output-prof runs/om6_profile_4w_gross_d500_seed123.prof

echo
echo "OM6_PROFILING_GATE=COMPLETE"
echo "Send back at least:"
echo "  runs/om6_profile_4w_gross_d500_seed123.json"
echo "The .txt and .prof files are retained for deeper inspection if needed."
