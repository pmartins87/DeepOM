# OM6 Evaluator Rank-Cache Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant;
- identical exact PLO4 state representation.

## Legacy

- train time: **4.272364216 s**
- throughput: **234.062441647 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Cached showdown ranks

- train time: **1.849131240 s**
- throughput: **540.794497641 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Equivalence

**PASS — exact trajectory match.**

Regrets, average-strategy accumulators and visits are bit-identical. The final solver-array SHA256 is identical.

## Performance

Speedup:

`540.794497641 / 234.062441647 = 2.31047106x`

This is a **131.0% throughput increase** relative to the legacy path.

Decision: keep per-deal showdown-rank caching enabled by default.

## Post-optimization profile

Frozen 500-deal cProfile:

- `evaluate_omaha`: **65.568985%**
- `canonical_key_plo4`: **28.844394%**
- residual: **5.586621%**
- profiled throughput: **172.293278 deals/s**
- visited infosets: 1,953

The cProfile throughput number is not compared directly with the unprofiled A/B because profiler overhead is material. The attribution is the decision signal.

## Next decision

Although evaluator work is still the largest single family, canonicalization is now almost 29% and is another repeated immutable per-deal computation.

Before rewriting or compiling the evaluator, DeepOM will eliminate repeated class canonicalization by computing each player's exact class index once per sampled deal.

This is selected because it is:
- lossless;
- very low risk;
- easy to prove trajectory-equivalent;
- likely to remove most of a measured 28.8% hot-path family.

After that finite A/B, profile again. Only then decide whether to rewrite/compile the evaluator.
