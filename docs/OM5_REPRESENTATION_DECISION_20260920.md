# OM5 Representation Decision — 2026-09-20

Decision: **PASS — exact PLO4 representation selected.**

## Selected representation

Use all **16,432 suit-isomorphic PLO4 classes** exactly.

The equivalence relation is limited to global suit renaming. This preserves:
- ranks;
- pair structure;
- connectedness/gaps;
- single/double/triple/quad-suited structure;
- blockers;
- Royal Flush Jackpot eligibility;
- all poker-equity information invariant under suit renaming.

## Rejected for v1

Do not introduce:
- coarse Omaha hand buckets;
- percentile/equity buckets;
- Hold'em-style 169 classes;
- hand-strength-only abstraction.

## Reason

The exact state census gives only **361,504 canonical preflop infosets** across the current 4w/3w/HU action trees. Core dense solver arrays are small on current hardware. Abstraction would add model risk without solving a demonstrated resource bottleneck.

## Reversal condition

Revisit abstraction only if a measured downstream bottleneck appears in:
- chance traversal cost;
- opponent-card correlation handling;
- convergence/sample complexity;
- production lookup;
- memory after additional state dimensions are added.

The burden of proof is now on abstraction, not on exact representation.
