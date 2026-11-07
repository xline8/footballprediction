"""Materialise per-match shot-detail and lineup features from the
FotMob full-response store (data_enrichment/fotmob_full/, see
FOTMOB_FULL_COVERAGE.md) into one flat CSV for the next experiment
rounds:

    data_enrichment/shot_lineup_features.csv   (one row per stored match)

Sources per match are the stored matchDetails JSONs, joined via
fotmob_full_index.csv (no network, no fixture matching). Contents:

- shotmap aggregates per team, with the house SOT counting rule
  (on target, not blocked, not own goal — the rule that reconciles
  with football-data HST/AST): shots, SOT, xG, xG on target, blocked
  on-target, inside-box shots, per-half shots / SOT / xG, mean shot x
  (FotMob pitch coordinate toward the attacked goal; higher = closer
  to goal) and the share of shots from x >= 80;
- match stats (All period, [home, away] pairs): possession, big
  chances, corners, keeper saves, fouls, cards;
- lineup: formation string, starter count, unavailable-player count,
  and FotMob's team rating for the match;
- QC columns: the spine's football-data FT SOT and the delta of the
  extracted SOT sum against it.

IMPORTANT for experiment use: these are per-match materialisations.
Some fields are only known after the match (team rating, the stats
themselves); any model feature built from this file must be a
trailing aggregate over strictly earlier matches, under the usual
walk-forward discipline. This script makes no modelling claims.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from backfill_sot_fotmob import load_master  # noqa: E402

INDEX = BASE / "data_enrichment" / "fotmob_full_index.csv"
OUT = BASE / "data_enrichment" / "shot_lineup_features.csv"
STAT_KEYS = {"BallPossesion": "possession", "big_chance": "big_chances",
             "corners": "corners", "keeper_saves": "saves",
             "fouls": "fouls", "yellow_cards": "yellow", "red_cards": "red"}
FIELDS = (["div", "season", "date", "home", "away", "fotmob_match_id"] +
          [f"{p}_{s}" for s in ("h", "a") for p in
           ("shots", "sot", "xg", "xgot", "blocked_ot", "inside_box",
            "shots_1h", "shots_2h", "sot_1h", "sot_2h", "xg_1h", "xg_2h",
            "mean_x", "deep_share", "possession", "big_chances", "corners",
            "saves", "fouls", "yellow", "red")] +
          ["formation_h", "formation_a", "starters_h", "starters_a",
           "unavailable_h", "unavailable_a", "team_rating_h",
           "team_rating_a", "fd_sot_ft", "sot_delta"])


def stat_pair(periods_all: dict, key: str):
    for section in (periods_all or {}).get("stats", []):
        for st in section.get("stats", []):
            if st.get("key") == key:
                raw = st.get("stats") or []
                if len(raw) == 2 and all(
                        isinstance(v, (int, float)) for v in raw):
                    return raw[0], raw[1]
    return None, None


def team_shot_agg(shots: list, team_id) -> dict:
    mine = [s for s in shots if s.get("teamId") == team_id]
    agg = {"shots": len(mine), "sot": 0, "xg": 0.0, "xgot": 0.0,
           "blocked_ot": 0, "inside_box": 0,
           "shots_1h": 0, "shots_2h": 0, "sot_1h": 0, "sot_2h": 0,
           "xg_1h": 0.0, "xg_2h": 0.0, "mean_x": None, "deep_share": None}
    xs = []
    for s in mine:
        half = 1 if s.get("period") == "FirstHalf" else 2
        agg[f"shots_{half}h"] += 1
        xg = s.get("expectedGoals") or 0.0
        agg["xg"] += xg
        agg[f"xg_{half}h"] += xg
        if s.get("x") is not None:
            xs.append(float(s["x"]))
        if s.get("isFromInsideBox"):
            agg["inside_box"] += 1
        if s.get("isOwnGoal") or s.get("isOnTarget") is not True:
            continue
        if s.get("isBlocked") is True:
            agg["blocked_ot"] += 1
            continue
        agg["sot"] += 1
        agg[f"sot_{half}h"] += 1
        agg["xgot"] += s.get("expectedGoalsOnTarget") or 0.0
    if xs:
        agg["mean_x"] = round(sum(xs) / len(xs), 2)
        agg["deep_share"] = round(
            sum(1 for x in xs if x >= 80) / len(xs), 3)
    agg["xg"] = round(agg["xg"], 3)
    agg["xgot"] = round(agg["xgot"], 3)
    agg["xg_1h"] = round(agg["xg_1h"], 3)
    agg["xg_2h"] = round(agg["xg_2h"], 3)
    return agg


def main() -> int:
    spine = {(r["Div"], r["Date"], r["HomeTeam"], r["AwayTeam"]):
             int(float(r["HST"])) + int(float(r["AST"]))
             for r in load_master()}
    rows = []
    n_shotmap = n_lineup = 0
    with INDEX.open(encoding="utf-8", newline="") as fh:
        index = list(csv.DictReader(fh))
    for ix in index:
        payload = json.loads((BASE / ix["path"]).read_text(encoding="utf-8"))
        content = payload.get("content") or {}
        teams = (payload.get("header") or {}).get("teams") or []
        shots = (content.get("shotmap") or {}).get("shots") or []
        row = {k: ix[k] for k in
               ("div", "season", "date", "home", "away", "fotmob_match_id")}
        aggs = {}
        if len(teams) == 2 and shots:
            n_shotmap += 1
            aggs = {"h": team_shot_agg(shots, teams[0].get("id")),
                    "a": team_shot_agg(shots, teams[1].get("id"))}
        periods_all = ((content.get("stats") or {}).get("Periods")
                       or {}).get("All") or {}
        for s, agg in aggs.items():
            for k, v in agg.items():
                row[f"{k}_{s}"] = v
        for key, name in STAT_KEYS.items():
            hv, av = stat_pair(periods_all, key)
            row[f"{name}_h"], row[f"{name}_a"] = hv, av
        lineup = content.get("lineup") or {}
        for s, side in (("h", "homeTeam"), ("a", "awayTeam")):
            team = lineup.get(side) or {}
            row[f"formation_{s}"] = team.get("formation")
            row[f"starters_{s}"] = len(team.get("starters") or [])
            row[f"unavailable_{s}"] = len(team.get("unavailable") or [])
            row[f"team_rating_{s}"] = team.get("rating")
        if lineup:
            n_lineup += 1
        fd = spine.get((ix["div"], ix["date"], ix["home"], ix["away"]))
        row["fd_sot_ft"] = fd
        if aggs and fd is not None:
            row["sot_delta"] = (aggs["h"]["sot"] + aggs["a"]["sot"]) - fd
        rows.append(row)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    deltas = [r["sot_delta"] for r in rows if r.get("sot_delta") is not None]
    exact = sum(1 for d in deltas if d == 0)
    print(f"rows: {len(rows)} | with shotmap aggregates: {n_shotmap} | "
          f"with lineup: {n_lineup}")
    print(f"SOT delta vs spine: n={len(deltas)} exact={exact} "
          f"({100 * exact / len(deltas):.1f}%) "
          f"mean|delta|={sum(abs(d) for d in deltas) / len(deltas):.3f}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
