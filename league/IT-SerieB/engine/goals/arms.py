"""G-ITB arm adjustments layered over a fitted DC model.

X2 membership is the frozen mover table committed before fitting at
league/IT-SerieB/prereg/movers_itb.json (team_id x entry season ->
source tier), derived in EDA from team_id churn plus
accent-normalised tier name matching. It is NOT re-derived here.
"""
import json
import math
from collections import defaultdict
from pathlib import Path

MOVERS = json.loads((Path(__file__).resolve().parents[2] / "prereg" / "movers_itb.json").read_text())

# Frozen F4 magnitudes (EDA): from Serie A +0.145/-0.143, from Serie C -0.070/+0.118.
OFFSETS = {"serie_a": (0.145, -0.143), "serie_c": (-0.070, 0.118)}


def mover_ids(target_season):
    """{team_id (int): source} for clubs entering in target_season."""
    return {int(tid): v["source"] for tid, v in MOVERS.get(target_season, {}).items()}


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
    if arm == "x2":
        mu = model.mu
        for tid, att, dfn in ((home, "ah", "dh"), (away, "aa", "da")):
            src = movers.get(tid)
            if src is None:
                continue
            dgf, dga = OFFSETS[src]
            a_off = math.log(max(mu + dgf, 0.10) / mu)
            d_off = math.log(max(mu + dga, 0.10) / mu)
            if att == "ah":
                ah += a_off; dh += d_off
            else:
                aa += a_off; da += d_off
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    return lh, la
