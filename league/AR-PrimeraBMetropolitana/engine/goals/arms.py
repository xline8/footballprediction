"""G-PBM arm adjustments."""
import math

GF_GAP = -0.0325
GA_GAP = -0.0410


def newcomer_ids(target_block, rows):
    prior = str(int(target_block) - 1)
    current = {r["hi"] for r in rows if r["season"] == target_block} | {r["ai"] for r in rows if r["season"] == target_block}
    previous = {r["hi"] for r in rows if r["season"] == prior} | {r["ai"] for r in rows if r["season"] == prior}
    return current - previous


def adjusted_lambdas(model, home, away, arm, newcomers):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    offsets = {}
    if arm == "x2":
        mu = model.mu
        att_offset = math.log(max(mu + GF_GAP, 0.10) / mu)
        def_offset = math.log(max(mu + GA_GAP, 0.10) / mu)
        for team, side in ((home, "home"), (away, "away")):
            if team in newcomers:
                offsets[team] = {"attack": att_offset, "defence": def_offset}
        if home in newcomers:
            ah += att_offset; dh += def_offset
        if away in newcomers:
            aa += att_offset; da += def_offset
    return math.exp(ah + da + model.h), math.exp(aa + dh), offsets
