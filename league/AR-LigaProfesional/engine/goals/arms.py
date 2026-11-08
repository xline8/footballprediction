"""G-AR arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict


def mover_ids(target_season, rows):
    seasons = sorted({r["season"] for r in rows})
    i = seasons.index(target_season)
    prior = seasons[i - 1] if i else None
    current = {r["hi"] for r in rows if r["season"] == target_season} | {r["ai"] for r in rows if r["season"] == target_season}
    previous = ({r["hi"] for r in rows if r["season"] == prior} | {r["ai"] for r in rows if r["season"] == prior}) if prior else set()
    return current - previous


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


def adjusted_lambdas(model, home, away, arm, movers, multipliers):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("x2", "x3"):
        mu = model.mu
        if home in movers: ah += math.log(max(mu - 0.12, 0.10) / mu); dh += math.log((mu + 0.18) / mu)
        if away in movers: aa += math.log(max(mu - 0.12, 0.10) / mu); da += math.log((mu + 0.18) / mu)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x3":
        mh, ma = multipliers.get(home, {"att": 1, "def": 1}), multipliers.get(away, {"att": 1, "def": 1})
        lh *= math.sqrt(mh["att"] * ma["def"])
        la *= math.sqrt(ma["att"] * mh["def"])
    return lh, la
