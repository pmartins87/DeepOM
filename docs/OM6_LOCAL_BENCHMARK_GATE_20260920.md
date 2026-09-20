# OM6 Local Benchmark Gate — 2026-09-20

## Purpose

Measure the dense trainer on the target local hardware before adding multiprocessing or launching any long run.

This gate exists to answer one question first:

**What is actually limiting throughput after the exact 16,432-class representation and dense arrays are in place?**

Premature parallelization is explicitly avoided.

## Frozen finite benchmark

Run exactly two 4w tests with identical seed/work:

1. economic payoff enabled;
2. gross-chip payoff only.

Parameters:
- mode: 4w;
- iterations: 2;
- deals per iteration: 100;
- seed: 123;
- Fortune multiplier: 1.0;
- Jackpot multiplier: 1.0.

Script:
`tools/run_om6_local_benchmark.sh`

Outputs:
- `runs/om6_dense_4w_econ_i2_d100_seed123.json`
- `runs/om6_dense_4w_gross_i2_d100_seed123.json`

## Decision gate

After the two JSON outputs are collected:

- if economic vs gross throughput differs materially, profile the promotion/economic path;
- if both are similarly slow, profile evaluator/canonicalization/traversal;
- only then decide whether multiprocessing is the next optimization;
- do not increase iterations/deals simply to "see more".

## Stop criterion

This benchmark ends after the two prescribed files exist. It is not a convergence run and its policy output must not be interpreted as strategy quality.

## Next step after results

Record:
- index build time;
- training time;
- deals/s;
- visited infosets;
- core bytes;
- gross/economic throughput ratio.

Then choose one optimization target and update OM6.
