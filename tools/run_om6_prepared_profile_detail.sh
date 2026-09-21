#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
PROFILE="runs/om6_profile_post_prepared_integer_4w_d500_seed123.prof"
OUTPUT="runs/om6_profile_post_prepared_integer_detail.json"

if [ ! -x "$VENV/bin/python" ]; then
  echo "ERROR: $VENV is missing."
  exit 1
fi

if [ ! -f "$PROFILE" ]; then
  echo "ERROR: expected existing profile not found:"
  echo "  $PROFILE"
  exit 1
fi

echo "=== DeepOM OM6 prepared-integer detailed hotspot attribution ==="
echo "No training is run. This reads the existing post-prepared-integer cProfile artifact only."
echo

"$VENV/bin/python" tools/report_om6_profile_detail.py   "$PROFILE"   --top 30   --output "$OUTPUT"

echo
echo "OM6_PREPARED_PROFILE_DETAIL_GATE=COMPLETE"
echo "Send back the terminal output or:"
echo "  $OUTPUT"
