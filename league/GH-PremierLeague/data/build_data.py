"""Build the Ghana Premier League match tables.

The warehouse has 1,619 indexed payloads (FotMob 522), seasons
2021/2022 -> 2026/2027, one tier, single table, 18 teams, double
round robin.  The 2024/2025 season has 305 matches: the round-33
fixture Holy Stars vs Nations FC is absent from both the index and
the warehouse (both clubs on 33 matches); this builder records the
gap rather than inventing it.

Ghana payloads differ from the Nigeria ones in one structural way:
``general`` and ``header`` are null in every payload, so team
identity and the FT score CANNOT come from the payload — they come
from the index (``home``/``away``/``score`` columns), cross-checked
against the payload where a check exists (index date == payload
``Match Date`` on 1,619/1,619; goal-event FT scores agree with the
index score on 1,408/1,412 event-bearing matches — the 4 exceptions
are event-feed errors, see DATA_UNDERSTANDING.md section 5, and the
index score is the source of truth for all of them).
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
# Event-feed errors: goal events do not reproduce the official score
# (duplicate goal events in 3 matches, one missing away goal in 1).
# The index score is official; only these matches' HT values are
# suspect, so they are flagged and excluded from HT-share work only.
HT_SUSPECT = {"4015488", "4015491", "4015543", "4584614"}
FIELDS = ["match_id", "league", "season", "date", "round", "sub_tournament", "stage",
          "home_team_id", "home_team", "away_team_id", "away_team", "finished", "awarded",
          "home_goals", "away_goals", "has_events", "n_events", "n_goal_events",
          "n_card_events", "n_red_events", "ht_home_goals", "ht_away_goals", "ht_source",
          "ht_suspect", "has_stats_all", "has_stats_half", "has_shotmap", "referee",
          "has_lineup", "lineup_block", "eligible"]


def _score(value):
    a, b = (value or "").split("-", 1)
    return int(a.strip()), int(b.strip())


def build(index_row, warehouse_root=MAIN_REPO):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    content = payload.get("content") or {}
    # general/header are null in this league; identity + score come
    # from the index row (see module docstring).
    events = (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])
    goals_events = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    half = next((e for e in events if e.get("type") == "Half" and e.get("time") == 45), None)
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    tournament = info.get("Tournament") or {}
    stats = content.get("stats") or {}
    periods = stats.get("Periods") or {} if isinstance(stats, dict) else {}
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    referee = ((info.get("Referee") or {}).get("text") or "")
    lineup = content.get("lineup") or {}
    starters = bool(((lineup.get("homeTeam") or {}).get("starters"))
                    or ((lineup.get("awayTeam") or {}).get("starters")))
    goals = _score(index_row["score"])
    ht_suspect = int(index_row["match_id"] in HT_SUSPECT)
    # AWARDED RULE (frozen, DATA_UNDERSTANDING.md section 5): a played
    # match with >=1 goal ALWAYS carries a goal-event feed in this
    # corpus (1,408/1,412 event matches reproduce the index score
    # exactly; the 4 exceptions are flagged above). A 3-0 / 0-3 with
    # NO events at all is therefore a forfeit/awarded result, not a
    # played match: 23 rows (Nsoatreman 14 straight from 2025-03-16,
    # Hohoe United 7 straight from 2026-04-03, plus 2 singles).
    # Event-less 0-0 draws (184) are played goalless draws and stay
    # eligible. One awarded row is direction-reversed in the source
    # (4584723 Nsoatreman 3-0 Hearts of Oak, inside the withdrawal
    # run) — excluded either way; the flip is flagged, not repaired.
    awarded = int(not events and goals in ((3, 0), (0, 3)))
    return {
        "match_id": index_row["match_id"], "league": "GH-PremierLeague", "season": index_row["season"],
        "date": index_row["date"], "round": str(tournament.get("round") or ""),
        "sub_tournament": tournament.get("leagueName") or "Premier League",
        "stage": "regular", "home_team_id": None, "home_team": index_row["home"],
        "away_team_id": None, "away_team": index_row["away"], "finished": 1,
        "awarded": awarded, "home_goals": goals[0], "away_goals": goals[1],
        "has_events": int(bool(events)), "n_events": len(events), "n_goal_events": len(goals_events),
        "n_card_events": sum(e.get("type") == "Card" for e in events),
        "n_red_events": sum(e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") for e in events),
        "ht_home_goals": half.get("homeScore") if half else None,
        "ht_away_goals": half.get("awayScore") if half else None,
        "ht_source": "half_event" if half else None,
        "ht_suspect": ht_suspect,
        "has_stats_all": int(bool(periods.get("All") or periods.get("ALL"))),
        "has_stats_half": int(bool(periods.get("FirstHalf")) and bool(periods.get("SecondHalf"))),
        "has_shotmap": int(bool(shots)), "referee": referee,
        "has_lineup": int(starters), "lineup_block": int(bool(lineup)),
        "eligible": int(not awarded),
    }


def main():
    rows = [build(r) for r in csv.DictReader(INDEX.open()) if r["league_id"] == "522"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1619
    expected = {"2021/2022": 306, "2022/2023": 306, "2023/2024": 305,
                "2024/2025": 290, "2025/2026": 299, "2026/2027": 90}
    assert {s: sum(r["eligible"] and r["season"] == s for r in rows) for s in expected} == expected
    assert sum(r["eligible"] for r in rows) == 1596
    assert sum(r["awarded"] for r in rows) == 23
    out = HERE; out.mkdir(parents=True, exist_ok=True)
    with (out / "gh_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        if not r["eligible"]: continue
        for side, other in (("home", "away"), ("away", "home")):
            team.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                         "stage": r["stage"], "sub_tournament": r["sub_tournament"],
                         "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                         "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]})
    assert len(team) == 3192
    with (out / "gh_team_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} eligible={sum(r['eligible'] for r in rows)} team_rows={len(team)}")


if __name__ == "__main__": main()
