# DeepOM — Roadmap

Reference date: 2026-09-20

## Definition of done

DeepOM base v1 is complete when OpenHoldem can read the frozen GGPoker AoF Omaha state, map it losslessly to a validated policy, execute the correct ALL-IN/FOLD action, and the mathematical policy, packaged runtime and live scraper/action path have each passed finite gates.

---

## OM0 — Target game, rules and economy

Status: **PARTIAL PASS — ECONOMIC EVIDENCE COMPLETION ACTIVE**

Frozen:
- GGPoker AoF Omaha PLO4;
- exactly 2 hole + 3 board cards;
- 5 BB default stack;
- ALL-IN/FOLD;
- Jackpot pool $750,000;
- Fortune pool $75,000;
- RB modeling input 35%;
- development preset $0.20/$0.40.

Implemented:
- versioned economic preset;
- net base rake 0.01625 BB;
- inherited fixed-fee contract 0.06625 BB/player/hand;
- exact hand-dependent Omaha Jackpot EV;
- provisional Fortune EV 0.1040072480 BB/All-In;
- explicit promotion sensitivity multipliers.

Remaining:
- stronger Fortune evidence or policy-insensitivity proof;
- live 4w/3w/HU confirmation;
- RB/PVI interpretation;
- runtime/tablemap evidence.

**PASS criterion:** every strategy-relevant economic uncertainty is evidenced/frozen or bounded by a sensitivity test showing no material policy effect.

---

## OM1 — Independent Omaha evaluator

Status: **PASS**

Evidence:
- exact 2+3 evaluator;
- unit/rule corpus;
- exhaustive 2,598,960 five-card validation;
- independent Treys differential: 5,000 PLO4 HU comparisons, 0 mismatches.

Record: `docs/OM1_OM2_VALIDATION_20260920.md`.

---

## OM2 — Equity and Jackpot engine

Status: **PASS**

Implemented:
- exact tractable runouts;
- reproducible Monte Carlo;
- multiway sampling and confidence reporting;
- exact Royal Flush probability by PLO4 starting hand.

Record: `docs/OM1_OM2_VALIDATION_20260920.md`.

---

## OM3 — Deterministic AoF kernel

Status: **PARTIAL PASS**

Passed:
- 14 4w + 6 3w + 2 HU decision scenarios;
- transition legality;
- blinds/5 BB contributions;
- walks/showdowns/ties;
- gross chip conservation;
- economic payoff integration.

Remaining:
- OM0 economic freeze;
- live confirmation of table/player behavior.

---

## OM4 — Exact state-space census

Status: **PASS**

- raw PLO4 hands: 270,725;
- exact suit-isomorphic classes: 16,432;
- brute force == Burnside;
- canonical infosets:
  - 4w 230,048;
  - 3w 98,592;
  - HU 32,864;
  - total 361,504.

Record: `docs/OM4_CENSUS_20260920.md`.

---

## OM5 — Representation decision

Status: **PASS — EXACT REPRESENTATION**

No strategic bucketing for v1. Global suit relabeling is the only state reduction.

Record: `docs/OM5_REPRESENTATION_DECISION_20260920.md`.

---

## OM6 — Solver engineering

Status: **IN PROGRESS — PROFILING GATE**

Passed:
- sparse external-sampling CFR correctness oracle;
- CFR+ and linear averaging;
- exact PLO4 state keys;
- optional versioned economics;
- dense indexed NumPy trainer;
- full 16,432-class deterministic class index + SHA256;
- compact per-mode dense arrays;
- checkpoint/resume;
- exact RNG restoration;
- run manifest;
- class-index and solver-array content hashes;
- checkpoint/resume equivalence regression.

Target-hardware benchmark: **PASS**.

Measured on Ryzen 9 / WSL2:
- economic: 226.307 deals/s;
- gross: 229.477 deals/s;
- economic slowdown: ~1.38%.

Decision:
- economic/promotion arithmetic is not the material bottleneck;
- next finite gate is profiling the shared evaluator/canonicalization/CFR path;
- do not parallelize or launch long training until attribution exists.

Profiling harness: **IMPLEMENTED / TARGET RESULT PENDING**.

Frozen profile:
- 4w gross;
- 500 deals;
- seed 123;
- one-time class-index build excluded from profiled region.

Runner: `tools/run_om6_profile.sh`.

Remaining OM6 gate:
- target-hardware profiling result;
- one selected throughput optimization;
- cross-seed economic sensitivity mini-runs;
- production policy export format.

Benchmark record: `docs/OM6_TARGET_BENCHMARK_RESULT_20260920.md`.

---

## OM7 — Base training and convergence

Status: **BLOCKED BY OM6 + OM0/OM3**

Finite gates:
- cross-seed policy stability;
- regret / best-response diagnostics;
- EV confidence;
- policy-change trajectory;
- explicit stop criterion.

No deep training before OM6 and economics are ready.

---

## OM8 — Production policy freeze

Status: **BLOCKED BY OM7**

Freeze rules/economy/config/policy hashes and exact state coverage.

---

## OM9 — OpenHoldem runtime

Status: **BLOCKED BY OM8**

Four-card scraping, state reconstruction, exact lookup, fail-closed action transport and logging.

---

## OM10 — Live smoke / production gate

Status: **BLOCKED BY OM9**

Any invalid state/action mapping blocks production.

---

## OM11 — Opponent database

Status: **FUTURE**

---

## OM12 — Exploit layer

Status: **FUTURE / SEPARATE FROM BASE**

---

## Current critical path

**OM6 profiling -> one measured throughput optimization -> short sensitivity/cross-seed runs -> OM0/OM3 freeze -> OM7.**

Do not start a long solve before this sequence passes.
