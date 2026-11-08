"""The preregistered Gate Zero, SHRINK, and X2 adjustments."""
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
        sh = min(1.0, counts.get(home, 0) / 6.0)
        sa = min(1.0, counts.get(away, 0) / 6.0)
        ah *= sh
        dh *= sh
        aa *= sa
        da *= sa
    elif arm == "x2":
        if counts.get(home, 0) == 0:
            ah, dh = -0.18, 0.15
        if counts.get(away, 0) == 0:
            aa, da = -0.18, 0.15
    return math.exp(ah + da + model.h), math.exp(aa + dh)
