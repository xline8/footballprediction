#!/usr/bin/env python3
"""Build the GE-Erovnuli analysis CSV from the FotMob world warehouse.
Goals-only league: stats/shotmap/period-splits are absent corpus-wide
(verified in analysis/DATA_UNDERSTANDING.md). Per-match JSONs resolve
against the MAIN checkout (warehouse is gitignored there).
One row per played match. Rerun: python3 build_data.py
"""
import csv, json, os
MAIN = os.path.expanduser("~/workspace/footballprediction")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ge_matches.csv")
rows = []
idx = [r for r in csv.DictReader(open(os.path.join(MAIN, "data_enrichment/fotmob_world_index.csv"))) if r["league_id"] == "439"]
for r in idx:
    d = json.load(open(os.path.join(MAIN, r["path"])))
    g, h = d["general"], d["header"]
    evs = ((d.get("content") or {}).get("matchFacts") or {}).get("events") or {}
    evs = evs.get("events") or []
    g1h = sum(1 for e in evs if e.get("type") == "Goal" and (e.get("time") or 999) <= 45)
    rows.append(dict(match_id=r["match_id"], season=r["season"], date=g["matchTimeUTCDate"][:10],
        round=g.get("matchRound"), home_team_id=g["homeTeam"]["id"], home_team=g["homeTeam"]["name"],
        away_team_id=g["awayTeam"]["id"], away_team=g["awayTeam"]["name"],
        home_goals=h["teams"][0]["score"], away_goals=h["teams"][1]["score"],
        goals_1h=g1h, home_red=h["status"].get("numberOfHomeRedCards", 0), away_red=h["status"].get("numberOfAwayRedCards", 0)))
rows.sort(key=lambda x: (x["date"], x["match_id"]))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"wrote {len(rows)} rows -> {OUT}")
