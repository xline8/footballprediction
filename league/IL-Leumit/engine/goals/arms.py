"""Prediction-time adjustments for the registered G-IL arms."""
import math
from collections import Counter


def mover_tiers(target_season, leumit_rows, haal_by_season):
    year = int(target_season[:4])
    prior = f"{year - 1}/{year}"
    prior_il = {r["hi"] for r in leumit_rows if r["season"] == prior} | {r["ai"] for r in leumit_rows if r["season"] == prior}
    target = {r["hi"] for r in leumit_rows if r["season"] == target_season} | {r["ai"] for r in leumit_rows if r["season"] == target_season}
    haal = haal_by_season.get(prior, set())
    movers = {}
    for team in target - prior_il:
        if team in haal:
            movers[team] = "down"
        else:
            # Tier-3 records are not in the warehouse; a new Leumit club not
            # found in ha'Al is consequently the registered up-mover tier.
            movers[team] = "up"
    return movers


def prior_counts(games):
    counts = Counter()
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts, movers):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        for team, kind in ((home, "home"), (away, "away")):
            factor = min(counts[team], 6) / 6.0
            if kind == "home":
                ah *= factor; dh *= factor
            else:
                aa *= factor; da *= factor
    if arm == "x2":
        mu = model.mu
        def offsets(team):
            if movers.get(team) == "down":
                return math.log((mu + 0.291) / mu), math.log(max(mu - 0.239, 0.10) / mu)
            if movers.get(team) == "up":
                return math.log(max(mu - 0.080, 0.10) / mu), math.log((mu + 0.109) / mu)
            return 0.0, 0.0
        home_a, home_d = offsets(home); away_a, away_d = offsets(away)
        ah += home_a; dh += home_d; aa += away_a; da += away_d
    return math.exp(ah + da + model.h), math.exp(aa + dh)
