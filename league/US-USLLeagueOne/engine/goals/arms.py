"""US-MLS goals arm adjustments."""
import math
from collections import defaultdict


def x3_multipliers(games, cutoff):
    stats = defaultdict(lambda: [0.0] * 5); league = [0.0] * 5; league_weight = 0.0
    for g in games:
        vals = (g.get("oph"), g.get("opa"), g.get("sph"), g.get("spa"))
        if any(v is None for v in vals): continue
        w = 0.5 ** ((cutoff - g["date"]).days / 270.0); league_weight += 2.0 * w
        for team, values in ((g["hi"], (vals[0], vals[1], vals[2], vals[3])), (g["ai"], (vals[1], vals[0], vals[3], vals[2]))):
            s = stats[team]; s[0] += 1
            for i, v in enumerate(values, 1): s[i] += w * v
            for i, v in enumerate(values): league[i] += w * v
    if not stats: return {}
    lop, lsp = league[0] / league_weight, league[2] / league_weight; result = {}
    for team, (count, opf, opa, spf, spa) in stats.items():
        if count < 8 or lop <= 0 or lsp <= 0:
            result[team] = {"att": 1.0, "def": 1.0}; continue
        denom = sum(0.5 ** ((cutoff - g["date"]).days / 270.0) for g in games if (g["hi"] == team or g["ai"] == team) and all(g.get(k) is not None for k in ("oph", "opa", "sph", "spa")))
        att = math.sqrt((opf / denom / lop) * (spf / denom / lsp)); deff = math.sqrt((opa / denom / lop) * (spa / denom / lsp))
        result[team] = {"att": min(2.0, max(0.5, att)), "def": min(2.0, max(0.5, deff))}
    return result


def adjusted_lambdas(model, home, away, arm, counts, multipliers):
    lh, la = model.lambdas(home, away)
    if arm in ("shr", "x3"):
        if counts.get(home, 0) < 8: lh = 0.5 * lh + 0.5 * model.mu
        if counts.get(away, 0) < 8: la = 0.5 * la + 0.5 * model.mu
    if arm == "x3":
        mh = multipliers.get(home, {"att": 1, "def": 1}); ma = multipliers.get(away, {"att": 1, "def": 1})
        lh *= math.sqrt(mh["att"] * ma["def"]); la *= math.sqrt(ma["att"] * mh["def"])
    return lh, la
