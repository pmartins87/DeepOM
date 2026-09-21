# OM6 Resident / Pre-Indexed Deal Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

The detailed post-five-card-table profile identified the largest avoidable data-plumbing costs:

- memory-mapped table `__getitem__`: 0.031354 s self;
- repeated card normalization / validation: material cumulative cost;
- repeated string -> card-index conversion;
- exact PLO4 class lookup still receives strings even though sampled deals are already valid.

The evaluator and residual CFR path are now close enough that this is the last low-risk single-process evaluator/data-path optimization before moving to traversal or parallelism.

## Optimization

Reference path:
- five-card score table memory-mapped;
- sampled deal remains string-card based during Omaha/table lookup;
- public validated lookup functions are used.

Fast path:
- load the ~9.9 MiB table into resident NumPy memory;
- convert each sampled deal's cards to exact deck indices once;
- reuse those indices for all players' Omaha evaluation;
- reuse the same hole-card indices for exact raw PLO4 class-id lookup;
- skip repeated validation only inside the internal solver path, where the sampled deal is already generated from the canonical deck without replacement.

Public/reference APIs remain unchanged.

## Frozen A/B

Both variants:
- 4w;
- gross payoff;
- exact five-card table;
- packed scores;
- raw exact class table;
- seed 123;
- 2 × 500 deals.

PASS requires:
- identical regrets;
- identical average strategy;
- identical visits;
- identical final solver-array SHA256.

Then run one 500-deal post-optimization cProfile.

## Decision rule

If the evaluator/data path is no longer dominant after this gate, stop evaluator micro-optimization and move to CFR/state traversal.

If evaluator internals still dominate materially, only one further evaluator optimization is allowed before considering compiled code.

Runner:
`tools/run_om6_prepared_integer_gate.sh`
