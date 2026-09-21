#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
if [ ! -x "$VENV/bin/python" ]; then
  echo "ERROR: $VENV is missing."
  exit 1
fi

mkdir -p runs cache

echo "=== DeepOM OM6 exact five-card score-table gate ==="
echo "First run may spend time constructing the 2,598,960-entry table."
echo "The table is cached under cache/ and reused on later runs."
echo

"$VENV/bin/python" tools/benchmark_om6_fivecard_table_ab.py   --iterations 2   --deals 500   --seed 123   --table cache/five_card_scores_v1.npy   --output runs/om6_fivecard_table_ab_4w_i2_d500_seed123.json

echo
echo "=== Post-five-card-table hot-path profile ==="

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --five-card-table cache/five_card_scores_v1.npy   --output-json runs/om6_profile_post_fivecard_table_4w_d500_seed123.json   --output-text runs/om6_profile_post_fivecard_table_4w_d500_seed123.txt   --output-prof runs/om6_profile_post_fivecard_table_4w_d500_seed123.prof

echo
echo "OM6_FIVECARD_TABLE_GATE=COMPLETE"
echo "Send back:"
echo "  runs/om6_fivecard_table_ab_4w_i2_d500_seed123.json"
echo "  runs/om6_profile_post_fivecard_table_4w_d500_seed123.json"
