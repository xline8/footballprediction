"""Prediction-arm adjustments for the EE goals engine."""
import math
from collections import defaultdict


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def entrant_ids(all_rows, target_season, preceding_season):
    prior = {r["hi"] for r in all_rows if r["season"] == preceding_season} | {r["ai"] for r in all_rows if r["season"] == preceding_season}
    current = {r["hi"] for r in all_rows if r["season"] == target_season} | {r["ai"] for r in all_rows if r["season"] == target_season}
    return current - prior


OFFSETS = {
    "2023": (-0.358333, 1.030556),
    "2024": (-0.440278, 0.726389),
    "2025": (-0.588889, 0.716667),
}


def adjusted_lambdas(model, home, away, arm, counts, entrants, mu, season):
    a = defaultdict(float, model.a); d = defaultdict(float, model.d)
    if arm == "shrink":
        for team, n in counts.items():
            factor = n / (n + 6.0) if n < 6 else 1.0
            a[team] *= factor; d[team] *= factor
    if arm == "x2" and season in OFFSETS and mu > 0:
        dgf, dga = OFFSETS[season]
        offset_a = math.log(max(mu + dgf, 0.10) / mu)
        offset_d = math.log((mu + dga) / mu)
        if home in entrants: a[home] += offset_a; d[home] += offset_d
        if away in entrants: a[away] += offset_a; d[away] += offset_d
    return model.lambdas(home, away, a, d)
