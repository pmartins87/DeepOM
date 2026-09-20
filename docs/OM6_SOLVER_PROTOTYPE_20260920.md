# OM6 Solver Prototype Record — 2026-09-20

Implementation:
- `deepom/solver_proto.py`

Current prototype:
- external-sampling CFR;
- CFR+ regret clipping;
- linear strategy averaging;
- 4w / 3w / HU public AoF trees;
- exact 16,432-class PLO4 private state key;
- collision-safe full-deal sampling;
- gross mechanical payoff mode;
- optional economic payoff mode using a versioned `EconomicPreset`;
- explicit Fortune and Jackpot multipliers for sensitivity runs;
- deterministic seed behavior.

Regression tests verify:
- zero-regret uniform strategy;
- a forced losing call creates fold regret in the expected direction;
- identical seeds produce identical snapshots;
- quick runs visit infosets and keep finite regret.

## Not yet complete

OM6 is **IN PROGRESS**, not PASS. Remaining requirements:
- dense indexed tables instead of Python dict keys;
- checkpoint/resume;
- run manifest and content hashes;
- multiprocessing/parallel traversal;
- benchmark on the Ryzen 9;
- economic sensitivity comparison across seeds;
- production export format.

## Next engineering decision

Because OM4/OM5 show only 361,504 canonical infosets, the next solver should use dense indexed arrays. The sparse Python prototype remains the correctness oracle, not the intended high-throughput trainer.
