"""The preregistered NZ-Championship arm adjustments."""
import math
from collections import defaultdict


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        ah *= min(1, counts.get(home, 0) / 6)
        da *= min(1, counts.get(away, 0) / 6)
        aa *= min(1, counts.get(away, 0) / 6)
        dh *= min(1, counts.get(home, 0) / 6)
    return math.exp(ah + da + model.h), math.exp(aa + dh)
