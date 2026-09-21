# OM6 Packed Showdown Score Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- all previously accepted caches ON;
- fast encoded evaluator ON;
- raw class lookup ON;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## HandRank path

- train time: **0.353975763 s**
- throughput: **2,825.052177208 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Packed integer score path

- train time: **0.335467688 s**
- throughput: **2,980.913023289 deals/s**
- visited infosets: 3,870
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`

## Equivalence

**PASS — exact trajectory match.**

Packed scores preserve regrets, average-strategy accumulators, visits and the final solver-array SHA256 exactly.

## Performance

Speedup:

`2980.913023289 / 2825.052177208 = 1.055170962x`

That is a **5.52% throughput increase**.

Decision: keep packed scores because they are exact, low-cost, and form the natural storage format for the next lookup-table optimization. The gain alone is modest, so no further object-level micro-optimization is justified.

## Post-packed-score profile

- evaluator: **59.701953%**
- direct class lookup: **4.826973%**
- residual CFR/Python/NumPy/state work: **35.471074%**
- canonicalization: 0%
- profiled throughput: **1,478.579956 deals/s**
- visited infosets: 1,953

## Next decision

The evaluator remains the largest family. The next finite optimization targets the inner 5-card evaluator itself with a lossless precomputed score table over all **2,598,960** possible five-card combinations.

The table will:
- use the packed exact score already validated above;
- use a deterministic combinadic index for every unordered five-card set;
- store one `uint32` per five-card hand (~9.9 MiB);
- be cached on disk after first construction and later memory-mappable/shareable across processes;
- preserve exact Omaha 2+3 enumeration;
- keep the arithmetic evaluator as the reference oracle.

Only after this gate will DeepOM decide whether remaining evaluator work justifies compiled code or whether CFR/Python/process parallelism is the better next target.
