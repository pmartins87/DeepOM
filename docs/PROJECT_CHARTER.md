# DeepOM — Project Charter

Reference date: 2026-09-20

## Mission

Create a reproducible, solver-driven Omaha strategy and OpenHoldem runtime that can be audited from frozen game rules all the way to a live action.

## Scope rule

DeepOM is not "DeepKK with four cards" and not "DeepPot with an Omaha evaluator". Reuse infrastructure only where equivalence is demonstrated. Game logic, evaluator semantics, equity, canonicalization and solver state are Omaha-specific until proven otherwise.

## Decision hierarchy

1. Verified game rules/economy.
2. Mathematical correctness.
3. Reproducibility and auditability.
4. Runtime correctness.
5. Computational efficiency.
6. Exploit sophistication.

A faster method that changes the game or loses strategically material information is not an acceptable optimization.

## Source-of-truth policy

GitHub is an active project record, not an archive.

When the project changes:

- update `STATUS.md`;
- update the affected gate in `ROADMAP.md`;
- update the rules/economy contract if economics changed;
- add a decision record when an architectural choice is frozen;
- preserve superseded production artifacts by version/hash instead of silently overwriting them.

## Base vs exploit

The production base is a frozen mathematical strategy for a frozen game/economy.

Exploit logic:

- is optional;
- is versioned independently;
- must identify the relevant opponent/context;
- must satisfy minimum evidence criteria;
- must fall back to the base on missing/weak/mismatched evidence.

## Experiment policy

Every material experiment must state before execution:

- hypothesis/question;
- candidate methods;
- dataset/game configuration;
- primary metric;
- gate/threshold;
- what result changes the decision;
- stop condition.

This prevents both endless testing and premature optimization.

## Safety / rollback

Live deployment must be reversible. A new runtime/policy is not production merely because it loads. It must pass offline equivalence first and a finite live smoke gate second.
