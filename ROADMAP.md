# DeepOM — Roadmap

Reference date: 2026-09-20

## Definition of done

DeepOM base v1 is complete when OpenHoldem can read the real frozen Omaha game state, map it losslessly to a validated production policy, execute the correct legal action, and the mathematical policy, packaged runtime and live scraper/action path have each passed explicit finite gates.

Population exploitation is a later layer and is **not** required to declare the base bot complete.

---

## OM0 — Target game, rules and economy

Status: **ACTIVE**

Freeze before solver design:

- exact variant: PLO4, PLO5 or another Omaha format;
- table size(s);
- cash/tournament/game mode;
- blinds, ante and stack model;
- legal bet sizes and pot-limit semantics;
- all-in, side-pot and split-pot behavior;
- run-it-twice / insurance / jackpot features if they affect EV;
- gross rake and cap by player count/stake;
- rakeback/PVI assumptions;
- target poker room and OpenHoldem runtime environment.

### Gate OM0 PASS

A versioned rules/economy contract exists with primary evidence for every EV-relevant rule and no unresolved item capable of changing optimal strategy.

---

## OM1 — Independent Omaha evaluator

Status: **NOT STARTED**

Requirements:

- exact Omaha hand semantics: exactly 2 hole + exactly 3 board cards;
- complete hand ranking tests;
- board-only hand false-positive tests;
- duplicate-card/deck-integrity checks;
- differential tests against at least one trusted independent implementation/reference;
- deterministic test vectors committed to the repo.

### Gate OM1 PASS

Evaluator passes the frozen corpus with zero mismatches.

---

## OM2 — Equity engine

Status: **NOT STARTED**

Build and validate:

- HU exact river/turn enumeration where tractable;
- multiway sampled/exact modes as justified;
- collision-safe card removal;
- suit-isomorphic caching only if equivalence is formally preserved;
- reproducible RNG for sampled paths;
- confidence/error reporting.

### Gate OM2 PASS

Equity engine matches independent reference results within exact equality or predefined statistical tolerance.

---

## OM3 — Deterministic game kernel

Status: **NOT STARTED**

Implement:

- positions and player counts;
- legal pot-limit action bounds;
- check/call/fold/bet/raise/all-in transitions;
- contribution accounting;
- side pots;
- rake/cap application at the correct terminal point;
- terminal payouts including split pots.

### Gate OM3 PASS

Property tests conserve chips and every legal/terminal transition matches the frozen rules contract.

---

## OM4 — Exact state-space census

Status: **NOT STARTED**

Before choosing a solver architecture:

- enumerate public action histories;
- enumerate/canonicalize hole-board card states;
- quantify exact infosets/nodes per street/player count;
- benchmark memory, traversal cost and runtime lookup footprint;
- identify where exact solving is feasible and where abstraction may be unavoidable.

### Decision gate

**Do not copy DeepKK or DeepPot's state model.** The solver architecture is selected only after the Omaha state-space census.

---

## OM5 — Abstraction decision

Status: **BLOCKED BY OM4**

Default preference: preserve exact information.

If exact solving is impractical, candidate abstractions must be benchmarked against finer/exact subgames. No abstraction is accepted merely because it is conventional.

### Gate OM5 PASS

Either:

- exact representation is feasible and frozen; or
- an abstraction is accepted with measured error/loss and explicit stop criteria.

---

## OM6 — Solver prototype

Status: **BLOCKED BY OM5**

Candidate algorithms may include CFR-family methods and other scalable equilibrium solvers. The choice is evidence-driven.

Requirements:

- deterministic manifests;
- resumable checkpoints;
- stable RNG state;
- per-infoset visits/regrets/strategy data;
- scalable parallelism benchmark on available hardware;
- no production action export yet.

---

## OM7 — Base training and convergence

Status: **BLOCKED BY OM6**

Use finite gates rather than open-ended training:

- cross-seed/action stability;
- regret/exploitability or best-response diagnostics appropriate to the solved game;
- EV confidence;
- policy-change trajectory by depth;
- explicit stop criterion.

A deeper run is launched only if the preceding gate identifies convergence as the current bottleneck.

---

## OM8 — Production policy selection and freeze

Status: **BLOCKED BY OM7**

Compare candidate representations/actions without inventing a winner in advance.

Freeze:

- strategy version;
- economy/rules version;
- solver/config hashes;
- policy hashes;
- exact state coverage;
- release manifest.

The frozen base is immutable.

---

## OM9 — OpenHoldem state contract and runtime

Status: **BLOCKED BY OM8**

Build:

- tablemap/scrape contract;
- state reconstruction;
- exact policy key;
- runtime lookup;
- legal action adapter;
- fail-closed behavior on mismatch;
- logging sufficient to reproduce every live decision.

### Gate OM9 PASS

Offline mathematical-policy -> packaged-runtime equivalence is exact for all supported states.

---

## OM10 — Live smoke and production gate

Status: **BLOCKED BY OM9**

Finite live validation:

- correct cards/player count/position;
- correct pot and amount-to-call;
- correct legal pot-limit sizing;
- correct policy key;
- correct action transport;
- no stale state across hands/streets.

Any invalid state/action blocks production and triggers rollback.

---

## OM11 — Opponent database

Status: **FUTURE**

Only after base/runtime reliability:

- structured action events;
- player aliases;
- context-conditioned frequencies;
- showdown/revealed-card evidence;
- pool priors;
- sample confidence and shrinkage.

---

## OM12 — Exploit layer

Status: **FUTURE / SEPARATE FROM BASE**

Start only if measured opponent/population deviations are stable and material.

Principles:

- exploit policy never overwrites the frozen base;
- exact context/model match required;
- weak evidence falls back to base;
- exploit EV is validated against held-out or otherwise independent evidence where possible.

---

## Current critical path

**OM0 -> OM1 -> OM2 -> OM3 -> OM4 -> OM5 -> OM6.**

The immediate project task is to freeze the target Omaha game/economy. No expensive solver run is justified before that gate closes.
