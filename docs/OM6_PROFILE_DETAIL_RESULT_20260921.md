# OM6 Detailed Hotspot Attribution Result — 2026-09-21

Source:
`runs/om6_profile_post_fivecard_table_4w_d500_seed123.prof`

No new training was performed for this gate.

## Top cumulative paths

Total profiled training time was about **0.270 s**.

Largest cumulative paths:

1. `prepare_sampled_deal`: **0.153040 s**
2. `evaluate_omaha_score_table`: **0.134086 s**
3. `_traverse_external`: **0.090612 s**
4. `normalize_cards`: **0.030998 s**
5. `current_strategy`: **0.025014 s**
6. `_validate_omaha_inputs`: **0.023831 s**
7. `sorted`: **0.023448 s**
8. `gross_terminal_payoff_from_ranks`: **0.018003 s**
9. `apply_action`: **0.018633 s**
10. `next_actor_index`: **0.016190 s**
11. `index_of`: **0.016019 s**
12. `scenario_for_state`: **0.009167 s**

## Top self-time signals

The most actionable self-time entries are:

- `evaluate_omaha_score_table`: **0.047901 s**
- NumPy memmap `__getitem__`: **0.031354 s** across 120,000 table accesses
- built-in `sorted`: **0.019505 s** across 126,000 calls
- `_traverse_external`: **0.019208 s**
- `normalize_card`: **0.013432 s**
- `current_strategy`: **0.011529 s**
- `colex_rank5_sorted`: **0.010369 s**
- `gross_terminal_payoff_from_ranks`: **0.009466 s**
- `next_actor_index`: **0.009242 s**
- `scenario_for_state`: **0.009167 s**
- `apply_action`: **0.008230 s**

## Interpretation

The family-level profile had evaluator 50.61% vs residual solver 43.35%. The function-level profile shows that a substantial part of the evaluator cost is not poker hand ranking itself anymore. It is data plumbing:

- memory-mapped table element access;
- repeated string-card normalization;
- repeated card-to-index conversion;
- repeated validation of sampled deals that are already known-valid;
- repeated sorting before combinadic lookup.

This means jumping directly to C++ or multiprocessing would still leave easy exact single-process work on the table.

## Selected next optimization

Use a **resident pre-indexed deal path**:

1. load the ~9.9 MiB five-card table into ordinary resident NumPy memory for training instead of per-element memmap access;
2. convert the sampled deal's card strings to integer deck indices once;
3. evaluate Omaha from those already-valid indices, avoiding repeated normalization/validation/card lookup;
4. compute exact PLO4 class ids directly from the same prepared indices.

The public validated string-card APIs remain unchanged as reference oracles.

This is one coherent optimization target: eliminate redundant data-conversion/memory-access overhead inside `prepare_sampled_deal`.

## Stop rule

Run one exact A/B plus one post-optimization profile. If residual CFR/state work becomes dominant, stop evaluator micro-optimization and move to the solver traversal path.
