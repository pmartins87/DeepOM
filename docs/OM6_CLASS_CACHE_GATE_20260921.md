# OM6 PLO4 Class-Index Cache Gate — 2026-09-21

Status: **READY TO RUN**

The rank-cache optimization increased unprofiled throughput from 234.06 to 540.79 deals/s (**2.31x**) with bit-identical solver arrays.

The post-rank-cache profile still showed:
- evaluator: 65.57%;
- canonicalization/class lookup: 28.84%;
- residual: 5.59%.

Rather than rewrite the evaluator immediately, this gate removes the second large repeated immutable computation first.

## Optimization

Each player's four-card hand is fixed for the entire sampled deal. Its exact one-of-16,432 class index is therefore computed once and reused at every infoset reached for that player.

This changes no abstraction and no poker semantics.

## A/B

Both variants:
- 4w;
- gross payoff;
- showdown-rank cache enabled;
- seed 123;
- 2 × 500 deals.

Only class-index caching differs.

PASS requires bit-identical regrets, average strategy, visits and final array SHA256.

After the A/B, one 500-deal profile is run with both caches enabled.

Runner:
`tools/run_om6_class_cache_gate.sh`

Do not start convergence training yet.
