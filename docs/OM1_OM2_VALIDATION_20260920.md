# OM1 / OM2 Validation Record — 2026-09-20

## OM1 evaluator

Implementation:
- `deepom/evaluator.py`
- exact Omaha rule: exactly 2 of 4 hole cards + exactly 3 board cards;
- duplicate-card protection;
- full 5-card ranking and tiebreak logic;
- AoF Omaha Royal Flush qualifier.

Validation:
- unit/rule corpus;
- exhaustive enumeration of all **2,598,960** five-card hands;
- exact category frequencies reproduced:
  - high card 1,302,540
  - one pair 1,098,240
  - two pair 123,552
  - three of a kind 54,912
  - straight 10,200
  - flush 5,108
  - full house 3,744
  - four of a kind 624
  - straight flush 40
- official-style Omaha edge cases are explicitly tested;
- independent differential gate against the external `treys==0.1.8` evaluator compares deterministic random PLO4 showdowns using an independent 2+3 enumeration.

Decision: **OM1 PASS** once the CI differential gate is green.

## OM2 equity / jackpot engine

Implementation:
- `deepom/equity.py`
- exact board-runout enumeration for tractable states;
- reproducible Monte Carlo for known opponent hands;
- reproducible multiway Monte Carlo versus random hands;
- confidence interval reporting;
- exact Royal Flush probability conditioned on the four-card PLO4 hand.

Jackpot formula:
- a suit is Royal-eligible iff the four-card hand contains **exactly two** T/J/Q/K/A cards of that suit;
- one qualifying suit requires the three missing royal cards on the board;
- full-board probability per qualifying suit:
  `C(45,2) / C(48,5) = 990 / 1,712,304 ≈ 0.000578168362627`.

Validation:
- Monte Carlo is compared to exact enumeration on fixed subgames;
- jackpot probability is checked by exhaustive enumeration of **1,712,304 boards** for representative 0-, 1- and 2-suit eligible hands;
- collision removal and deterministic RNG are covered by tests.

Decision: **OM2 PASS for the current mathematical engine**. Production EV remains conditional on the economic contract in OM0/OM3.
