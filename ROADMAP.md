# DeepOM — Roadmap

Reference date: 2026-09-20

## Definition of done

DeepOM base v1 is complete when OpenHoldem can read the real frozen GGPoker AoF Omaha state, map it losslessly to a validated production policy, execute the correct ALL-IN/FOLD action, and the mathematical policy, packaged runtime and live scraper/action path have each passed explicit finite gates.

Population exploitation is a later layer and is **not** required to declare the base bot complete.

---

## OM0 — Target game, rules and economy

Status: **PARTIAL PASS — CORE PRODUCT FROZEN / EVIDENCE COMPLETION ACTIVE**

Frozen:

- GGPoker All-In or Fold Omaha cash;
- PLO4 / four hole cards;
- exactly 2 hole + 3 board cards at showdown;
- 5 BB default stack for the published Omaha AoF cash rows;
- ALL-IN/FOLD action set;
- project jackpot pool scenario = $750,000;
- project Fortune pool scenario = $75,000;
- project rakeback model = 35% of the base-rake component;
- stake-dependent economics represented by separate presets;
- development preset = $0.20/$0.40.

Still to close:

- live confirmation of maximum table size / 4w-3w-HU transitions;
- exact Fortune probability/tier calibration for the $75k pool;
- exact rakeback eligibility/PVI treatment if the intended 35% is not an effective rebate on base rake;
- any client-only jackpot/Fortune mechanics not exposed by the public rules;
- runtime/tablemap details.

### Gate OM0 PASS

A versioned rules/economy contract exists with evidence or an explicit project assumption for every EV-relevant rule. No unresolved item may be capable of changing the production strategy.

---

## OM1 — Independent Omaha evaluator

Status: **READY TO START; PRODUCTION GATE STILL DEPENDS ON OM0**

Requirements:

- exact Omaha semantics: exactly 2 hole + exactly 3 board cards;
- complete hand-ranking tests;
- Royal Flush jackpot-qualifier tests;
- board-only-hand false-positive tests;
- duplicate-card/deck-integrity checks;
- differential tests against at least one trusted independent implementation/reference;
- deterministic test vectors committed to the repo.

### Gate OM1 PASS

Evaluator passes the frozen corpus with zero mismatches.

---

## OM2 — Equity engine

Status: **BLOCKED BY OM1**

Build and validate:

- exact river/turn enumeration where tractable;
- preflop Omaha equity sampling/exact subcases;
- multiway sampled modes with confidence reporting;
- collision-safe card removal;
- suit-isomorphic caching only if formal equivalence is preserved;
- reproducible RNG;
- jackpot trigger probability conditioned on the exact Omaha hole-card state.

### Gate OM2 PASS

Equity and jackpot-probability engines match independent reference results within exact equality or predefined statistical tolerance.

---

## OM3 — Deterministic AoF game kernel

Status: **BLOCKED BY OM1/OM2**

The public decision tree is much smaller than normal PLO because the game is AoF.

Implement and revalidate the DeepAoF structural tree:

- 4w, 3w and HU modes if confirmed live;
- FOLD or ALL-IN only;
- blinds and 5 BB effective stack;
- public action history;
- terminal pot/contribution accounting;
- split pots/ties;
- fixed stake-specific rake/jackpot/Fortune fees;
- rakeback;
- jackpot and Fortune EV.

### Gate OM3 PASS

Property tests conserve chips and every transition/payoff matches the frozen contract.

---

## OM4 — Exact Omaha state-space census

Status: **BLOCKED BY OM1**

Before choosing the solver representation:

- enumerate all C(52,4)=270,725 raw four-card starting combinations;
- derive suit-isomorphic canonical classes without strategic information loss;
- combine them with AoF public action histories;
- quantify exact infosets for 4w/3w/HU;
- benchmark memory, traversal cost and runtime lookup footprint.

### Decision gate

Do not import the 169-class Hold'em state model. Select exact representation or abstraction only after the Omaha census.

---

## OM5 — Abstraction decision

Status: **BLOCKED BY OM4**

Default preference: preserve exact Omaha information.

If exact solving is impractical, candidate abstractions must be benchmarked against finer/exact subgames. No abstraction is accepted merely because it is conventional.

### Gate OM5 PASS

Either exact representation is feasible and frozen, or an abstraction is accepted with measured error/loss and explicit stop criteria.

---

## OM6 — Solver prototype

Status: **BLOCKED BY OM5**

First candidate: adapt the proven DeepAoF CFR+ orchestration while replacing Hold'em-specific card/equity/payoff components.

Requirements:

- resumable checkpoints;
- deterministic manifests;
- stable RNG state;
- per-infoset visits/regrets/strategy data;
- scalable parallel benchmark;
- no production export until validation.

---

## OM7 — Base training and convergence

Status: **BLOCKED BY OM6**

Finite gates:

- cross-seed policy stability;
- regret / best-response diagnostics;
- EV confidence;
- policy-change trajectory by depth;
- explicit stop criterion.

Deeper training is launched only if convergence remains the measured bottleneck.

---

## OM8 — Production policy selection and freeze

Status: **BLOCKED BY OM7**

Freeze per economic preset:

- rules/economy version;
- solver/config hashes;
- policy hashes;
- exact state coverage;
- release manifest.

Never silently reuse a policy across stake presets whose fees or jackpot payout differ.

---

## OM9 — OpenHoldem state contract and runtime

Status: **BLOCKED BY OM8**

Build:

- GGPoker AoF Omaha tablemap/scrape contract;
- four-card hero hand extraction;
- player-count/position reconstruction;
- exact policy key;
- legal ALL-IN/FOLD transport;
- fail-closed mismatch behavior;
- complete decision logging.

### Gate OM9 PASS

Offline mathematical-policy -> packaged-runtime equivalence is exact for all supported states.

---

## OM10 — Live smoke and production gate

Status: **BLOCKED BY OM9**

Finite live validation:

- all four hero cards correct;
- correct player count and position;
- correct blinds/stack;
- correct previous ALL-IN/FOLD history;
- correct policy key;
- correct action;
- no stale hand/state.

Any invalid state/action blocks production and triggers rollback.

---

## OM11 — Opponent database

Status: **FUTURE**

Reuse DeepAoF architecture only after adapting it to Omaha hand/state semantics.

---

## OM12 — Exploit layer

Status: **FUTURE / SEPARATE FROM BASE**

Exploit policies never overwrite the frozen base and must fall back on weak/mismatched evidence.

---

## Current critical path

**Finish OM0 evidence in parallel with OM1 evaluator -> OM2 -> OM3 + OM4 -> OM5 -> OM6.**

No long solver run is justified yet.
