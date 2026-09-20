from __future__ import annotations

import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.aof_kernel import enumerate_decision_scenarios
from deepom.canonical import brute_force_plo4_census


def main() -> None:
    start = perf_counter()
    result = brute_force_plo4_census()

    scenarios_by_mode = {
        mode: len(enumerate_decision_scenarios(mode))
        for mode in ("4w", "3w", "2w")
    }
    classes = int(result["canonical_classes"])
    raw_hands = int(result["raw_hands"])

    infosets_by_mode = {
        mode: classes * count for mode, count in scenarios_by_mode.items()
    }
    raw_states_by_mode = {
        mode: raw_hands * count for mode, count in scenarios_by_mode.items()
    }

    result["decision_scenarios_by_mode"] = scenarios_by_mode
    result["exact_infosets_by_mode"] = infosets_by_mode
    result["exact_infosets_total"] = sum(infosets_by_mode.values())
    result["raw_hand_scenario_states_by_mode"] = raw_states_by_mode
    result["raw_hand_scenario_states_total"] = sum(raw_states_by_mode.values())
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
    if scenarios_by_mode != {"4w": 14, "3w": 6, "2w": 2}:
        raise SystemExit("AoF decision-scenario census mismatch")
    if infosets_by_mode != {"4w": 230_048, "3w": 98_592, "2w": 32_864}:
        raise SystemExit("canonical infoset census mismatch")
    if result["exact_infosets_total"] != 361_504:
        raise SystemExit("total canonical infoset census mismatch")

    print("OM4_PREFLOP_CENSUS=PASS")


if __name__ == "__main__":
    main()
