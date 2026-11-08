"""The preregistered Gate Zero, SHRINK, and X2 adjustments."""
import math
from collections import defaultdict

def mover_ids(target_season, rows):
    seasons = sorted({r["season"] for r in rows}); i = seasons.index(target_season)
    prior = seasons[i-1] if i else None
    current = {r["hi"] for r in rows if r["season"] == target_season} | {r["ai"] for r in rows if r["season"] == target_season}
    previous = ({r["hi"] for r in rows if r["season"] == prior} | {r["ai"] for r in rows if r["season"] == prior}) if prior else set()
    return current - previous

def match_counts(games):
    counts = defaultdict(int)
    for g in games: counts[g["hi"]] += 1; counts[g["ai"]] += 1
    return counts

def adjusted_lambdas(model, home, away, arm, movers, counts):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        sh = min(1.0, counts.get(home, 0)/6.0); sa = min(1.0, counts.get(away, 0)/6.0)
        ah *= sh; dh *= sh; aa *= sa; da *= sa
    if arm == "x2":
        shift_a = math.log(max(model.mu - 0.093, 0.10) / model.mu)
        shift_d = math.log((model.mu + 0.181) / model.mu)
        if home in movers: ah += shift_a; dh += shift_d
        if away in movers: aa += shift_a; da += shift_d
    return math.exp(ah + da + model.h), math.exp(aa + dh)
