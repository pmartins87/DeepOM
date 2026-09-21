from __future__ import annotations

import argparse
import cProfile
import json
from pathlib import Path
import pstats
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.dense_solver import DenseExternalSamplingCFR, PLO4ClassIndex


TARGET_FUNCTIONS = (
    "evaluate_omaha",
    "evaluate_five",
    "canonical_key_plo4",
    "canonicalize_plo4",
    "normalized_hand",
    "index_of",
    "info_indices",
    "_traverse_external",
    "current_strategy",
    "_terminal_utility",
    "gross_terminal_payoff",
    "scenario_for_state",
    "next_actor_index",
    "apply_action",
    "sample_full_deal",
)


def _function_stats(stats: pstats.Stats, function_name: str) -> dict[str, float | int]:
    calls = 0
    primitive_calls = 0
    self_seconds = 0.0
    cumulative_seconds = 0.0

    for (filename, lineno, funcname), values in stats.stats.items():
        if funcname != function_name:
            continue
        cc, nc, tt, ct, _callers = values
        primitive_calls += int(cc)
        calls += int(nc)
        self_seconds += float(tt)
        cumulative_seconds += float(ct)

    return {
        "primitive_calls": primitive_calls,
        "calls": calls,
        "self_seconds": self_seconds,
        "cumulative_seconds": cumulative_seconds,
    }


def _top_rows(stats: pstats.Stats, *, limit: int = 40) -> list[dict[str, object]]:
    rows = []
    for (filename, lineno, funcname), values in stats.stats.items():
        cc, nc, tt, ct, _callers = values
        rows.append(
            {
                "file": Path(filename).name,
                "line": int(lineno),
                "function": funcname,
                "primitive_calls": int(cc),
                "calls": int(nc),
                "self_seconds": float(tt),
                "cumulative_seconds": float(ct),
            }
        )
    rows.sort(key=lambda row: float(row["cumulative_seconds"]), reverse=True)
    return rows[:limit]


def _share(seconds: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, seconds / total))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("4w", "3w", "2w"), default="4w")
    ap.add_argument("--deals", type=int, default=500)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--output-text", type=Path, required=True)
    ap.add_argument("--output-prof", type=Path, required=True)
    args = ap.parse_args()

    if args.deals < 1:
        raise SystemExit("--deals must be >= 1")

    # Deliberately exclude the one-time exact class-index build from hot-path profiling.
    t0 = time.perf_counter()
    class_index = PLO4ClassIndex.build()
    index_build_seconds = time.perf_counter() - t0

    solver = DenseExternalSamplingCFR(
        mode=args.mode,
        class_index=class_index,
        seed=args.seed,
        economic_preset=None,
    )

    profiler = cProfile.Profile()
    wall_start = time.perf_counter()
    profiler.enable()
    solver.run(additional_iterations=1, deals_per_iteration=args.deals)
    profiler.disable()
    wall_seconds = time.perf_counter() - wall_start

    args.output_prof.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(str(args.output_prof))

    stats = pstats.Stats(profiler)
    total_profile_seconds = float(stats.total_tt)

    targeted = {
        name: _function_stats(stats, name)
        for name in TARGET_FUNCTIONS
    }

    eval_seconds = float(targeted["evaluate_omaha"]["cumulative_seconds"])
    canonical_seconds = float(targeted["canonical_key_plo4"]["cumulative_seconds"])

    eval_share = _share(eval_seconds, total_profile_seconds)
    canonical_share = _share(canonical_seconds, total_profile_seconds)
    residual_share = max(0.0, 1.0 - eval_share - canonical_share)

    if eval_share >= canonical_share and eval_share >= residual_share:
        provisional_dominant_family = "omaha_evaluator"
    elif canonical_share >= eval_share and canonical_share >= residual_share:
        provisional_dominant_family = "plo4_canonicalization_lookup"
    else:
        provisional_dominant_family = "cfr_python_and_other"

    result = {
        "schema": 1,
        "mode": args.mode,
        "deals": args.deals,
        "seed": args.seed,
        "economics": None,
        "class_count": len(class_index.keys),
        "class_index_sha256": class_index.sha256,
        "index_build_excluded_from_profile": True,
        "index_build_seconds": index_build_seconds,
        "wall_seconds_profiled": wall_seconds,
        "profile_total_seconds": total_profile_seconds,
        "profiled_deals_per_second": (
            args.deals / wall_seconds if wall_seconds > 0 else None
        ),
        "visited_infosets": solver.visited_infosets(),
        "mean_positive_regret": solver.mean_positive_regret(),
        "target_functions": targeted,
        "high_level_attribution": {
            "evaluate_omaha_cumulative_seconds": eval_seconds,
            "evaluate_omaha_share_of_profile": eval_share,
            "canonical_key_plo4_cumulative_seconds": canonical_seconds,
            "canonical_key_plo4_share_of_profile": canonical_share,
            "residual_share": residual_share,
            "provisional_dominant_family": provisional_dominant_family,
            "note": (
                "evaluate_omaha and canonical_key_plo4 are disjoint high-level paths "
                "in the gross trainer, so their cumulative shares are directly useful. "
                "Residual includes traversal/state/NumPy/Python and other work."
            ),
        },
        "top_functions_by_cumulative_time": _top_rows(stats, limit=40),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    args.output_text.parent.mkdir(parents=True, exist_ok=True)
    with args.output_text.open("w", encoding="utf-8") as fh:
        fh.write("DeepOM OM6 hot-path profile\n")
        fh.write("=" * 72 + "\n")
        fh.write(json.dumps(result["high_level_attribution"], indent=2, sort_keys=True))
        fh.write("\n\nTop 40 by cumulative time\n")
        fh.write("-" * 72 + "\n")
        stats_stream = pstats.Stats(profiler, stream=fh).strip_dirs().sort_stats("cumulative")
        stats_stream.print_stats(40)

    print(json.dumps(result["high_level_attribution"], indent=2, sort_keys=True))
    print(f"profiled_deals_per_second={result['profiled_deals_per_second']:.6f}")
    print(f"visited_infosets={result['visited_infosets']}")
    print("OM6_HOTPATH_PROFILE=COMPLETE")
    print(f"json={args.output_json}")
    print(f"text={args.output_text}")
    print(f"prof={args.output_prof}")


if __name__ == "__main__":
    main()
