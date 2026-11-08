"""G-KW arm adjustments layered over a fitted DC model.

Identical to the reference arms.py EXCEPT the entrant rule uses the
frozen canonical season ORDER (KW seasons are split-season labels,
not integers): "previous season" = the preceding label in
SEASON_ORDER. Documented divergence #2 in PREREG_G_KW.md; the rule
itself (mean GF/GA diff of completed entrant transitions, clamped
to [log 0.8, log 1.25], 0 if fewer than 3) is unchanged.
"""
import math
from collections import defaultdict

SEASON_ORDER = ["2021", "2021/2022", "2022/2023", "2023/2024",
                "2024/2025", "2025/2026", "2026/2027"]
SORD = {s: i for i, s in enumerate(SEASON_ORDER)}


def mover_ids(*_):
    return set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def _prev_season(s):
    i = SORD[s]
    return SEASON_ORDER[i - 1] if i > 0 else None


def x2_multipliers(games, target):
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
        prev = _prev_season(s)
        if prev is None or prev not in seasons: continue  # first corpus season: absence unverifiable, not an entrant transition
        for team, (n, gf, ga) in teams.items():
            if team not in seasons.get(prev, {}):
                completed.append((s, team, gf / n - means[s][0], ga / n - means[s][1]))
    target_season = target[0]["season"]
    prior = [x for x in completed if SORD[x[0]] < SORD[target_season]]
    if len(prior) < 3: return {}
    g = max(math.log(.8), min(math.log(1.25), sum(x[2] for x in prior) / len(prior)))
    c = max(math.log(.8), min(math.log(1.25), sum(x[3] for x in prior) / len(prior)))
    prev_target = _prev_season(target_season)
    entrants = current - set(seasons.get(prev_target, {}))
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
