"""SK goals arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict
import csv
from pathlib import Path


MOVERS = {"2022/2023": {"Dukla Banska Bystrica", "Zeleziarne Podbrezova", "Skalica"}, "2023/2024": {"FC Kosice"}, "2024/2025": {"Komarno"}, "2025/2026": {"Tatran Presov"}}
OFFSETS = {"2022/2023": (0.0, 0.0), "2023/2024": (-0.008, 0.055), "2024/2025": (-0.135, 0.138), "2025/2026": (-0.162, 0.132)}

def mover_ids(target_season):
    path = Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
    found = set()
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["league_id"] == "8973":
                allnames = set().union(*MOVERS.values()); found.update({row["home"], row["away"]} & allnames)
    assert found == allnames, f"2. Liga mover index mismatch: {found}"
    return set(MOVERS[target_season]) if target_season in MOVERS else set()


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def x3_multipliers(*_):
    return {}


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None, mu=0.0):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x3"):
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        dgf, dga = multipliers
        if home in movers: lh *= max(mu + dgf, 0.10) / mu; la *= (mu + dga) / mu
        if away in movers: la *= max(mu + dgf, 0.10) / mu; lh *= (mu + dga) / mu
    return lh, la
