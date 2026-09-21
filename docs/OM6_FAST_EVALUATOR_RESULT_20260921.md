# OM6 Fast Omaha Evaluator Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- showdown-rank cache ON;
- class-index cache ON;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## Reference evaluator

- train time: **1.311543734 s**
- throughput: **762.460277981 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Encoded fast evaluator

- train time: **0.418456716 s**
- throughput: **2,389.733421956 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Equivalence

**PASS — exact trajectory match.**

The fast evaluator preserves the exact CFR trajectory and final solver arrays.

The independent Treys differential, direct fast-vs-reference corpus, exhaustive five-card validation, and full CI suite also pass.

## Performance

Speedup over the reference evaluator with both prior caches enabled:

`2389.733421956 / 762.460277981 = 3.134239895x`

That is a **213.4% throughput increase**.

Relative to the pre-cache/pre-fast-evaluator legacy measurement of 234.062 deals/s, the current trainer reaches 2,389.733 deals/s, approximately **10.21x** the original throughput while preserving the same solver trajectory.

## Post-fast-evaluator profile

- `evaluate_omaha`: **40.475596%**
- `canonical_key_plo4`: **29.959930%**
- residual: **29.564474%**
- profiled throughput: **1,107.987618 deals/s**
- visited infosets: 1,953

The evaluator is no longer overwhelmingly dominant. Exact canonical-class computation and general Python/CFR overhead are now comparable.

## Next decision

Before introducing C++/compiled code or multiprocessing, remove the remaining expensive suit-canonicalization step from the per-deal hot path.

DeepOM already enumerates all 270,725 raw PLO4 starting hands while building the class index. The next optimization adds a lossless raw-hand -> exact 16,432-class lookup table so each sampled four-card hand can resolve its class directly without 24 suit permutations.

This is exact, small, deterministic, and can be A/B validated against the canonical reference lookup.
