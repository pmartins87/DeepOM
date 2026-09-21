# OM6 Raw PLO4 Class-Lookup Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- showdown-rank cache ON;
- per-deal class cache ON;
- fast encoded evaluator ON;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## Canonical reference lookup

- train time: **0.423819331 s**
- throughput: **2,359.495961486 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Dense raw-hand lookup

- train time: **0.318281865 s**
- throughput: **3,141.869236132 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

Raw lookup:
- entries: 270,725;
- storage: **541,450 bytes**;
- SHA256:
  `36724bf9dca3269d020b2bd40e5072077e393d5ed08fd1a11830087aa953fad3`.

## Equivalence

**PASS — exact trajectory match.**

The direct raw-hand table and the canonical 24-suit reference route produce the same CFR arrays.

## Performance

Speedup over canonical reference lookup:

`3141.869236132 / 2359.495961486 = 1.331584918x`

That is a further **33.16% throughput increase**.

Relative to the original pre-optimization measurement of 234.062 deals/s, the current trainer reaches 3,141.869 deals/s, approximately **13.42x** the original throughput while preserving the same solver trajectory.

## Post-raw-lookup profile

- evaluator family: **57.256739%**
- direct class lookup: **5.126772%**
- residual CFR/Python/NumPy/state work: **37.616489%**
- canonical-key path: **0.0%**
- profiled throughput: **1,558.574540 deals/s**
- visited infosets: 1,953

## Decision

Canonicalization is no longer a meaningful training bottleneck.

The evaluator is again the largest family, but generic Python/CFR overhead is now also material. Before introducing C++ or multiprocessing, the next finite optimization removes per-candidate `HandRank` object construction from the evaluator hot path by using an exact packed integer hand score.

This preserves total hand ordering exactly and can be proven against the existing fast `HandRank` evaluator and solver trajectory.
