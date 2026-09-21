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
    precompute_showdown_ranks: bool,
) -> tuple[DenseExternalSamplingCFR, float]:
    solver = DenseExternalSamplingCFR(
        mode="4w",
        class_index=class_index,
        seed=seed,
        economic_preset=None,
        precompute_showdown_ranks=precompute_showdown_ranks,
    )
    t0 = time.perf_counter()
    solver.run(
        additional_iterations=iterations,
        deals_per_iteration=deals,
    )
    elapsed = time.perf_counter() - t0
    return solver, elapsed


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

    legacy, legacy_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        precompute_showdown_ranks=False,
    )
    cached, cached_seconds = run_variant(
        class_index=index,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
        precompute_showdown_ranks=True,
    )

    np.testing.assert_array_equal(legacy.regrets, cached.regrets)
    np.testing.assert_array_equal(legacy.strategy_sum, cached.strategy_sum)
    np.testing.assert_array_equal(legacy.visits, cached.visits)

    total_deals = args.iterations * args.deals
    legacy_dps = total_deals / legacy_seconds
    cached_dps = total_deals / cached_seconds
    speedup = cached_dps / legacy_dps

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
        "legacy": {
            "precompute_showdown_ranks": False,
            "train_seconds": legacy_seconds,
            "deals_per_second": legacy_dps,
            "visited_infosets": legacy.visited_infosets(),
            "arrays_sha256": legacy.manifest()["arrays_sha256"],
        },
        "cached": {
            "precompute_showdown_ranks": True,
            "train_seconds": cached_seconds,
            "deals_per_second": cached_dps,
            "visited_infosets": cached.visited_infosets(),
            "arrays_sha256": cached.manifest()["arrays_sha256"],
        },
        "exact_trajectory_match": (
            legacy.manifest()["arrays_sha256"]
            == cached.manifest()["arrays_sha256"]
        ),
        "speedup_cached_over_legacy": speedup,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["exact_trajectory_match"]:
        raise SystemExit("cached solver changed the CFR trajectory")
    print("OM6_RANK_CACHE_AB=PASS")


if __name__ == "__main__":
    main()
