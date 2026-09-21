import random
import unittest
from itertools import combinations

import numpy as np

from deepom.evaluator import (
    CARD_CODE,
    _evaluate_five_codes_score,
    evaluate_omaha_score,
)
from deepom.fivecard_table import (
    CARD_INDEX,
    FIVE_CARD_COUNT,
    FiveCardScoreTable,
    colex_rank5,
    colex_rank5_sorted,
    evaluate_omaha_score_table,
    evaluate_omaha_score_table_indices,
)


class FiveCardCombinadicTests(unittest.TestCase):
    def test_boundary_ranks(self):
        self.assertEqual(colex_rank5((0, 1, 2, 3, 4)), 0)
        self.assertEqual(colex_rank5((47, 48, 49, 50, 51)), FIVE_CARD_COUNT - 1)

    def test_order_independent_rank(self):
        cards = (3, 17, 21, 40, 51)
        expected = colex_rank5(cards)
        self.assertEqual(colex_rank5(reversed(cards)), expected)

    def test_duplicate_index_rejected(self):
        with self.assertRaises(ValueError):
            colex_rank5((1, 1, 2, 3, 4))


class PartialTableOmahaTests(unittest.TestCase):
    def test_table_path_matches_arithmetic_on_random_corpus(self):
        ranks = "23456789TJQKA"
        suits = "cdhs"
        deck = [r + s for r in ranks for s in suits]
        rng = random.Random(2026092102)

        scores = np.zeros(FIVE_CARD_COUNT, dtype=np.uint32)

        corpus = []
        for _ in range(50):
            cards = rng.sample(deck, 9)
            hole = tuple(cards[:4])
            board = tuple(cards[4:])
            corpus.append((hole, board))

            for h2 in combinations(hole, 2):
                for b3 in combinations(board, 3):
                    five = tuple(sorted(CARD_INDEX[c] for c in (*h2, *b3)))
                    idx = colex_rank5_sorted(*five)
                    encoded = tuple(CARD_CODE[c] for c in (*h2, *b3))
                    scores[idx] = _evaluate_five_codes_score(*encoded)

        table = FiveCardScoreTable(
            scores=scores,
            sha256="partial-test-table",
            path=None,
            build_seconds=None,
            loaded_from_cache=False,
        )

        for hole, board in corpus:
            with self.subTest(hole=hole, board=board):
                expected = evaluate_omaha_score(hole, board)
                self.assertEqual(
                    evaluate_omaha_score_table(hole, board, table),
                    expected,
                )
                self.assertEqual(
                    evaluate_omaha_score_table_indices(
                        tuple(CARD_INDEX[c] for c in hole),
                        tuple(CARD_INDEX[c] for c in board),
                        table,
                    ),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
