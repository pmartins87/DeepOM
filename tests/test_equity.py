import math
import unittest

from deepom.equity import (
    exact_equity_known_hands,
    monte_carlo_equity_known_hands,
    monte_carlo_equity_vs_random,
    qualifying_royal_suits,
    royal_flush_flop_probability,
    royal_flush_full_board_probability,
)


class ExactEquityTests(unittest.TestCase):
    def test_river_locked_winner(self):
        hero = "As Ks 2c 3d".split()
        villain = "Ah Kh 4c 5d".split()
        board = "Qs Js Ts 7c 8d".split()
        r = exact_equity_known_hands(hero, [villain], board=board)
        self.assertTrue(r.exact)
        self.assertEqual(r.samples, 1)
        self.assertEqual(r.equity, 1.0)
        self.assertEqual(r.win_rate, 1.0)

    def test_exact_equity_rates_sum_to_one(self):
        hero = "As Ks 2c 3d".split()
        villain = "Ah Kh 4c 5d".split()
        board = "Qs Js 7c 8d".split()
        r = exact_equity_known_hands(hero, [villain], board=board)
        self.assertAlmostEqual(
            r.win_rate + r.tie_rate + r.loss_rate, 1.0, places=12
        )
        self.assertEqual(r.samples, 40)

    def test_preflop_guard_prevents_accidental_huge_exact_run(self):
        hero = "As Ks 2c 3d".split()
        villain = "Ah Kh 4c 5d".split()
        with self.assertRaises(ValueError):
            exact_equity_known_hands(hero, [villain])


class MonteCarloTests(unittest.TestCase):
    def test_seed_is_reproducible(self):
        hero = "As Ks Qh Jd".split()
        villain = "Ah Kh Qc Jc".split()
        a = monte_carlo_equity_known_hands(
            hero, [villain], samples=200, seed=123
        )
        b = monte_carlo_equity_known_hands(
            hero, [villain], samples=200, seed=123
        )
        self.assertEqual(a, b)

    def test_monte_carlo_matches_exact_flop_within_statistical_tolerance(self):
        hero = "As Ks Qh Jd".split()
        villain = "Ah Kh Qc Jc".split()
        flop = "2s 7d Tc".split()
        exact = exact_equity_known_hands(
            hero, [villain], board=flop, max_runouts=1000
        )
        mc = monte_carlo_equity_known_hands(
            hero, [villain], board=flop, samples=2500, seed=991
        )
        tolerance = max(0.04, 4.0 * mc.standard_error)
        self.assertLessEqual(abs(mc.equity - exact.equity), tolerance)

    def test_random_multiway_equity_is_bounded_and_rates_sum(self):
        hero = "As Ks Qh Jd".split()
        r = monte_carlo_equity_vs_random(
            hero, num_opponents=2, samples=100, seed=5
        )
        self.assertGreaterEqual(r.equity, 0.0)
        self.assertLessEqual(r.equity, 1.0)
        self.assertAlmostEqual(
            r.win_rate + r.tie_rate + r.loss_rate, 1.0, places=12
        )


class JackpotProbabilityTests(unittest.TestCase):
    def test_one_qualifying_suit(self):
        hole = "As Ks 2c 3d".split()
        self.assertEqual(qualifying_royal_suits(hole), ("s",))
        expected_full = math.comb(45, 2) / math.comb(48, 5)
        expected_flop = 1 / math.comb(48, 3)
        self.assertAlmostEqual(
            royal_flush_full_board_probability(hole), expected_full, places=15
        )
        self.assertAlmostEqual(
            royal_flush_flop_probability(hole), expected_flop, places=15
        )

    def test_two_qualifying_suits(self):
        hole = "As Ks Ah Kh".split()
        self.assertEqual(set(qualifying_royal_suits(hole)), {"s", "h"})
        expected = 2 * math.comb(45, 2) / math.comb(48, 5)
        self.assertAlmostEqual(
            royal_flush_full_board_probability(hole), expected, places=15
        )

    def test_three_royal_cards_same_suit_cannot_make_omaha_royal(self):
        hole = "As Ks Qs 2d".split()
        self.assertEqual(qualifying_royal_suits(hole), ())
        self.assertEqual(royal_flush_full_board_probability(hole), 0.0)


if __name__ == "__main__":
    unittest.main()
