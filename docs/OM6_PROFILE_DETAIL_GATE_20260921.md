# OM6 Detailed Hotspot Attribution Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

After the exact five-card score table, the target profile is:

- Omaha evaluator: 50.61%;
- direct class lookup: 6.05%;
- residual CFR/Python/NumPy/state work: 43.35%.

The top two families are now close enough that another implementation decision should use function-level evidence rather than family-level percentages.

## Method

No new training run is required.

Read the existing cProfile artifact:

`runs/om6_profile_post_fivecard_table_4w_d500_seed123.prof`

and report:
- top 25 functions by cumulative time;
- top 25 functions by self time.

Runner:
`tools/run_om6_profile_detail.sh`

Output:
`runs/om6_profile_post_fivecard_table_detail.json`

## Decision rule

Use the detailed profile to select exactly one next engineering target:

- evaluator/indexing if table-evaluator internals still dominate;
- CFR/state traversal if recursive/state/NumPy work dominates;
- controlled multiprocessing only if the remaining serial hot path is sufficiently balanced and deterministic single-process correctness is already frozen.

## Stop rule

This gate does not train or mutate solver state. One report is sufficient.
