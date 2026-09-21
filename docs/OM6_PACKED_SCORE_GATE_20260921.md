# OM6 Packed Showdown Score Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

After the raw-hand exact class lookup:

- evaluator: 57.26% of profiled time;
- direct class lookup: 5.13%;
- residual CFR/Python/NumPy/state work: 37.62%.

The evaluator is still the largest family, but the remaining cost is now mostly inside the exact five-card candidate loop.

## Optimization

The current fast evaluator creates a `HandRank` dataclass for every legal Omaha 2+3 candidate and compares those objects.

The optimized solver path instead uses one exact monotone packed integer:

`category | tiebreak ranks`

with fixed 4-bit rank fields.

Properties:
- no approximation;
- preserves the complete `HandRank` ordering exactly;
- no category collapse;
- no change to Omaha 2+3 semantics;
- public `evaluate_omaha` still returns `HandRank`;
- solver hot path can keep packed scores all the way through winner comparison.

## Validation

1. deterministic direct packed-score -> `HandRank` equivalence corpus;
2. existing fast/reference evaluator validation remains;
3. independent Treys differential remains;
4. solver A/B requires bit-identical regrets, average strategy, visits and final SHA256.

## Frozen A/B

Both variants:
- 4w;
- gross payoff;
- showdown cache ON;
- class cache ON;
- exact raw class lookup ON;
- fast evaluator ON;
- seed 123;
- 2 × 500 deals.

Only showdown-rank representation differs.

## Decision rule

Keep packed scores if:
- exact trajectory PASS; and
- target-hardware throughput improves materially.

Then profile once more. That profile decides whether OM6 should next attack:
- remaining evaluator internals;
- CFR/Python traversal;
- or controlled process-level parallelism.

Runner:
`tools/run_om6_packed_score_gate.sh`

No convergence training yet.
