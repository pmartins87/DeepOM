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

echo "=== DeepOM OM6 PLO4 class-index cache gate ==="
echo "Both variants keep showdown-rank caching enabled."
echo

"$VENV/bin/python" tools/benchmark_om6_class_cache_ab.py   --iterations 2   --deals 500   --seed 123   --output runs/om6_class_cache_ab_4w_i2_d500_seed123.json

echo
echo "=== Post-class-cache hot-path profile ==="

"$VENV/bin/python" tools/profile_om6_hotpath.py   --mode 4w   --deals 500   --seed 123   --output-json runs/om6_profile_post_class_cache_4w_d500_seed123.json   --output-text runs/om6_profile_post_class_cache_4w_d500_seed123.txt   --output-prof runs/om6_profile_post_class_cache_4w_d500_seed123.prof

echo
echo "OM6_CLASS_CACHE_GATE=COMPLETE"
echo "Send back:"
echo "  runs/om6_class_cache_ab_4w_i2_d500_seed123.json"
echo "  runs/om6_profile_post_class_cache_4w_d500_seed123.json"
