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
- OM6 Solver engineering: **IN PROGRESS — FAST EVALUATOR GATE**
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

The Ryzen 9 hot-path profile is complete:

- Omaha evaluator: **83.20%** of profiled time;
- PLO4 canonicalization/lookup: **11.78%**;
- residual CFR/Python/NumPy/state work: **5.02%**.

Decision: optimize evaluator reuse first.

Implemented:
- precomputed exact Omaha rank per player once per sampled deal;
- fast terminal payoff path using those precomputed ranks;
- economics applied on top of a precomputed gross payoff;
- checkpoint schema updated;
- exact cached-vs-legacy trajectory regression;
- finite A/B benchmark + post-optimization profiler.

Rank-cache gate: **PASS**.

Measured on Ryzen 9:
- legacy: 234.062 deals/s;
- cached showdown ranks: 540.794 deals/s;
- speedup: **2.310x**;
- exact solver-array SHA256 match: PASS.

Post-rank-cache profile:
- evaluator: 65.57%;
- canonicalization/class lookup: 28.84%;
- residual: 5.59%.

Class-index cache gate: **PASS**.

Measured on Ryzen 9:
- uncached class lookup: 528.219 deals/s;
- cached class index: 751.926 deals/s;
- speedup: **1.4235x**;
- exact solver-array SHA256 match: PASS.

Combined with showdown-rank caching, throughput improved from 234.062 to 751.926 deals/s, about **3.21x** overall.

Post-class-cache profile:
- evaluator: **87.61%**;
- canonicalization/class lookup: **6.05%**;
- residual: **6.33%**.

Current selected optimization:
- replace repeated validation/dictionary-heavy five-card work inside the Omaha evaluator with an exact encoded integer fast path;
- keep the original evaluator as a reference oracle;
- require independent Treys PASS, direct fast-vs-reference equality, and bit-identical solver trajectory.

Current runner:
`tools/run_om6_fast_evaluator_gate.sh`

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
- `docs/OM6_TARGET_BENCHMARK_RESULT_20260920.md`
- `docs/OM6_HOTPATH_PROFILE_RESULT_20260921.md`
- `docs/OM6_RANK_CACHE_GATE_20260921.md`
- `docs/OM6_RANK_CACHE_RESULT_20260921.md`
- `docs/OM6_CLASS_CACHE_GATE_20260921.md`
- `docs/OM6_CLASS_CACHE_RESULT_20260921.md`
- `docs/OM6_FAST_EVALUATOR_GATE_20260921.md`
