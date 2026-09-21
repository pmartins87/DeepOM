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

echo "=== DeepOM OM6 raw PLO4 class-lookup gate ==="
echo "Both variants keep showdown-rank cache, per-deal class cache and fast evaluator enabled."
echo "Only exact class resolution changes: 24-suit canonicalization vs raw-hand table."
echo

"$VENV/bin/python" tools/benchmark_om6_raw_class_lookup_ab.py   --iterations 2   --deals 500   --seed 123   --output runs/om6_raw_class_lookup_ab_4w_i2_d500_seed123.json

echo
echo "=== Post-raw-lookup hot-path profile ==="

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --output-json runs/om6_profile_post_raw_class_lookup_4w_d500_seed123.json   --output-text runs/om6_profile_post_raw_class_lookup_4w_d500_seed123.txt   --output-prof runs/om6_profile_post_raw_class_lookup_4w_d500_seed123.prof

echo
echo "OM6_RAW_CLASS_LOOKUP_GATE=COMPLETE"
echo "Send back:"
echo "  runs/om6_raw_class_lookup_ab_4w_i2_d500_seed123.json"
echo "  runs/om6_profile_post_raw_class_lookup_4w_d500_seed123.json"
