"""G-SE arm adjustments layered over a fitted DC model."""
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


def x2_multipliers(games, target):
    seasons_order = ["2021", "2022", "2023", "2024", "2025"]
    current = {t for g in target for t in (g["hi"], g["ai"])}
    seasons = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for g in games:
        for team, n, gf, ga in ((g["hi"], 1, g["yh"], g["ya"]), (g["ai"], 1, g["ya"], g["yh"])):
            seasons[g["season"]][team][0] += n; seasons[g["season"]][team][1] += gf; seasons[g["season"]][team][2] += ga
    means = {}
    for s, teams in seasons.items():
        means[s] = (sum(gf / n for n, gf, _ in teams.values()) / len(teams), sum(ga / n for n, _, ga in teams.values()) / len(teams))
    completed = []
    for s, teams in seasons.items():
        prev = seasons_order[seasons_order.index(s) - 1] if s in seasons_order and seasons_order.index(s) else None
        if prev not in seasons: continue  # first corpus season: absence unverifiable, not an entrant transition
        for team, (n, gf, ga) in teams.items():
            if team not in seasons.get(prev, {}):
                completed.append((s, team, gf / n - means[s][0], ga / n - means[s][1]))
    prior = [x for x in completed if seasons_order.index(x[0]) < seasons_order.index(target[0]["season"])]
    if len(prior) < 3: return {}
    g = max(math.log(.8), min(math.log(1.25), sum(x[2] for x in prior) / len(prior)))
    c = max(math.log(.8), min(math.log(1.25), sum(x[3] for x in prior) / len(prior)))
    target_season = target[0]["season"]
    previous = seasons_order[seasons_order.index(target_season) - 1] if target_season in seasons_order and seasons_order.index(target_season) else None
    entrants = current - set(seasons.get(previous, {}))
    return {team: {"g": g, "c": c} for team in current if team in entrants}

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
