"""G-BR arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict


INDEX = "/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv"
def mover_ids(games, target, cutoff):
    prior = str(cutoff.year - 1)
    current = {g["home"] for g in target} | {g["away"] for g in target}
    prior_b = {g["home"] for g in games if str(g["date"].year) == prior} | {g["away"] for g in games if str(g["date"].year) == prior}
    tiers = {268: set(), 8971: set()}
    import csv
    with open(INDEX, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("season") == prior and r.get("league_id") in ("268", "8971"):
                tiers[int(r["league_id"])].update((r.get("home", ""), r.get("away", "")))
    return {name: ("ex-A" if name in tiers[268] else "ex-C") for name in current - prior_b if name in tiers[268] | tiers[8971]}


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def x3_multipliers(games, cutoff):
    stats = defaultdict(lambda: [0.0] * 5)
    league = [0.0] * 5
    league_weight = 0.0
    for g in games:
        vals = (g.get("oph"), g.get("opa"), g.get("sph"), g.get("spa"))
        if any(v is None for v in vals):
            continue
        w = 0.5 ** ((cutoff - g["date"]).days / 270.0)
        league_weight += 2.0 * w
        for team, values in ((g["hi"], (vals[0], vals[1], vals[2], vals[3])),
                             (g["ai"], (vals[1], vals[0], vals[3], vals[2]))):
            s = stats[team]; s[0] += 1; s[1] += w * values[0]; s[2] += w * values[1]; s[3] += w * values[2]; s[4] += w * values[3]
            for i, v in enumerate(values): league[i] += w * v
    n = sum(v[0] for v in stats.values())
    if n == 0:
        return {}
    lop = league[0] / league_weight
    lsp = league[2] / league_weight
    result = {}
    for team, (count, opf, opa, spf, spa) in stats.items():
        if count < 8 or lop <= 0 or lsp <= 0:
            result[team] = {"att": 1.0, "def": 1.0}
            continue
        denom = sum(0.5 ** ((cutoff - g["date"]).days / 270.0) for g in games
                    if (g["hi"] == team or g["ai"] == team) and all(g.get(k) is not None for k in ("oph", "opa", "sph", "spa")))
        att = math.sqrt((opf / denom / lop) * (spf / denom / lsp))
        deff = math.sqrt((opa / denom / lop) * (spa / denom / lsp))
        result[team] = {"att": min(2.0, max(0.5, att)), "def": min(2.0, max(0.5, deff))}
    return result


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        for team, tier in ((home, movers.get(home)), (away, movers.get(away))):
            if tier == "ex-A":
                if team == home: lh *= (model.mu + .131) / model.mu; la *= max(model.mu - .088, .10) / model.mu
                else: la *= (model.mu + .131) / model.mu; lh *= max(model.mu - .088, .10) / model.mu
            elif tier == "ex-C":
                if team == home: lh *= max(model.mu - .081, .10) / model.mu; la *= max(model.mu - .015, .10) / model.mu
                else: la *= max(model.mu - .081, .10) / model.mu; lh *= max(model.mu - .015, .10) / model.mu
    if arm == "shrink":
        pass
    if arm == "x3":
        mh, ma = multipliers.get(home, {"att": 1, "def": 1}), multipliers.get(away, {"att": 1, "def": 1})
        lh *= math.sqrt(mh["att"] * ma["def"])
        la *= math.sqrt(ma["att"] * mh["def"])
    return lh, la
