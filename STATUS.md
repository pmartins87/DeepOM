# DeepOM Status

Reference date: 2026-09-20

## Current gate

**OM0 — PARTIAL PASS / CORE PRODUCT FROZEN**

Repository: `pmartins87/DeepOM`.

The project is now specifically targeting **GGPoker All-In or Fold Omaha (PLO4)** rather than generic Omaha.

## Frozen decisions

- four hole cards;
- Omaha final hand = exactly 2 hole + exactly 3 board;
- AoF action set = ALL-IN or FOLD;
- default published Omaha AoF buy-in = 5 BB;
- project Jackpot pool = $750,000;
- project All-In Fortune pool = $75,000;
- project rakeback model = 35% rebate on base rake;
- economics are stake-dependent and will be versioned as presets;
- first development preset = GGPoker Omaha $0.20/$0.40.

For the $0.20/$0.40 development preset, the current GGPoker table publishes:

- buy-in: $2 = 5 BB;
- rake: 0.025 BB;
- AoF jackpot fee: 0.025 BB;
- Fortune fee: $0.01 = 0.025 BB;
- jackpot payout: 0.02% of the jackpot pool.

With the project $750,000 jackpot pool, 0.02% corresponds to a $150 jackpot award, or 375 BB at BB=$0.40.

With 35% rakeback applied only to the 0.025 BB base rake, deterministic fees become:

- net base rake: 0.01625 BB;
- jackpot fee: 0.025 BB;
- Fortune fee: 0.025 BB;
- total deterministic fee before promotional EV: **0.06625 BB**.

This is a project model. If later evidence shows that the 35% figure is nominal/PVI-adjusted or applies to a different fee base, the economy version must change and affected policies must be retrained.

## Important source reconciliation

GGPoker's generic AoF marketing copy says "8BB", but its current **Omaha-specific table rows consistently show 5 BB default buy-ins** (e.g. $0.20/$0.40 -> $2). DeepOM uses the specific Omaha table data, not the generic sentence.

## Jackpot rule

GGPoker states that AoF Omaha requires a **Royal Flush using two of the four hole cards and three community cards**. Hands normally must reach showdown; the published rule gives an Omaha exception when the Royal Flush is immediately completed on the flop.

This means the old Hold'em jackpot grouping cannot be reused. DeepOM must calculate Omaha jackpot probability from the actual four-card hand.

## Fortune model

Official GGPoker rules confirm:

- each All-In is eligible;
- winning the poker hand is not required;
- probability accumulates with All-In actions;
- award depends on blind level and RNG;
- a fixed Fortune fee is charged.

The public page does not publish enough probability/tier detail to derive exact EV. Until a better source or live data is available, DeepOM will reuse the **architecture** of the previous DeepAoF Fortune model, not blindly reuse its dollar values. The old model's 2% trigger/tier schedule will be treated as a provisional calibration and scaled from its documented ~$77,273.23 pool reference to the project's $75,000 scenario.

No production strategy is frozen on that provisional Fortune calibration.

## DeepAoF reuse

The previous `pmartins87/DeepAoF` repository is now an explicit upstream engineering reference.

Reuse candidates:

- 4w/3w/HU AoF public action tree;
- CFR+ training orchestration;
- multi-seed stability audits;
- EV confidence/reporting;
- manifests/hashes;
- opponent-stat/alias architecture;
- fail-closed runtime architecture.

Forbidden direct reuse:

- 169 Hold'em classes;
- Hold'em equities;
- Hold'em jackpot probability/grouping;
- solved Hold'em policies/ranges.

See `docs/DEEPAOF_REUSE_PLAN.md`.

## Remaining OM0 items

- confirm the live maximum player count / 4w-3w-HU behavior in the GGPoker AoF Omaha client;
- replace the provisional Fortune calibration if stronger evidence is found;
- confirm whether the intended 35% should be modeled as effective rakeback or nominal before PVI;
- freeze the first production stake preset;
- runtime/tablemap evidence.

## Current source of truth

- `README.md`;
- `ROADMAP.md`;
- `STATUS.md`;
- `docs/PROJECT_CHARTER.md`;
- `docs/RULES_ECONOMY.md`;
- `docs/OM0_EVIDENCE.md`;
- `docs/DEEPAOF_REUSE_PLAN.md`.

## Immediate next action

Begin OM1 with an independent PLO4 evaluator/test corpus while OM0 evidence completion continues. Do not start long CFR training yet.
