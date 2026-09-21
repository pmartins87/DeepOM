from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .evaluator import HandRank, evaluate_omaha, normalize_cards

FOLD = "FOLD"
ALLIN = "ALLIN"
UNSET = None

MODE_CONFIGS = {
    "4w": {
        "roles": ("CO", "BTN", "SB", "BB"),
        "blind_roles": (2, 3),
        "scenarios": (
            "CO_open",
            "BTN_vs_CO_fold",
            "BTN_vs_CO_ai",
            "SB_vs_CO_fold_BTN_fold",
            "SB_vs_CO_ai_BTN_fold",
            "SB_vs_CO_fold_BTN_ai",
            "SB_vs_CO_ai_BTN_ai",
            "BB_vs_CO_ai_BTN_fold_SB_fold",
            "BB_vs_CO_fold_BTN_ai_SB_fold",
            "BB_vs_CO_ai_BTN_ai_SB_fold",
            "BB_vs_CO_fold_BTN_fold_SB_ai",
            "BB_vs_CO_ai_BTN_fold_SB_ai",
            "BB_vs_CO_fold_BTN_ai_SB_ai",
            "BB_vs_CO_ai_BTN_ai_SB_ai",
        ),
        "walk_label": "BB_vs_CO_fold_BTN_fold_SB_fold",
    },
    "3w": {
        "roles": ("BTN", "SB", "BB"),
        "blind_roles": (1, 2),
        "scenarios": (
            "BTN_open_3w",
            "SB_vs_BTN_fold_3w",
            "SB_vs_BTN_ai_3w",
            "BB_vs_BTN_fold_SB_ai_3w",
            "BB_vs_BTN_ai_SB_fold_3w",
            "BB_vs_BTN_ai_SB_ai_3w",
        ),
        "walk_label": "BB_vs_BTN_fold_SB_fold_3w",
    },
    "2w": {
        "roles": ("SB", "BB"),
        "blind_roles": (0, 1),
        "scenarios": (
            "SB_open_2w",
            "BB_vs_SB_ai_2w",
        ),
        "walk_label": "BB_vs_SB_fold_2w",
    },
}


@dataclass(frozen=True)
class AOFState:
    mode: str
    actions: tuple[str | None, ...]

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(MODE_CONFIGS[self.mode]["roles"])


@dataclass(frozen=True)
class GrossPayoff:
    contributions_bb: tuple[float, ...]
    payouts_bb: tuple[float, ...]
    utilities_bb: tuple[float, ...]

    @property
    def utility_sum_bb(self) -> float:
        return float(sum(self.utilities_bb))


def initial_state(mode: str) -> AOFState:
    if mode not in MODE_CONFIGS:
        raise ValueError(f"unsupported mode: {mode}")
    n = len(MODE_CONFIGS[mode]["roles"])
    return AOFState(mode=mode, actions=(UNSET,) * n)


def scenario_for_state(state: AOFState) -> str | None:
    a = state.actions
    mode = state.mode

    if mode == "4w":
        if a[0] is None:
            return "CO_open"
        if a[1] is None:
            return "BTN_vs_CO_ai" if a[0] == ALLIN else "BTN_vs_CO_fold"
        if a[2] is None:
            co, btn = a[0], a[1]
            if co == FOLD and btn == FOLD:
                return "SB_vs_CO_fold_BTN_fold"
            if co == ALLIN and btn == FOLD:
                return "SB_vs_CO_ai_BTN_fold"
            if co == FOLD and btn == ALLIN:
                return "SB_vs_CO_fold_BTN_ai"
            return "SB_vs_CO_ai_BTN_ai"
        if a[:3] == (FOLD, FOLD, FOLD):
            return None
        if a[3] is None:
            co, btn, sb = a[:3]
            mapping = {
                (ALLIN, FOLD, FOLD): "BB_vs_CO_ai_BTN_fold_SB_fold",
                (FOLD, ALLIN, FOLD): "BB_vs_CO_fold_BTN_ai_SB_fold",
                (ALLIN, ALLIN, FOLD): "BB_vs_CO_ai_BTN_ai_SB_fold",
                (FOLD, FOLD, ALLIN): "BB_vs_CO_fold_BTN_fold_SB_ai",
                (ALLIN, FOLD, ALLIN): "BB_vs_CO_ai_BTN_fold_SB_ai",
                (FOLD, ALLIN, ALLIN): "BB_vs_CO_fold_BTN_ai_SB_ai",
                (ALLIN, ALLIN, ALLIN): "BB_vs_CO_ai_BTN_ai_SB_ai",
            }
            return mapping[(co, btn, sb)]
        return None

    if mode == "3w":
        if a[0] is None:
            return "BTN_open_3w"
        if a[1] is None:
            return "SB_vs_BTN_ai_3w" if a[0] == ALLIN else "SB_vs_BTN_fold_3w"
        if a[:2] == (FOLD, FOLD):
            return None
        if a[2] is None:
            btn, sb = a[:2]
            mapping = {
                (FOLD, ALLIN): "BB_vs_BTN_fold_SB_ai_3w",
                (ALLIN, FOLD): "BB_vs_BTN_ai_SB_fold_3w",
                (ALLIN, ALLIN): "BB_vs_BTN_ai_SB_ai_3w",
            }
            return mapping[(btn, sb)]
        return None

    if mode == "2w":
        if a[0] is None:
            return "SB_open_2w"
        if a[0] == FOLD:
            return None
        if a[1] is None:
            return "BB_vs_SB_ai_2w"
        return None

    raise ValueError(f"unsupported mode: {mode}")


def next_actor_index(state: AOFState) -> int | None:
    scenario = scenario_for_state(state)
    if scenario is None:
        return None
    for i, action in enumerate(state.actions):
        if action is None:
            return i
    return None


def is_terminal(state: AOFState) -> bool:
    return next_actor_index(state) is None


def apply_action(state: AOFState, action: str) -> AOFState:
    if action not in (FOLD, ALLIN):
        raise ValueError(f"invalid AoF action: {action}")
    idx = next_actor_index(state)
    if idx is None:
        raise ValueError("cannot act in a terminal state")
    actions = list(state.actions)
    actions[idx] = action
    return AOFState(mode=state.mode, actions=tuple(actions))


def terminal_label(state: AOFState) -> str:
    if not is_terminal(state):
        raise ValueError("state is not terminal")
    spec = MODE_CONFIGS[state.mode]
    if state.mode == "4w" and state.actions[:3] == (FOLD, FOLD, FOLD):
        return str(spec["walk_label"])
    if state.mode == "3w" and state.actions[:2] == (FOLD, FOLD):
        return str(spec["walk_label"])
    if state.mode == "2w" and state.actions[0] == FOLD:
        return str(spec["walk_label"])
    return "SHOWDOWN_OR_LAST_PLAYER"


def enumerate_decision_scenarios(mode: str) -> tuple[str, ...]:
    seen: list[str] = []

    def walk(state: AOFState) -> None:
        scenario = scenario_for_state(state)
        if scenario is None:
            return
        if scenario not in seen:
            seen.append(scenario)
        for action in (FOLD, ALLIN):
            walk(apply_action(state, action))

    walk(initial_state(mode))
    return tuple(seen)


def enumerate_terminal_states(mode: str) -> tuple[AOFState, ...]:
    out: list[AOFState] = []

    def walk(state: AOFState) -> None:
        if is_terminal(state):
            out.append(state)
            return
        for action in (FOLD, ALLIN):
            walk(apply_action(state, action))

    walk(initial_state(mode))
    return tuple(out)


def _gross_contributions_bb(
    state: AOFState,
    *,
    sb_bb: float,
    bb_bb: float,
    stack_bb: float,
) -> list[float]:
    n = len(state.actions)
    contributions = [0.0] * n
    sb_role, bb_role = MODE_CONFIGS[state.mode]["blind_roles"]
    contributions[int(sb_role)] = float(sb_bb)
    contributions[int(bb_role)] = float(bb_bb)

    for i, action in enumerate(state.actions):
        if action == ALLIN:
            contributions[i] = float(stack_bb)
    return contributions


def gross_terminal_payoff_from_ranks(
    state: AOFState,
    *,
    hand_ranks: Sequence[HandRank | None],
    sb_bb: float = 0.5,
    bb_bb: float = 1.0,
    stack_bb: float = 5.0,
) -> GrossPayoff:
    """Fast terminal chip payoff using already-computed Omaha hand ranks.

    This path intentionally performs no card parsing or hand evaluation. It is
    for solver hot paths where the sampled deal has already been validated and
    each player's showdown rank has been computed once.
    """
    if not is_terminal(state):
        raise ValueError("payoff requires a terminal state")
    n = len(state.actions)
    if len(hand_ranks) != n:
        raise ValueError(f"expected {n} hand ranks, got {len(hand_ranks)}")

    contributions = _gross_contributions_bb(
        state, sb_bb=sb_bb, bb_bb=bb_bb, stack_bb=stack_bb
    )
    active = [i for i, action in enumerate(state.actions) if action != FOLD]
    if not active:
        raise RuntimeError("invalid terminal state: no active player")

    pot = sum(contributions)
    payouts = [0.0] * n

    if len(active) == 1:
        payouts[active[0]] = pot
    else:
        active_ranks: dict[int, HandRank] = {}
        for i in active:
            rank = hand_ranks[i]
            if rank is None:
                raise ValueError(f"missing precomputed hand rank for active player {i}")
            active_ranks[i] = rank

        best = max(active_ranks.values())
        winners = [i for i, rank in active_ranks.items() if rank == best]
        share = pot / len(winners)
        for i in winners:
            payouts[i] += share

    utilities = [payouts[i] - contributions[i] for i in range(n)]
    return GrossPayoff(
        contributions_bb=tuple(contributions),
        payouts_bb=tuple(payouts),
        utilities_bb=tuple(utilities),
    )


def gross_terminal_payoff(
    state: AOFState,
    *,
    hole_cards: Sequence[Iterable[str]],
    board_cards: Iterable[str],
    sb_bb: float = 0.5,
    bb_bb: float = 1.0,
    stack_bb: float = 5.0,
) -> GrossPayoff:
    """Return zero-sum chip utilities before rake, jackpot and Fortune.

    Promotional/economic adjustments are intentionally excluded until OM0 has
    frozen their exact debit/credit semantics. This function validates the
    mechanical AoF tree and Omaha showdown accounting only.
    """
    if not is_terminal(state):
        raise ValueError("payoff requires a terminal state")
    n = len(state.actions)
    if len(hole_cards) != n:
        raise ValueError(f"expected {n} hole-card hands, got {len(hole_cards)}")

    holes = tuple(normalize_cards(h, expected=4) for h in hole_cards)
    board = normalize_cards(board_cards, expected=5)
    all_known = tuple(c for h in holes for c in h) + board
    if len(set(all_known)) != len(all_known):
        raise ValueError("duplicate card detected across players/board")

    contributions = _gross_contributions_bb(
        state, sb_bb=sb_bb, bb_bb=bb_bb, stack_bb=stack_bb
    )
    active = [i for i, action in enumerate(state.actions) if action != FOLD]
    if not active:
        raise RuntimeError("invalid terminal state: no active player")

    pot = sum(contributions)
    payouts = [0.0] * n

    if len(active) == 1:
        payouts[active[0]] = pot
    else:
        ranks: dict[int, HandRank] = {
            i: evaluate_omaha(holes[i], board) for i in active
        }
        best = max(ranks.values())
        winners = [i for i, rank in ranks.items() if rank == best]
        share = pot / len(winners)
        for i in winners:
            payouts[i] += share

    utilities = [payouts[i] - contributions[i] for i in range(n)]
    return GrossPayoff(
        contributions_bb=tuple(contributions),
        payouts_bb=tuple(payouts),
        utilities_bb=tuple(utilities),
    )
