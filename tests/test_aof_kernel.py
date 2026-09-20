import unittest

from deepom.aof_kernel import (
    ALLIN,
    FOLD,
    MODE_CONFIGS,
    apply_action,
    enumerate_decision_scenarios,
    enumerate_terminal_states,
    gross_terminal_payoff,
    initial_state,
    is_terminal,
    scenario_for_state,
)


class ActionTreeTests(unittest.TestCase):
    def test_decision_scenarios_match_frozen_deepaof_tree(self):
        for mode in ("4w", "3w", "2w"):
            with self.subTest(mode=mode):
                self.assertEqual(
                    set(enumerate_decision_scenarios(mode)),
                    set(MODE_CONFIGS[mode]["scenarios"]),
                )

    def test_expected_decision_node_counts(self):
        self.assertEqual(len(enumerate_decision_scenarios("4w")), 14)
        self.assertEqual(len(enumerate_decision_scenarios("3w")), 6)
        self.assertEqual(len(enumerate_decision_scenarios("2w")), 2)

    def test_expected_terminal_leaf_counts(self):
        self.assertEqual(len(enumerate_terminal_states("4w")), 15)
        self.assertEqual(len(enumerate_terminal_states("3w")), 7)
        self.assertEqual(len(enumerate_terminal_states("2w")), 3)

    def test_hu_sb_fold_ends_without_bb_decision(self):
        s = apply_action(initial_state("2w"), FOLD)
        self.assertTrue(is_terminal(s))
        self.assertIsNone(scenario_for_state(s))

    def test_4w_walk_ends_after_sb_fold(self):
        s = initial_state("4w")
        for action in (FOLD, FOLD, FOLD):
            s = apply_action(s, action)
        self.assertTrue(is_terminal(s))


class GrossPayoffTests(unittest.TestCase):
    HOLES_2 = [
        "As Ks 2c 3d".split(),
        "Ah Kh 4c 5d".split(),
    ]
    BOARD = "Qs Js Ts 7c 8d".split()

    def test_hu_sb_fold_chip_conservation(self):
        s = apply_action(initial_state("2w"), FOLD)
        p = gross_terminal_payoff(s, hole_cards=self.HOLES_2, board_cards=self.BOARD)
        self.assertEqual(p.contributions_bb, (0.5, 1.0))
        self.assertEqual(p.payouts_bb, (0.0, 1.5))
        self.assertAlmostEqual(p.utility_sum_bb, 0.0, places=12)
        self.assertEqual(p.utilities_bb, (-0.5, 0.5))

    def test_hu_sb_shove_bb_fold(self):
        s = initial_state("2w")
        s = apply_action(s, ALLIN)
        s = apply_action(s, FOLD)
        p = gross_terminal_payoff(s, hole_cards=self.HOLES_2, board_cards=self.BOARD)
        self.assertEqual(p.contributions_bb, (5.0, 1.0))
        self.assertEqual(p.payouts_bb, (6.0, 0.0))
        self.assertEqual(p.utilities_bb, (1.0, -1.0))
        self.assertAlmostEqual(p.utility_sum_bb, 0.0, places=12)

    def test_hu_allin_showdown_uses_omaha_evaluator(self):
        s = initial_state("2w")
        s = apply_action(s, ALLIN)
        s = apply_action(s, ALLIN)
        p = gross_terminal_payoff(s, hole_cards=self.HOLES_2, board_cards=self.BOARD)
        self.assertEqual(p.payouts_bb, (10.0, 0.0))
        self.assertEqual(p.utilities_bb, (5.0, -5.0))
        self.assertAlmostEqual(p.utility_sum_bb, 0.0, places=12)

    def test_4w_walk_conservation(self):
        holes = [
            "2c 3c 4c 5c".split(),
            "6c 7c 8c 9c".split(),
            "Tc Jc Qc Kc".split(),
            "Ad 2d 3d 4d".split(),
        ]
        board = "5d 6d 7d 8d 9d".split()
        s = initial_state("4w")
        for action in (FOLD, FOLD, FOLD):
            s = apply_action(s, action)
        p = gross_terminal_payoff(s, hole_cards=holes, board_cards=board)
        self.assertEqual(p.contributions_bb, (0.0, 0.0, 0.5, 1.0))
        self.assertEqual(p.utilities_bb, (0.0, 0.0, -0.5, 0.5))
        self.assertAlmostEqual(p.utility_sum_bb, 0.0, places=12)

    def test_nonterminal_payoff_rejected(self):
        with self.assertRaises(ValueError):
            gross_terminal_payoff(
                initial_state("2w"),
                hole_cards=self.HOLES_2,
                board_cards=self.BOARD,
            )


if __name__ == "__main__":
    unittest.main()
