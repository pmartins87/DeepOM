from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from deepom.dense_solver import DenseExternalSamplingCFR, PLO4ClassIndex


def run_variant(
    *,
    class_index: PLO4ClassIndex,
    seed: int,
    iterations: int,
    deals: int,
    packed_showdown_scores: bool,
) -> tuple[DenseExternalSamplingCFR, float]:
    solver = DenseExternalSamplingCFR(
        mode="4w",
        class_index=class_index,
        seed=seed,
        economic_preset=None,
        precompute_showdown_ranks=True,
        precompute_class_indices=True,
        fast_omaha_evaluator=True,
        packed_showdown_scores=packed_showdown_scores,
        fast_class_lookup=True,
    )
    t0 = time.perf_counter()
    solver.run(additional_iterations=iterations, deals_per_iteration=deals)
    return solver, time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=2)
    ap.add_argument("--deals", type=int, default=500)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    index = PLO4ClassIndex.build()
    index_seconds = time.perf_counter() - t0

    handrank, handrank_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        packed_showdown_scores=False,
    )
    packed, packed_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        packed_showdown_scores=True,
    )

    np.testing.assert_array_equal(handrank.regrets, packed.regrets)
    np.testing.assert_array_equal(handrank.strategy_sum, packed.strategy_sum)
    np.testing.assert_array_equal(handrank.visits, packed.visits)

    total_deals = args.iterations * args.deals
    handrank_dps = total_deals / handrank_seconds
    packed_dps = total_deals / packed_seconds

    result = {
        "schema": 1,
        "mode": "4w",
        "iterations": args.iterations,
        "deals_per_iteration": args.deals,
        "total_deals": total_deals,
        "seed": args.seed,
        "class_count": len(index.keys),
        "class_index_sha256": index.sha256,
        "raw_lookup_sha256": index.raw_lookup_sha256,
        "index_build_seconds": index_seconds,
        "handrank": {
            "packed_showdown_scores": False,
            "train_seconds": handrank_seconds,
            "deals_per_second": handrank_dps,
            "visited_infosets": handrank.visited_infosets(),
            "arrays_sha256": handrank.manifest()["arrays_sha256"],
        },
        "packed": {
            "packed_showdown_scores": True,
            "train_seconds": packed_seconds,
            "deals_per_second": packed_dps,
            "visited_infosets": packed.visited_infosets(),
            "arrays_sha256": packed.manifest()["arrays_sha256"],
        },
        "exact_trajectory_match": (
            handrank.manifest()["arrays_sha256"] == packed.manifest()["arrays_sha256"]
        ),
        "speedup_packed_over_handrank": packed_dps / handrank_dps,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["exact_trajectory_match"]:
        raise SystemExit("packed showdown score changed the CFR trajectory")
    print("OM6_PACKED_SCORE_AB=PASS")


if __name__ == "__main__":
    main()
