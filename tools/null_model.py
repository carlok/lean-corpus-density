"""Subject-matched null: what would a real library look like at this size and shape?

Comparing a small corpus against a uniform draw from a large one is unfair,
because subject concentration is most of what produces internal edges and a
uniform draw has none. This null instead reproduces the target corpus's own
area profile in the reference corpus, drawing the same number of modules from
the same-named subject areas -- 11 from NumberTheory, 3 from Analysis, and so
on -- and asks how many internal edges that yields.

Area is the coarsest and only available match: target modules are three
components deep (Corpus.Area.Name), so there is no sub-area to align on. The
match is therefore conservative in a known direction. Drawing 11 modules from
the whole of Mathlib.NumberTheory spreads them across subtopics that a focused
effort would not spread across, so the null probably understates how many edges
real mathematics would produce at this shape.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter
from pathlib import Path


def area(module: str) -> str:
    parts = module.split(".")
    return parts[1] if len(parts) > 2 else "(root)"


def load(path: Path) -> dict[str, list[str]]:
    return json.loads(path.read_text())["graph"]


def observed_edges(graph: dict[str, list[str]], sample: set[str] | None = None) -> int:
    sample = sample if sample is not None else set(graph)
    return sum(1 for m in sample for t in graph[m] if t in sample)


def simulate(
    reference: dict[str, list[str]],
    profile: Counter,
    trials: int,
    seed: int,
    missing: str,
) -> tuple[list[int], dict]:
    rng = random.Random(seed)
    by_area: dict[str, list[str]] = {}
    for module in reference:
        by_area.setdefault(area(module), []).append(module)

    plan: list[tuple[str, int]] = []
    notes: dict[str, str] = {}
    for name, count in profile.items():
        pool = by_area.get(name, [])
        if len(pool) >= count:
            plan.append((name, count))
        elif missing == "uniform":
            plan.append(("*", count))
            notes[name] = f"absent from reference; {count} drawn corpus-wide"
        else:
            notes[name] = f"absent from reference; {count} slot(s) dropped"

    everything = list(reference)
    counts = []
    for _ in range(trials):
        sample: set[str] = set()
        for name, count in plan:
            pool = everything if name == "*" else by_area[name]
            sample |= set(rng.sample(pool, count))
        counts.append(observed_edges(reference, sample))
    return counts, {"plan_k": sum(c for _, c in plan), "adjustments": notes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="corpus whose shape and edge count are tested")
    parser.add_argument("reference", type=Path, help="corpus supplying the null")
    parser.add_argument("--trials", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--missing", choices=["drop", "uniform"], default="drop")
    args = parser.parse_args()

    target = load(args.target)
    profile = Counter(area(m) for m in target)
    actual = observed_edges(target)

    counts, meta = simulate(load(args.reference), profile, args.trials, args.seed, args.missing)
    counts.sort()
    at_least = sum(1 for c in counts if c >= actual) / len(counts)
    print(json.dumps({
        "target": args.target.stem,
        "reference": args.reference.stem,
        "target_modules": len(target),
        "target_edges": actual,
        "profile": dict(profile.most_common()),
        "null_k": meta["plan_k"],
        "adjustments": meta["adjustments"],
        "null_mean": round(statistics.mean(counts), 3),
        "null_median": counts[len(counts) // 2],
        "null_p95": counts[int(0.95 * len(counts))],
        "p_value": round(at_least, 5),
    }, indent=1))


if __name__ == "__main__":
    main()
