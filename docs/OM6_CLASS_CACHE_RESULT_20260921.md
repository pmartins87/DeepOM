# OM6 PLO4 Class-Index Cache Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- showdown-rank cache enabled in both variants;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## Uncached class lookup

- train time: **1.893152771 s**
- throughput: **528.219389012 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Per-deal cached class index

- train time: **1.329917481 s**
- throughput: **751.926352041 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Equivalence

**PASS — exact trajectory match.**

Regrets, average-strategy accumulators and visits are bit-identical.

## Performance

Speedup over the already rank-cached baseline:

`751.926352041 / 528.219389012 = 1.423511457x`

That is a further **42.35% throughput increase**.

Relative to the pre-rank-cache legacy measurement (234.062 deals/s), the two immutable-deal caches together raise throughput to 751.926 deals/s, approximately **3.21x** overall.

Decision: keep exact per-deal PLO4 class-index caching enabled by default.

## Post-class-cache profile

- `evaluate_omaha`: **87.614349%**
- `canonical_key_plo4`: **6.051851%**
- residual: **6.333800%**
- profiled throughput: **225.077 deals/s**
- visited infosets: 1,953

The remaining dominant bottleneck is now unambiguous: the internal Omaha evaluator.

## Next gate

Optimize the evaluator implementation itself while preserving exact 2+3 semantics and exact solver trajectory.

The first evaluator optimization removes repeated card validation/dictionary-heavy five-card evaluation inside the 60 legal Omaha 2+3 combinations, replacing it with a validated encoded five-card fast path.

No abstraction and no approximation are introduced.
