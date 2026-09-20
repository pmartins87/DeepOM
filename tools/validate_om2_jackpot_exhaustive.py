from __future__ import annotations

from itertools import combinations
from math import comb
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.equity import (
    DECK,
    qualifying_royal_suits,
    royal_flush_full_board_probability,
)
from deepom.evaluator import normalize_cards


def brute_count(hole_cards: list[str]) -> tuple[int, int]:
    hole = normalize_cards(hole_cards, expected=4)
    hole_set = set(hole)
    remaining = tuple(c for c in DECK if c not in hole_set)
    targets = []
    for suit in qualifying_royal_suits(hole):
        royal = {r + suit for r in "TJQKA"}
        targets.append(royal - hole_set)

    favorable = 0
    total = 0
    for board in combinations(remaining, 5):
        b = set(board)
        if any(target <= b for target in targets):
            favorable += 1
        total += 1
    return favorable, total


def main() -> None:
    cases = [
        ["As", "Ks", "2c", "3d"],
        ["As", "Ks", "Ah", "Kh"],
        ["As", "Ks", "Qs", "2d"],
    ]
    start = perf_counter()

    for hole in cases:
        favorable, total = brute_count(hole)
        formula = royal_flush_full_board_probability(hole)
        expected_favorable = round(formula * total)
        print(
            "hole={} favorable={} expected={} total={} probability={:.15f} {}".format(
                "".join(hole),
                favorable,
                expected_favorable,
                total,
                formula,
                "PASS" if favorable == expected_favorable else "FAIL",
            )
        )
        if total != comb(48, 5) or favorable != expected_favorable:
            raise SystemExit(1)

    print(f"elapsed_seconds={perf_counter() - start:.3f}")
    print("OM2_JACKPOT_EXHAUSTIVE=PASS")


if __name__ == "__main__":
    main()
