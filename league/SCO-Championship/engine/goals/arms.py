"""G-SCOCH arm adjustments: Gate Zero, SHRINK, and frozen X2."""
import math
from collections import defaultdict
import json
from pathlib import Path


def mover_ids(*_):
    try:
        data = json.loads((Path(__file__).resolve().parents[2] / "analysis" / "movers.json").read_text())
        return set(data) if isinstance(data, list) else set(data.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, movers=None, multipliers=None, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    if arm == "x2":
        # X2 offsets are injected by the harness when the frozen mover table
        # identifies a direction; absent/insufficient history is zero.
        for team, direction in ( (home, "home"), (away, "away") ):
            off = (multipliers or {}).get(team, (0.0, 0.0))
            if team == home: ah += off[0]; dh += off[1]
            else: aa += off[0]; da += off[1]
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    return lh, la
