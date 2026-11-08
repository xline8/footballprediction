"""FNL goal-model arm adjustments."""
import csv, json, math
from collections import defaultdict
from pathlib import Path

INDEX = Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
CZ_DATA = Path("/home/hatch/workspace/footballprediction/league/CZ-Liga/data/cz_matches.csv")
OFFSETS = {"2022/2023": (0.0, 0.0), "2023/2024": (0.545833, -0.154167), "2024/2025": (0.240625, -0.092708), "2025/2026": (0.240278, -0.326389)}
MOVER_IDS = {"2022/2023": {143833}, "2023/2024": {1673}, "2024/2025": {1860}, "2025/2026": {7840}}

def _regular_cz_match_ids():
    with CZ_DATA.open(newline="", encoding="utf-8") as fh:
        return {r["match_id"] for r in csv.DictReader(fh) if r["phase"] != "placement"}

def _index_team_ids(league_id, season, allowed_match_ids=None):
    found = set()
    with INDEX.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["league_id"] != str(league_id) or row["season"] != season or (allowed_match_ids is not None and row["match_id"] not in allowed_match_ids): continue
            payload = json.loads((INDEX.parent.parent / row["path"]).read_text(encoding="utf-8"))
            found.update(int(t["id"]) for t in ((payload.get("header") or {}).get("teams") or []))
    return found

def _assert_movers():
    regular_cz = _regular_cz_match_ids()
    for target, ids in MOVER_IDS.items():
        prior = f"{int(target[:4]) - 1}/{int(target[-4:]) - 1}"
        cz, fnl = _index_team_ids(122, prior, regular_cz), _index_team_ids(253, prior)
        assert ids <= cz, f"mover ids missing from CZ-Liga {prior}: {ids - cz}"
        assert not ids & fnl, f"mover ids present in FNL {prior}: {ids & fnl}"
_assert_movers()

def mover_ids(target_season): return set(MOVER_IDS.get(target_season, set()))

def match_counts(games):
    counts = defaultdict(int)
    for g in games: counts[g["hi"]] += 1; counts[g["ai"]] += 1
    return counts

def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None, mu=0.0):
    ah, da, aa, dh = model.a[home], model.d[away], model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        dgf, dga = multipliers
        if home in movers: lh *= max(mu + dgf, 0.10) / mu; la *= (mu + dga) / mu
        if away in movers: la *= max(mu + dgf, 0.10) / mu; lh *= (mu + dga) / mu
    return lh, la
