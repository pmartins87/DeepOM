# DeepOM Status

Reference date: 2026-09-20

Repository: `pmartins87/DeepOM`

## Gate summary

- OM0 Rules/economy: **PARTIAL PASS**
- OM1 PLO4 evaluator: **PASS**
- OM2 Equity/Jackpot: **PASS**
- OM3 AoF kernel: **PARTIAL PASS**
- OM4 State census: **PASS**
- OM5 Representation: **PASS**
- OM6 Solver engineering: **IN PROGRESS — PROFILING GATE**
- OM7+: **BLOCKED**

## Validated foundation

Current CI covers the exhaustive evaluator, independent Treys differential, equity/Jackpot validation, action-tree mechanics, exact PLO4 census, economy sensitivity, sparse CFR oracle, dense indexing, and exact checkpoint/resume equivalence.

## Exact state representation

- raw PLO4 starting hands: 270,725;
- exact suit-isomorphic classes: 16,432;
- exact canonical infosets: **361,504** total.

No strategic hand bucketing is used for v1.

## Economics

Development preset:
`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

- 5 BB stack;
- 0.01625 BB net base rake under RB35;
- 0.025 BB Jackpot fee;
- 0.025 BB Fortune fee;
- 0.06625 BB inherited fixed fee/player/hand;
- 375 BB Jackpot award;
- provisional Fortune EV 0.1040072480 BB/All-In.

## OM6 dense trainer

Implemented:
- dense NumPy arrays by scenario × exact PLO4 class;
- CFR+ / external sampling / linear averaging;
- gross and economic utility modes;
- deterministic RNG;
- checkpoint/resume;
- RNG restoration;
- manifests;
- class-index and solver-array SHA256.

4w core size: 8,281,728 bytes (~7.9 MiB).

## Target-hardware benchmark — PASS

Ryzen 9 / WSL2, 4w, seed 123, 2 × 100 deals:

Economic:
- 226.307383558 deals/s;
- 0.883753755 s train time;
- 6.282509262 s index build;
- 783 visited infosets.

Gross:
- 229.477456977 deals/s;
- 0.871545304 s train time;
- 6.478470776 s index build;
- 783 visited infosets.

Economic slowdown versus gross is only about **1.38%**.

Decision:
- economics is not the throughput bottleneck;
- do not optimize Fortune/Jackpot arithmetic for speed;
- do not parallelize yet.

## Current gate

Profile the common hot path and measure the share of time in:
1. Omaha evaluator;
2. PLO4 canonicalization/class lookup;
3. recursive CFR/Python overhead.

After profiling, select exactly one throughput optimization target.

No long convergence training yet.

## Source of truth

- `README.md`
- `ROADMAP.md`
- `STATUS.md`
- `docs/RULES_ECONOMY.md`
- `docs/OM1_OM2_VALIDATION_20260920.md`
- `docs/OM4_CENSUS_20260920.md`
- `docs/OM5_REPRESENTATION_DECISION_20260920.md`
- `docs/ECONOMY_SENSITIVITY_20260920.md`
- `docs/OM6_SOLVER_PROTOTYPE_20260920.md`
- `docs/OM6_LOCAL_BENCHMARK_GATE_20260920.md`
- `docs/OM6_TARGET_BENCHMARK_RESULT_20260920.md`
