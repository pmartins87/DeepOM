from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepom.economics import (
    GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0,
    inherited_deepaof_fortune_ev_bb,
)
from deepom.equity import DECK, qualifying_royal_suits, royal_flush_full_board_probability


def main() -> None:
    raw_hist = Counter()
    probability_sum = 0.0
    total = 0

    for hand in combinations(DECK, 4):
        k = len(qualifying_royal_suits(hand))
        raw_hist[k] += 1
        probability_sum += royal_flush_full_board_probability(hand)
        total += 1

    preset = GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0
    one_suit_prob = royal_flush_full_board_probability(("As", "Ks", "2c", "3d"))
    one_suit_jp_ev = one_suit_prob * preset.jackpot_prize_bb
    two_suit_jp_ev = 2.0 * one_suit_jp_ev
    avg_jp_prob = probability_sum / total
    avg_jp_ev = avg_jp_prob * preset.jackpot_prize_bb

    fortune_base = inherited_deepaof_fortune_ev_bb(pool_usd=75_000.0)
    sensitivity = {
        str(mult): fortune_base * mult
        for mult in (0.0, 0.5, 1.0, 1.5, 2.0)
    }

    result = {
        "raw_hands": total,
        "royal_qualifying_suits_histogram": dict(sorted(raw_hist.items())),
        "eligible_raw_hands": total - raw_hist[0],
        "eligible_raw_hand_fraction": (total - raw_hist[0]) / total,
        "one_suit_royal_probability": one_suit_prob,
        "one_suit_jackpot_ev_bb": one_suit_jp_ev,
        "two_suit_jackpot_ev_bb": two_suit_jp_ev,
        "random_hand_mean_jackpot_probability": avg_jp_prob,
        "random_hand_mean_jackpot_ev_bb_per_showdown_allin": avg_jp_ev,
        "fixed_fee_per_player_bb": preset.fixed_fee_per_player_bb,
        "fortune_ev_bb_provisional": fortune_base,
        "fortune_sensitivity_bb_per_allin": sensitivity,
    }

    print(json.dumps(result, indent=2, sort_keys=True))

    if raw_hist != Counter({0: 228_085, 1: 42_040, 2: 600}):
        raise SystemExit("unexpected Royal-Flush eligibility histogram")
    if total != 270_725:
        raise SystemExit("unexpected raw PLO4 hand count")
    print("ECONOMY_SENSITIVITY_CENSUS=PASS")


if __name__ == "__main__":
    main()
