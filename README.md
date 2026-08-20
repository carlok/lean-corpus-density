# lean-corpus-density

Measuring how much Lean 4 libraries depend on themselves.

Measured 20 August 2026.

## Finding

**Machine-generated mathematics accumulates.** Tau Ceti, a Lean 4 library
written by AI contributors, went from nothing to 2774 modules in 79 days, and
its internal import density rose monotonically the whole way: 0.40 internal
imports per module at 10 modules, 0.92 at 24, 1.04 at 99, 1.22 at 398, 1.55 at
2314. Its most-reused module went from an in-degree of 2 to 26. Later
machine-generated results build on earlier ones, and increasingly so as the
library grows.

| modules | internal edges | per module | max in-degree |
|---|---|---|---|
| 10 | 4 | 0.40 | 2 |
| 24 | 22 | 0.92 | 3 |
| 99 | 103 | 1.04 | 7 |
| 398 | 486 | 1.22 | 11 |
| 1524 | 2175 | 1.43 | 22 |
| 2314 | 3582 | 1.55 | 26 |

Those are observed library states, recovered by replaying Tau Ceti's own commit
history, not samples drawn from a finished library. The distinction matters and
is the subject of most of this repository.

Two qualifications belong with that finding rather than beneath it. Tau Ceti is
directed by human-written roadmaps, and a roadmap is a dependency graph
specified in advance by a person, so what is shown is accumulation under human
direction, not unaided. And it is one library: LeanFrontier, which has no
roadmap and free subject choice, has 4 internal edges at the same 24 modules
where Tau Ceti had 22 (p = 2.7×10⁻⁴ per module; per declaration the gap is
2.20× with 95% CI [0.75×, 8.80×], p = 0.096, and is not established).

Whether accumulation survives without a roadmap is open, and is what
LeanFrontier's [pre-registered
experiment](https://github.com/carlok/LeanFrontier/blob/main/PREREGISTRATION.md)
is designed to answer.

## Why the obvious comparisons fail

Raw density is not comparable across corpora of different sizes: under uniform
sampling internal edges scale as E·(k/N)², so per-module density is roughly
linear in corpus size. Subsampling a large library does not fix this, because a
subsample is a fragment rather than a small library — the nodes survive and
every edge routed through an undrawn module is lost.

Replaying a library's own commit history sidesteps the problem entirely, which
is where the figures above come from.

One more caveat on the table below: Mathlib's density reflects an enforced
import-minimization effort, so it measures maintenance as well as authorship.
File granularity, the other obvious confound, does not explain the Tau Ceti /
LeanFrontier gap — Tau Ceti's modules are the larger ones, 20.2 declarations
against 8.1.

| Corpus | modules | internal edges | per module |
|---|---|---|---|
| Mathlib `v4.33.0-rc1` | 8268 | 25872 | 3.13 |
| merely-true | 41 | 94 | 2.29 |
| Tau Ceti | 2774 | 4518 | 1.63 |
| LeanFrontier | 24 | 4 | 0.17 |

Those four numbers are the ones that should *not* be compared directly. They
are here because they are what a naive reading produces.

## Method

Direct `import` lines, read from file headers. No Lean toolchain and no build,
so the scripts run against any checkout at any toolchain version.

- **Direct imports, not transitive closure.** Through the foundations every
  module reaches every other one and closure density carries no information.
- **Comments are stripped first.** A wrapped comment line beginning with the
  word "import" otherwise reads as an edge.
- **Lean 4.34's module system matters.** Tau Ceti and current Mathlib write
  `public import` and `meta import`; a `^import` scan misses 76% of Tau Ceti's
  files and reports a library with almost no structure.

## Running it

```sh
./clone.sh
python3 tools/import_graph.py <mathlib-checkout> Mathlib --json-out data/mathlib.json
python3 tools/import_graph.py corpora/TauCeti TauCeti --json-out data/tauceti.json
python3 tools/null_model.py data/leanfrontier.json data/mathlib.json
```

Python standard library only. Mathlib is not cloned by `clone.sh`: pass an
existing checkout. Record the toolchain version alongside any numbers, since
the module system changed the import syntax.

- `tools/import_graph.py` — build a corpus's direct import graph
- `tools/null_model.py` — subject-matched null (retained; see the caveat above)
- `tools/subsample.py` — matched-size draws, scattered and concentrated
- `data/tauceti_growth.csv` — Tau Ceti's density by replay of its history

## Corpora

- [Mathlib](https://github.com/leanprover-community/mathlib4)
- [Tau Ceti](https://github.com/TauCetiProject/TauCeti)
- [merely-true](https://github.com/merely-true/merely-true) — 41 modules, 34 in
  one directory; one project rather than a library, and not comparable at these
  sizes
- [LeanFrontier](https://github.com/carlok/LeanFrontier)

## Note

This analysis was carried out with an AI assistant. The numbers are
reproducible from the scripts above against public checkouts, which is the
intended basis for trusting or refuting any of it.

Apache 2.0.
