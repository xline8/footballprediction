"""The preregistered G-KR3 arms: Gate Zero and SHRINK."""
from collections import defaultdict
import math


def match_counts(rows):
    counts = defaultdict(int)
    for row in rows:
        counts[row['hi']] += 1
        counts[row['ai']] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts=None):
    counts = counts or {}
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == 'shrink':
        ah *= min(1.0, counts.get(home, 0) / 6.0)
        da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0)
        dh *= min(1.0, counts.get(home, 0) / 6.0)
    return math.exp(ah + da + model.h), math.exp(aa + dh)
