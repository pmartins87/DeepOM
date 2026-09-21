# OM6 Evaluator Rank-Cache Optimization Gate — 2026-09-21

Status: **READY TO RUN**

## Trigger

The Ryzen 9 hot-path profile showed:

- `evaluate_omaha`: **83.20%** of profiled time;
- `canonical_key_plo4`: **11.78%**;
- residual traversal/NumPy/Python: **5.02%**.

Therefore the first throughput optimization target is the Omaha evaluator path.

## Optimization selected

A sampled deal has one fixed five-card board and fixed four-card hole cards for every player.

The previous trainer recalculated a player's Omaha showdown rank at every terminal branch reached during CFR traversal.

The optimized trainer computes every player's exact Omaha showdown rank **once per sampled deal** and reuses those immutable ranks at all terminal nodes.

No poker abstraction is introduced and no evaluator semantics are changed.

## Equivalence gate

The A/B test runs cached and legacy trainers with:
- mode 4w;
- gross utility;
- seed 123;
- 2 iterations;
- 500 deals/iteration.

PASS requires:
- identical regret arrays;
- identical average-strategy arrays;
- identical visit arrays;
- identical solver-array SHA256.

This is stronger than an EV-tolerance check: the optimization must preserve the exact CFR trajectory.

## Performance gate

Report cached-vs-legacy deals/s and speedup.

After A/B, immediately run one 500-deal post-optimization profile. That profile determines the **next** bottleneck.

Runner:
`tools/run_om6_rank_cache_gate.sh`

Outputs:
- `runs/om6_rank_cache_ab_4w_i2_d500_seed123.json`
- `runs/om6_profile_post_rank_cache_4w_d500_seed123.json`

## Stop rule

Do not parallelize and do not start convergence training yet. One A/B plus one post-optimization profile is sufficient for this gate.
