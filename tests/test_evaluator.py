import unittest

from deepom.evaluator import (
    FLUSH,
    FOUR_OF_A_KIND,
    FULL_HOUSE,
    HIGH_CARD,
    ONE_PAIR,
    STRAIGHT,
    STRAIGHT_FLUSH,
    THREE_OF_A_KIND,
    TWO_PAIR,
    evaluate_five,
    evaluate_omaha,
    qualifies_aof_omaha_jackpot,
)


class FiveCardEvaluatorTests(unittest.TestCase):
    def test_all_categories(self):
        cases = [
            ("As Kd 9h 6c 3s", HIGH_CARD),
            ("As Ad 9h 6c 3s", ONE_PAIR),
            ("As Ad 9h 9c 3s", TWO_PAIR),
            ("As Ad Ah 6c 3s", THREE_OF_A_KIND),
            ("9s 8d 7h 6c 5s", STRAIGHT),
            ("As Js 9s 6s 3s", FLUSH),
            ("As Ad Ah 6c 6s", FULL_HOUSE),
            ("As Ad Ah Ac 3s", FOUR_OF_A_KIND),
            ("9s 8s 7s 6s 5s", STRAIGHT_FLUSH),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(evaluate_five(text.split()).category, expected)

    def test_wheel_is_five_high_straight(self):
        r = evaluate_five("As 2d 3h 4c 5s".split())
        self.assertEqual((r.category, r.tiebreak), (STRAIGHT, (5,)))

    def test_tiebreak_ordering(self):
        self.assertGreater(
            evaluate_five("As Ad Kh Qc Js".split()),
            evaluate_five("Ks Kd Ah Qc Js".split()),
        )
        self.assertGreater(
            evaluate_five("As Kd Qh Jc 9s".split()),
            evaluate_five("As Kd Qh Tc 9s".split()),
        )


class OmahaSemanticsTests(unittest.TestCase):
    def test_official_style_four_spade_board_is_not_automatic_flush(self):
        # GGPoker example: one spade in hand cannot make a flush in Omaha.
        board = "As Ks Qs Js 2d".split()
        hole = "Ts 9c 7c 6d".split()
        r = evaluate_omaha(hole, board)
        self.assertEqual(r.category, STRAIGHT)

    def test_official_style_second_example_is_king_high_straight_flush_not_royal(self):
        # GGPoker example: Kd Jd Ts 9s on As Ks Qs Js 2d makes a K-high
        # straight flush with Ts9s + KsQsJs, not a royal flush.
        board = "As Ks Qs Js 2d".split()
        hole = "Kd Jd Ts 9s".split()
        r = evaluate_omaha(hole, board)
        self.assertEqual((r.category, r.tiebreak), (STRAIGHT_FLUSH, (13,)))

    def test_two_hole_cards_are_mandatory(self):
        board = "As Ks Qs Js Ts".split()
        hole = "2c 3d 4h 5c".split()
        self.assertNotEqual(evaluate_omaha(hole, board).category, STRAIGHT_FLUSH)

    def test_four_hole_card_shortcut_is_forbidden(self):
        hole = "As Ks Qs Js".split()
        board = "Ts 2d 3c 4h 9d".split()
        self.assertFalse(
            qualifies_aof_omaha_jackpot(hole, board, reached_showdown=True)
        )

    def test_duplicate_card_rejected_across_hole_and_board(self):
        with self.assertRaises(ValueError):
            evaluate_omaha(
                "As Kd Qh Jc".split(),
                "As 2d 3h 4c 5s".split(),
            )

    def test_requires_four_hole_cards(self):
        with self.assertRaises(ValueError):
            evaluate_omaha(
                "As Kd Qh".split(),
                "2s 3d 4h 5c 6s".split(),
            )


class JackpotTests(unittest.TestCase):
    def test_royal_flush_on_flop_qualifies_without_showdown(self):
        hole = "As Ks 2c 3d".split()
        flop = "Qs Js Ts".split()
        self.assertTrue(
            qualifies_aof_omaha_jackpot(hole, flop, reached_showdown=False)
        )

    def test_royal_flush_by_river_requires_showdown(self):
        hole = "As Ks 2c 3d".split()
        board = "Qs 7h Ts 4d Js".split()
        self.assertFalse(
            qualifies_aof_omaha_jackpot(hole, board, reached_showdown=False)
        )
        self.assertTrue(
            qualifies_aof_omaha_jackpot(hole, board, reached_showdown=True)
        )

    def test_same_suit_royal_requires_two_hole_cards(self):
        hole = "As 2c 3d 4h".split()
        board = "Ks Qs Js Ts 9s".split()
        self.assertFalse(
            qualifies_aof_omaha_jackpot(hole, board, reached_showdown=True)
        )


if __name__ == "__main__":
    unittest.main()
