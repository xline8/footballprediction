"""Frozen G-UYSEG arm adjustments."""
import math
from collections import defaultdict


MOVERS = {
    "2022": {1835, 1838, 188312},
    "2023": {924934, 2220, 2221},
    "2024": {395613, 1319664, 4669},
    "2025": {7808, 4421, 1833},
}
OFFSETS = {
    "2022": (0.0, 0.0),
    "2023": (-0.129264, 0.179378),
    "2024": (-0.044284, 0.134240),
    "2025": (0.004892, 0.066170),
}


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts, mu):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0)
        da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0)
        dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        dgf, dga = multipliers
        if home in movers:
            lh *= max(mu + dgf, 0.10) / mu
            la *= (mu + dga) / mu
        if away in movers:
            la *= max(mu + dgf, 0.10) / mu
            lh *= (mu + dga) / mu
    return lh, la
