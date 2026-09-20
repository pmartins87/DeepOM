import random
import unittest

from deepom.aof_kernel import ALLIN, apply_action, initial_state
from deepom.solver_proto import (
    ACT_ALLIN,
    ACT_FOLD,
    SampledDeal,
    SparseExternalSamplingCFR,
)


class SolverPrototypeTests(unittest.TestCase):
    DEAL = SampledDeal(
        hole_cards=(
            tuple("As Ks 2c 3d".split()),
            tuple("Ah Kh 4c 5d".split()),
        ),
        board_cards=tuple("Qs Js Ts 7c 8d".split()),
    )

    def test_zero_regret_strategy_is_uniform(self):
        s = SparseExternalSamplingCFR(mode="2w", seed=1)
        state = initial_state("2w")
        key = s.info_key(state, 0, self.DEAL)
        self.assertEqual(s.current_strategy(key), (0.5, 0.5))

    def test_bb_regret_prefers_fold_when_call_is_certain_loss(self):
        s = SparseExternalSamplingCFR(mode="2w", seed=1, cfr_plus=True)

        root = initial_state("2w")
        sb_key = s.info_key(root, 0, self.DEAL)
        # Force SB to shove at the sampled opponent node.
        s.regrets[sb_key] = [0.0, 1.0]

        bb_state = apply_action(root, ALLIN)
        bb_key = s.info_key(bb_state, 1, self.DEAL)

        s.update_target_on_deal(
            self.DEAL,
            target_role=1,
            rng=random.Random(7),
        )

        fold_regret, allin_regret = s.regrets[bb_key]
        self.assertGreater(fold_regret, 0.0)
        self.assertEqual(allin_regret, 0.0)
        self.assertEqual(s.current_strategy(bb_key), (1.0, 0.0))

    def test_same_seed_produces_identical_quick_run(self):
        a = SparseExternalSamplingCFR(mode="2w", seed=123)
        b = SparseExternalSamplingCFR(mode="2w", seed=123)
        a.run(iterations=2, deals_per_iteration=5)
        b.run(iterations=2, deals_per_iteration=5)
        self.assertEqual(a.snapshot(), b.snapshot())

    def test_quick_run_visits_infosets_and_has_finite_regret(self):
        s = SparseExternalSamplingCFR(mode="3w", seed=77)
        s.run(iterations=1, deals_per_iteration=3)
        self.assertGreater(len(s.visits), 0)
        self.assertGreaterEqual(s.mean_positive_regret(), 0.0)


if __name__ == "__main__":
    unittest.main()
