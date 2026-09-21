# OM6 Hot-Path Profiling Gate — 2026-09-20

Status: **READY TO RUN**

## Why this gate exists

The target-hardware benchmark measured:

- economic payoff: 226.307 deals/s;
- gross payoff: 229.477 deals/s;
- economic overhead: only ~1.38%.

Therefore the next optimization must target the shared training path, not Fortune/Jackpot arithmetic.

## Frozen profile

Run:
- mode: 4w;
- gross payoff;
- seed: 123;
- 500 deals;
- one CFR iteration;
- exact 16,432-class representation.

The one-time class-index build is measured separately and excluded from the profiler.

Runner:
`tools/run_om6_profile.sh`

Outputs:
- `runs/om6_profile_4w_gross_d500_seed123.json`;
- `runs/om6_profile_4w_gross_d500_seed123.txt`;
- `runs/om6_profile_4w_gross_d500_seed123.prof`.

## Attribution

The JSON reports direct targeted statistics plus two disjoint high-level cumulative paths:

1. `evaluate_omaha` — terminal Omaha evaluation;
2. `canonical_key_plo4` — exact private-hand canonicalization used for infoset lookup.

The remaining share contains CFR recursion, public-state handling, NumPy operations, random sampling and other Python work.

## Decision rule

After the profile:

- if Omaha evaluation is the largest attributable family, optimize the evaluator first;
- if canonicalization/lookup is the largest, replace repeated 24-permutation canonicalization in the training hot path with a validated direct/raw-hand lookup;
- if residual CFR/Python work dominates, inspect the top cumulative/self-time functions and choose between traversal restructuring, compiled hot path, or parallelism.

Only **one** optimization target is selected from the profile.

## Stop criterion

One 500-deal profile is enough for this gate unless the result is ambiguous (top families within 10% relative share or profiler instability). Do not extend to convergence training.
