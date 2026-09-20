from __future__ import annotations

from itertools import combinations
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from treys import Card, Evaluator

from deepom.equity import DECK
from deepom.evaluator import evaluate_omaha


E = Evaluator()


def treys_omaha_score(hole: tuple[str, ...], board: tuple[str, ...]) -> int:
    best = None
    for h2 in combinations(hole, 2):
        for b3 in combinations(board, 3):
            five = [Card.new(c) for c in (*h2, *b3)]
            score = E.evaluate([], five)
            if best is None or score < best:
                best = score
    assert best is not None
    return best


def sign(v: int) -> int:
    return (v > 0) - (v < 0)


def main() -> None:
    rng = random.Random(20260920)
    cases = 5000
    mismatches = 0

    for _ in range(cases):
        cards = rng.sample(DECK, 13)
        a = tuple(cards[:4])
        b = tuple(cards[4:8])
        board = tuple(cards[8:13])

        ours_a = evaluate_omaha(a, board)
        ours_b = evaluate_omaha(b, board)
        ours_cmp = sign((ours_a > ours_b) - (ours_a < ours_b))

        treys_a = treys_omaha_score(a, board)
        treys_b = treys_omaha_score(b, board)
        # Treys uses lower score = stronger hand.
        treys_cmp = sign(treys_b - treys_a)

        if ours_cmp != treys_cmp:
            mismatches += 1
            print(
                "MISMATCH",
                a,
                b,
                board,
                ours_a,
                ours_b,
                treys_a,
                treys_b,
            )
            if mismatches >= 10:
                break

    print(f"cases={cases} mismatches={mismatches}")
    if mismatches:
        raise SystemExit(1)
    print("OM1_TREYS_DIFFERENTIAL=PASS")


if __name__ == "__main__":
    main()
