"""Compute the descriptive first-season mover gap for the CN feature review.

This is descriptive only: it does not fit ratings or estimate a model.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATCHES = HERE.parent / "data" / "cn_matches.csv"
OUT = HERE / "mover_gap.json"

rows = list(csv.DictReader(MATCHES.open()))
seasons = defaultdict(list)
for row in rows:
    seasons[row["season"]].append(row)

first_seen = {}
for season in sorted(seasons, key=int):
    for row in seasons[season]:
        for side in ("home", "away"):
            team = row[f"{side}_id"]
            first_seen.setdefault(team, season)

eligible = {team: season for team, season in first_seen.items() if int(season) >= 2023}
team_values = []
for team, season in sorted(eligible.items(), key=lambda item: (int(item[1]), item[0])):
    played = []
    for row in seasons[season]:
        if team == row["home_id"]:
            played.append((float(row["home_goals"]), float(row["away_goals"])))
        elif team == row["away_id"]:
            played.append((float(row["away_goals"]), float(row["home_goals"])))
    league = seasons[season]
    league_gf = sum(float(r["home_goals"]) + float(r["away_goals"]) for r in league) / (2 * len(league))
    # The league GA mean is identical to the league GF mean, but retain the
    # separate fields to make the direction of the mover gap explicit.
    gf = sum(v[0] for v in played) / len(played)
    ga = sum(v[1] for v in played) / len(played)
    team_values.append({
        "team_id": team,
        "first_season": season,
        "matches": len(played),
        "gf_per_match": round(gf, 6),
        "ga_per_match": round(ga, 6),
        "gf_gap_vs_season_mean": round(gf - league_gf, 6),
        "ga_gap_vs_season_mean": round(ga - league_gf, 6),
    })

def avg(key):
    return sum(v[key] for v in team_values) / len(team_values) if team_values else None

out = {
    "definition": "Teams whose first observed CN season is 2023 or later; first-season team GF/GA compared with that season's league team-match mean.",
    "n_teams": len(team_values),
    "mean_first_season_gf_per_match": round(avg("gf_per_match"), 6),
    "mean_first_season_ga_per_match": round(avg("ga_per_match"), 6),
    "mean_league_gf_gap": round(avg("gf_gap_vs_season_mean"), 6),
    "mean_league_ga_gap": round(avg("ga_gap_vs_season_mean"), 6),
    "teams": team_values,
}
OUT.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({k: out[k] for k in ("n_teams", "mean_league_gf_gap", "mean_league_ga_gap")}))
