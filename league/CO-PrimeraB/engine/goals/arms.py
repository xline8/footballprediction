"""Prediction-time arm logic for G-CO."""
import math
from collections import Counter

def prior_match_counts(games):
    counts = Counter()
    for game in games: counts[game["hi"]] += 1; counts[game["ai"]] += 1
    return counts

def adjusted_lambdas(model, home, away, arm, counts, home_mover_down=False, away_mover_down=False):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        home_factor = min(counts[home], 6) / 6.0; away_factor = min(counts[away], 6) / 6.0
        ah *= home_factor; dh *= home_factor; aa *= away_factor; da *= away_factor
    elif arm == "x2":
        if home_mover_down: ah, dh = math.log(1.10), dh
        if away_mover_down: aa, da = math.log(1.10), da
        if home_mover_down: dh = math.log(0.73)
        if away_mover_down: da = math.log(0.73)
    elif arm != "gate_zero":
        raise ValueError(f"unknown arm: {arm}")
    return math.exp(ah + da + model.h), math.exp(aa + dh)
