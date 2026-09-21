# OM6 Exact Five-Card Score Table Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- all previously accepted caches ON;
- packed showdown scores ON;
- raw PLO4 class lookup ON;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## Arithmetic packed-score backend

- train time: **0.330810397 s**
- throughput: **3,022.879597867 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Exact five-card score-table backend

- train time: **0.222914681 s**
- throughput: **4,486.021268114 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Table identity

- entries: **2,598,960**
- payload bytes: **10,395,840**
- first build: **2.243499249 s**
- first build/load wrapper: **2.260322296 s**
- SHA256:
  `d50cf3a649b8c778c5f84389b6f4d287b9ebaffd526d6b4bf32d4e9e7f5c65c4`
- first run loaded from cache: false

Validation:
- 5,000 deterministic five-card arithmetic-vs-table cases;
- 1,000 deterministic Omaha arithmetic-vs-table cases;
- mismatches: **0**.

## Equivalence

**PASS — exact trajectory match.**

The arithmetic and table evaluators produce bit-identical regrets, average-strategy accumulators, visits, and final solver-array SHA256.

## Performance

Speedup:

`4486.021268114 / 3022.879597867 = 1.484022477x`

That is a **48.40% throughput increase** over the packed arithmetic evaluator.

Relative to the early 234.062 deals/s legacy path, the measured current path is roughly **19.2x faster**, while preserving the same solver trajectory.

## Post-table profile

- table Omaha evaluator: **50.606942%**
- direct PLO4 class lookup: **6.046098%**
- residual CFR/Python/NumPy/state work: **43.346960%**
- canonicalization: 0%
- profiled throughput: **1,849.127348 deals/s**
- visited infosets: 1,953

## Decision

Keep the five-card score table.

The evaluator and the residual solver path are now close enough that another structural optimization should not be selected from family-level attribution alone.

The next finite gate is **detailed hotspot attribution from the already-created cProfile file**. No new training run is required.

The detail report will separate cumulative and self time for:
- five-card table indexing / card conversion / sorting;
- CFR recursion;
- state transitions;
- strategy calculation / NumPy operations;
- RNG and sampling.

Only after this detail report will DeepOM choose among:
- one final evaluator/indexing optimization;
- CFR traversal restructuring/compilation;
- controlled process-level parallelism.
