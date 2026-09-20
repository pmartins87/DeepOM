# DeepOM Status

Reference date: 2026-09-20

Repository: `pmartins87/DeepOM`

## Gate summary

- OM0 Rules/economy: **PARTIAL PASS**
- OM1 PLO4 evaluator: **PASS**
- OM2 Equity/Jackpot: **PASS**
- OM3 AoF kernel: **PARTIAL PASS**
- OM4 State census: **PASS**
- OM5 Representation: **PASS**
- OM6 Solver engineering: **IN PROGRESS — LOCAL BENCHMARK GATE**
- OM7+: **BLOCKED**

## Validated foundation

Current CI covers:

- exhaustive 2,598,960 five-card evaluator;
- independent Treys differential: 5,000 cases / 0 mismatches;
- exact and sampled equity;
- exhaustive Royal Flush probability validation;
- 4w/3w/HU action tree and chip conservation;
- exact PLO4 state census;
- economy/promotion sensitivity;
- sparse CFR correctness;
- dense CFR indexing and checkpoint/resume equivalence.

## Exact state representation

- raw starting hands: 270,725;
- exact suit-isomorphic classes: 16,432;
- exact canonical infosets across current scenarios: **361,504**.

Decision: no strategic hand bucketing for v1.

## Economics

Development preset:
`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

- stack 5 BB;
- net base rake after RB35: 0.01625 BB;
- Jackpot fee: 0.025 BB;
- Fortune fee: 0.025 BB;
- inherited fixed fee: 0.06625 BB/player/hand;
- Jackpot award: 375 BB;
- provisional Fortune EV: 0.1040072480 BB/All-In.

Jackpot remains materially hand-dependent and is modeled inside terminal utility. Fortune remains sensitivity-controlled.

## OM6 implementation

Correctness oracle:
- `deepom/solver_proto.py`

Dense trainer:
- `deepom/dense_solver.py`

Implemented in dense trainer:
- NumPy arrays indexed by scenario × one of 16,432 exact PLO4 classes;
- external-sampling CFR+;
- linear averaging;
- gross/economic utility modes;
- deterministic seed;
- checkpoint/resume;
- exact RNG restoration;
- manifest;
- class-index SHA256;
- solver-array SHA256.

For 4w, dense core arrays are about **7.9 MiB**. Across all three modes the corresponding basic core is about **12.4 MiB**.

## Current engineering decision

Do **not** parallelize yet. First measure the dense trainer on target hardware. This separates:
- evaluator/traversal cost;
- economic-payoff cost;
- state/index cost.

The benchmark is deliberately finite:
- 4w;
- 2 iterations;
- 100 deals/iteration;
- seed 123;
- one economic run;
- one gross run.

Contract:
`docs/OM6_LOCAL_BENCHMARK_GATE_20260920.md`

One-command runner:
`tools/run_om6_local_benchmark.sh`

Expected output files:
- `runs/om6_dense_4w_econ_i2_d100_seed123.json`
- `runs/om6_dense_4w_gross_i2_d100_seed123.json`

## After the benchmark

Choose the next optimization based on measured evidence, then run a finite Fortune-sensitivity/cross-seed matrix. Only after that can OM0/OM3 be frozen and OM7 convergence training begin.

## Source of truth

- `README.md`
- `ROADMAP.md`
- `STATUS.md`
- `docs/PROJECT_CHARTER.md`
- `docs/RULES_ECONOMY.md`
- `docs/OM0_EVIDENCE.md`
- `docs/DEEPAOF_REUSE_PLAN.md`
- `docs/OM1_OM2_VALIDATION_20260920.md`
- `docs/OM4_CENSUS_20260920.md`
- `docs/OM5_REPRESENTATION_DECISION_20260920.md`
- `docs/ECONOMY_SENSITIVITY_20260920.md`
- `docs/OM6_SOLVER_PROTOTYPE_20260920.md`
- `docs/OM6_LOCAL_BENCHMARK_GATE_20260920.md`
