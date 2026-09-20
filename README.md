# DeepOM

DeepOM is the Omaha branch of the DeepPoker project: a solver-driven strategy, validation pipeline, opponent-modeling layer, and OpenHoldem runtime for Omaha.

The project inherits engineering principles from DeepKK and DeepPot, but **does not inherit their game model**. Omaha changes the card state space, equity calculation, hand evaluation and strategic tree. In particular, any implementation must enforce Omaha hand construction rules exactly: the final hand uses exactly 2 hole cards and exactly 3 board cards.

## Project objective

Build a mathematically defensible Omaha bot whose production strategy can be reproduced, validated, packaged and executed by OpenHoldem with a fail-closed runtime.

The first release target is deliberately **not frozen yet**. Before solver work begins, OM0 must freeze the real game variant and economy: PLO4/PLO5, table size, stack/blinds/ante, rake/cap, rakeback assumptions, allowed bet sizing, run-it-twice behavior if relevant, and the exact KKPoker/OpenHoldem environment.

## Core architecture

1. **Rules/economy evidence gate** — freeze the exact Omaha product and live economics.
2. **Deterministic game kernel** — legal actions, betting tree, terminal payouts and side-pot logic.
3. **Omaha evaluator/equity engine** — exact 2-from-hole + 3-from-board semantics, tested independently.
4. **Canonical state representation** — suit-isomorphism/canonicalization with zero strategic information loss.
5. **Base solver** — equilibrium-oriented strategy for the frozen target game.
6. **Validation gates** — determinism, cross-seed stability, exploitability/regret/BR diagnostics, EV confidence and reproducible manifests.
7. **Production freeze** — immutable base policy with hashes and release manifest.
8. **OpenHoldem runtime** — exact lookup and action transport; unknown/mismatched state falls back safely.
9. **Opponent data/modeling** — only after the base strategy/runtime are reliable.
10. **Exploit layer** — separate from the immutable base and activated only with sufficient evidence.

## Engineering principles

- No solver before the game/economy contract is frozen.
- No strategic abstraction merely to make the problem fit memory/time unless an explicit abstraction gate proves the loss is acceptable.
- Base strategy and exploit strategy remain separate.
- Unknown or inconsistent state never maps to a "nearby" strategy by guess.
- Every long run must be resumable and emit configs, manifests, hashes and validation artifacts.
- Production policies are immutable once published; new economics or game rules create a new version.
- GitHub documents are part of the source of truth and must be updated as the project evolves.

## Current state

Repository initialized on 2026-09-20.

Current gate: **OM0 — TARGET GAME / RULES / ECONOMY FREEZE**.

No solver architecture, abstraction, target stack, rake model, PLO4/PLO5 choice or production strategy is considered frozen yet.

See [ROADMAP.md](ROADMAP.md), [STATUS.md](STATUS.md), [docs/PROJECT_CHARTER.md](docs/PROJECT_CHARTER.md), and [docs/RULES_ECONOMY.md](docs/RULES_ECONOMY.md).
