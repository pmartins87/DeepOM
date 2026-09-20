from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import time

from deepom.dense_solver import DenseExternalSamplingCFR, PLO4ClassIndex
from deepom.economics import GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("4w", "3w", "2w"), default="4w")
    ap.add_argument("--iterations", type=int, default=2)
    ap.add_argument("--deals", type=int, default=100)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--gross", action="store_true")
    ap.add_argument("--fortune-multiplier", type=float, default=1.0)
    ap.add_argument("--jackpot-multiplier", type=float, default=1.0)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    t0 = time.perf_counter()
    index = PLO4ClassIndex.build()
    index_seconds = time.perf_counter() - t0

    solver = DenseExternalSamplingCFR(
        mode=args.mode,
        class_index=index,
        seed=args.seed,
        economic_preset=(
            None if args.gross else GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0
        ),
        fortune_multiplier=args.fortune_multiplier,
        jackpot_multiplier=args.jackpot_multiplier,
    )

    t1 = time.perf_counter()
    solver.run(
        additional_iterations=args.iterations,
        deals_per_iteration=args.deals,
    )
    train_seconds = time.perf_counter() - t1
    traversed_deals = args.iterations * args.deals

    result = {
        "mode": args.mode,
        "iterations": args.iterations,
        "deals_per_iteration": args.deals,
        "total_deals": traversed_deals,
        "seed": args.seed,
        "economics": None if args.gross else solver.economic_preset.preset_id,
        "fortune_multiplier": args.fortune_multiplier,
        "jackpot_multiplier": args.jackpot_multiplier,
        "class_count": len(index.keys),
        "class_index_sha256": index.sha256,
        "index_build_seconds": index_seconds,
        "train_seconds": train_seconds,
        "deals_per_second": (
            traversed_deals / train_seconds if train_seconds > 0 else None
        ),
        "visited_infosets": solver.visited_infosets(),
        "mean_positive_regret": solver.mean_positive_regret(),
        "core_bytes": solver.bytes_core,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
