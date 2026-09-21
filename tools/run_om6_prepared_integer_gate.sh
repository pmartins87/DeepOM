#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
TABLE="cache/five_card_scores_v1.npy"

if [ ! -x "$VENV/bin/python" ]; then
  echo "ERROR: $VENV is missing."
  exit 1
fi

if [ ! -f "$TABLE" ]; then
  echo "ERROR: expected five-card cache not found:"
  echo "  $TABLE"
  echo "Run tools/run_om6_fivecard_table_gate.sh first."
  exit 1
fi

mkdir -p runs

echo "=== DeepOM OM6 resident/pre-indexed deal gate ==="
echo "Reference: memory-mapped table + validated string-card path."
echo "Fast: resident table + one-time card-index preparation."
echo

"$VENV/bin/python" tools/benchmark_om6_prepared_integer_ab.py   --iterations 2   --deals 500   --seed 123   --table "$TABLE"   --output runs/om6_prepared_integer_ab_4w_i2_d500_seed123.json

echo
echo "=== Post-prepared-integer hot-path profile ==="

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --five-card-table "$TABLE"   --output-json runs/om6_profile_post_prepared_integer_4w_d500_seed123.json   --output-text runs/om6_profile_post_prepared_integer_4w_d500_seed123.txt   --output-prof runs/om6_profile_post_prepared_integer_4w_d500_seed123.prof

echo
echo "OM6_PREPARED_INTEGER_GATE=COMPLETE"
echo "Send back:"
echo "  runs/om6_prepared_integer_ab_4w_i2_d500_seed123.json"
echo "  runs/om6_profile_post_prepared_integer_4w_d500_seed123.json"
