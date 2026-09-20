from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from math import comb
from typing import Iterable

from .evaluator import RANK_CHARS, SUIT_CHARS, RANK_VALUE, normalize_cards

SUIT_INDEX = {s: i for i, s in enumerate(SUIT_CHARS)}
INDEX_SUIT = {i: s for i, s in enumerate(SUIT_CHARS)}
ALL_SUIT_PERMS = tuple(permutations(range(4)))


def _sort_key(card: str) -> tuple[int, int]:
    return (-RANK_VALUE[card[0]], SUIT_INDEX[card[1]])


def normalized_hand(hole_cards: Iterable[str]) -> tuple[str, ...]:
    cards = normalize_cards(hole_cards, expected=4)
    return tuple(sorted(cards, key=_sort_key))


def canonicalize_plo4(hole_cards: Iterable[str]) -> tuple[str, ...]:
    """Canonicalize an unordered PLO4 hand under all 24 global suit permutations."""
    hand = normalized_hand(hole_cards)
    best_key: tuple[tuple[int, int], ...] | None = None
    best_cards: tuple[str, ...] | None = None

    for perm in ALL_SUIT_PERMS:
        transformed = []
        for card in hand:
            r, s = card[0], card[1]
            new_suit_idx = perm[SUIT_INDEX[s]]
            transformed.append(r + INDEX_SUIT[new_suit_idx])
        transformed.sort(key=_sort_key)
        key = tuple((RANK_VALUE[c[0]], SUIT_INDEX[c[1]]) for c in transformed)
        # Ranks are fixed across suit permutations; choose lowest suit encoding.
        if best_key is None or key < best_key:
            best_key = key
            best_cards = tuple(transformed)

    assert best_cards is not None
    return best_cards


def canonical_key_plo4(hole_cards: Iterable[str]) -> str:
    return "".join(canonicalize_plo4(hole_cards))


def raw_plo4_hand_count() -> int:
    return comb(52, 4)


def burnside_plo4_class_count() -> int:
    """Independent Burnside count of 4-card subsets modulo suit permutations.

    For each suit permutation, its cycles repeat independently at each of 13
    ranks. A 4-card subset is fixed exactly when it is a union of card cycles.
    We compute the x^4 coefficient of the product over all 52 card cycles.
    """

    def suit_cycle_lengths(perm: tuple[int, ...]) -> list[int]:
        seen = set()
        lengths = []
        for start in range(4):
            if start in seen:
                continue
            cur = start
            length = 0
            while cur not in seen:
                seen.add(cur)
                length += 1
                cur = perm[cur]
            lengths.append(length)
        return lengths

    fixed_sum = 0
    for perm in ALL_SUIT_PERMS:
        cycle_lengths = suit_cycle_lengths(perm) * 13
        coeff = [0, 0, 0, 0, 0]
        coeff[0] = 1
        for length in cycle_lengths:
            for k in range(4, length - 1, -1):
                coeff[k] += coeff[k - length]
        fixed_sum += coeff[4]

    if fixed_sum % len(ALL_SUIT_PERMS) != 0:
        raise RuntimeError("Burnside fixed-point sum is not divisible by group size")
    return fixed_sum // len(ALL_SUIT_PERMS)


def brute_force_plo4_census() -> dict[str, object]:
    deck = tuple(r + s for r in RANK_CHARS for s in SUIT_CHARS)
    counts: Counter[str] = Counter()

    for hand in combinations(deck, 4):
        counts[canonical_key_plo4(hand)] += 1

    orbit_histogram = Counter(counts.values())
    reconstructed_raw = sum(size * n for size, n in orbit_histogram.items())

    return {
        "raw_hands": comb(52, 4),
        "canonical_classes": len(counts),
        "burnside_classes": burnside_plo4_class_count(),
        "orbit_size_histogram": dict(sorted(orbit_histogram.items())),
        "reconstructed_raw": reconstructed_raw,
    }
