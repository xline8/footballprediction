"""G-RS arm adjustments layered over a fitted DC model.

Port of the FI-Veikkausliiga reference ``arms.py`` (same file in the
reference engine), with the RS adaptations listed below. Everything not
listed here is verbatim FI behaviour.

RS adaptations (frozen in PREREG_G_RS.md):
(a) Seasons are "YYYY/YYYY" strings, not plain years. The FI code did
    ``int(season)`` and ``str(int(s) - 1)``; that arithmetic is meaningless
    on "2022/2023". Season arithmetic here goes through the explicit
    ``SEASON_ORDER`` map and ``_prev_season()`` — no integer parsing of
    season strings anywhere.
(b) Entrant identification uses the previous season's REGULAR-phase teams
    only (``phase == "regular"``). The plain-absence rule catches the
    tier-2 qualification opponents (FK Graficar, Indjija), who appear in
    qualification rows but never as regular members; the regular-phase
    rule removes them (EDA.md F4). This applies both to the completed
    entrant transitions (the offset's estimation sample) and to the
    entrants of the predicted season (who gets the tilt).
(c) Entrant transitions are measured on league-member rows only
    (``phase != "qualification"``). The loader enforces this, so every
    row reaching this module is already league-member; the measurement
    itself additionally uses only the regular-phase team set for the
    previous-season membership test (see (b)).
(d) SHRINK is unchanged from FI: at prediction time a team with n < 6
    prior in-league matches has its log-ratings scaled, ``a *= n/6`` and
    ``d *= n/6`` (``adjusted_lambdas`` below, identical to FI).

Note on the SHRINK numeric identity (also present in FI): in this dev
run SHRINK is numerically identical to Gate Zero, by construction, not
by tuning. Every incumbent has >= 30 prior in-league matches (factor 1),
and every entrant has no fitted ratings at all (``a = d = 0`` in the
defaultdict, so scaling by ``n/6 = 0`` leaves 0). See README.md.
"""
import math
from collections import defaultdict

# Explicit season order. Season arithmetic must go through this map;
# never parse "YYYY/YYYY" strings as integers.
SEASON_ORDER = ("2021/2022", "2022/2023", "2023/2024", "2024/2025",
                "2025/2026", "2026/2027")
SEASON_IDX = {s: i for i, s in enumerate(SEASON_ORDER)}


def _prev_season(season):
    """Previous season in SEASON_ORDER, or None for the first season."""
    i = SEASON_IDX[season]
    return SEASON_ORDER[i - 1] if i > 0 else None


def mover_ids(*_):
    return set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def x2_multipliers(games, target):
    current = {t for g in target for t in (g["hi"], g["ai"])}
    seasons = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    # RS (b): previous-season membership is tested against REGULAR-phase
    # teams only, not against every team that appeared that season.
    regular_teams = defaultdict(set)
    for g in games:
        if g["phase"] == "regular":
            regular_teams[g["season"]].add(g["hi"])
            regular_teams[g["season"]].add(g["ai"])
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
            if team not in regular_teams.get(prev, set()):
                completed.append((s, team, gf / n - means[s][0], ga / n - means[s][1]))
    target_season = target[0]["season"]
    prior = [x for x in completed if SEASON_IDX[x[0]] < SEASON_IDX[target_season]]
    if len(prior) < 3: return {}
    g = max(math.log(.8), min(math.log(1.25), sum(x[2] for x in prior) / len(prior)))
    c = max(math.log(.8), min(math.log(1.25), sum(x[3] for x in prior) / len(prior)))
    prev_target = _prev_season(target_season)
    entrants = current - set(regular_teams.get(prev_target, set()))
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
