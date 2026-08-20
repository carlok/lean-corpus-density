# Dependency density in four Lean 4 corpora

*Measured 20 August 2026. Everything below is reproducible from this repository
against public checkouts; `clone.sh` fetches the two corpora that are not
already on disk.*

## The question

Three Lean 4 libraries now exist that are written by machines and sit
downstream of Mathlib. They differ in how much human judgement sits between a
generated theorem and the library:

| Corpus | Statements chosen by | Gate |
|---|---|---|
| Mathlib | humans | human review, plus an enforced import-minimization effort |
| Tau Ceti | machines, under human-written roadmaps | adversarial AI review against rubrics |
| LeanFrontier | machines, free subject choice | mechanical receiver, no human review |
| merely-true | machines, free subject choice | `lake build`, no `sorry`, no `axiom` |

The question is whether machine-generated mathematics accumulates — whether
later results build on earlier machine-generated ones, or whether the corpus
stays a pile of unrelated theorems. That is a question about the import graph,
so the import graph is what gets measured.

## What is measured

Direct `import` lines, read from file headers. No Lean toolchain and no build,
so the scripts run against any checkout at any toolchain version.

Two decisions worth stating, because both change the answer:

**Direct imports, not the transitive closure.** Through the foundations every
module reaches every other one, and closure density carries no information.

**Comments are stripped first.** Prose about imports is common in these
libraries, and a wrapped comment line beginning with the word "import" reads as
an edge to a naive scan.

One trap: Lean 4.34 introduced the module system, so Tau Ceti and current
Mathlib write `public import` and `meta import`. A `^import` regex silently
misses 76% of Tau Ceti's files and reports a corpus with almost no structure.

## Raw density, and why it means nothing

| Corpus | modules | internal edges | per module |
|---|---|---|---|
| Mathlib | 8268 | 25872 | 3.13 |
| merely-true | 41 | 94 | 2.29 |
| Tau Ceti | 2774 | 4518 | 1.63 |
| LeanFrontier | 24 | 4 | 0.17 |

That ordering is mostly size. Take a corpus of N modules with E internal edges
and draw k of them: an edge survives only when both endpoints are drawn, so
internal edges fall off like E·(k/N)² and edges per drawn module like E·k/N².
Density is roughly linear in corpus size. Comparing an 8268-module library to a
24-module one at full size measures the sizes.

## Why subsampling does not fix it

The obvious correction is to draw 24 modules from Mathlib and compare. Doing
that gives 0.21 internal edges on average, with 81% of draws containing none at
all, against LeanFrontier's 4 — p = 0.0002 in LeanFrontier's favour.

That result is an artifact. LeanFrontier is not scattered: 11 of its 24 modules
are number theory, and subject concentration is most of what produces edges.
Imposing LeanFrontier's own area profile on Mathlib — 11 from NumberTheory, 3
from Analysis, 3 from Combinatorics, one each from seven more — drops the null
to 0.72 expected edges, p = 0.006.

Both numbers are still wrong, for a reason that no amount of profile-matching
repairs: **sampling a large library does not produce a small library, it
produces a fragment.** Mathlib's number theory graph is dense, but drawing 11
of its 240 modules keeps the nodes and discards every edge that ran through the
229 left behind. LeanFrontier's 24 modules are not a fragment of anything —
they are the whole graph, intact. The (k/N)² correction handles the counting
consequence of that and does nothing about the coherence consequence, so any
subsample null is biased toward whichever corpus is being measured whole.

Three passes over these data produced p = 0.0002, then p = 0.22, then p = 0.006
before the flaw surfaced. The instability was the signal.

## The measurement that works

A corpus with genuine organic history supplies real small-library states
instead of simulated ones. Tau Ceti has 3440 commits since 2 June 2026, so
replaying its history gives the library as it actually stood at 10 modules, at
24, at 99. Mathlib 4 cannot supply the equivalent: its early history is a port,
not growth.

Tau Ceti's accumulation curve:

| modules | internal edges | per module | isolated | max in-degree |
|---|---|---|---|---|
| 10 | 4 | 0.40 | 6 | 2 |
| 24 | 22 | 0.92 | 6 | 3 |
| 50 | 47 | 0.94 | 13 | 6 |
| 99 | 103 | 1.04 | 25 | 7 |
| 198 | 220 | 1.11 | 50 | 11 |
| 398 | 486 | 1.22 | 82 | 11 |
| 761 | 1022 | 1.34 | 159 | 11 |
| 1524 | 2175 | 1.43 | 352 | 22 |
| 2314 | 3582 | 1.55 | 518 | 26 |

The density rises monotonically and the most-reused module goes from an
in-degree of 2 to 26. Machine-generated mathematics accumulates here, and the
rate of accumulation increases as the library grows.

## Tau Ceti against LeanFrontier at matched size

Both whole young libraries, no sampling:

| | modules | internal edges | per module | declarations/module |
|---|---|---|---|---|
| Tau Ceti, 10 June 2026 | 24 | 22 | 0.92 | 20.2 |
| LeanFrontier, 20 August 2026 | 24 | 4 | 0.17 | 8.1 |

Per module, with equal exposure, the difference is significant: p = 2.7×10⁻⁴.

The obvious objection is file granularity — a library that splits work across
many small files manufactures imports. It fails, and in the opposite direction:
Tau Ceti's modules are larger, 20.2 declarations against 8.1. Normalising by
declaration rather than by module shrinks the gap from 5.5× to 2.20×, and at
that point the counts are too small to carry it: 95% CI [0.75×, 8.80×],
p = 0.096. **Per module the gap is established. Per declaration it is not.**

Which normalisation is right is a judgement call that decides the headline, so
both belong in any statement of the result.

## merely-true

Not comparable, and it is worth saying why rather than forcing it into the
table. It holds 41 modules, 34 of them inside a single `Landau` directory, and
its last commit is 3 July 2026. It is one project rather than a library, and at
N = 41 no subsample is small relative to the corpus, so the scaling argument
above does not apply to it. Its raw internal density of 2.29 edges per module
is what a single focused development looks like.

## What this does and does not show

It shows that machine-generated mathematics can accumulate. Tau Ceti is the
existence proof, and it is not a marginal one: 2774 modules in 79 days, density
rising throughout.

It does not show that machine-generated mathematics accumulates on its own. Tau
Ceti is directed by human-written roadmaps, and a roadmap is a dependency graph
specified in advance by a person. The observed structure may be the roadmap's
structure. Separating those requires a corpus with no roadmap, measured at a
size where the test has power.

At 24 modules, the per-declaration test has 42% power against the observed 2.2×
effect. It reaches 80% near 60 modules. Below that, a null result is not
evidence of anything.

## Reproducing

```sh
./clone.sh
python3 tools/import_graph.py <mathlib-checkout> Mathlib --json-out data/mathlib.json
python3 tools/import_graph.py corpora/TauCeti TauCeti --json-out data/tauceti.json
python3 tools/null_model.py data/leanfrontier.json data/mathlib.json
```

Python standard library only. The Mathlib checkout used here was the one pinned
by LeanFrontier at `v4.33.0-rc1`; any recent checkout gives comparable numbers,
and the toolchain version is worth recording alongside them, since the module
system changed the import syntax.
