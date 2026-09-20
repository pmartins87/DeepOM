# DeepOM Status

Reference date: 2026-09-20

## Current gate

**OM0 — TARGET GAME / RULES / ECONOMY FREEZE: ACTIVE**

Repository: `pmartins87/DeepOM`.

The project has been initialized, but no poker-economy assumptions and no solver architecture have been frozen yet.

## What is already decided

- DeepOM will use the same engineering discipline that proved useful in DeepKK/DeepPot: explicit gates, reproducible runs, immutable production freezes, exact runtime equivalence checks and safe fallback behavior.
- Omaha requires a new evaluator, equity engine and state-space analysis.
- The Omaha rule that the final five-card hand uses exactly 2 hole cards and exactly 3 board cards is a non-negotiable evaluator invariant.
- Base strategy and opponent exploitation will remain separate.
- No expensive training begins before rules/economy and state representation are frozen.

## Deliberately unresolved

- PLO4 vs PLO5 (or another Omaha variant);
- table size(s);
- stack/blind/ante model;
- target stakes;
- rake/cap;
- rakeback/PVI model;
- KKPoker-specific optional mechanics;
- whether the first solver covers preflop only, postflop only or full game;
- exact vs abstract card/state representation;
- solver family;
- production action representation.

These are unresolved by design. Freezing them without evidence would create technical debt and potentially invalidate training.

## Current source of truth

- `README.md` — project identity and architecture.
- `ROADMAP.md` — gates and stopping criteria.
- `STATUS.md` — current state and next action.
- `docs/PROJECT_CHARTER.md` — project boundaries and decision rules.
- `docs/RULES_ECONOMY.md` — versioned rules/economy contract; currently UNFROZEN.

These files must be reviewed and updated whenever a gate closes or a structural decision changes.

## Immediate next action

Close OM0. Obtain/verify the exact first target game and all EV-relevant economics before implementing the evaluator/solver stack.
