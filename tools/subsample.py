"""Compare corpora of very different sizes at a matched module count.

A uniform draw of k modules from a corpus of N keeps an edge only when both
endpoints are drawn, so internal edges fall off like (k/N)^2 and edges per
sampled module like k/N. Comparing a 8000-module library against a 24-module
one at full size therefore measures size, not structure. Everything here is
reported at a matched k, against two null draws:

  scattered    -- k modules drawn uniformly from the whole corpus
  concentrated -- k modules drawn from within one top-level subject area

The gap between those two says how much of a corpus's connectivity comes from
working inside one subject rather than across many.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path


def area(module: str) -> str:
    """Top-level subject area: Mathlib.Analysis.Foo.Bar -> Analysis."""
    parts = module.split(".")
    return parts[1] if len(parts) > 2 else "(root)"


def internal_edges(graph: dict[str, list[str]], sample: set[str]) -> int:
    return sum(1 for m in sample for t in graph[m] if t in sample)


def draw_scattered(graph: dict[str, list[str]], k: int, rng: random.Random) -> set[str]:
    return set(rng.sample(list(graph), k))


def draw_concentrated(
    graph: dict[str, list[str]], k: int, rng: random.Random, by_area: dict[str, list[str]]
) -> set[str] | None:
    eligible = [a for a, ms in by_area.items() if len(ms) >= k]
    if not eligible:
        return None
    # Weight by size so a draw is not dominated by many tiny areas.
    chosen = rng.choices(eligible, weights=[len(by_area[a]) for a in eligible])[0]
    return set(rng.sample(by_area[chosen], k))


def run(graph: dict[str, list[str]], k: int, trials: int, seed: int) -> dict:
    rng = random.Random(seed)
    by_area: dict[str, list[str]] = {}
    for module in graph:
        by_area.setdefault(area(module), []).append(module)

    result: dict = {"k": k, "trials": trials, "modules": len(graph), "areas": len(by_area)}
    for label, drawer in (("scattered", draw_scattered), ("concentrated", None)):
        counts: list[int] = []
        for _ in range(trials):
            sample = (
                draw_scattered(graph, k, rng)
                if label == "scattered"
                else draw_concentrated(graph, k, rng, by_area)
            )
            if sample is None:
                break
            counts.append(internal_edges(graph, sample))
        if not counts:
            result[label] = None
            continue
        counts.sort()
        result[label] = {
            "mean_edges": round(statistics.mean(counts), 3),
            "per_module": round(statistics.mean(counts) / k, 4),
            "median": counts[len(counts) // 2],
            "p05": counts[int(0.05 * len(counts))],
            "p95": counts[int(0.95 * len(counts))],
            "zero_edge_fraction": round(sum(1 for c in counts if c == 0) / len(counts), 3),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph_json", type=Path, help="output of import_graph.py --json-out")
    parser.add_argument("-k", type=int, required=True, help="matched module count")
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260820)
    args = parser.parse_args()

    graph = json.loads(args.graph_json.read_text())["graph"]
    print(json.dumps(run(graph, args.k, args.trials, args.seed), indent=1))


if __name__ == "__main__":
    main()
