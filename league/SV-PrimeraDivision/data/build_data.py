"""Build scores-only match and team-match tables for El Salvador Primera Division."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INDEX = REPO / "data_enrichment" / "fotmob_world_index.csv"
WAREHOUSE = REPO / "data_enrichment" / "fotmob_world"

TOURNAMENT_TOTALS = {
    "2021/2022 - Apertura": 145,
    "2021/2022 - Clausura": 145,
    "2022/2023 - Apertura": 80,
    "2022/2023 - Clausura": 137,
    "2023/2024 - Apertura": 145,
    "2023/2024 - Clausura": 145,
    "2024/2025 - Apertura": 123,
    "2024/2025 - Clausura": 123,
    "2025/2026 - Apertura": 145,
    "2025/2026 - Clausura": 145,
    "2026/2027 - Apertura": 115,
}
REGULAR_COUNTS = {
    "2021/2022 - Apertura": 132,
    "2021/2022 - Clausura": 132,
    "2022/2023 - Apertura": 67,
    "2022/2023 - Clausura": 132,
    "2023/2024 - Apertura": 132,
    "2023/2024 - Clausura": 132,
    "2024/2025 - Apertura": 110,
    "2024/2025 - Clausura": 110,
    "2025/2026 - Apertura": 132,
    "2025/2026 - Clausura": 132,
    "2026/2027 - Apertura": 115,
}
MISMATCH_ID = "4708064"

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
    relative = Path(index_path).relative_to(prefix)
    return WAREHOUSE / relative


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
    payload = json.loads(payload_path(index_row["path"]).read_text(encoding="utf-8"))
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    teams = header.get("teams") or []
    assert len(teams) == 2, index_row["match_id"]
    home, away = teams
    assert int(home["id"]) != int(away["id"]), index_row["match_id"]
    index_score = tuple(int(x.strip()) for x in index_row["score"].split("-", 1))
    payload_score = (int(home["score"]), int(away["score"]))
    assert payload_score == index_score, (index_row["match_id"], payload_score, index_score)

    content = payload.get("content") or {}
    events = _event_list(content)
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    card_events = [e for e in events if e.get("type") == "Card"]
    yellow_events = [e for e in card_events if e.get("card") == "Yellow"]
    assert not yellow_events, index_row["match_id"]
    mismatch = int(index_row["match_id"] == MISMATCH_ID)
    if mismatch:
        assert len({e.get("eventId") for e in goals}) < len(goals)
    elif index_row["match_id"] == MISMATCH_ID:
        raise AssertionError("unreachable")

    half = next((e for e in events if e.get("type") == "Half" and e.get("time") == 45), None)
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    tournament = info.get("Tournament") or {}
    round_value = str(general.get("matchRound") or "")
    if round_value.isdigit():
        stage = "regular"
    elif round_value in {"1/4", "1/2", "final"}:
        stage = "playoff"
    else:
        raise AssertionError((index_row["match_id"], round_value))
    stats = content.get("stats")
    shotmap = content.get("shotmap") or {}
    lineup = content.get("lineup")
    player_stats = content.get("playerStats") or {}
    has_playerstats = int(bool(player_stats.get("homeTeam") or player_stats.get("awayTeam")))
    starters = bool(
        ((lineup or {}).get("homeTeam") or {}).get("starters")
        or ((lineup or {}).get("awayTeam") or {}).get("starters")
    )
    referee = ((info.get("Referee") or {}).get("text") or "")
    assert referee == "", index_row["match_id"]
    row = {
        "match_id": index_row["match_id"], "league": "SV-PrimeraDivision",
        "season": index_row["season"], "date": index_row["date"], "round": round_value,
        "sub_tournament": tournament.get("leagueName") or "",
        "stage": stage, "home_team_id": int(home["id"]), "home_team": home["name"],
        "away_team_id": int(away["id"]), "away_team": away["name"], "finished": 1,
        "awarded": 0, "home_goals": payload_score[0], "away_goals": payload_score[1],
        "has_events": int(bool(events)), "n_events": len(events), "n_goal_events": len(goals),
        "n_card_events": len(card_events),
        "n_red_events": sum(e.get("card") in {"Red", "YellowRed"} for e in card_events),
        "ht_home_goals": half.get("homeScore") if half else None,
        "ht_away_goals": half.get("awayScore") if half else None,
        "ht_source": "half_event" if half else None, "ht_suspect": 0,
        "has_stats_all": int(_nonempty_stats(stats)),
        "has_stats_half": 0,
        "has_shotmap": int(bool(shotmap.get("shots") or [])), "referee": referee,
        "has_lineup": int(starters), "lineup_block": int(bool(lineup)),
        "has_playerstats": has_playerstats,
        "eligible": 1, "event_ft_mismatch": mismatch,
    }
    assert row["has_stats_all"] == row["has_stats_half"] == row["has_shotmap"] == 0
    assert row["has_lineup"] == 0
    assert row["has_playerstats"] == 0
    return row


def main():
    with INDEX.open(newline="", encoding="utf-8") as fh:
        rows = [build(r) for r in csv.DictReader(fh) if r["league_id"] == "335"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1448
    assert {s: sum(r["season"] == s for r in rows) for s in TOURNAMENT_TOTALS} == TOURNAMENT_TOTALS
    assert {s: sum(r["season"] == s and r["stage"] == "regular" for r in rows) for s in REGULAR_COUNTS} == REGULAR_COUNTS
    assert sum(r["stage"] == "regular" for r in rows) == 1326
    assert sum(r["stage"] == "playoff" for r in rows) == 122
    assert sum(r["eligible"] for r in rows) == 1448
    assert sum(r["event_ft_mismatch"] for r in rows) == 1
    assert sum(r["ht_suspect"] for r in rows) == 0
    ids = {x for r in rows for x in (r["home_team_id"], r["away_team_id"])}
    assert len(ids) == 19, ids
    assert sum(r["n_card_events"] for r in rows) == 593
    assert sum(r["n_red_events"] for r in rows) == 593
    assert sum(r["has_events"] for r in rows) == 1334
    assert sum(r["ht_source"] == "half_event" for r in rows) == 1334

    out = HERE
    out.mkdir(parents=True, exist_ok=True)
    with (out / "sv_matches.csv").open("w", newline="", encoding="utf-8") as fh:
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
    assert len(team_rows) == 2896
    with (out / "sv_team_matches.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        writer.writeheader(); writer.writerows(team_rows)
    print(f"matches={len(rows)} regular=1326 playoff=122 eligible=1448 team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
