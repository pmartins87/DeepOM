# DeepOM

DeepOM is the **GGPoker All-In or Fold Omaha** branch of the DeepPoker project: a solver-driven base strategy, validation pipeline, opponent-modeling layer, and OpenHoldem runtime.

The project deliberately reuses the mature **DeepAoF/DeepKK engineering architecture** where it is game-independent, but it does **not** reuse Hold'em hand classes, equities or solved policies. Omaha changes the private-card state space, evaluator, jackpot qualification and equity engine.

## Frozen product direction

Initial target:

- room/product: **GGPoker All-In or Fold Omaha cash**;
- variant: **4-card Omaha (PLO4)**;
- action set: **ALL-IN or FOLD**;
- default Omaha stack: **5 BB**;
- board/deck: standard 52-card deck;
- final Omaha hand: exactly **2 hole cards + 3 board cards**;
- AoF Omaha jackpot qualifier: **Royal Flush using 2 of the 4 hole cards + 3 board cards**;
- project jackpot pool scenario: **$750,000**;
- project All-In Fortune pool scenario: **$75,000**;
- project rakeback model: **35% rebate on the base rake component** unless later evidence requires a different eligibility/PVI treatment.

The first engineering/calibration preset is **$0.20/$0.40 Omaha**.

## Mathematical state

DeepOM now has:

- an independent PLO4 evaluator with exact 2+3 semantics;
- exact/sampled Omaha equity;
- exact Omaha Royal Flush jackpot probability;
- the revalidated DeepAoF 4w/3w/HU All-In/Fold public tree;
- an exact PLO4 suit-isomorphism canonicalizer;
- **270,725 raw PLO4 hands -> 16,432 exact canonical classes**;
- **361,504 canonical preflop infosets** across 14 4w + 6 3w + 2 HU decision scenarios;
- an external-sampling CFR+/linear-averaging correctness prototype;
- a versioned economic payoff model with RB35, Jackpot $750k and sensitivity-controlled Fortune $75k.

The exact state census makes strategic bucketing unnecessary for v1. The selected representation preserves all ranks and suit structure and removes only global suit-label symmetry.

## Validation

CI validates:

- all **2,598,960** five-card hands against exact known category frequencies;
- deterministic PLO4 showdown comparison against independent **Treys** on 5,000 random HU boards with zero mismatches;
- exact/sampled equity invariants;
- exhaustive Omaha Jackpot probability checks;
- action-tree and chip-conservation properties;
- exact state-space census via both brute force and Burnside's lemma;
- economy/promotion sensitivity census;
- deterministic CFR prototype regressions.

## DeepAoF reuse policy

Reusable after review:

- 4w/3w/HU AoF public action-history structure;
- CFR+/training orchestration patterns;
- run manifests, hashes and cross-seed audits;
- opponent aliases/statistics architecture;
- base-versus-exploit separation;
- runtime fail-closed principles.

Not reusable as poker math:

- 169 Hold'em hand classes;
- Hold'em equity tables;
- Hold'em jackpot grouping/probability code;
- Hold'em ranges/policies;
- two-card evaluator assumptions.

See [docs/DEEPAOF_REUSE_PLAN.md](docs/DEEPAOF_REUSE_PLAN.md).

## Current state

- **OM0:** PARTIAL PASS — core product/economy preset exists; Fortune calibration, live player-count confirmation and RB/PVI evidence remain open.
- **OM1:** PASS.
- **OM2:** PASS.
- **OM3:** PARTIAL PASS — mechanical tree/payoffs validated and economics implemented; production economic semantics are not fully frozen.
- **OM4:** PASS.
- **OM5:** PASS — exact 16,432-class representation selected.
- **OM6:** IN PROGRESS — correctness prototype exists; dense indexed/parallel trainer, checkpoints and manifests remain.

No long production training run is justified until OM0/OM3 economic uncertainty is sensitivity-tested and the OM6 dense trainer is validated.

See [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/RULES_ECONOMY.md](docs/RULES_ECONOMY.md), and the dated validation records under [docs/](docs/).
