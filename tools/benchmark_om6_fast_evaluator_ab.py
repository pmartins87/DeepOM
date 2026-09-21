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
    fast_omaha_evaluator: bool,
) -> tuple[DenseExternalSamplingCFR, float]:
    solver = DenseExternalSamplingCFR(
        mode="4w",
        class_index=class_index,
        seed=seed,
        economic_preset=None,
        precompute_showdown_ranks=True,
        precompute_class_indices=True,
        fast_omaha_evaluator=fast_omaha_evaluator,
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

    reference, reference_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        fast_omaha_evaluator=False,
    )
    fast, fast_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        fast_omaha_evaluator=True,
    )

    np.testing.assert_array_equal(reference.regrets, fast.regrets)
    np.testing.assert_array_equal(reference.strategy_sum, fast.strategy_sum)
    np.testing.assert_array_equal(reference.visits, fast.visits)

    total_deals = args.iterations * args.deals
    reference_dps = total_deals / reference_seconds
    fast_dps = total_deals / fast_seconds

    result = {
        "schema": 1,
        "mode": "4w",
        "iterations": args.iterations,
        "deals_per_iteration": args.deals,
        "total_deals": total_deals,
        "seed": args.seed,
        "class_count": len(index.keys),
        "class_index_sha256": index.sha256,
        "index_build_seconds": index_seconds,
        "reference": {
            "fast_omaha_evaluator": False,
            "train_seconds": reference_seconds,
            "deals_per_second": reference_dps,
            "visited_infosets": reference.visited_infosets(),
            "arrays_sha256": reference.manifest()["arrays_sha256"],
        },
        "fast": {
            "fast_omaha_evaluator": True,
            "train_seconds": fast_seconds,
            "deals_per_second": fast_dps,
            "visited_infosets": fast.visited_infosets(),
            "arrays_sha256": fast.manifest()["arrays_sha256"],
        },
        "exact_trajectory_match": (
            reference.manifest()["arrays_sha256"] == fast.manifest()["arrays_sha256"]
        ),
        "speedup_fast_over_reference": fast_dps / reference_dps,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["exact_trajectory_match"]:
        raise SystemExit("fast evaluator changed the CFR trajectory")
    print("OM6_FAST_EVALUATOR_AB=PASS")


if __name__ == "__main__":
    main()
