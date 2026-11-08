"""Gate Zero and the preregistered X2 relegated-mover prior."""
import math


MOVER_NAMES = {
    "2022": ("Longford Town", "Waterford FC"),
    "2023": ("Finn Harps",),
    "2024": ("UCD", "Cork City"),
    "2025": ("Dundalk",),
    "2026": ("Cork City",),
}


def mover_ids(target_season, name_to_id):
    return {int(name_to_id[name]) for name in MOVER_NAMES.get(str(target_season), ())
            if name in name_to_id}


def adjusted_lambdas(model, home, away, arm, movers):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "x2":
        att = math.log(max(model.mu + 0.23, 0.10) / model.mu)
        deff = math.log(max(model.mu - 0.27, 0.10) / model.mu)
        if home in movers:
            ah += att
            dh += deff
        if away in movers:
            aa += att
            da += deff
    return math.exp(ah + da + model.h), math.exp(aa + dh)
