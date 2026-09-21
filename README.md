# DeepOM

DeepOM is the **GGPoker All-In or Fold Omaha** branch of the DeepPoker project: a solver-driven base strategy, validation pipeline, opponent-modeling layer, and OpenHoldem runtime.

The project deliberately reuses the mature **DeepAoF/DeepKK engineering architecture** where it is game-independent, but it does **not** reuse Hold'em hand classes, equities or solved policies.

## Frozen product direction

Initial target:

- room/product: **GGPoker All-In or Fold Omaha cash**;
- variant: **4-card Omaha (PLO4)**;
- action set: **ALL-IN or FOLD**;
- default Omaha stack: **5 BB**;
- final Omaha hand: exactly **2 hole cards + 3 board cards**;
- project Jackpot pool: **$750,000**;
- project All-In Fortune pool: **$75,000**;
- project rakeback input: **35% on the base-rake component** unless later evidence requires a different PVI/eligibility treatment;
- first development preset: **$0.20/$0.40**.

## Mathematical state

DeepOM now has:

- independent PLO4 evaluator with exact 2+3 semantics;
- exact/sampled Omaha equity;
- exact Royal Flush Jackpot probability by starting hand;
- revalidated 4w/3w/HU AoF public tree;
- exact suit-isomorphism canonicalizer;
- **270,725 raw PLO4 hands -> 16,432 exact canonical classes**;
- **361,504 canonical preflop infosets** across the current action trees;
- sparse CFR correctness oracle;
- **dense indexed NumPy CFR trainer**;
- versioned economic payoffs;
- exact checkpoint/resume with RNG restoration;
- deterministic manifests, class-index hash and solver-array hash;
- finite local benchmark harness.

The exact state census makes strategic bucketing unnecessary for v1. Only lossless global suit-label symmetry is removed.

## Validation

CI validates:

- all **2,598,960** five-card hands against exact known category frequencies;
- PLO4 differential against independent **Treys** on 5,000 deterministic random HU showdowns with zero mismatches;
- exact/sampled equity invariants;
- exhaustive Omaha Jackpot probability checks;
- AoF action-tree and chip-conservation properties;
- exact state-space census by brute force and Burnside's lemma;
- promotion/economy sensitivity;
- sparse CFR regressions;
- dense class indexing, dense-array shape/memory, regret direction and **checkpoint/resume exact equivalence**.

## Current gates

- **OM0:** PARTIAL PASS — economic evidence completion remains.
- **OM1:** PASS.
- **OM2:** PASS.
- **OM3:** PARTIAL PASS — mechanics pass; production economics/live behavior remain.
- **OM4:** PASS.
- **OM5:** PASS — exact 16,432-class representation selected.
- **OM6:** IN PROGRESS — function-level profiling found avoidable memmap/string-normalization overhead inside deal preparation; the next finite gate tests a resident five-card table plus one-time integer card preparation before moving to CFR traversal or multiprocessing.
- **OM7+:** BLOCKED.

No long production solve is justified yet.

See [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/RULES_ECONOMY.md](docs/RULES_ECONOMY.md), and the dated records under [docs/](docs/).
