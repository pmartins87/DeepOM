#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
if [ ! -x "$VENV/bin/python" ]; then
  echo "ERROR: $VENV is missing."
  exit 1
fi

mkdir -p runs

echo "=== DeepOM OM6 packed-showdown-score gate ==="
echo "Both variants use all previously accepted caches, fast evaluator and raw class lookup."
echo "Only evaluator result representation changes: HandRank objects vs packed monotone integer scores."
echo

"$VENV/bin/python" tools/benchmark_om6_packed_score_ab.py   --iterations 2   --deals 500   --seed 123   --output runs/om6_packed_score_ab_4w_i2_d500_seed123.json

echo
echo "=== Post-packed-score hot-path profile ==="

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --output-json runs/om6_profile_post_packed_score_4w_d500_seed123.json   --output-text runs/om6_profile_post_packed_score_4w_d500_seed123.txt   --output-prof runs/om6_profile_post_packed_score_4w_d500_seed123.prof

echo
echo "OM6_PACKED_SCORE_GATE=COMPLETE"
echo "Send back:"
echo "  runs/om6_packed_score_ab_4w_i2_d500_seed123.json"
echo "  runs/om6_profile_post_packed_score_4w_d500_seed123.json"
