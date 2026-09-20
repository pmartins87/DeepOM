from __future__ import annotations

import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.canonical import brute_force_plo4_census


def main() -> None:
    start = perf_counter()
    result = brute_force_plo4_census()
    result["elapsed_seconds"] = perf_counter() - start

    print(json.dumps(result, indent=2, sort_keys=True))

    if result["raw_hands"] != 270_725:
        raise SystemExit("raw PLO4 hand count mismatch")
    if result["canonical_classes"] != result["burnside_classes"]:
        raise SystemExit("brute-force and Burnside class counts disagree")
    if result["canonical_classes"] != 16_432:
        raise SystemExit("unexpected canonical PLO4 class count")
    if result["reconstructed_raw"] != result["raw_hands"]:
        raise SystemExit("orbit histogram does not reconstruct raw hand count")

    print("OM4_PREFLOP_CENSUS=PASS")


if __name__ == "__main__":
    main()
