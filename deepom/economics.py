from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .aof_kernel import ALLIN, FOLD, AOFState, GrossPayoff, gross_terminal_payoff
from .equity import royal_flush_full_board_probability
from .evaluator import normalize_cards

DEEPAOF_FORTUNE_REFERENCE_POOL_USD = 77_273.23
DEEPAOF_FORTUNE_TRIGGER_P = 0.02
DEEPAOF_FORTUNE_REFERENCE_BB_CHIPS = 250
DEEPAOF_FORTUNE_TIERS_CHIPS: tuple[tuple[int, int], ...] = (
    (200_000, 400),
    (9_000, 9_996),
    (4_500, 39_984),
    (1_800, 149_940),
    (900, 799_680),
)

PROJECT_FORTUNE_POOL_USD = 75_000.0


def inherited_deepaof_fortune_ev_bb(
    *,
    pool_usd: float = PROJECT_FORTUNE_POOL_USD,
) -> float:
    """Provisional Fortune EV per All-In, normalized in BB.

    This preserves the prior DeepAoF trigger/tier structure and scales it only by
    the Fortune pool ratio. It is deliberately marked provisional because GGPoker
    states that Fortune awards depend on blind level and the public page does not
    expose the complete current tier/probability table.
    """
    if pool_usd < 0:
        raise ValueError("pool_usd must be non-negative")
    weighted_bb = sum(
        (prize_chips / DEEPAOF_FORTUNE_REFERENCE_BB_CHIPS) * weight
        for prize_chips, weight in DEEPAOF_FORTUNE_TIERS_CHIPS
    ) / 1_000_000.0
    base_ev = DEEPAOF_FORTUNE_TRIGGER_P * weighted_bb
    return base_ev * (pool_usd / DEEPAOF_FORTUNE_REFERENCE_POOL_USD)


@dataclass(frozen=True)
class EconomicPreset:
    preset_id: str
    base_rake_bb: float
    jackpot_fee_bb: float
    fortune_fee_bb: float
    rakeback_rate: float
    jackpot_prize_bb: float
    fortune_ev_bb: float
    fee_policy: str = "per_dealt_player"

    def __post_init__(self) -> None:
        for name in (
            "base_rake_bb",
            "jackpot_fee_bb",
            "fortune_fee_bb",
            "jackpot_prize_bb",
            "fortune_ev_bb",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if not 0.0 <= self.rakeback_rate <= 1.0:
            raise ValueError("rakeback_rate must be in [0,1]")
        if self.fee_policy != "per_dealt_player":
            raise ValueError("only per_dealt_player is currently supported")

    @property
    def net_base_rake_bb(self) -> float:
        return self.base_rake_bb * (1.0 - self.rakeback_rate)

    @property
    def fixed_fee_per_player_bb(self) -> float:
        return self.net_base_rake_bb + self.jackpot_fee_bb + self.fortune_fee_bb


GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0 = EconomicPreset(
    preset_id="GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0",
    base_rake_bb=0.025,
    jackpot_fee_bb=0.025,
    fortune_fee_bb=0.025,
    rakeback_rate=0.35,
    jackpot_prize_bb=375.0,
    fortune_ev_bb=inherited_deepaof_fortune_ev_bb(pool_usd=75_000.0),
)


@dataclass(frozen=True)
class EconomicPayoff:
    gross_utilities_bb: tuple[float, ...]
    fixed_fees_bb: tuple[float, ...]
    fortune_credits_bb: tuple[float, ...]
    jackpot_credits_bb: tuple[float, ...]
    net_utilities_bb: tuple[float, ...]

    @property
    def external_flow_bb(self) -> float:
        return float(sum(self.net_utilities_bb))


def deterministic_jackpot_ev_bb(
    hole_cards: Iterable[str],
    *,
    jackpot_prize_bb: float,
) -> float:
    if jackpot_prize_bb < 0:
        raise ValueError("jackpot_prize_bb must be non-negative")
    return float(jackpot_prize_bb) * royal_flush_full_board_probability(hole_cards)


def apply_economics_to_gross(
    state: AOFState,
    *,
    hole_cards: Sequence[Iterable[str]],
    gross: GrossPayoff,
    preset: EconomicPreset = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
    fortune_multiplier: float = 1.0,
    jackpot_multiplier: float = 1.0,
) -> EconomicPayoff:
    """Apply action-dependent AoF economics to an already-computed chip payoff."""
    if fortune_multiplier < 0 or jackpot_multiplier < 0:
        raise ValueError("sensitivity multipliers must be non-negative")

    holes = tuple(normalize_cards(h, expected=4) for h in hole_cards)
    n = len(holes)
    if len(gross.utilities_bb) != n or len(state.actions) != n:
        raise ValueError("gross payoff / hole cards / state length mismatch")

    fixed = tuple(preset.fixed_fee_per_player_bb for _ in range(n))
    went_allin = tuple(action == ALLIN for action in state.actions)
    fortune = tuple(
        (preset.fortune_ev_bb * fortune_multiplier) if ai else 0.0
        for ai in went_allin
    )

    active = [i for i, action in enumerate(state.actions) if action != FOLD]
    reaches_showdown = len(active) >= 2
    jackpot_values = [0.0] * n
    if reaches_showdown:
        for i in active:
            if went_allin[i]:
                jackpot_values[i] = deterministic_jackpot_ev_bb(
                    holes[i],
                    jackpot_prize_bb=preset.jackpot_prize_bb * jackpot_multiplier,
                )

    net = tuple(
        gross.utilities_bb[i] - fixed[i] + fortune[i] + jackpot_values[i]
        for i in range(n)
    )
    return EconomicPayoff(
        gross_utilities_bb=tuple(gross.utilities_bb),
        fixed_fees_bb=fixed,
        fortune_credits_bb=fortune,
        jackpot_credits_bb=tuple(jackpot_values),
        net_utilities_bb=net,
    )


def economic_terminal_payoff(
    state: AOFState,
    *,
    hole_cards: Sequence[Iterable[str]],
    board_cards: Iterable[str],
    preset: EconomicPreset = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
    fortune_multiplier: float = 1.0,
    jackpot_multiplier: float = 1.0,
) -> EconomicPayoff:
    """Add expected GGPoker AoF economics to the mechanical chip payoff."""
    gross = gross_terminal_payoff(
        state,
        hole_cards=hole_cards,
        board_cards=board_cards,
    )
    return apply_economics_to_gross(
        state,
        hole_cards=hole_cards,
        gross=gross,
        preset=preset,
        fortune_multiplier=fortune_multiplier,
        jackpot_multiplier=jackpot_multiplier,
    )
