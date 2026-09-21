# DeepOM Status

Reference date: 2026-09-21

Repository: `pmartins87/DeepOM`

## Gate summary

- OM0 Rules/economy: **PARTIAL PASS**
- OM1 PLO4 evaluator: **PASS**
- OM2 Equity/Jackpot: **PASS**
- OM3 AoF kernel: **PARTIAL PASS**
- OM4 State census: **PASS**
- OM5 Representation: **PASS**
- OM6 Solver engineering: **IN PROGRESS — PREPARED-INTEGER DETAIL GATE**
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

Fast evaluator gate: **PASS**.

Measured on Ryzen 9:
- reference evaluator: 762.460 deals/s;
- encoded fast evaluator: 2,389.733 deals/s;
- speedup: **3.134x**;
- exact solver-array SHA256 match: PASS.

Relative to the original 234.062 deals/s path, the current trainer is about **10.21x faster** with the same solver trajectory.

Post-fast-evaluator profile:
- evaluator: **40.48%**;
- canonical class computation: **29.96%**;
- residual CFR/Python/NumPy/state work: **29.56%**.

Raw class-lookup gate: **PASS**.

Measured on Ryzen 9:
- canonical reference lookup: 2,359.496 deals/s;
- dense raw-hand lookup: 3,141.869 deals/s;
- speedup: **1.3316x**;
- exact solver-array SHA256 match: PASS.

Relative to the original 234.062 deals/s path, the current trainer is about **13.42x faster** with the same solver trajectory.

Post-raw-lookup profile:
- evaluator: **57.26%**;
- direct class lookup: **5.13%**;
- residual CFR/Python/NumPy/state work: **37.62%**;
- canonicalization: 0%.

Packed showdown-score gate: **PASS**.

Measured on Ryzen 9:
- HandRank path: 2,825.052 deals/s;
- packed score path: 2,980.913 deals/s;
- speedup: **1.0552x**;
- exact solver-array SHA256 match: PASS.

Post-packed-score profile:
- evaluator: **59.70%**;
- direct class lookup: **4.83%**;
- residual CFR/Python/NumPy/state work: **35.47%**.

Decision:
- keep packed scores because they are exact and useful as the storage format for lookup-table evaluation;
- do not pursue more object-level micro-optimization because the gain was only ~5.5%.

Five-card score-table gate: **PASS**.

Measured on Ryzen 9:
- arithmetic packed-score backend: 3,022.880 deals/s;
- exact five-card table backend: 4,486.021 deals/s;
- speedup: **1.4840x**;
- exact solver-array SHA256 match: PASS;
- 5,000 five-card + 1,000 Omaha direct validation cases: 0 mismatches.

Table:
- 2,598,960 entries;
- 10,395,840 bytes;
- first build ~2.24 s;
- SHA256 `d50cf3a649b8c778c5f84389b6f4d287b9ebaffd526d6b4bf32d4e9e7f5c65c4`.

Post-table profile:
- evaluator: **50.61%**;
- direct class lookup: **6.05%**;
- residual CFR/Python/NumPy/state work: **43.35%**.

Decision:
- keep the five-card table;
- do not choose C++/multiprocessing yet from family-level data because evaluator and residual are now close.

Detailed hotspot attribution: **PASS**.

Key function-level findings:
- `prepare_sampled_deal`: 0.153040 s cumulative;
- `evaluate_omaha_score_table`: 0.134086 s cumulative / 0.047901 s self;
- memmap `__getitem__`: 0.031354 s self;
- repeated `normalize_cards` / validation / card conversion: material;
- `sorted`: 0.019505 s self;
- `_traverse_external`: 0.090612 s cumulative / 0.019208 s self;
- `current_strategy`: 0.025014 s cumulative.

Decision:
- one final low-risk evaluator/data-path optimization before touching CFR traversal or multiprocessing;
- load the small five-card table into resident memory;
- convert each sampled deal to card indices once;
- reuse those indices for Omaha table evaluation and exact class lookup.

Resident/pre-indexed deal gate: **PASS**.

Measured on Ryzen 9:
- reference memmap/string path: 4,472.200 deals/s;
- resident/pre-indexed path: 5,134.580 deals/s;
- speedup: **1.1481x**;
- exact solver-array SHA256 match: PASS.

Relative to the original ~234.062 deals/s path, this is about **21.94x** faster with the same solver trajectory.

Important profiling caveat:
- the post-run family summary printed evaluator=0/class=0/residual=100%;
- this is an instrumentation miss, not a real attribution;
- the fast path changed function names to `evaluate_omaha_score_table_indices` and `index_of_indices`;
- the cProfile artifact itself is valid.

Profiler instrumentation has now been corrected for future runs.

Current gate:
- read the existing post-prepared-integer cProfile at function level;
- no new training.

Current runner:
`tools/run_om6_prepared_profile_detail.sh`

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
- `docs/OM6_FAST_EVALUATOR_RESULT_20260921.md`
- `docs/OM6_RAW_CLASS_LOOKUP_GATE_20260921.md`
- `docs/OM6_RAW_CLASS_LOOKUP_RESULT_20260921.md`
- `docs/OM6_PACKED_SCORE_GATE_20260921.md`
- `docs/OM6_PACKED_SCORE_RESULT_20260921.md`
- `docs/OM6_FIVECARD_TABLE_GATE_20260921.md`
- `docs/OM6_FIVECARD_TABLE_RESULT_20260921.md`
- `docs/OM6_PROFILE_DETAIL_GATE_20260921.md`
- `docs/OM6_PROFILE_DETAIL_RESULT_20260921.md`
- `docs/OM6_PREPARED_INTEGER_GATE_20260921.md`
- `docs/OM6_PREPARED_INTEGER_RESULT_20260921.md`
- `docs/OM6_PREPARED_PROFILE_DETAIL_GATE_20260921.md`
