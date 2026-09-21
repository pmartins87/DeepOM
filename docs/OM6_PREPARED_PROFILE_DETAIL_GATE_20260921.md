# OM6 Prepared-Integer Detailed Profile Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

The resident/pre-indexed deal A/B passed:

- 4,472.200 -> 5,134.580 deals/s;
- **1.1481x** speedup;
- exact solver trajectory match.

The automatic family attribution for the post-run profile reported evaluator/class lookup as zero because the profiler still referenced the pre-optimization function names.

The cProfile artifact itself is valid.

## Method

No new training is required.

Read:

`runs/om6_profile_post_prepared_integer_4w_d500_seed123.prof`

and report the top 30 functions by:
- cumulative time;
- self time.

Runner:

`tools/run_om6_prepared_profile_detail.sh`

Output:

`runs/om6_profile_post_prepared_integer_detail.json`

## Decision rule

After this report:

- if `evaluate_omaha_score_table_indices` / sorting / combinadic lookup remain dominant, allow one final evaluator/indexing optimization;
- if `_traverse_external`, state transitions, strategy extraction, terminal payoff, or NumPy operations dominate, stop evaluator work and move to CFR/state traversal;
- consider controlled multiprocessing only after the dominant serial path is identified and the single-process implementation is frozen.

## Stop rule

No training, no new random sample, no solver-state mutation. One report is sufficient.
