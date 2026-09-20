from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable

from .aof_kernel import (
    ALLIN,
    FOLD,
    AOFState,
    apply_action,
    gross_terminal_payoff,
    initial_state,
    next_actor_index,
    scenario_for_state,
)
from .canonical import canonical_key_plo4
from .equity import DECK
from .economics import EconomicPreset, economic_terminal_payoff

ACT_FOLD = 0
ACT_ALLIN = 1
ACTIONS = (FOLD, ALLIN)

InfoKey = tuple[str, str, str]


@dataclass(frozen=True)
class SampledDeal:
    hole_cards: tuple[tuple[str, ...], ...]
    board_cards: tuple[str, ...]


def sample_full_deal(mode: str, rng: random.Random) -> SampledDeal:
    n = {"4w": 4, "3w": 3, "2w": 2}[mode]
    needed = 4 * n + 5
    cards = rng.sample(DECK, needed)
    holes = tuple(
        tuple(cards[4 * i : 4 * (i + 1)])
        for i in range(n)
    )
    board = tuple(cards[4 * n :])
    return SampledDeal(hole_cards=holes, board_cards=board)


class SparseExternalSamplingCFR:
    """Small correctness-first CFR prototype for the AoF Omaha tree.

    This intentionally mirrors the structural external-sampling approach used by
    the prior DeepAoF solver, while replacing all Hold'em hand-state/evaluator
    assumptions with PLO4 components.

    It currently uses *gross chip payoffs only*. Rake, Jackpot and Fortune are
    excluded until OM0/OM3 freezes their exact debit/credit semantics. Therefore
    this class is a solver-mechanics prototype, not a production strategy engine.
    """

    def __init__(
        self,
        *,
        mode: str,
        seed: int = 123,
        cfr_plus: bool = True,
        linear_average: bool = True,
        economic_preset: EconomicPreset | None = None,
        fortune_multiplier: float = 1.0,
        jackpot_multiplier: float = 1.0,
    ) -> None:
        if mode not in ("4w", "3w", "2w"):
            raise ValueError(f"unsupported mode: {mode}")
        self.mode = mode
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.cfr_plus = bool(cfr_plus)
        self.linear_average = bool(linear_average)
        self.economic_preset = economic_preset
        self.fortune_multiplier = float(fortune_multiplier)
        self.jackpot_multiplier = float(jackpot_multiplier)
        if self.fortune_multiplier < 0 or self.jackpot_multiplier < 0:
            raise ValueError("economic sensitivity multipliers must be non-negative")
        self.regrets: dict[InfoKey, list[float]] = {}
        self.strategy_sum: dict[InfoKey, list[float]] = {}
        self.visits: dict[InfoKey, int] = {}

    def info_key(self, state: AOFState, actor: int, deal: SampledDeal) -> InfoKey:
        scenario = scenario_for_state(state)
        if scenario is None:
            raise ValueError("terminal state has no infoset")
        return (
            self.mode,
            scenario,
            canonical_key_plo4(deal.hole_cards[actor]),
        )

    def current_strategy(self, key: InfoKey) -> tuple[float, float]:
        reg = self.regrets.get(key, [0.0, 0.0])
        p0 = max(0.0, reg[ACT_FOLD])
        p1 = max(0.0, reg[ACT_ALLIN])
        total = p0 + p1
        if total <= 1e-15:
            return 0.5, 0.5
        return p0 / total, p1 / total

    def average_strategy(self, key: InfoKey) -> tuple[float, float]:
        total = self.strategy_sum.get(key, [0.0, 0.0])
        denom = total[0] + total[1]
        if denom <= 1e-15:
            return 0.5, 0.5
        return total[0] / denom, total[1] / denom

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
        rng: random.Random,
    ) -> float:
        actor = next_actor_index(state)
        if actor is None:
            return self._terminal_utility(state, deal, target_role)

        key = self.info_key(state, actor, deal)
        sigma_fold, sigma_allin = self.current_strategy(key)

        if actor == target_role:
            values = [0.0, 0.0]
            for action_idx, action in enumerate(ACTIONS):
                values[action_idx] = self._traverse_external(
                    state=apply_action(state, action),
                    deal=deal,
                    target_role=target_role,
                    rng=rng,
                )

            node_u = sigma_fold * values[ACT_FOLD] + sigma_allin * values[ACT_ALLIN]
            reg = self.regrets.setdefault(key, [0.0, 0.0])
            reg[ACT_FOLD] += values[ACT_FOLD] - node_u
            reg[ACT_ALLIN] += values[ACT_ALLIN] - node_u
            if self.cfr_plus:
                reg[ACT_FOLD] = max(0.0, reg[ACT_FOLD])
                reg[ACT_ALLIN] = max(0.0, reg[ACT_ALLIN])
            self.visits[key] = self.visits.get(key, 0) + 1
            return node_u

        sampled = ALLIN if rng.random() < sigma_allin else FOLD
        return self._traverse_external(
            state=apply_action(state, sampled),
            deal=deal,
            target_role=target_role,
            rng=rng,
        )

    def update_target_on_deal(
        self,
        deal: SampledDeal,
        *,
        target_role: int,
        rng: random.Random | None = None,
    ) -> float:
        n = {"4w": 4, "3w": 3, "2w": 2}[self.mode]
        if not 0 <= target_role < n:
            raise ValueError("target_role out of range")
        local_rng = rng if rng is not None else self.rng
        return self._traverse_external(
            state=initial_state(self.mode),
            deal=deal,
            target_role=target_role,
            rng=local_rng,
        )

    def _accumulate_average_path(
        self,
        deal: SampledDeal,
        *,
        weight: float,
        rng: random.Random,
    ) -> None:
        state = initial_state(self.mode)
        while True:
            actor = next_actor_index(state)
            if actor is None:
                return
            key = self.info_key(state, actor, deal)
            sigma_fold, sigma_allin = self.current_strategy(key)
            dst = self.strategy_sum.setdefault(key, [0.0, 0.0])
            dst[ACT_FOLD] += weight * sigma_fold
            dst[ACT_ALLIN] += weight * sigma_allin
            sampled = ALLIN if rng.random() < sigma_allin else FOLD
            state = apply_action(state, sampled)

    def step(self, *, iteration: int, deals: int) -> None:
        if iteration < 1:
            raise ValueError("iteration must be >= 1")
        if deals < 1:
            raise ValueError("deals must be >= 1")
        n = {"4w": 4, "3w": 3, "2w": 2}[self.mode]
        weight = float(iteration) if self.linear_average else 1.0

        for _ in range(deals):
            deal = sample_full_deal(self.mode, self.rng)
            for target in range(n):
                self.update_target_on_deal(deal, target_role=target, rng=self.rng)
            self._accumulate_average_path(deal, weight=weight, rng=self.rng)

    def run(self, *, iterations: int, deals_per_iteration: int) -> None:
        for iteration in range(1, int(iterations) + 1):
            self.step(iteration=iteration, deals=int(deals_per_iteration))

    def mean_positive_regret(self) -> float:
        vals = [
            max(0.0, value)
            for pair in self.regrets.values()
            for value in pair
        ]
        return sum(vals) / len(vals) if vals else 0.0

    def snapshot(self) -> dict[str, object]:
        def serialize(table: dict[InfoKey, list[float]]) -> list[tuple[InfoKey, tuple[float, float]]]:
            return sorted((k, (float(v[0]), float(v[1]))) for k, v in table.items())

        return {
            "mode": self.mode,
            "seed": self.seed,
            "economic_preset": (
                self.economic_preset.preset_id if self.economic_preset is not None else None
            ),
            "fortune_multiplier": self.fortune_multiplier,
            "jackpot_multiplier": self.jackpot_multiplier,
            "regrets": serialize(self.regrets),
            "strategy_sum": serialize(self.strategy_sum),
            "visits": sorted(self.visits.items()),
            "mean_positive_regret": self.mean_positive_regret(),
        }
