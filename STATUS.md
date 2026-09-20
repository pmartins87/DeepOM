# DeepOM Status

Reference date: 2026-09-20

## Current position

Repository: `pmartins87/DeepOM`

Current critical gate: **OM6 dense trainer + OM0/OM3 economic freeze**.

## Gate summary

- OM0 Rules/economy: **PARTIAL PASS**
- OM1 PLO4 evaluator: **PASS**
- OM2 Equity/Jackpot engine: **PASS**
- OM3 AoF kernel: **PARTIAL PASS**
- OM4 Exact state census: **PASS**
- OM5 Representation decision: **PASS**
- OM6 Solver prototype: **IN PROGRESS**
- OM7+ production training/runtime: **BLOCKED**

## Validated mathematical foundation

CI run on 2026-09-20 passed the complete current suite, including:

- independent Treys differential: **5,000 cases, 0 mismatches**;
- exhaustive five-card evaluator: **2,598,960 hands PASS**;
- exhaustive Jackpot probability validator: PASS;
- exact PLO4 state census: PASS;
- economy sensitivity census: PASS;
- unit/regression suite: PASS.

### State space

- raw PLO4 starting hands: **270,725**;
- exact global-suit-isomorphic classes: **16,432**;
- 4w decision scenarios: 14 -> **230,048 infosets**;
- 3w decision scenarios: 6 -> **98,592 infosets**;
- HU decision scenarios: 2 -> **32,864 infosets**;
- total exact canonical preflop infosets: **361,504**.

Decision: **no strategic hand bucketing for v1**.

## Development economic preset

`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

- stack: 5 BB;
- base rake: 0.025 BB;
- RB: 35% on base rake in the current project model;
- net base rake: 0.01625 BB;
- Jackpot fee: 0.025 BB;
- Fortune fee: 0.025 BB;
- fixed fee: **0.06625 BB per dealt player per hand** under the inherited DeepAoF fee-placement model;
- Jackpot pool: $750,000;
- Jackpot award at this preset: 375 BB;
- Fortune pool: $75,000;
- provisional inherited/scaled Fortune EV: **0.1040072480 BB per All-In**.

### Jackpot census

Among 270,725 raw PLO4 hands:

- 228,085 have 0 Royal-eligible suits;
- 42,040 have 1;
- 600 have 2;
- **42,640 / 270,725 = 15.7503%** have at least one Royal-eligible suit.

At a 375 BB jackpot:
- one-suit expected Jackpot credit at showdown = **0.2168131360 BB**;
- two-suit = **0.4336262720 BB**;
- random-hand mean = **0.0346292363 BB per showdown All-In**.

Jackpot is therefore strategically material and remains inside the solver payoff.

## Fortune uncertainty

The prior DeepAoF model is now normalized rather than copied blindly. Its reference calibration gives 0.10715968 BB/All-In at a $77,273.23 pool; pool-only scaling to $75,000 gives 0.1040072480 BB/All-In.

This remains provisional because current public Fortune material does not expose the complete blind-specific payout/probability table. The solver now accepts explicit Fortune multipliers so policy sensitivity can be measured before production freeze.

## Solver

`deepom/solver_proto.py` is the correctness oracle:

- external sampling;
- CFR+;
- linear averaging;
- exact PLO4 canonical key;
- 4w/3w/HU;
- gross or economic payoffs;
- deterministic seeds;
- explicit Fortune/Jackpot sensitivity.

It is not the intended production trainer.

## Immediate next work

1. build dense indexed class/scenario tables;
2. add checkpoint/resume and run manifests/hashes;
3. parallelize traversal;
4. run a small benchmark and Fortune sensitivity matrix;
5. use those results to finish OM0/OM3;
6. only then start OM7 convergence training.

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
