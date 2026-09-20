from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.evaluator import CATEGORY_NAME, RANK_CHARS, SUIT_CHARS, evaluate_five

EXPECTED = {
    "high_card": 1_302_540,
    "one_pair": 1_098_240,
    "two_pair": 123_552,
    "three_of_a_kind": 54_912,
    "straight": 10_200,
    "flush": 5_108,
    "full_house": 3_744,
    "four_of_a_kind": 624,
    "straight_flush": 40,
}


def main() -> None:
    deck = [r + s for r in RANK_CHARS for s in SUIT_CHARS]
    counts: Counter[str] = Counter()
    started = perf_counter()
    total = 0

    for hand in combinations(deck, 5):
        counts[CATEGORY_NAME[evaluate_five(hand).category]] += 1
        total += 1

    elapsed = perf_counter() - started
    print(f"enumerated={total} elapsed_seconds={elapsed:.3f}")

    for name, expected in EXPECTED.items():
        got = counts[name]
        print(
            f"{name}: got={got} expected={expected} "
            f"{'PASS' if got == expected else 'FAIL'}"
        )

    if total != 2_598_960 or dict(counts) != EXPECTED:
        raise SystemExit(1)

    print("OM1_5CARD_EXHAUSTIVE=PASS")


if __name__ == "__main__":
    main()
