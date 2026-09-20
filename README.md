# DeepOM

DeepOM is the **GGPoker All-In or Fold Omaha** branch of the DeepPoker project: a solver-driven base strategy, validation pipeline, opponent-modeling layer, and OpenHoldem runtime.

The project deliberately reuses the mature **DeepAoF/DeepKK engineering architecture** where it is game-independent, but it does **not** reuse Hold'em hand classes, equities or solved policies. Omaha changes the private-card state space, evaluator, jackpot qualification and equity engine.

## Frozen product direction

Initial target:

- room/product: **GGPoker All-In or Fold Omaha cash**;
- variant: **4-card Omaha (PLO4)**;
- action set: **ALL-IN or FOLD**;
- default Omaha stack: **5 BB** according to the Omaha rows in GGPoker's current AoF table;
- ante: none identified in the published AoF cash table;
- board/deck: standard 52-card deck;
- final Omaha hand: exactly **2 hole cards + 3 board cards**;
- AoF Omaha jackpot qualifier: **Royal Flush using 2 of the 4 hole cards + 3 board cards**;
- project jackpot pool scenario: **$750,000**;
- project All-In Fortune pool scenario: **$75,000**;
- project rakeback model: **35% rebate on the base rake component** unless later evidence requires a different eligibility/PVI treatment.

GGPoker publishes stake-dependent AoF Omaha rake, jackpot fee, Fortune fee and jackpot payout percentages, so DeepOM will use **economic presets per stake** rather than pretending one policy is automatically correct for every blind level.

The first engineering/calibration preset is **$0.20/$0.40 Omaha** because the official table gives a clean 5 BB buy-in and equal 0.025 BB rake / jackpot / Fortune fees. This is a development reference, not a claim that every stake has the same economics.

## Project objective

Build a mathematically defensible AoF Omaha bot whose production strategy can be reproduced, validated, packaged and executed by OpenHoldem with fail-closed behavior.

## Core architecture

1. **Rules/economy evidence gate** — freeze the GGPoker AoF Omaha rules and stake preset.
2. **Independent Omaha evaluator** — enforce exactly 2 hole + exactly 3 board cards.
3. **Equity engine** — exact/sampled Omaha equity with collision-safe card removal.
4. **Deterministic AoF game kernel** — 4w/3w/HU action histories inherited structurally from DeepAoF, revalidated for Omaha.
5. **Exact state-space census** — count Omaha private-card/canonical states before choosing abstraction.
6. **Base solver** — equilibrium-oriented strategy for a frozen economic preset.
7. **Validation gates** — determinism, cross-seed stability, BR/regret/EV diagnostics, manifests and hashes.
8. **Production freeze** — immutable base policy.
9. **OpenHoldem runtime** — exact lookup and action transport; mismatch => safe fallback.
10. **Opponent model + exploit layer** — later and separate from the frozen base.

## DeepAoF reuse policy

Reusable after review:

- 4w/3w/2w AoF public action-history structure;
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

Current gate: **OM0 — PARTIALLY FROZEN / EVIDENCE COMPLETION**.

The game variant and main economic scenario are now fixed. Remaining OM0 work is to finish the evidence contract for Fortune calibration, live player-count/table-state details and runtime-specific items before any production training.

See [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/RULES_ECONOMY.md](docs/RULES_ECONOMY.md), and [docs/OM0_EVIDENCE.md](docs/OM0_EVIDENCE.md).
