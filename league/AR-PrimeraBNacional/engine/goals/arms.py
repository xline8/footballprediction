"""BNAC goals arms: Gate Zero and preregistered X2 newcomer offsets."""
import math

def mover_ids(target_season, rows):
    seasons = sorted({r["season"] for r in rows}); i = seasons.index(target_season)
    prior = seasons[i-1] if i else None
    cur = {r["hi"] for r in rows if r["season"] == target_season} | {r["ai"] for r in rows if r["season"] == target_season}
    old = ({r["hi"] for r in rows if r["season"] == prior} | {r["ai"] for r in rows if r["season"] == prior}) if prior else set()
    return cur - old

def adjusted_lambdas(model, home, away, arm, movers):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "x2":
        mu = model.mu
        ao = math.log(max(mu - 0.087, 0.10) / mu)
        do = math.log((mu + 0.036) / mu)
        if home in movers: ah += ao; dh += do
        if away in movers: aa += ao; da += do
    return math.exp(ah + da + model.h), math.exp(aa + dh)
