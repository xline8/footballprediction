"""Build the Nigeria Professional Football League match tables.

The warehouse has 1,830 indexed payloads.  The 2025/2026 season has 379
matches because El Kanemi Warriors--Kun Khalifat is absent from both the
index and warehouse; this builder records the gap rather than inventing it.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
FIELDS = ["match_id", "league", "season", "date", "round", "sub_tournament", "stage",
          "home_team_id", "home_team", "away_team_id", "away_team", "finished", "awarded",
          "home_goals", "away_goals", "has_events", "n_events", "n_goal_events",
          "n_card_events", "n_red_events", "ht_home_goals", "ht_away_goals", "ht_source",
          "has_stats_all", "has_stats_half", "has_shotmap", "referee", "has_lineup", "eligible"]


def _score(value):
    a, b = (value or "").split("-", 1)
    return int(a.strip()), int(b.strip())


def build(index_row, warehouse_root=MAIN_REPO):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general = payload.get("general") or {}
    status = ((payload.get("header") or {}).get("status") or {})
    content = payload.get("content") or {}
    name = general.get("leagueName") or ""
    stage = ("championship_group" if "Championship" in name else
             "group_a" if "Grp. A" in name else
             "group_b" if "Grp. B" in name else "regular")
    home = general.get("homeTeam") or {}
    away = general.get("awayTeam") or {}
    finished = bool(status.get("finished"))
    awarded = bool(status.get("awarded"))
    goals = (None, None)
    if status.get("scoreStr"):
        goals = _score(status["scoreStr"])
    events = (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])
    goals_events = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    half = next((e for e in events if e.get("type") == "Half" and e.get("time") == 45), None)
    stats = content.get("stats") or {}
    periods = stats.get("Periods") or {}
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    referee = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    # Frozen anomaly handling: 4765626 has a stale finished flag, but its
    # score and six Goal events reconcile, so it remains eligible.
    stale_played = index_row["match_id"] == "4765626"
    eligible = int((finished or stale_played) and not awarded and stage != "championship_group")
    return {
        "match_id": index_row["match_id"], "league": "NG-ProfessionalLeague", "season": index_row["season"],
        "date": index_row["date"], "round": str(general.get("matchRound") or ""), "sub_tournament": name,
        "stage": stage, "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"), "finished": int(finished),
        "awarded": int(awarded), "home_goals": goals[0], "away_goals": goals[1],
        "has_events": int(bool(events)), "n_events": len(events), "n_goal_events": len(goals_events),
        "n_card_events": sum(e.get("type") == "Card" for e in events),
        "n_red_events": sum(e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") for e in events),
        "ht_home_goals": half.get("homeScore") if half else None,
        "ht_away_goals": half.get("awayScore") if half else None,
        "ht_source": "half_event" if half else None,
        "has_stats_all": int(any((periods.get(k) or {}).get("stats") or (periods.get(k) or {}).get("statistics")
                                  for k in ("All", "ALL"))),
        "has_stats_half": int(bool(periods.get("FirstHalf")) and bool(periods.get("SecondHalf"))),
        "has_shotmap": int(bool(shots)), "referee": referee,
        "has_lineup": int(bool(((content.get("lineup") or {}).get("homeTeam") or {}).get("starters")
                          or ((content.get("lineup") or {}).get("awayTeam") or {}).get("starters"))), "eligible": eligible,
    }


def main():
    rows = [build(r) for r in csv.DictReader(INDEX.open()) if r["league_id"] == "533"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1830
    expected = {"2021/2022": 379, "2023": 180, "2023/2024": 379,
                "2024/2025": 380, "2025/2026": 379, "2026/2027": 116}
    assert sum(r["eligible"] for r in rows) == 1813
    assert {s: sum(r["eligible"] and r["season"] == s for r in rows) for s in expected} == expected
    out = HERE; out.mkdir(parents=True, exist_ok=True)
    with (out / "ng_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        if not r["eligible"]: continue
        for side, other in (("home", "away"), ("away", "home")):
            team.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                         "stage": r["stage"], "sub_tournament": r["sub_tournament"],
                         "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                         "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]})
    assert len(team) == 3626
    with (out / "ng_team_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} eligible={sum(r['eligible'] for r in rows)} team_rows={len(team)}")


if __name__ == "__main__": main()
