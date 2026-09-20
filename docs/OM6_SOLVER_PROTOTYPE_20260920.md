# OM6 Solver Engineering Record — 2026-09-20

## Stage A — sparse correctness oracle

Implementation:
- `deepom/solver_proto.py`

Validated:
- external-sampling CFR;
- CFR+ regret clipping;
- linear averaging;
- 4w/3w/HU public tree;
- exact 16,432-class PLO4 keys;
- deterministic seeds;
- gross and optional economic payoffs;
- Fortune/Jackpot sensitivity multipliers.

This implementation remains the readable correctness oracle.

## Stage B — dense indexed trainer

Implementation:
- `deepom/dense_solver.py`

Implemented:
- deterministic full 16,432-class index;
- SHA256 of the class index;
- NumPy `float64` regrets;
- NumPy `float64` average-strategy accumulators;
- `uint32` visits;
- scenario × class direct addressing;
- CFR+ / external sampling / linear averaging;
- economic or gross terminal utility;
- checkpoint to `state.npz`;
- versioned `manifest.json`;
- exact RNG-state restoration;
- solver-array SHA256 validation on load.

4w dense core:
- 230,048 infosets;
- basic regret/strategy/visit arrays ≈ **7.9 MiB**.

The corresponding core across 4w+3w+HU is ≈ **12.4 MiB**.

## Regression gate

`tests/test_dense_solver.py` validates:
- full class count = 16,432;
- deterministic class-index hash;
- expected dense array shape;
- compact memory bound;
- correct regret direction in a forced losing-call fixture;
- **continuous run == checkpoint/resume run exactly**, including final arrays/hash.

## Current OM6 status

**IN PROGRESS — TARGET-HARDWARE BENCHMARK REQUIRED.**

Dense representation, checkpointing and manifests are no longer open items.

Do not add multiprocessing merely because it was planned earlier. The correct next step is to measure the target hardware first.

## Finite benchmark

Runner:
`tools/run_om6_local_benchmark.sh`

Contract:
`docs/OM6_LOCAL_BENCHMARK_GATE_20260920.md`

Two runs only:
- economic 4w, 2 × 100 deals, seed 123;
- gross 4w, 2 × 100 deals, seed 123.

Decision after results:
- economic-only slowdown -> profile economics/promotions;
- similar gross/economic slowdown -> profile evaluator/canonicalization/traversal;
- multiprocessing is selected only if profiling supports it.

## Remaining OM6 requirements after benchmark

- measured throughput optimization;
- cross-seed Fortune sensitivity mini-runs;
- production export format;
- final OM6 PASS decision.

No long solver run is allowed before these gates.
