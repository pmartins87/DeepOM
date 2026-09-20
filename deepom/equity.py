from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb, sqrt
import random
from typing import Iterable, Sequence

from .evaluator import (
    RANK_CHARS,
    SUIT_CHARS,
    HandRank,
    evaluate_omaha,
    normalize_cards,
)

DECK = tuple(r + s for r in RANK_CHARS for s in SUIT_CHARS)
ROYAL_RANKS = frozenset("TJQKA")


@dataclass(frozen=True)
class EquityResult:
    samples: int
    equity: float
    win_rate: float
    tie_rate: float
    loss_rate: float
    standard_error: float
    ci95_low: float
    ci95_high: float
    exact: bool


def _validate_state(
    hero_hole: Iterable[str],
    opponent_holes: Sequence[Iterable[str]],
    board: Iterable[str],
) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...], tuple[str, ...], tuple[str, ...]]:
    hero = normalize_cards(hero_hole, expected=4)
    opponents = tuple(normalize_cards(h, expected=4) for h in opponent_holes)
    if not opponents:
        raise ValueError("at least one opponent is required")
    board_cards = normalize_cards(board)
    if len(board_cards) > 5:
        raise ValueError("board cannot contain more than 5 cards")

    used = hero + tuple(c for h in opponents for c in h) + board_cards
    if len(set(used)) != len(used):
        raise ValueError("duplicate card detected across known state")
    used_set = set(used)
    remaining = tuple(c for c in DECK if c not in used_set)
    return hero, opponents, board_cards, remaining


def _showdown_share(
    hero_rank: HandRank,
    opponent_ranks: Sequence[HandRank],
) -> tuple[float, str]:
    ranks = (hero_rank, *opponent_ranks)
    best = max(ranks)
    if hero_rank < best:
        return 0.0, "loss"
    winners = sum(1 for r in ranks if r == best)
    if winners == 1:
        return 1.0, "win"
    return 1.0 / winners, "tie"


def _result_from_accumulators(
    *,
    samples: int,
    share_sum: float,
    share_sq_sum: float,
    wins: int,
    ties: int,
    losses: int,
    exact: bool,
) -> EquityResult:
    if samples <= 0:
        raise ValueError("samples must be positive")
    equity = share_sum / samples
    if exact or samples == 1:
        stderr = 0.0
    else:
        variance = max(0.0, (share_sq_sum / samples) - equity * equity)
        stderr = sqrt(variance / samples)
    half = 1.96 * stderr
    return EquityResult(
        samples=samples,
        equity=equity,
        win_rate=wins / samples,
        tie_rate=ties / samples,
        loss_rate=losses / samples,
        standard_error=stderr,
        ci95_low=max(0.0, equity - half),
        ci95_high=min(1.0, equity + half),
        exact=exact,
    )


def exact_equity_known_hands(
    hero_hole: Iterable[str],
    opponent_holes: Sequence[Iterable[str]],
    *,
    board: Iterable[str] = (),
    max_runouts: int = 100_000,
) -> EquityResult:
    """Exact equity for fully known Omaha hole cards by enumerating board runouts.

    Preflop HU has more than one million board runouts and is intentionally blocked
    by the default guard. Raise max_runouts only for deliberate benchmarks.
    """
    hero, opponents, board_cards, remaining = _validate_state(
        hero_hole, opponent_holes, board
    )
    missing = 5 - len(board_cards)
    runouts = comb(len(remaining), missing)
    if runouts > max_runouts:
        raise ValueError(
            f"exact enumeration would require {runouts} runouts; "
            f"max_runouts={max_runouts}"
        )

    share_sum = 0.0
    share_sq_sum = 0.0
    wins = ties = losses = 0

    for extra in combinations(remaining, missing):
        full_board = board_cards + extra
        hero_rank = evaluate_omaha(hero, full_board)
        opp_ranks = [evaluate_omaha(h, full_board) for h in opponents]
        share, outcome = _showdown_share(hero_rank, opp_ranks)
        share_sum += share
        share_sq_sum += share * share
        if outcome == "win":
            wins += 1
        elif outcome == "tie":
            ties += 1
        else:
            losses += 1

    return _result_from_accumulators(
        samples=runouts,
        share_sum=share_sum,
        share_sq_sum=share_sq_sum,
        wins=wins,
        ties=ties,
        losses=losses,
        exact=True,
    )


def monte_carlo_equity_known_hands(
    hero_hole: Iterable[str],
    opponent_holes: Sequence[Iterable[str]],
    *,
    board: Iterable[str] = (),
    samples: int = 10_000,
    seed: int = 1,
) -> EquityResult:
    hero, opponents, board_cards, remaining = _validate_state(
        hero_hole, opponent_holes, board
    )
    if samples <= 0:
        raise ValueError("samples must be positive")
    missing = 5 - len(board_cards)
    rng = random.Random(seed)

    share_sum = 0.0
    share_sq_sum = 0.0
    wins = ties = losses = 0

    for _ in range(samples):
        extra = tuple(rng.sample(remaining, missing))
        full_board = board_cards + extra
        hero_rank = evaluate_omaha(hero, full_board)
        opp_ranks = [evaluate_omaha(h, full_board) for h in opponents]
        share, outcome = _showdown_share(hero_rank, opp_ranks)
        share_sum += share
        share_sq_sum += share * share
        if outcome == "win":
            wins += 1
        elif outcome == "tie":
            ties += 1
        else:
            losses += 1

    return _result_from_accumulators(
        samples=samples,
        share_sum=share_sum,
        share_sq_sum=share_sq_sum,
        wins=wins,
        ties=ties,
        losses=losses,
        exact=False,
    )


def monte_carlo_equity_vs_random(
    hero_hole: Iterable[str],
    *,
    num_opponents: int,
    board: Iterable[str] = (),
    samples: int = 10_000,
    seed: int = 1,
) -> EquityResult:
    hero = normalize_cards(hero_hole, expected=4)
    board_cards = normalize_cards(board)
    if len(board_cards) > 5:
        raise ValueError("board cannot contain more than 5 cards")
    if num_opponents < 1:
        raise ValueError("num_opponents must be >= 1")
    if samples <= 0:
        raise ValueError("samples must be positive")

    used = hero + board_cards
    if len(set(used)) != len(used):
        raise ValueError("duplicate card detected across known state")
    used_set = set(used)
    remaining = tuple(c for c in DECK if c not in used_set)
    needed = 4 * num_opponents + (5 - len(board_cards))
    if needed > len(remaining):
        raise ValueError("not enough cards remaining for requested state")

    rng = random.Random(seed)
    share_sum = 0.0
    share_sq_sum = 0.0
    wins = ties = losses = 0

    for _ in range(samples):
        drawn = rng.sample(remaining, needed)
        opponents = [
            tuple(drawn[4 * i : 4 * (i + 1)]) for i in range(num_opponents)
        ]
        extra = tuple(drawn[4 * num_opponents :])
        full_board = board_cards + extra
        hero_rank = evaluate_omaha(hero, full_board)
        opp_ranks = [evaluate_omaha(h, full_board) for h in opponents]
        share, outcome = _showdown_share(hero_rank, opp_ranks)
        share_sum += share
        share_sq_sum += share * share
        if outcome == "win":
            wins += 1
        elif outcome == "tie":
            ties += 1
        else:
            losses += 1

    return _result_from_accumulators(
        samples=samples,
        share_sum=share_sum,
        share_sq_sum=share_sq_sum,
        wins=wins,
        ties=ties,
        losses=losses,
        exact=False,
    )


def qualifying_royal_suits(hole_cards: Iterable[str]) -> tuple[str, ...]:
    """Return suits with exactly two T/J/Q/K/A hole cards.

    Exactly two are necessary and sufficient for a future Omaha royal flush of that
    suit because the final hand must use exactly two hole cards and three board cards.
    """
    hole = normalize_cards(hole_cards, expected=4)
    out = []
    for suit in SUIT_CHARS:
        count = sum(1 for c in hole if c[1] == suit and c[0] in ROYAL_RANKS)
        if count == 2:
            out.append(suit)
    return tuple(out)


def royal_flush_full_board_probability(hole_cards: Iterable[str]) -> float:
    """Exact probability a random 5-card board contains an Omaha royal flush.

    For each qualifying suit, the board must contain its three missing royal cards;
    the other two board cards can be any two of the remaining 45 cards. Events for
    two qualifying suits are disjoint because a 5-card board cannot contain six
    required cards.
    """
    k = len(qualifying_royal_suits(hole_cards))
    if k == 0:
        return 0.0
    return k * comb(45, 2) / comb(48, 5)


def royal_flush_flop_probability(hole_cards: Iterable[str]) -> float:
    """Exact probability the Royal Flush is already complete on the 3-card flop."""
    k = len(qualifying_royal_suits(hole_cards))
    if k == 0:
        return 0.0
    return k / comb(48, 3)
