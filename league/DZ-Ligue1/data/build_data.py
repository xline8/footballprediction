"""Build scores-only match and team-match tables for Algeria Ligue 1."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INDEX = REPO / "data_enrichment" / "fotmob_world_index.csv"
WAREHOUSE = REPO / "data_enrichment" / "fotmob_world"

SEASON_COUNTS = {
    "2021/2022": 306, "2022/2023": 240, "2023/2024": 240,
    "2024/2025": 240, "2025/2026": 240, "2026/2027": 66,
}
MISMATCH_ID = "4366461"

FIELDS = [
    "match_id", "league", "season", "date", "round", "sub_tournament", "stage",
    "home_team_id", "home_team", "away_team_id", "away_team", "finished", "awarded",
    "home_goals", "away_goals", "has_events", "n_events", "n_goal_events",
    "n_card_events", "n_red_events", "ht_home_goals", "ht_away_goals", "ht_source",
    "ht_suspect", "has_stats_all", "has_stats_half", "has_shotmap", "referee",
    "has_lineup", "lineup_block", "has_playerstats", "eligible", "event_ft_mismatch",
]


def payload_path(index_path):
    prefix = Path("data_enrichment/fotmob_world")
    return WAREHOUSE / Path(index_path).relative_to(prefix)


def _event_list(content):
    return (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])


def _nonempty_stats(stats):
    if not isinstance(stats, dict):
        return False
    periods = stats.get("Periods") or {}
    if not isinstance(periods, dict):
        return False
    for value in periods.values():
        if isinstance(value, dict):
            for key in ("stats", "statistics", "rows"):
                if value.get(key):
                    return True
        elif value:
            return True
    return False


def build(index_row):
    match_id = index_row["match_id"]
    payload = json.loads(payload_path(index_row["path"]).read_text(encoding="utf-8"))
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    teams = header.get("teams") or []
    assert len(teams) == 2, match_id
    home, away = teams
    assert int(home["id"]) != int(away["id"]), match_id
    index_score = tuple(int(x.strip()) for x in index_row["score"].split("-", 1))
    payload_score = (int(home["score"]), int(away["score"]))
    assert payload_score == index_score, (match_id, payload_score, index_score)

    content = payload.get("content") or {}
    events = _event_list(content)
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    card_events = [e for e in events if e.get("type") == "Card"]
    assert not [e for e in card_events if e.get("card") == "Yellow"], match_id
    half_events = [e for e in events if e.get("type") == "Half" and e.get("time") == 45]
    assert len(half_events) <= 1, match_id
    half = half_events[0] if half_events else None

    round_value = str(general.get("matchRound") or "")
    assert round_value.isdigit(), (match_id, round_value)
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    referee = ((info.get("Referee") or {}).get("text") or "")
    assert referee == "", match_id
    stats = content.get("stats")
    shotmap = content.get("shotmap") or {}
    lineup = content.get("lineup")
    player_stats = content.get("playerStats") or {}
    starters = bool(
        ((lineup or {}).get("homeTeam") or {}).get("starters")
        or ((lineup or {}).get("awayTeam") or {}).get("starters")
    )
    has_stats_all = int(_nonempty_stats(stats))
    has_stats_half = int(_nonempty_stats(stats))
    has_shotmap = int(bool(shotmap.get("shots") or []))
    has_playerstats = int(bool(player_stats.get("homeTeam") or player_stats.get("awayTeam")))
    awarded = int(bool((header.get("status") or {}).get("awarded")))
    row = {
        "match_id": match_id, "league": "DZ-Ligue1", "season": index_row["season"],
        "date": index_row["date"], "round": round_value, "sub_tournament": "",
        "stage": "regular", "home_team_id": int(home["id"]), "home_team": home["name"],
        "away_team_id": int(away["id"]), "away_team": away["name"], "finished": 1,
        "awarded": awarded, "home_goals": payload_score[0], "away_goals": payload_score[1],
        "has_events": int(bool(events)), "n_events": len(events), "n_goal_events": len(goals),
        "n_card_events": len(card_events),
        "n_red_events": sum(e.get("card") in {"Red", "YellowRed"} for e in card_events),
        "ht_home_goals": half.get("homeScore") if half else None,
        "ht_away_goals": half.get("awayScore") if half else None,
        "ht_source": "half_event" if half else None, "ht_suspect": 0,
        "has_stats_all": has_stats_all, "has_stats_half": has_stats_half,
        "has_shotmap": has_shotmap, "referee": referee, "has_lineup": int(starters),
        "lineup_block": int(bool(lineup)), "has_playerstats": has_playerstats,
        "eligible": int(not awarded), "event_ft_mismatch": int(match_id == MISMATCH_ID),
    }
    assert row["has_stats_all"] == row["has_stats_half"] == row["has_shotmap"] == 0, match_id
    assert row["has_playerstats"] == 0, match_id
    return row


def main():
    with INDEX.open(newline="", encoding="utf-8") as fh:
        rows = [build(r) for r in csv.DictReader(fh) if r["league_id"] == "516"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1332
    assert {s: sum(r["season"] == s for r in rows) for s in SEASON_COUNTS} == SEASON_COUNTS
    assert sum(r["eligible"] for r in rows) == 1331
    assert sum(r["awarded"] for r in rows) == 1
    assert sum(r["event_ft_mismatch"] for r in rows) == 1
    assert sum(r["has_events"] for r in rows) == 1190
    assert sum(r["ht_source"] == "half_event" for r in rows) == 1190
    assert sum(r["n_card_events"] for r in rows) == 244
    assert sum(r["n_red_events"] for r in rows) == 244
    assert len({x for r in rows for x in (r["home_team_id"], r["away_team_id"])}) == 27
    assert sum(r["has_stats_all"] for r in rows) == 0
    assert sum(r["has_shotmap"] for r in rows) == 0
    assert sum(r["has_playerstats"] for r in rows) == 0
    assert sum(r["has_lineup"] for r in rows) == 1
    assert sum(r["lineup_block"] for r in rows) == 10
    assert sum(bool(r["referee"]) for r in rows) == 0

    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "dz_matches.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(rows)
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": r["match_id"], "season": r["season"], "date": r["date"],
                "stage": r["stage"], "sub_tournament": r["sub_tournament"],
                "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
            })
    assert len(team_rows) == 2664
    with (HERE / "dz_team_matches.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        writer.writeheader(); writer.writerows(team_rows)
    print(f"matches={len(rows)} regular=1332 eligible=1331 team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
