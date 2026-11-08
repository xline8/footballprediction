"""Build Tanzania Premier League match and team-match tables from the warehouse."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "9066"
FIELDS = ["match_id", "league", "season", "date", "round", "sub_tournament", "stage",
          "home_team_id", "home_team", "away_team_id", "away_team", "finished", "awarded",
          "home_goals", "away_goals", "has_events", "n_events", "n_goal_events",
          "n_card_events", "n_red_events", "ht_home_goals", "ht_away_goals", "ht_source",
          "ht_suspect", "has_stats_all", "has_stats_half", "has_shotmap", "referee",
          "has_lineup", "lineup_block", "eligible"]


def _score(value):
    value = str(value).replace(" ", "")
    a, b = value.split("-", 1)
    return int(a), int(b)


def build(index_row, warehouse_root=MAIN_REPO):
    payload = json.loads((warehouse_root / index_row["path"]).read_text(encoding="utf-8"))
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    content = payload.get("content") or {}
    facts = content.get("matchFacts") or {}
    events = ((facts.get("events") or {}).get("events") or [])
    goals_events = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    cards = [e for e in events if e.get("type") == "Card"]
    half = next((e for e in events if e.get("type") == "Half" and str(e.get("time")) == "45"), None)
    info = facts.get("infoBox") or {}
    tournament = info.get("Tournament") or {}
    stats = content.get("stats")
    periods = stats.get("Periods") if isinstance(stats, dict) else None
    shotmap = content.get("shotmap")
    shots = shotmap.get("shots") if isinstance(shotmap, dict) else None
    referee = ((info.get("Referee") or {}).get("text") or "").strip()
    lineup = content.get("lineup")
    starters = bool((lineup or {}).get("homeTeam", {}).get("starters") or
                    (lineup or {}).get("awayTeam", {}).get("starters")) if isinstance(lineup, dict) else False
    home = general.get("homeTeam") or {}
    away = general.get("awayTeam") or {}
    goals = _score(index_row["score"])
    awarded = bool(status.get("awarded") is True or (status.get("reason") or {}).get("short") == "AW")
    ht_suspect = int(index_row["match_id"] == "4950929")
    return {
        "match_id": index_row["match_id"], "league": "TZ-PremierLeague", "season": index_row["season"],
        "date": index_row["date"], "round": str(tournament.get("round") or general.get("matchRound") or ""),
        "sub_tournament": tournament.get("leagueName") or "Premier League", "stage": "regular",
        "home_team_id": home.get("id"), "home_team": home.get("name") or index_row["home"],
        "away_team_id": away.get("id"), "away_team": away.get("name") or index_row["away"],
        "finished": int(bool(status.get("finished", general.get("finished", False)))), "awarded": int(awarded),
        "home_goals": goals[0], "away_goals": goals[1], "has_events": int(bool(events)),
        "n_events": len(events), "n_goal_events": len(goals_events), "n_card_events": len(cards),
        "n_red_events": sum(e.get("card") in ("Red", "YellowRed") for e in cards),
        "ht_home_goals": half.get("homeScore") if half else None,
        "ht_away_goals": half.get("awayScore") if half else None,
        "ht_source": "half_event" if half else None, "ht_suspect": ht_suspect,
        "has_stats_all": int(isinstance(stats, dict) and bool(periods and (periods.get("All") or periods.get("ALL")))),
        "has_stats_half": int(isinstance(periods, dict) and bool(periods.get("FirstHalf") and periods.get("SecondHalf"))),
        "has_shotmap": int(bool(shots)), "referee": referee, "has_lineup": int(starters),
        "lineup_block": int(isinstance(lineup, dict)), "eligible": int(not awarded),
    }


def main():
    with INDEX.open(encoding="utf-8", newline="") as f:
        rows = [build(r) for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    # Frozen build-time counts asserted as FLOORS (the AU/MLS runner
    # pattern): the daily runner rebuilds this table as the in-progress
    # season (2026/2027) grows, so exact-equality asserts would break
    # the rebuild. Completed seasons keep their exact counts; the
    # in-progress season and all totals are floors.
    assert len(rows) >= 1284
    expected = {"2021/2022": 239, "2022/2023": 240, "2023/2024": 240,
                "2024/2025": 240, "2025/2026": 239, "2026/2027": 84}
    per_season = {s: sum(r["eligible"] and r["season"] == s for r in rows) for s in expected}
    for s, n in expected.items():
        if s == "2026/2027":
            assert per_season[s] >= n, (s, per_season[s], n)
        else:
            assert per_season[s] == n, (s, per_season[s], n)
    assert sum(r["eligible"] for r in rows) >= 1282
    assert sum(r["awarded"] for r in rows) >= 2
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "tz_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        if not r["eligible"]: continue
        for side, other in (("home", "away"), ("away", "home")):
            team.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                         "stage": r["stage"], "sub_tournament": r["sub_tournament"],
                         "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                         "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]})
    assert len(team) >= 2564
    with (HERE / "tz_team_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} eligible={sum(r['eligible'] for r in rows)} team_rows={len(team)}")


if __name__ == "__main__": main()
