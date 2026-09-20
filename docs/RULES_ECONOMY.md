# DeepOM — Rules and Economy Contract

Contract status: **PARTIALLY FROZEN**
Reference date: 2026-09-20
Contract family: `GG_AOF_OMAHA_PLO4_5BB`

This is the authoritative EV-relevant contract for DeepOM.

## 1. Target product

- Poker room: **GGPoker**
- Product: **All-In or Fold Omaha cash**
- Variant: **PLO4**
- Hole cards: **4**
- Deck: **52 cards**
- Final hand construction: **exactly 2 hole cards + exactly 3 board cards**
- Available decision: **ALL-IN or FOLD**
- Default Omaha AoF stack: **5 BB**
- Table modes: current mathematical model supports **4w / 3w / HU**; live confirmation remains an OM0 item.

## 2. Omaha showdown invariant

The evaluator MUST select exactly two cards from a player's four hole cards and exactly three community cards.

This invariant is covered by unit tests, exhaustive five-card validation and an independent Treys differential gate.

## 3. AoF Omaha Jackpot

Qualification model:
- Royal Flush;
- uses exactly 2 of the 4 hole cards;
- uses exactly 3 community cards;
- normally reaches showdown;
- published Omaha exception for a Royal Flush immediately completed on the flop.

Project pool scenario:
- **Jackpot pool = $750,000**.

Development preset $0.20/$0.40:
- payout percentage = 0.02%;
- award = **$150 = 375 BB**.

Exact probability per qualifying suit:
`C(45,2) / C(48,5) = 990 / 1,712,304 ≈ 0.000578168362627`.

A four-card hand is Royal-eligible in a suit only when it contains exactly two T/J/Q/K/A cards of that suit.

Raw starting-hand census:
- 0 eligible suits: 228,085 hands;
- 1 eligible suit: 42,040;
- 2 eligible suits: 600.

Expected Jackpot credit at a showdown All-In:
- 1 eligible suit: **0.216813135985 BB**;
- 2 eligible suits: **0.433626271970 BB**.

The old Hold'em jackpot grouping is not used.

## 4. All-In Fortune

Project pool scenario:
- **Fortune pool = $75,000**.

Current public behavior used by the project:
- each All-In is eligible;
- hand victory is not required;
- award mechanics depend on blind level/RNG;
- a Fortune fee is charged.

### Provisional DeepAoF-normalized calibration

The previous DeepAoF implementation contains:
- trigger probability = 0.02;
- payout/weight tiers:
  - 200000 / 400
  - 9000 / 9996
  - 4500 / 39984
  - 1800 / 149940
  - 900 / 799680
- reference pool ≈ $77,273.23;
- reference BB denominator = 250 internal chips.

Those tiers sum to 1,000,000 weight units and imply **0.10715968 BB expected Fortune credit per All-In** in the previous normalized model.

Pool-only scaling:
`75000 / 77273.23 ≈ 0.9705819208`

gives the DeepOM provisional value:

**0.10400724804696272 BB per All-In.**

This is NOT a final blind-specific Fortune freeze. Production requires either stronger evidence or a sensitivity result showing that plausible Fortune-model variation does not materially change policy.

The solver exposes an explicit Fortune multiplier for this purpose.

## 5. Rakeback and fee placement

Project input:
- **35% rakeback**.

Current interpretation:
- rebate only the base-rake component;
- Jackpot and Fortune fees are unreduced;
- no additional PVI multiplier.

Development preset:
- base rake = 0.025 BB;
- net base rake after RB35 = 0.01625 BB;
- Jackpot fee = 0.025 BB;
- Fortune fee = 0.025 BB;
- total deterministic charge = **0.06625 BB**.

Fee placement is inherited from the prior DeepAoF GGPoker AoF implementation as **per dealt player per hand**, including a player who folds.

This placement remains explicitly marked as an inherited project assumption until independently evidenced. Because the charge is constant with respect to FOLD versus ALL-IN inside the same hand, it affects absolute EV but not the action comparison by itself.

## 6. Development preset

Preset ID:
`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

Values:
- SB = 0.5 BB;
- BB = 1 BB = $0.40;
- stack = 5 BB;
- base rake = 0.025 BB;
- RB = 35%;
- net base rake = 0.01625 BB;
- Jackpot fee = 0.025 BB;
- Fortune fee = 0.025 BB;
- fixed per-player charge = 0.06625 BB;
- Jackpot prize = 375 BB;
- Fortune EV = 0.10400724804696272 BB/All-In **provisional**.

Implementation:
- `deepom/economics.py`.

Sensitivity record:
- `docs/ECONOMY_SENSITIVITY_20260920.md`.

## 7. Stake isolation

GGPoker AoF Omaha economics vary by stake. Policies must be keyed by an unambiguous economic preset.

Never silently reuse a solved policy when any of these change:
- stack;
- base rake;
- rakeback treatment;
- Jackpot fee;
- Fortune fee;
- Jackpot payout;
- Fortune EV;
- qualification semantics.

## 8. DeepAoF reuse boundary

Reusable:
- public AoF action chronology;
- fee/promotion decomposition as an architecture;
- CFR orchestration patterns;
- validation/reporting;
- fallback/runtime architecture.

Replaced:
- two-card hand classes/evaluator;
- Hold'em equities;
- Hold'em jackpot grouping/probabilities;
- solved Hold'em policies.

## 9. Evidence

Primary public references recorded by the project:
- GGPoker AoF rules/table;
- GGPoker AoF Jackpot;
- GGPoker All-In Fortune;
- GGPoker Omaha rules.

Internal reference:
- previous `pmartins87/DeepAoF` / `aof_deep_generator_unificado`.

See `docs/OM0_EVIDENCE.md` for source classification and unresolved evidence items.

## 10. Change control

After a production preset is frozen, an EV-relevant change requires:
1. contract version change;
2. retraining-impact assessment;
3. policy regeneration when the action-dependent payoff changes;
4. new validation manifest and hashes.

No production policy is yet frozen.
