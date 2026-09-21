# OM6 Target-Hardware Benchmark Result — 2026-09-20

Hardware/runtime:
- Ryzen 9 host;
- WSL2 Ubuntu 24.04.3;
- Linux 6.6.87.2-microsoft-standard-WSL2;
- Python 3.12.3.

Frozen benchmark:
- mode: 4w;
- 2 iterations;
- 100 deals/iteration;
- seed 123;
- exact 16,432-class index;
- identical workload for economic and gross variants.

## Economic payoff run

- class index build: 6.282509262 s
- train time: 0.883753755 s
- throughput: **226.307383558 deals/s**
- visited infosets: 783
- mean positive regret: 0.004316864280
- dense core bytes: 8,281,728

## Gross-chip payoff run

- class index build: 6.478470776 s
- train time: 0.871545304 s
- throughput: **229.477456977 deals/s**
- visited infosets: 783
- mean positive regret: 0.004349364046
- dense core bytes: 8,281,728

## Comparison

Gross/economic throughput ratio:

`229.477456977 / 226.307383558 = 1.01401`

Economic payoff is only about **1.38% slower** than gross payoff on this finite benchmark.

The two runs visit exactly the same number of infosets. Their small regret difference is expected because the utility model differs.

## Decision

**OM6 local benchmark gate: PASS.**

The promotion/economic payoff layer is **not** the material throughput bottleneck.

Do not spend engineering effort optimizing Fortune/Jackpot arithmetic for speed at this stage.

The one-time class-index construction takes about 6.3-6.5 s, far longer than this deliberately tiny training sample, but this does not imply it dominates a real training run because the index is built once per process.

The next finite gate is profiling the shared hot path:
1. Omaha terminal evaluator;
2. repeated PLO4 canonicalization / class lookup;
3. recursive CFR traversal / Python-call overhead.

Only after measured attribution should multiprocessing or a lower-level evaluator/lookup optimization be selected.

## Stop rule

Do not increase training depth yet. The next action is profiling, not convergence training.
