import unittest

from deepom.aof_kernel import ALLIN, FOLD, apply_action, initial_state
from deepom.economics import (
    GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
    deterministic_jackpot_ev_bb,
    economic_terminal_payoff,
    inherited_deepaof_fortune_ev_bb,
)


class EconomicPresetTests(unittest.TestCase):
    def test_development_preset_fixed_fee(self):
        p = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0
        self.assertAlmostEqual(p.net_base_rake_bb, 0.01625, places=12)
        self.assertAlmostEqual(p.fixed_fee_per_player_bb, 0.06625, places=12)

    def test_inherited_fortune_calibration(self):
        self.assertAlmostEqual(
            inherited_deepaof_fortune_ev_bb(pool_usd=77_273.23),
            0.10715968,
            places=12,
        )
        self.assertAlmostEqual(
            inherited_deepaof_fortune_ev_bb(pool_usd=75_000.0),
            0.10400724804696271,
            places=12,
        )


class EconomicPayoffTests(unittest.TestCase):
    HOLES = [
        "As Ks 2c 3d".split(),
        "Ah 9h 4c 5d".split(),
    ]
    BOARD = "Qs Js Ts 7c 8d".split()

    def test_folded_player_still_pays_fixed_aof_fee_under_inherited_contract(self):
        s = apply_action(initial_state("2w"), FOLD)
        p = economic_terminal_payoff(
            s,
            hole_cards=self.HOLES,
            board_cards=self.BOARD,
        )
        fee = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0.fixed_fee_per_player_bb
        self.assertAlmostEqual(p.net_utilities_bb[0], -0.5 - fee, places=12)
        self.assertAlmostEqual(p.net_utilities_bb[1], 0.5 - fee, places=12)

    def test_fortune_credit_only_after_allin(self):
        s = initial_state("2w")
        s = apply_action(s, ALLIN)
        s = apply_action(s, FOLD)
        p = economic_terminal_payoff(
            s,
            hole_cards=self.HOLES,
            board_cards=self.BOARD,
        )
        fortune = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0.fortune_ev_bb
        self.assertAlmostEqual(p.fortune_credits_bb[0], fortune, places=12)
        self.assertEqual(p.fortune_credits_bb[1], 0.0)
        self.assertEqual(p.jackpot_credits_bb, (0.0, 0.0))

    def test_jackpot_credit_on_multi_player_showdown(self):
        s = initial_state("2w")
        s = apply_action(s, ALLIN)
        s = apply_action(s, ALLIN)
        p = economic_terminal_payoff(
            s,
            hole_cards=self.HOLES,
            board_cards=self.BOARD,
        )
        expected = deterministic_jackpot_ev_bb(
            self.HOLES[0],
            jackpot_prize_bb=375.0,
        )
        self.assertAlmostEqual(p.jackpot_credits_bb[0], expected, places=12)
        self.assertGreater(expected, 0.2)
        self.assertEqual(p.jackpot_credits_bb[1], 0.0)

    def test_sensitivity_multipliers_are_linear(self):
        s = initial_state("2w")
        s = apply_action(s, ALLIN)
        s = apply_action(s, ALLIN)
        a = economic_terminal_payoff(
            s,
            hole_cards=self.HOLES,
            board_cards=self.BOARD,
            fortune_multiplier=1.0,
            jackpot_multiplier=1.0,
        )
        b = economic_terminal_payoff(
            s,
            hole_cards=self.HOLES,
            board_cards=self.BOARD,
            fortune_multiplier=2.0,
            jackpot_multiplier=2.0,
        )
        self.assertAlmostEqual(
            b.fortune_credits_bb[0],
            2.0 * a.fortune_credits_bb[0],
            places=12,
        )
        self.assertAlmostEqual(
            b.jackpot_credits_bb[0],
            2.0 * a.jackpot_credits_bb[0],
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
