"""Prediction-time arm logic for G-GE."""
import math
from collections import Counter


def prior_match_counts(games):
    counts = Counter()
    for game in games:
        counts[game["hi"]] += 1
        counts[game["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        home_factor = min(counts[home], 6) / 6.0
        away_factor = min(counts[away], 6) / 6.0
        ah *= home_factor; dh *= home_factor
        aa *= away_factor; da *= away_factor
    elif arm != "gate_zero":
        raise ValueError(f"unknown arm: {arm}")
    return math.exp(ah + da + model.h), math.exp(aa + dh)
