from __future__ import annotations

import argparse
import json
from pathlib import Path
import pstats


def _rows(stats: pstats.Stats) -> list[dict[str, object]]:
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
    return rows


def _top(rows: list[dict[str, object]], key: str, n: int) -> list[dict[str, object]]:
    return sorted(rows, key=lambda row: float(row[key]), reverse=True)[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("profile", type=Path)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    if not args.profile.exists():
        raise SystemExit(f"profile not found: {args.profile}")

    stats = pstats.Stats(str(args.profile))
    rows = _rows(stats)

    result = {
        "profile": str(args.profile),
        "profile_total_seconds": float(stats.total_tt),
        "top_by_cumulative": _top(rows, "cumulative_seconds", args.top),
        "top_by_self": _top(rows, "self_seconds", args.top),
    }

    print("=== OM6 profile detail: top by cumulative time ===")
    for i, row in enumerate(result["top_by_cumulative"], 1):
        print(
            f"{i:2d}. {row['cumulative_seconds']:.6f}s cum | "
            f"{row['self_seconds']:.6f}s self | "
            f"{row['calls']} calls | "
            f"{row['file']}:{row['line']} {row['function']}"
        )

    print()
    print("=== OM6 profile detail: top by self time ===")
    for i, row in enumerate(result["top_by_self"], 1):
        print(
            f"{i:2d}. {row['self_seconds']:.6f}s self | "
            f"{row['cumulative_seconds']:.6f}s cum | "
            f"{row['calls']} calls | "
            f"{row['file']}:{row['line']} {row['function']}"
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print()
        print(f"json={args.output}")

    print("OM6_PROFILE_DETAIL=COMPLETE")


if __name__ == "__main__":
    main()
