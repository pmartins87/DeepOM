# DeepOM — Roadmap

Reference date: 2026-09-20

## Definition of done

DeepOM base v1 is complete when OpenHoldem can read the real frozen GGPoker AoF Omaha state, map it losslessly to a validated production policy, execute the correct ALL-IN/FOLD action, and the mathematical policy, packaged runtime and live scraper/action path have each passed explicit finite gates.

Population exploitation is a later layer and is **not** required to declare the base bot complete.

---

## OM0 — Target game, rules and economy

Status: **PARTIAL PASS — CORE PRODUCT FROZEN / ECONOMIC EVIDENCE COMPLETION ACTIVE**

Frozen:
- GGPoker All-In or Fold Omaha cash;
- PLO4 / four hole cards;
- exactly 2 hole + 3 board cards;
- 5 BB default stack;
- ALL-IN/FOLD action set;
- Jackpot pool scenario = $750,000;
- Fortune pool scenario = $75,000;
- rakeback modeling input = 35% of base rake;
- development preset = $0.20/$0.40.

Implemented:
- versioned `EconomicPreset`;
- net base rake 0.01625 BB;
- fixed deterministic fee 0.06625 BB/player/hand under the inherited DeepAoF fee-placement contract;
- exact Omaha Jackpot EV by starting hand;
- provisional Fortune EV = 0.1040072480 BB per All-In after pool-only scaling;
- explicit Fortune/Jackpot sensitivity multipliers.

Still to close:
- stronger Fortune tier/probability evidence or a strategy-insensitivity proof;
- live maximum table size / 4w-3w-HU confirmation;
- 35% rakeback/PVI eligibility interpretation;
- runtime/tablemap evidence.

### Gate OM0 PASS

Every EV-relevant rule must be either evidenced and frozen or proven strategically immaterial over a predefined sensitivity envelope.

---

## OM1 — Independent Omaha evaluator

Status: **PASS**

Evidence:
- exact 2-hole + 3-board evaluator;
- complete category/tiebreak tests;
- board-only and wrong-hole-count false-positive tests;
- duplicate-card integrity tests;
- exhaustive 2,598,960 five-card frequency validation;
- independent Treys differential: 5,000 deterministic random HU PLO4 showdowns, 0 mismatches.

Record: `docs/OM1_OM2_VALIDATION_20260920.md`.

---

## OM2 — Equity and Jackpot engine

Status: **PASS**

Implemented:
- exact tractable runout enumeration;
- reproducible known-hand Monte Carlo;
- reproducible multiway random-opponent Monte Carlo;
- confidence reporting;
- exact Royal Flush probability conditioned on PLO4 starting hand.

Validation:
- sampled vs exact fixed subgames;
- exhaustive 1,712,304-board checks for representative jackpot classes.

Record: `docs/OM1_OM2_VALIDATION_20260920.md`.

---

## OM3 — Deterministic AoF game kernel

Status: **PARTIAL PASS**

Passed:
- 4w: 14 decision scenarios;
- 3w: 6;
- HU: 2;
- fold/all-in transition legality;
- blinds/5 BB contribution accounting;
- walks, showdown, ties/splits;
- gross chip conservation;
- economic payoff module integrated.

Remaining:
- final economic semantic freeze from OM0;
- live confirmation that the inherited 4w/3w/HU table behavior matches GGPoker AoF Omaha.

---

## OM4 — Exact Omaha state-space census

Status: **PASS**

Results:
- 270,725 raw four-card hands;
- 16,432 exact suit-isomorphic classes;
- brute force == Burnside;
- exact infosets:
  - 4w 230,048;
  - 3w 98,592;
  - HU 32,864;
  - total 361,504.

Record: `docs/OM4_CENSUS_20260920.md`.

---

## OM5 — Representation decision

Status: **PASS — EXACT REPRESENTATION SELECTED**

No strategic hand bucketing for v1.

Global suit relabeling is the only equivalence reduction. Core dense regret/average/visit arrays are about 12.4 MiB before metadata/alignment.

Reversal requires a measured downstream bottleneck.

Record: `docs/OM5_REPRESENTATION_DECISION_20260920.md`.

---

## OM6 — Solver prototype / production trainer

Status: **IN PROGRESS**

Passed:
- sparse external-sampling CFR correctness prototype;
- CFR+ clipping;
- linear averaging;
- exact PLO4 canonical keys;
- deterministic seeds;
- optional versioned economics and sensitivity multipliers;
- regression tests.

Remaining OM6 gate:
- dense indexed arrays;
- checkpoint/resume;
- deterministic run manifest and hashes;
- multiprocessing/parallel traversal;
- benchmark on Ryzen 9;
- cross-seed economic sensitivity mini-runs;
- export format.

Record: `docs/OM6_SOLVER_PROTOTYPE_20260920.md`.

---

## OM7 — Base training and convergence

Status: **BLOCKED BY OM6 + OM0 ECONOMIC FREEZE**

Finite gates:
- cross-seed policy stability;
- regret / best-response diagnostics;
- EV confidence;
- policy-change trajectory;
- explicit stop criterion.

No deep training before the mini-run gates pass.

---

## OM8 — Production policy selection and freeze

Status: **BLOCKED BY OM7**

Freeze per economic preset:
- rules/economy version;
- solver/config hashes;
- policy hashes;
- exact state coverage;
- release manifest.

---

## OM9 — OpenHoldem state contract and runtime

Status: **BLOCKED BY OM8**

Build:
- GGPoker AoF Omaha tablemap/scrape contract;
- four-card hero extraction;
- player-count/position reconstruction;
- exact policy key;
- ALL-IN/FOLD action transport;
- fail-closed mismatch behavior;
- complete decision logging.

---

## OM10 — Live smoke and production gate

Status: **BLOCKED BY OM9**

Any invalid card/state/action mapping blocks production and triggers rollback.

---

## OM11 — Opponent database

Status: **FUTURE**

Reuse DeepAoF architecture only after adapting statistics to Omaha state semantics.

---

## OM12 — Exploit layer

Status: **FUTURE / SEPARATE FROM BASE**

Exploit policies never overwrite the frozen base.

---

## Current critical path

**OM6 dense indexed trainer -> short benchmark/sensitivity runs -> finish OM0/OM3 economic freeze -> OM7 convergence.**

The next run must be a small engineering benchmark, not a long production solve.
