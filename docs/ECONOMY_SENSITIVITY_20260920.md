# Economy / Promotion Sensitivity Record — 2026-09-20

Preset:
`GG_AOF_OMAHA_020_040_JP750K_F75K_RB35_V0`

## Fixed per-player charge model

Inherited from the previous DeepAoF GGPoker AoF implementation:

- base rake: 0.025 BB;
- rakeback: 35% on base rake only;
- net base rake: 0.01625 BB;
- Jackpot fee: 0.025 BB;
- Fortune fee: 0.025 BB;
- fixed deterministic charge: **0.06625 BB per dealt player per hand**.

This fee-placement rule is an inherited project assumption, not a newly inferred public GGPoker rule. It is isolated in `deepom/economics.py` so it can be replaced without changing the poker kernel.

Because this charge is constant with respect to a player's FOLD/ALL-IN choice inside a hand, it shifts absolute EV but does not by itself change the equilibrium action at an infoset. Action-dependent promotion credits do change strategy.

## Fortune provisional normalization

Previous DeepAoF calibration:
- reference Fortune pool: $77,273.23;
- trigger probability: 2%;
- five payout tiers with weights summing to 1,000,000;
- normalized expected Fortune credit: **0.10715968 BB per All-In** at the reference pool.

Pool-only scaling to $75,000 gives:

**0.10400724804696271 BB per All-In.**

This is intentionally provisional because the public Fortune description states that awards depend on blind level and does not expose the full current tier table.

The solver accepts an explicit Fortune multiplier for sensitivity runs.

## Omaha Jackpot sensitivity

At the $0.20/$0.40 development preset:
- Jackpot prize = $150 = **375 BB**.

Raw PLO4 starting-hand census:
- 228,085 hands: no Royal-eligible suit;
- 42,040 hands: one Royal-eligible suit;
- 600 hands: two Royal-eligible suits.

Therefore:
- **15.7503%** of raw PLO4 hands have at least one Royal-eligible suit;
- one-suit Jackpot EV at a showdown All-In = **0.216813135985 BB**;
- two-suit Jackpot EV = **0.433626271970 BB**;
- random-hand mean Jackpot EV per showdown All-In = **0.034629236310 BB**.

This is large enough that Omaha Jackpot eligibility must remain in the exact infoset/payoff model; it cannot be treated as a tiny post-processing correction.

## Current gate

Economics are implemented and solver-compatible, but Fortune remains sensitivity-controlled rather than production-frozen.
