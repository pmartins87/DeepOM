import tempfile
import unittest

import numpy as np

from deepom.aof_kernel import ALLIN, apply_action, initial_state
from deepom.dense_solver import DenseExternalSamplingCFR, PLO4ClassIndex
from deepom.economics import GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0
from deepom.solver_proto import SampledDeal


class DenseSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = PLO4ClassIndex.build()

    def test_full_class_index(self):
        self.assertEqual(len(self.index.keys), 16_432)
        self.assertEqual(len(self.index.sha256), 64)

    def test_dense_core_size_is_small(self):
        s = DenseExternalSamplingCFR(
            mode="4w",
            class_index=self.index,
            seed=1,
        )
        self.assertEqual(s.regrets.shape, (14, 16_432, 2))
        self.assertLess(s.bytes_core, 9 * 1024 * 1024)

    def test_known_losing_call_pushes_bb_to_fold(self):
        deal = SampledDeal(
            hole_cards=(
                tuple("As Ks 2c 3d".split()),
                tuple("Ah 9h 4c 5d".split()),
            ),
            board_cards=tuple("Qs Js Ts 7c 8d".split()),
        )
        s = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=1,
        )
        root = initial_state("2w")
        sb_sc, sb_hi = s.info_indices(root, 0, deal)
        s.regrets[sb_sc, sb_hi] = np.array([0.0, 1.0])

        bb_state = apply_action(root, ALLIN)
        bb_sc, bb_hi = s.info_indices(bb_state, 1, deal)
        s.update_target_on_deal(deal, target_role=1)

        fold_p, allin_p = s.current_strategy(bb_sc, bb_hi)
        self.assertEqual((fold_p, allin_p), (1.0, 0.0))


    def test_rank_cache_matches_legacy_solver_exactly(self):
        legacy = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=987,
            precompute_showdown_ranks=False,
        )
        cached = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=987,
            precompute_showdown_ranks=True,
        )

        legacy.run(additional_iterations=2, deals_per_iteration=3)
        cached.run(additional_iterations=2, deals_per_iteration=3)

        np.testing.assert_array_equal(legacy.regrets, cached.regrets)
        np.testing.assert_array_equal(legacy.strategy_sum, cached.strategy_sum)
        np.testing.assert_array_equal(legacy.visits, cached.visits)
        self.assertEqual(
            legacy.manifest()["arrays_sha256"],
            cached.manifest()["arrays_sha256"],
        )

    def test_class_index_cache_matches_uncached_solver_exactly(self):
        uncached = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=321,
            precompute_showdown_ranks=True,
            precompute_class_indices=False,
        )
        cached = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=321,
            precompute_showdown_ranks=True,
            precompute_class_indices=True,
        )

        uncached.run(additional_iterations=2, deals_per_iteration=3)
        cached.run(additional_iterations=2, deals_per_iteration=3)

        np.testing.assert_array_equal(uncached.regrets, cached.regrets)
        np.testing.assert_array_equal(uncached.strategy_sum, cached.strategy_sum)
        np.testing.assert_array_equal(uncached.visits, cached.visits)
        self.assertEqual(
            uncached.manifest()["arrays_sha256"],
            cached.manifest()["arrays_sha256"],
        )

    def test_fast_evaluator_matches_reference_solver_exactly(self):
        reference = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=654,
            precompute_showdown_ranks=True,
            precompute_class_indices=True,
            fast_omaha_evaluator=False,
        )
        fast = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=654,
            precompute_showdown_ranks=True,
            precompute_class_indices=True,
            fast_omaha_evaluator=True,
        )

        reference.run(additional_iterations=2, deals_per_iteration=3)
        fast.run(additional_iterations=2, deals_per_iteration=3)

        np.testing.assert_array_equal(reference.regrets, fast.regrets)
        np.testing.assert_array_equal(reference.strategy_sum, fast.strategy_sum)
        np.testing.assert_array_equal(reference.visits, fast.visits)
        self.assertEqual(
            reference.manifest()["arrays_sha256"],
            fast.manifest()["arrays_sha256"],
        )

    def test_checkpoint_resume_matches_continuous_run(self):
        a = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=123,
            economic_preset=GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
        )
        b = DenseExternalSamplingCFR(
            mode="2w",
            class_index=self.index,
            seed=123,
            economic_preset=GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
        )

        a.run(additional_iterations=2, deals_per_iteration=2)

        b.run(additional_iterations=1, deals_per_iteration=2)
        with tempfile.TemporaryDirectory() as td:
            b.save_checkpoint(td)
            b2 = DenseExternalSamplingCFR.load_checkpoint(
                td,
                class_index=self.index,
                economic_preset=GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
            )
            b2.run(additional_iterations=1, deals_per_iteration=2)

        np.testing.assert_array_equal(a.regrets, b2.regrets)
        np.testing.assert_array_equal(a.strategy_sum, b2.strategy_sum)
        np.testing.assert_array_equal(a.visits, b2.visits)
        self.assertEqual(a.iteration_completed, b2.iteration_completed)
        self.assertEqual(a.manifest()["arrays_sha256"], b2.manifest()["arrays_sha256"])


if __name__ == "__main__":
    unittest.main()
