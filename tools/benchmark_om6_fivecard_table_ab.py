from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import random
import sys
import time
from itertools import combinations

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from deepom.dense_solver import DenseExternalSamplingCFR, PLO4ClassIndex
from deepom.evaluator import CARD_CODE, _evaluate_five_codes_score, evaluate_omaha_score
from deepom.fivecard_table import (
    CARD_CODE_BY_INDEX,
    DECK52,
    FIVE_CARD_COUNT,
    FiveCardScoreTable,
    colex_rank5,
    evaluate_omaha_score_table,
)


def validate_full_table(table: FiveCardScoreTable, *, seed: int = 20260921) -> dict[str, int]:
    rng = random.Random(seed)

    five_card_cases = 5000
    for _ in range(five_card_cases):
        indices = sorted(rng.sample(range(52), 5))
        expected = _evaluate_five_codes_score(
            *(CARD_CODE_BY_INDEX[i] for i in indices)
        )
        actual = int(table.scores[colex_rank5(indices)])
        if actual != expected:
            raise AssertionError(
                f"five-card table mismatch indices={indices}: "
                f"table={actual} arithmetic={expected}"
            )

    omaha_cases = 1000
    deck = list(DECK52)
    for _ in range(omaha_cases):
        cards = rng.sample(deck, 9)
        hole = cards[:4]
        board = cards[4:]
        expected = evaluate_omaha_score(hole, board)
        actual = evaluate_omaha_score_table(hole, board, table)
        if actual != expected:
            raise AssertionError(
                f"Omaha table mismatch hole={hole} board={board}: "
                f"table={actual} arithmetic={expected}"
            )

    return {
        "five_card_cases": five_card_cases,
        "omaha_cases": omaha_cases,
        "mismatches": 0,
    }


def run_variant(
    *,
    class_index: PLO4ClassIndex,
    table: FiveCardScoreTable | None,
    seed: int,
    iterations: int,
    deals: int,
) -> tuple[DenseExternalSamplingCFR, float]:
    solver = DenseExternalSamplingCFR(
        mode="4w",
        class_index=class_index,
        seed=seed,
        economic_preset=None,
        precompute_showdown_ranks=True,
        precompute_class_indices=True,
        fast_omaha_evaluator=True,
        packed_showdown_scores=True,
        fast_class_lookup=True,
        five_card_score_table=table,
    )
    t0 = time.perf_counter()
    solver.run(additional_iterations=iterations, deals_per_iteration=deals)
    return solver, time.perf_counter() - t0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=2)
    ap.add_argument("--deals", type=int, default=500)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument(
        "--table",
        type=Path,
        default=Path("cache/five_card_scores_v1.npy"),
    )
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    index = PLO4ClassIndex.build()
    index_seconds = time.perf_counter() - t0

    table_t0 = time.perf_counter()
    table = FiveCardScoreTable.load_or_build(args.table)
    table_total_seconds = time.perf_counter() - table_t0

    validation = validate_full_table(table)

    arithmetic, arithmetic_seconds = run_variant(
        class_index=index,
        table=None,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
    )
    lookup, lookup_seconds = run_variant(
        class_index=index,
        table=table,
        seed=args.seed,
        iterations=args.iterations,
        deals=args.deals,
    )

    np.testing.assert_array_equal(arithmetic.regrets, lookup.regrets)
    np.testing.assert_array_equal(arithmetic.strategy_sum, lookup.strategy_sum)
    np.testing.assert_array_equal(arithmetic.visits, lookup.visits)

    total_deals = args.iterations * args.deals
    arithmetic_dps = total_deals / arithmetic_seconds
    lookup_dps = total_deals / lookup_seconds

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
        "class_index_build_seconds": index_seconds,
        "five_card_table": {
            "path": str(args.table),
            "entries": FIVE_CARD_COUNT,
            "bytes": int(table.scores.nbytes),
            "sha256": table.sha256,
            "loaded_from_cache": table.loaded_from_cache,
            "build_or_load_seconds": table_total_seconds,
            "builder_seconds": table.build_seconds,
            "validation": validation,
        },
        "arithmetic": {
            "five_card_table": False,
            "train_seconds": arithmetic_seconds,
            "deals_per_second": arithmetic_dps,
            "visited_infosets": arithmetic.visited_infosets(),
            "arrays_sha256": arithmetic.manifest()["arrays_sha256"],
        },
        "lookup": {
            "five_card_table": True,
            "train_seconds": lookup_seconds,
            "deals_per_second": lookup_dps,
            "visited_infosets": lookup.visited_infosets(),
            "arrays_sha256": lookup.manifest()["arrays_sha256"],
        },
        "exact_trajectory_match": (
            arithmetic.manifest()["arrays_sha256"]
            == lookup.manifest()["arrays_sha256"]
        ),
        "speedup_lookup_over_arithmetic": lookup_dps / arithmetic_dps,
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
        raise SystemExit("five-card lookup changed the CFR trajectory")
    print("OM6_FIVECARD_TABLE_AB=PASS")


if __name__ == "__main__":
    main()
