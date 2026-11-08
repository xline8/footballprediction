"""G-CY2 arm adjustments: Gate Zero, X2, and SHRINK."""
import math
from collections import defaultdict

def mover_ids(target_season, cy2_rows, cy1_team_seasons):
    seasons = cy1_team_seasons.get("seasons", cy1_team_seasons)
    years = sorted(seasons)
    if target_season not in years or years.index(target_season) == 0: return set()
    prior = years[years.index(target_season) - 1]
    cy1 = {int(t) for t in seasons.get(prior, {})}
    cy2_prior = {r["hi"] for r in cy2_rows if r["season"] == prior} | {r["ai"] for r in cy2_rows if r["season"] == prior}
    cy2_target = {r["hi"] for r in cy2_rows if r["season"] == target_season} | {r["ai"] for r in cy2_rows if r["season"] == target_season}
    # Prereg definition: CY-1 in the prior season, NOT CY-2 in the prior
    # season, AND playing CY-2 in the target season. The last clause is
    # load-bearing: without it every CY-1 stalwart is a false "mover".
    return (cy1 - cy2_prior) & cy2_target

def match_counts(games):
    counts = defaultdict(int)
    for g in games: counts[g["hi"]] += 1; counts[g["ai"]] += 1
    return counts

def adjusted_lambdas(model, home, away, arm, movers=None, counts=None):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "x2":
        mu = model.mu
        if home in (movers or set()): ah += math.log((mu + .08) / mu); dh += math.log(max(mu - .21, .10) / mu)
        if away in (movers or set()): aa += math.log((mu + .08) / mu); da += math.log(max(mu - .21, .10) / mu)
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    return math.exp(ah + da + model.h), math.exp(aa + dh)
