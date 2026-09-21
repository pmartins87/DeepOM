from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import combinations
from math import comb
from pathlib import Path
import time
from typing import Iterable

import numpy as np

from .evaluator import (
    CARD_CODE,
    RANK_CHARS,
    SUIT_CHARS,
    _evaluate_five_codes_score,
    _validate_omaha_inputs,
)

DECK52 = tuple(r + s for r in RANK_CHARS for s in SUIT_CHARS)
CARD_INDEX = {card: i for i, card in enumerate(DECK52)}
CARD_CODE_BY_INDEX = tuple(CARD_CODE[card] for card in DECK52)

FIVE_CARD_COUNT = comb(52, 5)
FIVE_CARD_TABLE_DTYPE = np.dtype(np.uint32)
FIVE_CARD_TABLE_SCHEMA = 1

_C1 = tuple(comb(i, 1) for i in range(52))
_C2 = tuple(comb(i, 2) for i in range(52))
_C3 = tuple(comb(i, 3) for i in range(52))
_C4 = tuple(comb(i, 4) for i in range(52))
_C5 = tuple(comb(i, 5) for i in range(52))

_PAIR_POS_4 = tuple(combinations(range(4), 2))
_TRIPLE_POS = {
    n: tuple(combinations(range(n), 3))
    for n in (3, 4, 5)
}


def colex_rank5_sorted(a: int, b: int, c: int, d: int, e: int) -> int:
    """Perfect rank for a strictly increasing 5-card index tuple."""
    return _C1[a] + _C2[b] + _C3[c] + _C4[d] + _C5[e]


def colex_rank5(indices: Iterable[int]) -> int:
    a, b, c, d, e = sorted(int(i) for i in indices)
    if not (0 <= a < b < c < d < e < 52):
        raise ValueError("five-card indices must be distinct values in [0, 51]")
    return colex_rank5_sorted(a, b, c, d, e)


def _sha256_scores(scores: np.ndarray) -> str:
    arr = np.asarray(scores, dtype=FIVE_CARD_TABLE_DTYPE)
    return hashlib.sha256(arr.tobytes(order="C")).hexdigest()


@dataclass(frozen=True)
class FiveCardScoreTable:
    scores: np.ndarray
    sha256: str
    path: str | None
    build_seconds: float | None
    loaded_from_cache: bool
    memory_mapped: bool = False

    @classmethod
    def build(cls) -> "FiveCardScoreTable":
        t0 = time.perf_counter()
        scores = np.empty(FIVE_CARD_COUNT, dtype=FIVE_CARD_TABLE_DTYPE)

        for a, b, c, d, e in combinations(range(52), 5):
            idx = colex_rank5_sorted(a, b, c, d, e)
            scores[idx] = _evaluate_five_codes_score(
                CARD_CODE_BY_INDEX[a],
                CARD_CODE_BY_INDEX[b],
                CARD_CODE_BY_INDEX[c],
                CARD_CODE_BY_INDEX[d],
                CARD_CODE_BY_INDEX[e],
            )

        elapsed = time.perf_counter() - t0
        return cls(
            scores=scores,
            sha256=_sha256_scores(scores),
            path=None,
            build_seconds=elapsed,
            loaded_from_cache=False,
            memory_mapped=False,
        )

    @classmethod
    def load_or_build(
        cls,
        path: str | Path,
        *,
        memory_map: bool = False,
    ) -> "FiveCardScoreTable":
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            t0 = time.perf_counter()
            scores = np.load(
                path,
                mmap_mode=("r" if memory_map else None),
                allow_pickle=False,
            )
            if scores.shape != (FIVE_CARD_COUNT,):
                raise ValueError(
                    f"invalid five-card table shape: {scores.shape}; "
                    f"expected {(FIVE_CARD_COUNT,)}"
                )
            if scores.dtype != FIVE_CARD_TABLE_DTYPE:
                raise ValueError(
                    f"invalid five-card table dtype: {scores.dtype}; "
                    f"expected {FIVE_CARD_TABLE_DTYPE}"
                )
            digest = _sha256_scores(scores)
            return cls(
                scores=scores,
                sha256=digest,
                path=str(path),
                build_seconds=time.perf_counter() - t0,
                loaded_from_cache=True,
                memory_mapped=memory_map,
            )

        built = cls.build()
        tmp = path.with_name(path.name + ".tmp.npy")
        np.save(tmp, built.scores, allow_pickle=False)
        tmp.replace(path)

        scores = np.load(
            path,
            mmap_mode=("r" if memory_map else None),
            allow_pickle=False,
        )
        digest = _sha256_scores(scores)
        if digest != built.sha256:
            raise RuntimeError("five-card score-table hash changed after persistence")

        return cls(
            scores=scores,
            sha256=digest,
            path=str(path),
            build_seconds=built.build_seconds,
            loaded_from_cache=False,
            memory_mapped=memory_map,
        )

    def score_indices(self, indices: Iterable[int]) -> int:
        return int(self.scores[colex_rank5(indices)])

    def score_cards(self, cards: Iterable[str]) -> int:
        indices = tuple(CARD_INDEX[str(card)] for card in cards)
        if len(indices) != 5:
            raise ValueError(f"expected 5 cards, got {len(indices)}")
        return self.score_indices(indices)


def evaluate_omaha_score_table_indices(
    hole_indices: Iterable[int],
    board_indices: Iterable[int],
    table: FiveCardScoreTable,
) -> int:
    """Exact Omaha 2+3 score from already-valid deck indices."""
    hi = tuple(sorted(int(i) for i in hole_indices))
    bi = tuple(sorted(int(i) for i in board_indices))
    if len(hi) != 4:
        raise ValueError(f"expected 4 hole indices, got {len(hi)}")
    if len(bi) not in (3, 4, 5):
        raise ValueError(f"expected 3, 4 or 5 board indices, got {len(bi)}")

    scores = table.scores
    best = -1
    for i, j in _PAIR_POS_4:
        h0 = hi[i]
        h1 = hi[j]
        for x, y, z in _TRIPLE_POS[len(bi)]:
            a, b, c, d, e = sorted((h0, h1, bi[x], bi[y], bi[z]))
            score = int(scores[colex_rank5_sorted(a, b, c, d, e)])
            if score > best:
                best = score

    if best < 0:
        raise RuntimeError("no legal Omaha 2+3 combination")
    return best


def evaluate_omaha_score_table(
    hole_cards: Iterable[str],
    board_cards: Iterable[str],
    table: FiveCardScoreTable,
) -> int:
    """Exact Omaha 2+3 score using a precomputed all-five-card table."""
    hole, board = _validate_omaha_inputs(hole_cards, board_cards)
    hi = tuple(sorted(CARD_INDEX[c] for c in hole))
    bi = tuple(sorted(CARD_INDEX[c] for c in board))

    best = -1
    for i, j in _PAIR_POS_4:
        h0 = hi[i]
        h1 = hi[j]
        for x, y, z in _TRIPLE_POS[len(bi)]:
            a, b, c, d, e = sorted((h0, h1, bi[x], bi[y], bi[z]))
            score = int(table.scores[colex_rank5_sorted(a, b, c, d, e)])
            if score > best:
                best = score

    if best < 0:
        raise RuntimeError("no legal Omaha 2+3 combination")
    return best
