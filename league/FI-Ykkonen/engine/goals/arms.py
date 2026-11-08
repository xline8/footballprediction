"""G-FI arm adjustments layered over a fitted DC model (see
prereg/PREREG_G_FI.md). Port of the FI reference arms.py, with the X2
entrant multipliers FROZEN from EDA F4 (not recomputed from prior
transitions at run time): G_LOG = -0.182, C_LOG = +0.223 (c clamped
at log 1.25 from the raw mean GA diff +0.235; 22 dev transitions).

gate_zero: unmodified reference.
shrink:    n<6 prior in-league matches => a/d exponents scaled by n/6.
x2:        shrink + entrant multipliers exp(G_LOG) on own scoring /
           exp(C_LOG) on opponent scoring, for teams absent from the
           immediately preceding season (training data only).
"""
import math
from collections import defaultdict

# Frozen X2 entrant offsets (PREREG_G_FI, EDA F4): 22 dev transitions,
# mean GF diff -0.182 / GA diff +0.235 goals per match; g_log is the
# mean GF diff as-is, c_log is the mean GA diff clamped at log(1.25).
G_LOG = -0.182
C_LOG = 0.223


def mover_ids(*_):
    return set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def x2_multipliers(games, target):
    """Frozen multipliers for entrants in the target season: a team in
    the target season that played no match in the immediately
    preceding season (seasons taken from the training games only)."""
    current = {t for g in target for t in (g["hi"], g["ai"])}
    seasons = defaultdict(set)
    for g in games:
        seasons[g["season"]].add(g["hi"])
        seasons[g["season"]].add(g["ai"])
    target_season = target[0]["season"]
    prev = target_season - 1
    entrants = current - seasons.get(prev, set())
    return {team: {"g": G_LOG, "c": C_LOG} for team in entrants}


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x2"):
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        mh, ma = multipliers.get(home), multipliers.get(away)
        if mh: lh *= math.exp(mh["g"]); la *= math.exp(mh["c"])
        if ma: la *= math.exp(ma["g"]); lh *= math.exp(ma["c"])
    return lh, la
