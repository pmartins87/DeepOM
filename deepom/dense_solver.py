from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
from itertools import combinations
import json
from pathlib import Path
import pickle
import random
from typing import Iterable

import numpy as np

from .aof_kernel import (
    ALLIN,
    FOLD,
    MODE_CONFIGS,
    AOFState,
    apply_action,
    gross_terminal_payoff,
    initial_state,
    next_actor_index,
    scenario_for_state,
)
from .canonical import canonical_key_plo4
from .economics import EconomicPreset, economic_terminal_payoff
from .equity import DECK
from .solver_proto import SampledDeal, sample_full_deal

ACT_FOLD = 0
ACT_ALLIN = 1
ACTIONS = (FOLD, ALLIN)


@dataclass(frozen=True)
class PLO4ClassIndex:
    keys: tuple[str, ...]
    key_to_index: dict[str, int]
    sha256: str

    @classmethod
    def build(cls) -> "PLO4ClassIndex":
        keys = sorted(
            {
                canonical_key_plo4(hand)
                for hand in combinations(DECK, 4)
            }
        )
        if len(keys) != 16_432:
            raise RuntimeError(f"unexpected PLO4 class count: {len(keys)}")
        payload = ("\n".join(keys) + "\n").encode("ascii")
        digest = hashlib.sha256(payload).hexdigest()
        return cls(
            keys=tuple(keys),
            key_to_index={key: i for i, key in enumerate(keys)},
            sha256=digest,
        )

    def index_of(self, hole_cards: Iterable[str]) -> int:
        key = canonical_key_plo4(hole_cards)
        try:
            return self.key_to_index[key]
        except KeyError as exc:
            raise KeyError(f"canonical PLO4 class not present: {key}") from exc


class DenseExternalSamplingCFR:
    """Dense indexed CFR correctness/performance bridge.

    This is the next stage after the sparse dictionary oracle. It still uses the
    Python evaluator/chance traversal, but all regret, average-strategy and visit
    state is stored in compact NumPy arrays indexed by (scenario, hand class).
    """

    CHECKPOINT_SCHEMA = 1

    def __init__(
        self,
        *,
        mode: str,
        class_index: PLO4ClassIndex,
        seed: int = 123,
        cfr_plus: bool = True,
        linear_average: bool = True,
        economic_preset: EconomicPreset | None = None,
        fortune_multiplier: float = 1.0,
        jackpot_multiplier: float = 1.0,
    ) -> None:
        if mode not in MODE_CONFIGS:
            raise ValueError(f"unsupported mode: {mode}")
        if fortune_multiplier < 0 or jackpot_multiplier < 0:
            raise ValueError("economic sensitivity multipliers must be non-negative")

        self.mode = mode
        self.class_index = class_index
        self.seed = int(seed)
        self.cfr_plus = bool(cfr_plus)
        self.linear_average = bool(linear_average)
        self.economic_preset = economic_preset
        self.fortune_multiplier = float(fortune_multiplier)
        self.jackpot_multiplier = float(jackpot_multiplier)
        self.rng = random.Random(self.seed)
        self.iteration_completed = 0

        self.scenario_names = tuple(MODE_CONFIGS[mode]["scenarios"])
        self.scenario_to_index = {
            name: i for i, name in enumerate(self.scenario_names)
        }

        shape = (len(self.scenario_names), len(class_index.keys), 2)
        self.regrets = np.zeros(shape, dtype=np.float64)
        self.strategy_sum = np.zeros(shape, dtype=np.float64)
        self.visits = np.zeros(shape[:2], dtype=np.uint32)

    @property
    def bytes_core(self) -> int:
        return int(
            self.regrets.nbytes
            + self.strategy_sum.nbytes
            + self.visits.nbytes
        )

    def info_indices(
        self,
        state: AOFState,
        actor: int,
        deal: SampledDeal,
    ) -> tuple[int, int]:
        scenario = scenario_for_state(state)
        if scenario is None:
            raise ValueError("terminal state has no infoset")
        return (
            self.scenario_to_index[scenario],
            self.class_index.index_of(deal.hole_cards[actor]),
        )

    def current_strategy(self, scenario_i: int, hand_i: int) -> tuple[float, float]:
        reg = self.regrets[scenario_i, hand_i]
        positive = np.maximum(reg, 0.0)
        total = float(positive.sum())
        if total <= 1e-15:
            return 0.5, 0.5
        return float(positive[ACT_FOLD] / total), float(positive[ACT_ALLIN] / total)

    def average_strategy(self, scenario_i: int, hand_i: int) -> tuple[float, float]:
        total = self.strategy_sum[scenario_i, hand_i]
        denom = float(total.sum())
        if denom <= 1e-15:
            return 0.5, 0.5
        return float(total[ACT_FOLD] / denom), float(total[ACT_ALLIN] / denom)

    def _terminal_utility(
        self,
        state: AOFState,
        deal: SampledDeal,
        target_role: int,
    ) -> float:
        if self.economic_preset is None:
            payoff = gross_terminal_payoff(
                state,
                hole_cards=deal.hole_cards,
                board_cards=deal.board_cards,
            )
            return float(payoff.utilities_bb[target_role])

        payoff = economic_terminal_payoff(
            state,
            hole_cards=deal.hole_cards,
            board_cards=deal.board_cards,
            preset=self.economic_preset,
            fortune_multiplier=self.fortune_multiplier,
            jackpot_multiplier=self.jackpot_multiplier,
        )
        return float(payoff.net_utilities_bb[target_role])

    def _traverse_external(
        self,
        *,
        state: AOFState,
        deal: SampledDeal,
        target_role: int,
    ) -> float:
        actor = next_actor_index(state)
        if actor is None:
            return self._terminal_utility(state, deal, target_role)

        sc, hi = self.info_indices(state, actor, deal)
        sigma_fold, sigma_allin = self.current_strategy(sc, hi)

        if actor == target_role:
            values = [0.0, 0.0]
            for action_i, action in enumerate(ACTIONS):
                values[action_i] = self._traverse_external(
                    state=apply_action(state, action),
                    deal=deal,
                    target_role=target_role,
                )
            node_u = sigma_fold * values[ACT_FOLD] + sigma_allin * values[ACT_ALLIN]
            self.regrets[sc, hi, ACT_FOLD] += values[ACT_FOLD] - node_u
            self.regrets[sc, hi, ACT_ALLIN] += values[ACT_ALLIN] - node_u
            if self.cfr_plus:
                self.regrets[sc, hi] = np.maximum(self.regrets[sc, hi], 0.0)
            self.visits[sc, hi] += 1
            return node_u

        sampled = ALLIN if self.rng.random() < sigma_allin else FOLD
        return self._traverse_external(
            state=apply_action(state, sampled),
            deal=deal,
            target_role=target_role,
        )

    def update_target_on_deal(
        self,
        deal: SampledDeal,
        *,
        target_role: int,
    ) -> float:
        n = len(MODE_CONFIGS[self.mode]["roles"])
        if not 0 <= target_role < n:
            raise ValueError("target_role out of range")
        return self._traverse_external(
            state=initial_state(self.mode),
            deal=deal,
            target_role=target_role,
        )

    def _accumulate_average_path(self, deal: SampledDeal, *, weight: float) -> None:
        state = initial_state(self.mode)
        while True:
            actor = next_actor_index(state)
            if actor is None:
                return
            sc, hi = self.info_indices(state, actor, deal)
            sigma_fold, sigma_allin = self.current_strategy(sc, hi)
            self.strategy_sum[sc, hi, ACT_FOLD] += weight * sigma_fold
            self.strategy_sum[sc, hi, ACT_ALLIN] += weight * sigma_allin
            sampled = ALLIN if self.rng.random() < sigma_allin else FOLD
            state = apply_action(state, sampled)

    def step(self, *, deals: int) -> None:
        if deals < 1:
            raise ValueError("deals must be >= 1")
        iteration = self.iteration_completed + 1
        weight = float(iteration) if self.linear_average else 1.0
        n = len(MODE_CONFIGS[self.mode]["roles"])

        for _ in range(int(deals)):
            deal = sample_full_deal(self.mode, self.rng)
            for target in range(n):
                self.update_target_on_deal(deal, target_role=target)
            self._accumulate_average_path(deal, weight=weight)

        self.iteration_completed = iteration

    def run(self, *, additional_iterations: int, deals_per_iteration: int) -> None:
        if additional_iterations < 0:
            raise ValueError("additional_iterations must be >= 0")
        for _ in range(int(additional_iterations)):
            self.step(deals=int(deals_per_iteration))

    def mean_positive_regret(self) -> float:
        if not self.regrets.size:
            return 0.0
        return float(np.maximum(self.regrets, 0.0).mean())

    def visited_infosets(self) -> int:
        return int(np.count_nonzero(self.visits))

    def _arrays_sha256(self) -> str:
        h = hashlib.sha256()
        h.update(self.regrets.tobytes(order="C"))
        h.update(self.strategy_sum.tobytes(order="C"))
        h.update(self.visits.tobytes(order="C"))
        return h.hexdigest()

    def manifest(self) -> dict[str, object]:
        return {
            "schema": self.CHECKPOINT_SCHEMA,
            "mode": self.mode,
            "seed": self.seed,
            "iteration_completed": self.iteration_completed,
            "cfr_plus": self.cfr_plus,
            "linear_average": self.linear_average,
            "class_count": len(self.class_index.keys),
            "class_index_sha256": self.class_index.sha256,
            "scenario_names": list(self.scenario_names),
            "shape": list(self.regrets.shape),
            "bytes_core": self.bytes_core,
            "economic_preset": (
                self.economic_preset.preset_id
                if self.economic_preset is not None
                else None
            ),
            "fortune_multiplier": self.fortune_multiplier,
            "jackpot_multiplier": self.jackpot_multiplier,
            "arrays_sha256": self._arrays_sha256(),
        }

    def save_checkpoint(self, directory: str | Path) -> dict[str, object]:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        state_path = directory / "state.npz"
        np.savez_compressed(
            state_path,
            regrets=self.regrets,
            strategy_sum=self.strategy_sum,
            visits=self.visits,
        )

        manifest = self.manifest()
        rng_blob = base64.b64encode(
            pickle.dumps(self.rng.getstate(), protocol=5)
        ).decode("ascii")
        payload = dict(manifest)
        payload["rng_state_b64"] = rng_blob

        manifest_path = directory / "manifest.json"
        manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest

    @classmethod
    def load_checkpoint(
        cls,
        directory: str | Path,
        *,
        class_index: PLO4ClassIndex,
        economic_preset: EconomicPreset | None = None,
    ) -> "DenseExternalSamplingCFR":
        directory = Path(directory)
        payload = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))

        if int(payload["schema"]) != cls.CHECKPOINT_SCHEMA:
            raise ValueError("unsupported checkpoint schema")
        if payload["class_index_sha256"] != class_index.sha256:
            raise ValueError("class-index hash mismatch")

        expected_preset = (
            economic_preset.preset_id if economic_preset is not None else None
        )
        if payload["economic_preset"] != expected_preset:
            raise ValueError(
                f"economic preset mismatch: checkpoint={payload['economic_preset']} "
                f"requested={expected_preset}"
            )

        obj = cls(
            mode=str(payload["mode"]),
            class_index=class_index,
            seed=int(payload["seed"]),
            cfr_plus=bool(payload["cfr_plus"]),
            linear_average=bool(payload["linear_average"]),
            economic_preset=economic_preset,
            fortune_multiplier=float(payload["fortune_multiplier"]),
            jackpot_multiplier=float(payload["jackpot_multiplier"]),
        )

        data = np.load(directory / "state.npz")
        obj.regrets[...] = data["regrets"]
        obj.strategy_sum[...] = data["strategy_sum"]
        obj.visits[...] = data["visits"]
        obj.iteration_completed = int(payload["iteration_completed"])
        obj.rng.setstate(
            pickle.loads(base64.b64decode(payload["rng_state_b64"].encode("ascii")))
        )

        if obj._arrays_sha256() != payload["arrays_sha256"]:
            raise ValueError("checkpoint array hash mismatch")
        return obj
