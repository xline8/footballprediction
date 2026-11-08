"""G-SG arm adjustments layered over a fitted DC model.

Only the SHRINK mechanics are ported from the FI/BY arms.py: the
X2 entrant arm was DROPPED for this league pre-fitting (EDA F4 —
exactly 1 dev entrant transition, below the >=3 minimum, GA sign
contradicting the entrant pattern), so no x2_multipliers exists
here and no entrant offset can ever be applied.
"""
import math
from collections import defaultdict


def mover_ids(*_):
    return set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    return lh, la
