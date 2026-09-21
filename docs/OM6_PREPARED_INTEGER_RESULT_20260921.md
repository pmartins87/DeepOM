# OM6 Resident / Pre-Indexed Deal Result — 2026-09-21

Hardware/runtime:
- Ryzen 9;
- WSL2;
- Python 3.12.3.

Frozen A/B:
- mode: 4w;
- gross payoff;
- seed: 123;
- exact five-card score table;
- packed showdown scores;
- raw exact PLO4 class lookup;
- 2 iterations;
- 500 deals/iteration;
- 1,000 total deals per variant.

## Reference path

- memory-mapped five-card table;
- validated string-card lookup path;
- train time: **0.223603605 s**;
- throughput: **4,472.199810877 deals/s**;
- visited infosets: 3,870;
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`.

## Resident / pre-indexed path

- resident five-card table;
- sampled deal converted to integer deck indices once;
- exact class ids resolved from those same indices;
- train time: **0.194757913 s**;
- throughput: **5,134.579563742 deals/s**;
- visited infosets: 3,870;
- arrays SHA256:
  `baf0afcc375773e98cb5bfb0fe0f2d3fe74706fe4fd92525e95a19b9f48c9a7b`.

## Equivalence

**PASS — exact trajectory match.**

Regrets, average strategy, visits and final solver-array SHA256 are identical.

## Performance

Speedup:

`5134.579563742 / 4472.199810877 = 1.148110501x`

That is a further **14.81% throughput increase**.

Relative to the early 234.062 deals/s legacy path, the current measured path is about **21.94x faster** while preserving the same solver trajectory.

## Profiling caveat

The automatic high-level profiler printed:

- evaluator: 0%;
- class lookup: 0%;
- residual: 100%.

This is **not evidence that evaluator/class work vanished**.

The instrumentation was still keyed to the previous function names:
- `evaluate_omaha_score_table`;
- `index_of`.

The accepted fast path now executes:
- `evaluate_omaha_score_table_indices`;
- `index_of_indices`.

Therefore the family-level attribution for this run is stale/incomplete, although the cProfile artifact itself is valid.

## Decision

Do not infer that CFR is now 100% of runtime.

The next gate reads the already-created post-prepared-integer `.prof` and performs function-level attribution. No new training is required.

At the same time, the profiler instrumentation is updated so future profiles recognize both the string/reference and integer/prepared paths.
