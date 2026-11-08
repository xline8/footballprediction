"""G-BRC arm adjustments layered over a fitted DC model.

Movers are keyed by FotMob TEAM ID, never by name (Série C team names
vary by spelling: accents, hyphens, abbreviations). Team-id sets per
(league, season) come from the two leagues' analysis CSVs, which carry
team ids: league/BR-SerieC/data/brc_matches.csv (C) and
league/BR-SerieB/data/brb_matches.csv (B).

Prereg offsets (PREREG_G_BRC.md, lambda space, floor
max(mu+delta, 0.10)/mu):
  ex-B:      for dGF -0.0405, against dGA -0.0868
  newcomer:  for dGF -0.0627, against dGA +0.0667
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRC_CSV = ROOT / "data" / "brc_matches.csv"
# Série B analysis CSV (team ids per season). It is a gitignored runtime
# file: present in the main checkout, not in a fresh worktree. Resolve
# the worktree copy first, else the main checkout (same MAIN_REPO
# pattern as data/build_data.py).
_BRB_CANDIDATES = [
    Path(__file__).resolve().parents[2].parent / "BR-SerieB" / "data" / "brb_matches.csv",
    Path("/home/hatch/workspace/footballprediction/league/BR-SerieB/data/brb_matches.csv"),
]
BRB_CSV = next((p for p in _BRB_CANDIDATES if p.exists()), _BRB_CANDIDATES[0])

# Frozen mover id sets from PREREG_G_BRC.md (asserted in mover_ids()).
EXPECTED_MOVERS = {
    "2022": {"ex-B": {"162165", "162167", "1626", "7733"},
             "newcomer": {"109708", "165546", "239122", "696928"}},
    "2023": {"ex-B": {"197429", "197692", "2369", "239132"},
             "newcomer": {"1221708", "1340094", "231931", "47387"}},
    "2024": {"ex-B": {"109708", "162176", "298660", "414725"},
             "newcomer": {"1221604", "172206", "197695", "581832"}},
    "2025": {"ex-B": {"104823", "197692", "7817", "8630"},
             "newcomer": {"1116984", "197398", "412808", "509487"}},
}

X2_DELTAS = {"ex-B": (-0.0405, -0.0868), "newcomer": (-0.0627, 0.0667)}


def _id_sets(path):
    out = defaultdict(set)
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["season"]].add(str(r["home_team_id"]))
            out[r["season"]].add(str(r["away_team_id"]))
    return out


def mover_ids_for_season(target_season):
    """Return {team_id: tier} for movers into target_season (ids as str).

    ex-B: in C(target) and B(target-1), not in C(target-1).
    newcomer: in C(target), in neither B(target-1) nor C(target-1).
    """
    prior = str(int(target_season) - 1)
    c_sets = _id_sets(BRC_CSV)
    b_sets = _id_sets(BRB_CSV)
    cur = c_sets[target_season]
    c_prev = c_sets[prior]
    b_prev = b_sets[prior]
    movers = {}
    for tid in sorted(cur - c_prev):
        if tid in b_prev:
            movers[tid] = "ex-B"
        else:
            movers[tid] = "newcomer"
    return movers


def mover_ids(games, target, cutoff):
    """Compatibility wrapper: derive movers for the target season.

    `target` rows carry a "season" key; the season is taken from the
    first target row. The derived sets are asserted against the frozen
    prereg lists for dev seasons 2022-2025.
    """
    season = str(target[0]["season"])
    movers = mover_ids_for_season(season)
    if season in EXPECTED_MOVERS:
        expected = {}
        for tier, ids in EXPECTED_MOVERS[season].items():
            for tid in ids:
                expected[tid] = tier
        if movers != expected:
            raise ValueError(
                f"mover set mismatch for {season}: derived {movers} != "
                f"prereg {expected}")
    return movers


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, movers, multipliers=None, counts=None):
    """Return (lambda_home, lambda_away) for one match under an arm.

    `home`/`away` are team ids (int). `movers` maps team-id-as-str to
    tier ("ex-B" / "newcomer"). Offsets are lambda-space multipliers
    per PREREG_G_BRC.md; the rating-shift equivalent is log(mult).
    """
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x2":
        mu = model.mu
        for team, tier in ((home, movers.get(str(home))), (away, movers.get(str(away)))):
            if tier is None:
                continue
            dgf, dga = X2_DELTAS[tier]
            mult_for = max(mu + dgf, 0.10) / mu
            mult_against = max(mu + dga, 0.10) / mu
            if team == home:
                lh *= mult_for
                la *= mult_against
            else:
                la *= mult_for
                lh *= mult_against
    return lh, la
