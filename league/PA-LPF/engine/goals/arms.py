"""G-PA-LPF Gate Zero and pre-registered SHRINK arms."""
import math
from collections import defaultdict


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        home_factor = min(1.0, counts.get(home, 0) / 6.0)
        away_factor = min(1.0, counts.get(away, 0) / 6.0)
        ah *= home_factor; dh *= home_factor
        aa *= away_factor; da *= away_factor
    return math.exp(ah + da + model.h), math.exp(aa + dh)
