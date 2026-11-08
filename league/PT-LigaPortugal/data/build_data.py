#!/usr/bin/env python3
"""Build the flat Liga Portugal match table from the FotMob warehouse."""
import csv
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from league.jleague_lib import flat_stats, shots_of, ht_from_events  # noqa: E402

LEAGUE_ID = "61"
STAT_NAMES = {
    "expected_goals": "xg", "expected_goals_open_play": "xg_open",
    "expected_goals_set_play": "xg_set", "expected_goals_on_target": "xgot",
    "total_shots": "shots", "ShotsOnTarget": "sot", "ShotsOffTarget": "shots_off",
    "blocked_shots": "blocked", "corners": "corners", "yellow_cards": "yellow",
    "red_cards": "red", "BallPossesion": "poss", "big_chance": "bigchance",
    "touches_opp_box": "touches", "fouls": "fouls",
}


def warehouse_root():
    explicit = os.environ.get("FOOTMOB_WORLD_ROOT")
    if explicit:
        return Path(explicit)
    local = REPO / "data_enrichment"
    if (local / "fotmob_world").exists():
        return local
    return Path("/home/hatch/workspace/footballprediction/data_enrichment")


def load_index():
    with open(REPO / "data_enrichment/fotmob_world_index.csv", newline="") as f:
        return [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]


def val(x):
    return "" if x is None else x


def main():
    rows = []
    root = warehouse_root()
    for ix in load_index():
        path = root.parent / ix["path"]
        with open(path) as f:
            d = json.load(f)
        h = d.get("header") or {}
        status = h.get("status") or {}
        if not status.get("finished"):
            continue
        teams = h.get("teams") or [{}, {}]
        home, away = teams[0], teams[1]
        content = d.get("content") or {}
        row = {"match_id": ix["match_id"], "season": ix["season"], "date": ix["date"],
               "home_team": home.get("name", ""), "away_team": away.get("name", ""),
               "home_id": home.get("id", ""), "away_id": away.get("id", ""),
               "home_goals": val(home.get("score")), "away_goals": val(away.get("score"))}
        stats = flat_stats(content)
        fh = stats.get(("FirstHalf", "goals"))
        if fh is None:
            ht = ht_from_events(content)
            fh = ht if ht is not None else (None, None)
        row["ht_home"], row["ht_away"] = val(fh[0]), val(fh[1])
        info = (content.get("matchFacts") or {}).get("infoBox") or {}
        row["referee"] = ((info.get("Referee") or {}).get("text") or "")
        for period, suffix in (("All", ""), ("FirstHalf", "_1h")):
            for key, name in STAT_NAMES.items():
                pair = stats.get((period, key), (None, None))
                row[f"{name}_home{suffix}"] = val(pair[0])
                row[f"{name}_away{suffix}"] = val(pair[1])
        sm = {"sm_shots_home": 0, "sm_shots_away": 0, "sm_xg_home": 0.0, "sm_xg_away": 0.0,
              "sm_xgot_home": 0.0, "sm_xgot_away": 0.0, "sm_xgot_n_home": 0, "sm_xgot_n_away": 0}
        for shot in shots_of(content):
            if shot.get("period") == "PenaltyShootout":
                continue
            side = "home" if shot.get("teamId") == home.get("id") else "away" if shot.get("teamId") == away.get("id") else None
            if side is None:
                continue
            sm[f"sm_shots_{side}"] += 1
            sm[f"sm_xg_{side}"] += float(shot.get("expectedGoals") or 0)
            if shot.get("expectedGoalsOnTarget") is not None:
                sm[f"sm_xgot_{side}"] += float(shot["expectedGoalsOnTarget"])
                sm[f"sm_xgot_n_{side}"] += 1
        row.update(sm)
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    fields = ["match_id", "season", "date", "home_team", "away_team", "home_id", "away_id",
              "home_goals", "away_goals", "ht_home", "ht_away", "referee"]
    for suffix in ("", "_1h"):
        for name in STAT_NAMES.values():
            fields += [f"{name}_home{suffix}", f"{name}_away{suffix}"]
    fields += ["sm_shots_home", "sm_shots_away", "sm_xg_home", "sm_xg_away",
               "sm_xgot_home", "sm_xgot_away", "sm_xgot_n_home", "sm_xgot_n_away"]
    out = Path(__file__).resolve().parent / "pt_matches.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"Wrote {out}: {len(rows)} rows")
    for season in sorted({r["season"] for r in rows}):
        print(season, sum(r["season"] == season for r in rows))


if __name__ == "__main__":
    main()
