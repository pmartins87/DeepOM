# OM0 Evidence — GGPoker AoF Omaha

Reference date: 2026-09-20

## Purpose

Record what is official, what is inherited from the previous DeepAoF project, and what is a project assumption.

## Official GGPoker evidence

### AoF product

Source:
https://ggpoker.com/poker-games/all-in-or-fold/

Supported by the page:

- AoF is available in Hold'em and Omaha;
- player decision is All-In or Fold;
- Omaha-specific stakes table exists;
- current Omaha rows use 5 BB default buy-ins;
- rake, jackpot fee, Fortune fee and jackpot payout vary by blind level.

### Omaha hand rule

Source:
https://legal.ggpoker.com/poker-games/omaha/

Supported:

- normal PLO deals four hole cards;
- a valid Omaha hand uses exactly two hole cards and three board cards.

### AoF Omaha jackpot

Sources:
https://ggpoker.com/poker-games/all-in-or-fold/
https://ggpoker.com/jackpots/all-in-or-fold-jackpot/

Supported:

- qualifier is Royal Flush;
- uses two hole cards and three community cards;
- normally requires showdown;
- Omaha Royal Flush completed immediately on the flop receives the published exception;
- 50% of the AoF jackpot fee is stated to contribute to the jackpot.

### All-In Fortune

Source:
https://ggpoker.com/jackpots/all-in-fortune/

Supported:

- each All-In gives a chance;
- poker-hand victory is not required;
- chance accumulates through All-In actions;
- prize depends on blind level + RNG;
- fixed fee contributes to the pool;
- public page does not disclose a complete probability/tier table.

## Project assumptions supplied by the user

On 2026-09-20 the project selected:

- jackpot pool scenario: $750,000;
- Fortune pool scenario: $75,000;
- rakeback: 35%.

These are modeling inputs, not claims that the current public GGPoker page displays those exact pool/RB figures.

## Internal evidence from DeepAoF

The previous `aof_deep_generator_unificado` models rake fee, jackpot fee and Fortune fee separately, includes hand-dependent jackpot EV, and treats Fortune through a trigger probability plus payout distribution.

Its documented Fortune reference is approximately $77,273.23 with a 2% trigger parameter. DeepOM will reuse this architecture only provisionally, scaling the Fortune calibration to $75,000 until stronger evidence exists.

The DeepAoF RB40 manual also establishes the project rule that a change in stack, rake, rakeback or payoff requires regeneration of the mathematical strategy.

## Resolved conflict: 8 BB vs 5 BB

The generic AoF marketing sentence mentions 8 BB. The current Omaha-specific table rows show 5 BB buy-ins consistently. The more specific Omaha table controls DeepOM.

Decision: **5 BB**.

## Open evidence items

1. live maximum players / exact 4w->3w->HU behavior;
2. full Fortune trigger/tier calibration;
3. whether 35% is intended as effective rebate or nominal pre-PVI;
4. exact runtime/tablemap behavior for four hole cards.

These items block a final OM0 PASS but do not block creation/testing of the independent PLO4 evaluator.
