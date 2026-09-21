from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence

RANK_CHARS = "23456789TJQKA"
SUIT_CHARS = "cdhs"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANK_CHARS)}
VALUE_RANK = {v: r for r, v in RANK_VALUE.items()}
VALID_CARDS = {r + s for r in RANK_CHARS for s in SUIT_CHARS}
SUIT_VALUE = {s: i for i, s in enumerate(SUIT_CHARS)}
CARD_CODE = {
    r + s: (RANK_VALUE[r] << 2) | SUIT_VALUE[s]
    for r in RANK_CHARS
    for s in SUIT_CHARS
}

HIGH_CARD = 0
ONE_PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6
FOUR_OF_A_KIND = 7
STRAIGHT_FLUSH = 8

CATEGORY_NAME = {
    HIGH_CARD: "high_card",
    ONE_PAIR: "one_pair",
    TWO_PAIR: "two_pair",
    THREE_OF_A_KIND: "three_of_a_kind",
    STRAIGHT: "straight",
    FLUSH: "flush",
    FULL_HOUSE: "full_house",
    FOUR_OF_A_KIND: "four_of_a_kind",
    STRAIGHT_FLUSH: "straight_flush",
}


@dataclass(frozen=True, order=True)
class HandRank:
    category: int
    tiebreak: tuple[int, ...]

    @property
    def name(self) -> str:
        return CATEGORY_NAME[self.category]


def normalize_card(card: str) -> str:
    c = str(card).strip()
    if len(c) != 2:
        raise ValueError(f"invalid card: {card!r}")
    c = c[0].upper() + c[1].lower()
    if c not in VALID_CARDS:
        raise ValueError(f"invalid card: {card!r}")
    return c


def normalize_cards(cards: Iterable[str], *, expected: int | None = None) -> tuple[str, ...]:
    out = tuple(normalize_card(c) for c in cards)
    if expected is not None and len(out) != expected:
        raise ValueError(f"expected {expected} cards, got {len(out)}")
    if len(set(out)) != len(out):
        raise ValueError("duplicate card detected")
    return out


def _straight_high(unique_ranks_desc: Sequence[int]) -> int | None:
    ranks = set(unique_ranks_desc)
    if 14 in ranks:
        ranks.add(1)
    for high in range(14, 4, -1):
        if all(v in ranks for v in range(high - 4, high + 1)):
            return high
    return None


def evaluate_five(cards: Iterable[str]) -> HandRank:
    cs = normalize_cards(cards, expected=5)
    ranks = [RANK_VALUE[c[0]] for c in cs]
    suits = [c[1] for c in cs]

    counts: dict[int, int] = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1

    unique_desc = sorted(counts, reverse=True)
    flush = len(set(suits)) == 1
    straight_high = _straight_high(unique_desc) if len(unique_desc) == 5 else None

    if flush and straight_high is not None:
        return HandRank(STRAIGHT_FLUSH, (straight_high,))

    groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)

    if groups[0][0] == 4:
        quad = groups[0][1]
        kicker = max(r for r, c in counts.items() if c == 1)
        return HandRank(FOUR_OF_A_KIND, (quad, kicker))

    if sorted(counts.values()) == [2, 3]:
        trips = max(r for r, c in counts.items() if c == 3)
        pair = max(r for r, c in counts.items() if c == 2)
        return HandRank(FULL_HOUSE, (trips, pair))

    if flush:
        return HandRank(FLUSH, tuple(sorted(ranks, reverse=True)))

    if straight_high is not None:
        return HandRank(STRAIGHT, (straight_high,))

    trips = [r for r, c in counts.items() if c == 3]
    if trips:
        tr = max(trips)
        kickers = sorted((r for r, c in counts.items() if c == 1), reverse=True)
        return HandRank(THREE_OF_A_KIND, (tr, *kickers))

    pairs = sorted((r for r, c in counts.items() if c == 2), reverse=True)
    if len(pairs) == 2:
        kicker = max(r for r, c in counts.items() if c == 1)
        return HandRank(TWO_PAIR, (pairs[0], pairs[1], kicker))

    if len(pairs) == 1:
        pair = pairs[0]
        kickers = sorted((r for r, c in counts.items() if c == 1), reverse=True)
        return HandRank(ONE_PAIR, (pair, *kickers))

    return HandRank(HIGH_CARD, tuple(sorted(ranks, reverse=True)))


def _validate_omaha_inputs(
    hole_cards: Iterable[str],
    board_cards: Iterable[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    hole = normalize_cards(hole_cards, expected=4)
    board = normalize_cards(board_cards)
    if len(board) not in (3, 4, 5):
        raise ValueError(
            f"Omaha evaluation requires 3, 4, or 5 board cards; got {len(board)}"
        )
    all_cards = hole + board
    if len(set(all_cards)) != len(all_cards):
        raise ValueError("duplicate card detected across hole cards and board")
    return hole, board


def _evaluate_five_codes(
    c0: int,
    c1: int,
    c2: int,
    c3: int,
    c4: int,
) -> HandRank:
    """Fast exact five-card evaluator for already-validated encoded cards."""
    a, b, c, d, e = sorted(
        (c0 >> 2, c1 >> 2, c2 >> 2, c3 >> 2, c4 >> 2),
        reverse=True,
    )
    flush = (
        (c0 & 3) == (c1 & 3) == (c2 & 3) == (c3 & 3) == (c4 & 3)
    )

    distinct = a > b > c > d > e
    straight_high: int | None = None
    if distinct:
        if a - e == 4:
            straight_high = a
        elif (a, b, c, d, e) == (14, 5, 4, 3, 2):
            straight_high = 5

    if flush and straight_high is not None:
        return HandRank(STRAIGHT_FLUSH, (straight_high,))

    if a == d:
        return HandRank(FOUR_OF_A_KIND, (a, e))
    if b == e:
        return HandRank(FOUR_OF_A_KIND, (b, a))

    if a == c and d == e:
        return HandRank(FULL_HOUSE, (a, d))
    if a == b and c == e:
        return HandRank(FULL_HOUSE, (c, a))

    if flush:
        return HandRank(FLUSH, (a, b, c, d, e))

    if straight_high is not None:
        return HandRank(STRAIGHT, (straight_high,))

    if a == c:
        return HandRank(THREE_OF_A_KIND, (a, d, e))
    if b == d:
        return HandRank(THREE_OF_A_KIND, (b, a, e))
    if c == e:
        return HandRank(THREE_OF_A_KIND, (c, a, b))

    if a == b and c == d:
        return HandRank(TWO_PAIR, (a, c, e))
    if a == b and d == e:
        return HandRank(TWO_PAIR, (a, d, c))
    if b == c and d == e:
        return HandRank(TWO_PAIR, (b, d, a))

    if a == b:
        return HandRank(ONE_PAIR, (a, c, d, e))
    if b == c:
        return HandRank(ONE_PAIR, (b, a, d, e))
    if c == d:
        return HandRank(ONE_PAIR, (c, a, b, e))
    if d == e:
        return HandRank(ONE_PAIR, (d, a, b, c))

    return HandRank(HIGH_CARD, (a, b, c, d, e))


def evaluate_omaha_reference(
    hole_cards: Iterable[str],
    board_cards: Iterable[str],
) -> HandRank:
    """Readable reference implementation used as an optimization oracle."""
    hole, board = _validate_omaha_inputs(hole_cards, board_cards)
    best: HandRank | None = None
    for h2 in combinations(hole, 2):
        for b3 in combinations(board, 3):
            rank = evaluate_five((*h2, *b3))
            if best is None or rank > best:
                best = rank
    assert best is not None
    return best


def evaluate_omaha(hole_cards: Iterable[str], board_cards: Iterable[str]) -> HandRank:
    """Fast exact Omaha high: exactly 2 of 4 hole cards + exactly 3 board cards."""
    hole, board = _validate_omaha_inputs(hole_cards, board_cards)
    hc = tuple(CARD_CODE[c] for c in hole)
    bc = tuple(CARD_CODE[c] for c in board)

    best: HandRank | None = None
    for i, j in combinations(range(4), 2):
        hi = hc[i]
        hj = hc[j]
        for x, y, z in combinations(range(len(bc)), 3):
            rank = _evaluate_five_codes(hi, hj, bc[x], bc[y], bc[z])
            if best is None or rank > best:
                best = rank

    assert best is not None
    return best


def best_omaha_five(
    hole_cards: Iterable[str],
    board_cards: Iterable[str],
) -> tuple[HandRank, tuple[str, ...], tuple[str, ...]]:
    """Return best rank plus the exact 2 hole + 3 board cards used."""
    hole, board = _validate_omaha_inputs(hole_cards, board_cards)
    best: tuple[HandRank, tuple[str, ...], tuple[str, ...]] | None = None
    for h2 in combinations(hole, 2):
        for b3 in combinations(board, 3):
            rank = evaluate_five((*h2, *b3))
            candidate = (rank, tuple(h2), tuple(b3))
            if best is None or candidate[0] > best[0]:
                best = candidate
    assert best is not None
    return best


def is_royal_flush(rank: HandRank) -> bool:
    return rank.category == STRAIGHT_FLUSH and rank.tiebreak == (14,)


def qualifies_aof_omaha_jackpot(
    hole_cards: Iterable[str],
    board_cards: Iterable[str],
    *,
    reached_showdown: bool,
) -> bool:
    """Return whether a GGPoker AoF Omaha hand meets the Royal Flush jackpot rule.

    A qualifying hand is a Royal Flush formed with exactly 2 hole cards and 3 board
    cards. Normally the hand must reach showdown. The published Omaha exception
    allows qualification when the Royal Flush is immediately complete on the flop.
    """
    hole, board = _validate_omaha_inputs(hole_cards, board_cards)
    royal = is_royal_flush(evaluate_omaha(hole, board))
    if not royal:
        return False
    immediate_flop = len(board) == 3
    return reached_showdown or immediate_flop
