# Fact sheet

Raw material, not a draft. These are deliberately bare statements of what was
measured, with no connective prose, no framing and no conclusions written for
you. They are here so that whatever you write is your own sentences over
verified numbers.

Every line is checkable from this repository.

## Method

- Direct `import` lines only, read from file headers. No build, no toolchain.
- Transitive closure deliberately not computed.
- Comments stripped before scanning.
- Lean 4.34 module system: imports appear as `public import` and `meta import`.
  A `^import` scan misses 76% of Tau Ceti's files.
- Mathlib checkout used: the one pinned by LeanFrontier, `v4.33.0-rc1`.
- Measured 20 August 2026.

## Corpus sizes

- Mathlib: 8268 modules, 25872 internal edges.
- Tau Ceti: 2774 modules, 4518 internal edges. First commit 2 June 2026, 3440
  commits at time of measurement.
- merely-true: 41 modules, 94 internal edges, 34 modules under one directory,
  last commit 3 July 2026.
- LeanFrontier: 24 modules, 4 internal edges.

## Scaling

- Under uniform sampling of k from N, internal edges scale as E·(k/N)² and
  edges per sampled module as E·k/N².
- Consequence: per-module density across corpora of different sizes is not
  comparable without correction.
- Further consequence: a subsample of a large library is a fragment, not a
  small library. Edges routed through undrawn modules are lost. Profile
  matching does not repair this.

## Tau Ceti growth, by replay of its own history

Modules / internal edges / edges per module / max in-degree:

- 10 / 4 / 0.40 / 2
- 24 / 22 / 0.92 / 3
- 50 / 47 / 0.94 / 6
- 99 / 103 / 1.04 / 7
- 198 / 220 / 1.11 / 11
- 398 / 486 / 1.22 / 11
- 761 / 1022 / 1.34 / 11
- 1524 / 2175 / 1.43 / 22
- 2314 / 3582 / 1.55 / 26

## Matched-size comparison

- Tau Ceti at 24 modules: 22 internal edges, 20.2 declarations per module.
- LeanFrontier at 24 modules: 4 internal edges, 8.1 declarations per module.
- Per module, equal exposure: p = 2.7×10⁻⁴.
- Per declaration: rate ratio 2.20×, 95% CI [0.75×, 8.80×], p = 0.096.
- The per-declaration difference is not established at these counts.
- File granularity does not explain the gap: Tau Ceti's modules are larger.

## Power

- At 24 modules the per-declaration test has 42% power against a 2.2× effect.
- 80% power is reached near 60 modules.

## Known limits

- Tau Ceti is directed by human-written roadmaps. A roadmap specifies a
  dependency graph in advance.
- Mathlib is subject to an enforced import-minimization effort, so its density
  reflects maintenance as well as authorship.
- Mathlib 4's early history is a port, so it cannot supply organic
  small-library states.
- merely-true is one project rather than a library and is not comparable at
  these sizes.
