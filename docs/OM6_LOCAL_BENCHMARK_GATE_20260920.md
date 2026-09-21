# OM6 Local Benchmark Gate — 2026-09-20

Status: **PASS**

## Purpose

Measure the dense trainer on the target hardware before selecting a throughput optimization.

## Frozen run

Two 4w tests were completed on the Ryzen 9 / WSL2:
- 2 iterations;
- 100 deals/iteration;
- seed 123;
- economic payoff enabled vs gross-chip payoff only.

## Results

Economic:
- 226.307383558 deals/s
- 0.883753755 s training
- 6.282509262 s class-index build
- 783 visited infosets

Gross:
- 229.477456977 deals/s
- 0.871545304 s training
- 6.478470776 s class-index build
- 783 visited infosets

Gross/economic throughput ratio = **1.01401**.

Economic mode is only about **1.38% slower**.

## Gate decision

The economic/promotion arithmetic is not the material runtime bottleneck.

**Next gate:** profile the common path and attribute time among:
- Omaha hand evaluation;
- PLO4 canonicalization/class lookup;
- recursive CFR/Python overhead.

Do not add multiprocessing or launch a long solve until this profile exists.

Detailed record:
`docs/OM6_TARGET_BENCHMARK_RESULT_20260920.md`.
