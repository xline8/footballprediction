#!/usr/bin/env python3
"""Build the CO-PrimeraB match CSV from the FotMob world warehouse."""
import csv
import json
import os

MAIN = os.path.expanduser("~/workspace/footballprediction")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "co_primerab_matches.csv")
INDEX = os.path.join(MAIN, "data_enrichment", "fotmob_world_index.csv")


def read_json(row):
    with open(os.path.join(MAIN, row["path"]), encoding="utf-8") as handle:
        return json.load(handle)


def finished_b_teams(index_rows):
    teams = {}
    for row in index_rows:
        if row["league_id"] != "9125":
            continue
        data = read_json(row)
        if not data["header"]["status"].get("finished"):
            continue
        season = row["season"]
        teams.setdefault(season, set()).update((data["general"]["homeTeam"]["id"],
                                                data["general"]["awayTeam"]["id"]))
    return teams


def a_teams(index_rows):
    teams = {}
    for row in index_rows:
        if row["league_id"] != "274":
            continue
        year = row["season"][:4]
        data = read_json(row)
        general = data["general"]
        teams.setdefault(year, set()).update((general["homeTeam"]["id"], general["awayTeam"]["id"]))
    return teams


def is_goal(event):
    return event.get("type") == "Goal" and not event.get("isPenaltyShootoutEvent", False)


def main():
    with open(INDEX, encoding="utf-8") as handle:
        index_rows = list(csv.DictReader(handle))
    previous_b = finished_b_teams(index_rows)
    first_a = a_teams(index_rows)
    fields = ["match_id", "season", "date", "round", "tournament", "phase",
              "home_team_id", "home_team", "away_team_id", "away_team",
              "home_goals", "away_goals", "goals_1h", "events_exact", "home_red",
              "away_red", "home_mover_down", "away_mover_down"]
    rows = []
    for index_row in index_rows:
        if index_row["league_id"] != "9125":
            continue
        data = read_json(index_row)
        status = data["header"]["status"]
        if not status.get("finished"):
            continue
        general = data["general"]
        header = data["header"]
        info = ((data.get("content") or {}).get("matchFacts") or {}).get("infoBox") or {}
        tournament_info = info.get("Tournament") or {}
        tournament = tournament_info.get("leagueName", "")
        round_name = str(general.get("matchRound") or "")
        phase_text = f"{tournament} {round_name}"
        if "Playoff" in phase_text or "Quadrangular" in phase_text:
            phase = "quadrangular"
        elif "Final" in phase_text:
            phase = "final"
        else:
            phase = "regular"
        events = (((data.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
        goal_events = [event for event in events if is_goal(event)]
        home_goals = int(header["teams"][0]["score"])
        away_goals = int(header["teams"][1]["score"])
        exact = len(goal_events) == home_goals + away_goals
        goals_1h = "" if not exact else sum(1 for event in goal_events if (event.get("time") or 999) <= 45)
        season = index_row["season"]
        if season == "2021":
            movers = (False, False)
        else:
            prior = previous_b.get(str(int(season) - 1), set())
            top = first_a.get(str(int(season) - 1), set())
            movers = (general["homeTeam"]["id"] not in prior and general["homeTeam"]["id"] in top,
                      general["awayTeam"]["id"] not in prior and general["awayTeam"]["id"] in top)
        rows.append({"match_id": index_row["match_id"], "season": season,
                     "date": general["matchTimeUTCDate"][:10], "round": round_name,
                     "tournament": tournament, "phase": phase,
                     "home_team_id": general["homeTeam"]["id"], "home_team": general["homeTeam"]["name"],
                     "away_team_id": general["awayTeam"]["id"], "away_team": general["awayTeam"]["name"],
                     "home_goals": home_goals, "away_goals": away_goals,
                     "goals_1h": goals_1h, "events_exact": exact,
                     "home_red": status.get("numberOfHomeRedCards", 0),
                     "away_red": status.get("numberOfAwayRedCards", 0),
                     "home_mover_down": movers[0], "away_mover_down": movers[1]})
    rows.sort(key=lambda row: (row["date"], row["match_id"]))
    counts = {str(year): sum(row["season"] == str(year) for row in rows) for year in range(2021, 2027)}
    expected = {"2021": 144, "2022": 289, "2023": 310, "2024": 310, "2025": 308, "2026": 278}
    assert counts == expected, counts
    with open(OUT, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {OUT}")
    print("per-season counts:", counts)


if __name__ == "__main__":
    main()
