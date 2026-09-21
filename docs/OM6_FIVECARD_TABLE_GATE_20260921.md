# OM6 Exact Five-Card Score Table Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

After packed showdown scores, the target profile still attributes about 59.70% of runtime to the Omaha evaluator, versus 35.47% residual solver/Python work and 4.83% direct PLO4 class lookup.

Packed scores themselves improved throughput by only 5.52%, so further object-level micro-optimization is not justified.

## Optimization

There are exactly **2,598,960** unordered five-card combinations from a 52-card deck.

DeepOM now supports a deterministic lossless table:

`five exact cards -> combinadic index -> packed exact hand score`

The table stores one `uint32` per five-card combination:
- 2,598,960 entries;
- 10,395,840 payload bytes (~9.91 MiB);
- exact score ordering already validated by the packed-score gate.

The Omaha evaluator still enumerates exactly 2 hole + 3 board cards. Only the inner five-card scoring operation changes from arithmetic to direct lookup.

## Persistence

The first target-machine run builds:

`cache/five_card_scores_v1.npy`

Later runs load/memory-map the same table. The cache is not committed to Git.

The table SHA256 is recorded and becomes part of solver/checkpoint identity whenever the table backend is active.

## Validation

The finite gate performs:
- 5,000 deterministic random five-card arithmetic-vs-table checks;
- 1,000 deterministic random Omaha arithmetic-vs-table checks;
- 4w solver A/B with identical seed/work;
- exact regret, average-strategy, visit and final SHA256 equality;
- one post-optimization cProfile.

## Decision rule

If exact equivalence passes and throughput improves materially, retain the table backend.

The post-profile then decides between:
- remaining evaluator/indexing optimization;
- CFR/Python traversal optimization;
- controlled process-level parallelism.

No convergence run is allowed yet.

Runner:
`tools/run_om6_fivecard_table_gate.sh`.
