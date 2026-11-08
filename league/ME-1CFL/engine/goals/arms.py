"""The two preregistered G-ME prediction arms."""
import math
from collections import defaultdict

ARMS = ("gate_zero", "shrink")


def match_counts(games):
    counts = defaultdict(int)
    for game in games:
        counts[game["hi"]] += 1
        counts[game["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, counts=None):
    assert arm in ARMS
    # Prereg: teams unseen in training start at the league mean, a = d = 0
    # (same as the G-CY2 seed, which reads defaultdict(float) = 0.0).
    ah, da = model.a.get(home, 0.0), model.d.get(away, 0.0)
    aa, dh = model.a.get(away, 0.0), model.d.get(home, 0.0)
    if arm == "shrink":
        counts = counts or {}
        home_factor = min(1.0, counts.get(home, 0) / 6.0)
        away_factor = min(1.0, counts.get(away, 0) / 6.0)
        ah *= home_factor; dh *= home_factor
        aa *= away_factor; da *= away_factor
    return math.exp(ah + da + model.h), math.exp(aa + dh)
