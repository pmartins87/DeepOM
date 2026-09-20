# DeepAoF -> DeepOM Reuse Plan

Reference date: 2026-09-20
Upstream reference: `pmartins87/DeepAoF`

## Goal

Reuse mature AoF engineering without importing Hold'em mathematics into Omaha.

## Reuse directly after code review

### Public game tree

DeepAoF already represents 4w/3w/HU sequential All-In/Fold histories. The same public history concept is expected to remain valid for AoF Omaha once live player-count behavior is confirmed.

### Solver orchestration

Reuse patterns for:

- CFR+ / linear averaging;
- batched chance sampling;
- multi-process workers;
- manifests;
- seeds;
- cross-seed policy audits;
- EV confidence;
- immutable run outputs.

### Operational architecture

Reuse patterns for:

- base policy as universal fallback;
- exploit policy as separate overlay;
- exact context matching;
- opponent alias/stat database;
- safe rollback;
- fail-closed DLL behavior;
- run/version hashing.

## Reuse only after adaptation

### Economic model

The old generator separates:

- base rake;
- jackpot fee;
- Fortune fee;
- jackpot EV;
- Fortune EV.

Keep that decomposition, but replace parameter values and jackpot qualification for Omaha.

### State reconstruction

Action chronology can be reused conceptually. Card scraping and policy keys must expand from two hero cards to four.

## Must NOT be reused

- 169 Hold'em hand classes;
- 1,326-combo weighting assumptions;
- Hold'em hand evaluator;
- Hold'em preflop equity tables;
- Hold'em `jp_group`;
- Hold'em jackpot trigger probabilities;
- DeepKK ranges/actions;
- HU/VS1/multiway trained policies from Hold'em.

## Omaha replacements

- raw four-card space: C(52,4)=270,725 hands;
- new suit-isomorphic canonicalizer;
- exact 2-hole + 3-board evaluator;
- Omaha preflop/multiway equity engine;
- Royal-Flush jackpot probability engine;
- new strategy-key schema.

## First implementation rule

Do not fork the old 80k-line solver and edit until it works.

Instead:

1. isolate the game-independent CFR/action-tree components;
2. build and test the Omaha evaluator independently;
3. build the Omaha chance/equity module;
4. run a state-space census;
5. only then assemble the DeepOM solver.

This keeps cross-game assumptions auditable and makes differential testing possible.
