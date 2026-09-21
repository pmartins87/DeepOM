# OM6 Hot-Path Profile Result — 2026-09-21

Hardware/runtime:
- Ryzen 9 host;
- WSL2;
- DeepOM exact 16,432-class representation.

Frozen profile:
- mode: 4w;
- gross payoff;
- 500 deals;
- seed 123;
- class-index build excluded from the profiled region.

## Result

High-level cumulative attribution:

- `evaluate_omaha`: **6.261142125 s / 83.201383%**
- `canonical_key_plo4`: **0.886725398 s / 11.783278%**
- residual CFR/Python/NumPy/state work: **5.015339%**

Profiled throughput under cProfile:
- **66.376596 deals/s**

Visited infosets:
- **1,953**

## Decision

**OM6 profiling gate: PASS.**

The Omaha showdown evaluator is the dominant measured bottleneck by a wide margin.

The next optimization target is therefore **evaluator-path reuse**, not:
- economic arithmetic;
- multiprocessing;
- canonicalization;
- generic CFR traversal.

## Selected optimization

A sampled deal has fixed hole cards and a fixed final board. The previous CFR traversal recomputed identical Omaha showdown ranks at every terminal branch.

The selected low-risk optimization computes each player's exact showdown rank once per sampled deal and reuses it through all terminal branches.

This does not change:
- poker rules;
- hand-ranking semantics;
- state abstraction;
- CFR update equations;
- RNG sequence.

The optimization must pass an exact trajectory A/B gate before being accepted.

Next gate:
`docs/OM6_RANK_CACHE_GATE_20260921.md`.
