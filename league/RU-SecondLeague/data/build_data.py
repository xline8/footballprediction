"""Build Russia Second League (FotMob 9123) match tables from the FotMob warehouse.

Extraction only: no fitting, imputation, or feature windows.

League facts (payload-verified, see analysis/DATA_UNDERSTANDING.md):
- FotMob 9123 is a PARENT id: each payload's general.leagueName is one of
  44 sub-tournaments (groups / subgroups / stages / playoffs) across two
  parallel tracks from 2023: Division A (autumn-spring, Gold/Silver,
  first/second stage) and Division B (calendar year, 4 groups). Before
  2023 the same structure ran as FNL 2 / Second League groups.
- Scores exist for finished matches only. 1,181 index rows are phantom
  fixtures (started=False, no scoreStr, index score "0-0"): they enter
  the CSV with finished=0 and null goals and are excluded from every fit.
- stats / shotmap / referee are empty in ALL 6,558 payloads. Events exist
  only up to the 2024 season; card events are Red/YellowRed dismissals
  only (zero plain Yellow events anywhere). HT goals are derived from
  Goal events only where the event goal counts reconcile with scoreStr.
- 50 finished matches are awarded (administrative results, incl. 37
  recorded 0-0 whose Goal events contradict the score). They stay in the
  CSV with awarded=1 and are excluded from every fit and score.
- Season label "2025" (Division B) is a harvest fragment: 42/842 rows
  finished, distorted scorelines (mean 1.38 goals, 43% 0-0). It stays in
  the CSV and is excluded from every fit and score by the frozen rule in
  analysis/PREPROCESSING.md.
"""
import csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"


def track_of(league_name):
    name = league_name or ""
    if "Division A" in name:
        return "A"
    if "Division B" in name:
        return "B"
    return "pre-2023"


def phase_of(league_name):
    name = league_name or ""
    if "First Stage" in name:
        return "first_stage"
    if "Second Stage" in name:
        return "second_stage"
    if "Promotion Playoff" in name:
        return "promotion_playoff"
    if "Relegation Playoff" in name:
        return "relegation_playoff"
    if "Promotion Group" in name:
        return "promotion_group"
    if "Relegation Group" in name:
        return "relegation_group"
    if "Final Four" in name:
        return "final_four"
    return "group_stage"


def score(s):
    p = (s or "0 - 0").split("-")
    return int(p[0].strip()), int(p[1].strip())


def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general, header = payload.get("general") or {}, payload.get("header") or {}
    status, content = header.get("status") or {}, payload.get("content") or {}
    finished = bool(status.get("finished"))
    awarded = bool(status.get("awarded"))
    league_name = general.get("leagueName") or ""
    ht, at = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    row = {"match_id": index_row["match_id"], "league": "RU-SecondLeague",
           "season": index_row["season"], "date": index_row["date"],
           "round": str(general.get("matchRound") or ""),
           "sub_tournament": league_name,
           "track": track_of(league_name), "phase": phase_of(league_name),
           "home_team_id": ht.get("id"), "home_team": ht.get("name"),
           "away_team_id": at.get("id"), "away_team": at.get("name"),
           "finished": int(finished), "awarded": int(awarded)}
    if finished:
        hg, ag = score(status.get("scoreStr") or index_row.get("score"))
        row["home_goals"], row["away_goals"] = hg, ag
    else:
        row["home_goals"], row["away_goals"] = None, None
    es = (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
    goals = [e for e in es if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["has_events"] = int(bool(es))
    row["n_events"] = len(es)
    row["n_card_events"] = sum(1 for e in es if e.get("type") == "Card")
    row["n_red_events"] = sum(1 for e in es if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed"))
    # HT goals from events, only where event goal counts reconcile with the score.
    row["ht_home_goals"], row["ht_away_goals"], row["ht_source"] = None, None, "none"
    if finished and es:
        gh = sum(1 for e in goals if e.get("isHome"))
        ga = sum(1 for e in goals if not e.get("isHome"))
        if gh == row["home_goals"] and ga == row["away_goals"]:
            row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
            row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
            row["ht_source"] = "events"
    stats = (content.get("stats") or {})
    row["has_stats_all"] = int(bool((stats.get("Periods") or {}).get("All")))
    row["has_stats_half"] = int(bool((stats.get("Periods") or {}).get("FirstHalf")) and bool((stats.get("Periods") or {}).get("SecondHalf")))
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    row["has_shotmap"] = int(bool(shots))
    row["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    lineup = (content.get("lineup") or {})
    row["has_lineup"] = int(bool(lineup.get("homeTeam")) or bool(lineup.get("awayTeam")))
    return row


def main(warehouse_root=MAIN_REPO):
    index = warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [build(r, warehouse_root) for r in csv.DictReader(index.open()) if r["league_id"] == "9123"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 6558, len(rows)
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "ru2_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        if not r["finished"]:
            continue
        for side, other in (("home", "away"), ("away", "home")):
            team.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                         "track": r["track"], "phase": r["phase"], "sub_tournament": r["sub_tournament"],
                         "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                         "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                         "awarded": r["awarded"]})
    with (HERE / "ru2_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} finished={sum(r['finished'] for r in rows)} "
          f"awarded={sum(r['awarded'] for r in rows)} team_rows={len(team)}")


if __name__ == "__main__":
    main()
