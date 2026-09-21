# OM6 Raw PLO4 Class-Lookup Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

After the encoded fast evaluator:

- evaluator: 40.48% of profiled time;
- canonical class computation: 29.96%;
- residual solver/Python work: 29.56%.

The evaluator is no longer an overwhelming bottleneck.

## Optimization

DeepOM already enumerates all 270,725 raw four-card PLO4 hands while constructing the exact 16,432-class index.

The optimized index stores a dense lossless mapping:

`raw unordered 4-card hand -> exact canonical class id`

using a deterministic 4-card combinadic/colex index and a `uint16` table.

Size:
- 270,725 entries;
- 2 bytes per entry;
- about 529 KiB.

This removes all 24 global suit permutations from the training hot path.

The old `canonical_key_plo4 -> key_to_index` route remains available as the reference oracle.

## Frozen A/B

Both variants:
- 4w;
- gross payoff;
- showdown-rank cache ON;
- per-deal class cache ON;
- fast encoded evaluator ON;
- seed 123;
- 2 × 500 deals.

Only class-resolution implementation changes.

PASS requires:
- identical regrets;
- identical average strategy;
- identical visits;
- identical final solver-array SHA256.

The raw lookup itself is also checked against the canonical reference on a deterministic direct corpus.

## Post-profile

A 500-deal post-optimization profile follows automatically. It decides whether the next step should be:
- further evaluator acceleration;
- CFR/Python traversal optimization;
- or controlled multiprocessing.

Runner:
`tools/run_om6_raw_class_lookup_gate.sh`

Do not start convergence training yet.
