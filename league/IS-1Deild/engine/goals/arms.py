"""The preregistered IS-1Deild arm adjustments."""
import json
import math
from collections import defaultdict
from pathlib import Path

MEMBERSHIP = Path(__file__).resolve().parents[2] / "data" / "tier_membership.json"
ORIGINS = ("Besta deildin", "2. Deild")

def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1; counts[g["ai"]] += 1
    return counts

def _stats(games):
    out = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for g in games:
        for team, gf, ga in ((g["hi"], g["yh"], g["ya"]), (g["ai"], g["ya"], g["yh"])):
            out[g["season"]][team][0] += 1; out[g["season"]][team][1] += gf; out[g["season"]][team][2] += ga
    means = {s: sum(v[1] / v[0] for v in ts.values()) / len(ts) for s, ts in out.items()}
    return out, means

def x2_offsets(games, target_season, model):
    membership = json.loads(MEMBERSHIP.read_text(encoding="utf-8"))
    stats, means = _stats(games)
    completed = []
    for e in membership["entrants"]:
        if int(e["season"]) >= int(target_season): continue
        row = stats.get(e["season"], {}).get(int(e["team_id"]))
        if row:
            n, gf, ga = row
            completed.append({"origin": e["origin"], "season": e["season"], "team_id": int(e["team_id"]),
                              "gf_dev": gf / n - means[e["season"]], "ga_dev": ga / n - means[e["season"]]})
    by_origin = {}
    for origin in ORIGINS:
        rs = [r for r in completed if r["origin"] == origin]
        gf = sum(r["gf_dev"] for r in rs) / len(rs) if len(rs) >= 3 else 0.0
        ga = sum(r["ga_dev"] for r in rs) / len(rs) if len(rs) >= 3 else 0.0
        conv = lambda d: max(math.log(.8), min(math.log(1.25), math.log(max(model.mu + d, .10) / model.mu)))
        by_origin[origin] = {"transition_count": len(rs), "gf_dev": gf, "ga_dev": ga, "att": conv(gf), "con": conv(ga)}
    multipliers = {}
    for e in membership["entrants"]:
        if e["season"] == str(target_season):
            o = by_origin[e["origin"]]
            multipliers[int(e["team_id"])] = {"att": o["att"], "con": o["con"], "origin": e["origin"]}
    return multipliers, by_origin

def adjusted_lambdas(model, home, away, arm, multipliers, counts):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x2"):
        ah *= min(1, counts.get(home, 0) / 6); da *= min(1, counts.get(away, 0) / 6)
        aa *= min(1, counts.get(away, 0) / 6); dh *= min(1, counts.get(home, 0) / 6)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        mh, ma = multipliers.get(home), multipliers.get(away)
        if mh: lh *= math.exp(mh["att"]); la *= math.exp(mh["con"])
        if ma: la *= math.exp(ma["att"]); lh *= math.exp(ma["con"])
    return lh, la
