"""G-IN arm adjustments layered over a fitted DC model.

Only the Gate Zero and SHRINK arms exist for G-IN: the X2 entrant
offset was assessed pre-fitting and DROPPED on the EDA F4 evidence
(6 dev transitions, mean GF -0.110 / GA +0.025, signs mixed), so no
x2_multipliers function is carried over — see PREREG_G_IN.md.
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
