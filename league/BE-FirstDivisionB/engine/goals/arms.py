"""G-BEB prediction-time arm adjustments."""
import math
from collections import defaultdict

EXPECTED_MOVERS = {
    "2022/2023": {583877},
    "2023/2024": {149408, 8573, 10000},
    "2024/2025": {9992, 6351},
}


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def mover_ids(parent_games, target_games, target_season):
    seasons = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
    idx = seasons.index(target_season)
    previous = seasons[idx - 1]
    parent = {g["hi"] for g in parent_games if g["season"] == previous}
    parent |= {g["ai"] for g in parent_games if g["season"] == previous}
    b_previous = {g["hi"] for g in target_games if g["season"] == previous}
    b_previous |= {g["ai"] for g in target_games if g["season"] == previous}
    b_target = {g["hi"] for g in target_games if g["season"] == target_season}
    b_target |= {g["ai"] for g in target_games if g["season"] == target_season}
    movers = (parent - b_previous) & b_target
    expected = EXPECTED_MOVERS[target_season]
    if movers != expected:
        raise AssertionError(f"mover sanity failed for {target_season}: {sorted(movers)} != {sorted(expected)}")
    return movers


def adjusted_lambdas(model, home, away, arm, movers, counts):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x2"):
        hn = min(1.0, counts.get(home, 0) / 6.0)
        an = min(1.0, counts.get(away, 0) / 6.0)
        ah *= hn; dh *= hn
        aa *= an; da *= an
    if arm == "x2":
        attack_offset = math.log(max(model.mu - 0.0982, 0.10) / model.mu)
        defence_offset = math.log(max(model.mu - 0.1106, 0.10) / model.mu)
        if home in movers:
            ah += attack_offset; dh += defence_offset
        if away in movers:
            aa += attack_offset; da += defence_offset
    return math.exp(ah + da + model.h), math.exp(aa + dh)
