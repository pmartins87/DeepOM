# OM6 Fast Omaha Evaluator Gate — 2026-09-21

Status: **READY TO RUN**

The post-class-cache profile showed:
- evaluator: 87.61%;
- canonicalization: 6.05%;
- residual: 6.33%.

The evaluator is therefore the dominant remaining bottleneck.

## Optimization

The original readable evaluator validates and reparses five cards for every one of the 60 legal Omaha 2+3 combinations.

The fast evaluator:
- validates the 4 hole + board state once;
- encodes each card once;
- evaluates the 60 legal five-card candidates using integer rank/suit codes;
- uses direct sorted-rank pattern logic instead of per-candidate card normalization and rank-count dictionaries.

No abstraction, approximation, category change or 2+3 rule change is introduced.

The original implementation remains available as `evaluate_omaha_reference` for A/B validation.

## Validation layers

1. public fast evaluator continues to pass the independent Treys differential;
2. deterministic 1,000-case fast-vs-reference corpus;
3. solver-level A/B with exact regret/average/visit-array equality.

## Frozen solver A/B

Both variants:
- 4w;
- gross payoff;
- showdown-rank cache ON;
- class-index cache ON;
- seed 123;
- 2 × 500 deals.

Only evaluator implementation differs.

PASS requires identical final solver-array SHA256.

A 500-deal post-optimization profile follows automatically.

Runner:
`tools/run_om6_fast_evaluator_gate.sh`

Do not begin convergence training yet.
