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
- Ante: **none in the published AoF cash table**
- Default Omaha AoF stack: **5 BB**
- Table modes: **expected 4w/3w/HU from the prior AoF architecture; live maximum-player confirmation still required**

### 5 BB reconciliation

GGPoker's generic AoF marketing text refers to 8 BB, but the current Omaha rows show 5 BB buy-ins across the listed stakes. The game-specific table controls this contract.

Examples:

- $0.10/$0.20 Omaha -> $1 buy-in = 5 BB
- $0.20/$0.40 Omaha -> $2 = 5 BB
- $0.50/$1 Omaha -> $5 = 5 BB
- $1/$2 Omaha -> $10 = 5 BB
- $2/$4 Omaha -> $20 = 5 BB
- $5/$10 Omaha -> $50 = 5 BB
- $100/$200 Omaha -> $1,000 = 5 BB

## 2. Omaha showdown invariant

The evaluator MUST select exactly two cards from Hero's four hole cards and exactly three community cards.

Using 0/1/3/4 hole cards is always invalid, even if a Hold'em-style 7/9-card evaluator would report a stronger hand.

## 3. AoF Omaha Jackpot

Official qualification:

- Royal Flush;
- uses 2 of the 4 hole cards;
- uses 3 community cards;
- hands normally must reach showdown;
- published exception: if the Omaha Royal Flush is immediately completed on the flop, the hand qualifies.

Project pool scenario:

- **Jackpot pool = $750,000**

Jackpot award is stake dependent because GGPoker publishes a payout percentage of the pool.

For the development preset $0.20/$0.40:

- payout percentage = 0.02%;
- $750,000 × 0.0002 = **$150**;
- at BB=$0.40 this is **375 BB**.

The old Hold'em `jp_group` logic is NOT reusable. Omaha jackpot probability must be calculated from each four-card starting hand under the exact 2+3 rule.

## 4. All-In Fortune

Project pool scenario:

- **Fortune pool = $75,000**

Officially supported behavior:

- every All-In gives an All-In Fortune chance;
- winning the poker hand is not required;
- hit chance accumulates with All-In actions;
- prize size depends on blind level and RNG;
- buy-ins include a fixed Fortune fee.

The public GGPoker page does not expose enough tier/probability detail for exact EV reconstruction.

### Provisional DeepAoF calibration

The previous DeepAoF standalone contains:

- `fortune_trigger_p = 0.02`;
- a five-tier payout/weight distribution;
- an inline reference of approximately **$77,273.23**.

DeepOM may reuse this MODEL STRUCTURE provisionally, scaled by:

`FORTUNE_POOL_SCALE = 75000 / 77273.23 ≈ 0.9705819208`

Do not freeze a production policy on this approximation without either:

1. stronger official/client evidence; or
2. a sensitivity test proving that plausible Fortune-model error cannot change the chosen action at material infosets.

## 5. Rakeback

Project assumption supplied on 2026-09-20:

- **35% rakeback**

Current mathematical interpretation:

- apply 35% to the **base rake component only**;
- jackpot and Fortune fees remain unreduced;
- no additional PVI multiplier is modeled.

If 35% later proves to be nominal before PVI/eligibility, this contract changes.

## 6. Stake presets

GGPoker publishes different economic rows for Omaha AoF. One strategy is not assumed valid across all stakes.

Current rows captured from the official page:

| Blinds | Buy-in | Stack | Rake | Jackpot fee | Fortune fee | JP payout |
|---|---:|---:|---:|---:|---:|---:|
| $0.10/$0.20 | $1 | 5 BB | 0.03 BB | 0.035 BB | $0.007 = 0.035 BB | 0.01% |
| $0.20/$0.40 | $2 | 5 BB | 0.025 BB | 0.025 BB | $0.01 = 0.025 BB | 0.02% |
| $0.50/$1 | $5 | 5 BB | 0.03 BB | 0.03 BB | $0.03 = 0.03 BB | 0.06% |
| $1/$2 | $10 | 5 BB | 0.03 BB | 0.03 BB | $0.06 = 0.03 BB | 0.13% |
| $2/$4 | $20 | 5 BB | 0.03 BB | 0.03 BB | $0.12 = 0.03 BB | 0.26% |
| $5/$10 | $50 | 5 BB | 0.03 BB | 0.03 BB | $0.30 = 0.03 BB | 0.65% |
| $100/$200 | $1,000 | 5 BB | 0.025 BB | 0.025 BB | $0 | 10.00% |

Rows not captured from the current official table must not be invented.

## 7. Development preset v0

Preset ID:

`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

Values:

- SB = $0.20 = 0.5 BB
- BB = $0.40
- stack = $2 = 5 BB
- base rake = 0.025 BB
- jackpot fee = 0.025 BB
- Fortune fee = 0.025 BB
- rakeback = 35% of base rake
- net base rake = 0.01625 BB
- deterministic total fee = **0.06625 BB**
- jackpot pool = $750,000
- jackpot payout = 0.02% = $150 = 375 BB
- Fortune pool = $75,000
- Fortune payout model = provisional scaled DeepAoF calibration

This preset is suitable for evaluator/kernel development and economic sensitivity work. It is not yet a production policy freeze.

## 8. Prior DeepAoF reuse

The previous AoF project is a structural reference. Its solver records show that changes in stack/rake/rakeback/payoff invalidate the mathematical policy and require regeneration. DeepOM follows that same rule.

Reusable:

- public action-history tree;
- CFR orchestration;
- validation/reporting;
- opponent-model database patterns;
- runtime fallback architecture.

Must be replaced:

- two-card hand classes/evaluator;
- Hold'em equities;
- Hold'em jackpot logic;
- solved policies.

## 9. Evidence

Primary current sources:

- GGPoker AoF rules/table:
  https://ggpoker.com/poker-games/all-in-or-fold/
- GGPoker AoF Jackpot:
  https://ggpoker.com/jackpots/all-in-or-fold-jackpot/
- GGPoker All-In Fortune:
  https://ggpoker.com/jackpots/all-in-fortune/
- GGPoker Omaha rules:
  https://legal.ggpoker.com/poker-games/omaha/

Internal architecture references:

- `pmartins87/DeepAoF`;
- prior `aof_deep_generator_unificado` economic model;
- DeepAoF RB40 manual.

## 10. Change control

After a production preset is frozen, any change to stack, fees, jackpot payout, Fortune EV, rakeback treatment or jackpot qualification requires an explicit retraining-impact assessment. Policies from different economic presets must never share an ambiguous key.
