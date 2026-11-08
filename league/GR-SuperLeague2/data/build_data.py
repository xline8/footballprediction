"""Build the GR-SuperLeague2 Stage 1 analysis tables from the world warehouse.

Scores-only league (FotMob league_id 8815): every payload in this corpus
has ``content.stats`` null and an empty shotmap, so there are NO stats-feed
columns at all — the builder asserts that from the payloads (it does not
trust the index's has_stats flag) and raises if any payload ever carries
stats. The only per-match quantities are the FT score (header.status),
goal/card events (content.matchFacts.events), and the HT goal split
derived from goal-event times (the GR-SuperLeague convention, time <= 45).
Team identity is the FotMob team id, never the display name: the corpus
contains three same-id renames (Kallithea / Athens Kallithea FC 7975,
Iraklis / Iraklis Saloniki 8675, PAOK Thessaloniki B / PAOK Thessaloniki
FC B 1303118).
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

PHASE_MAP = {
    "Super League 2 North": "regular",
    "Super League 2 South": "regular",
    "Super League 2 Grp. A": "regular",
    "Super League 2 Grp. B": "regular",
    "Super League 2": "regular",
    "Super League 2 Grp. A Promotion Group": "playoff_promotion",
    "Super League 2 Grp. B Promotion Group": "playoff_promotion",
    "Super League 2 Grp. A Relegation Group": "playoff_relegation",
    "Super League 2 Grp. B Relegation Group": "playoff_relegation",
    "Super League 2 Playoff": "playoff",
    "Super League 2 Super Cup": "supercup",
}


def parse_score(score):
    parts = (score or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def is_b_team(name):
    return bool(name) and name.strip().endswith(" B")


def events_block(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def event_count(events, card, home):
    return sum(1 for e in events if e.get("type") == "Card" and e.get("card") == card
               and bool(e.get("isHome")) == home)


def build_match(index_row):
    payload = json.loads((ROOT / index_row["path"]).read_text())
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    content = payload.get("content") or {}
    # Scores-only assertion, from the payload itself: no stats block and
    # no shotmap shots in any match of this corpus.
    stats = content.get("stats")
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    assert stats is None, f"stats present in {index_row['match_id']}"
    assert not shots, f"shotmap shots present in {index_row['match_id']}"
    events = events_block(content)
    home_goals, away_goals = parse_score(status.get("scoreStr") or index_row.get("score"))
    home_team = general.get("homeTeam") or {}
    away_team = general.get("awayTeam") or {}
    league_name = general.get("leagueName") or ""
    phase = PHASE_MAP.get(league_name)
    if phase is None:
        raise AssertionError(f"unexpected leagueName={league_name!r} match={index_row['match_id']}")
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    ev_home = sum(1 for e in goals if e.get("isHome"))
    ev_away = sum(1 for e in goals if not e.get("isHome"))
    row = {
        "match_id": index_row["match_id"], "league": "GR-SuperLeague2",
        "season": index_row["season"], "date": index_row["date"],
        "round": str(general.get("matchRound") or ""), "phase": phase,
        "league_name_raw": league_name,
        "parent_league_id": general.get("parentLeagueId"),
        "home_team_id": home_team.get("id"), "home_team": home_team.get("name"),
        "away_team_id": away_team.get("id"), "away_team": away_team.get("name"),
        "coverage_level": general.get("coverageLevel"),
        "home_goals": home_goals, "away_goals": away_goals,
        "is_b_home": int(is_b_team(home_team.get("name"))),
        "is_b_away": int(is_b_team(away_team.get("name"))),
        "has_events": int(bool(events)),
        "has_stats": 0, "has_shotmap": 0,
    }
    if events:
        row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        row["ht_source"] = "events"
        # The event feed is validated per match: its FT goal count must
        # reproduce the FT score, else the HT split is unvalidated.
        row["ht_validated"] = int((ev_home, ev_away) == (home_goals, away_goals))
    else:
        row["ht_home_goals"] = None
        row["ht_away_goals"] = None
        row["ht_source"] = "none"
        row["ht_validated"] = 0
    for side in (True, False):
        prefix = "home" if side else "away"
        row[f"ev_yellow_{prefix}"] = event_count(events, "Yellow", side)
        row[f"ev_yellowred_{prefix}"] = event_count(events, "YellowRed", side)
        row[f"ev_red_{prefix}"] = event_count(events, "Red", side) + row[f"ev_yellowred_{prefix}"]
    return row


def main():
    index_rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "8815"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = [build_match(r) for r in index_rows]
    assert len(rows) == 1935, len(rows)
    assert len({r["match_id"] for r in rows}) == len(rows)
    expected = {
        "2021/2022": {"regular": 544, "playoff": 2},
        "2022/2023": {"regular": 420},
        "2023/2024": {"regular": 264, "playoff_promotion": 40, "playoff_relegation": 60},
        "2024/2025": {"regular": 180, "playoff_promotion": 40, "playoff_relegation": 40, "supercup": 1},
        "2025/2026": {"regular": 180, "playoff_promotion": 24, "playoff_relegation": 60, "supercup": 1},
        "2026/2027": {"regular": 79},
    }
    for season, counts in expected.items():
        got = {phase: sum(r["season"] == season and r["phase"] == phase for r in rows)
               for phase in ("regular", "playoff_promotion", "playoff_relegation", "playoff", "supercup")}
        got = {k: v for k, v in got.items() if v}
        assert got == counts, (season, got, counts)
    with (OUT / "gr2_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    team_rows = []
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": row["match_id"], "season": row["season"], "date": row["date"],
                "phase": row["phase"], "team_id": row[f"{side}_team_id"],
                "team": row[f"{side}_team"], "venue": side,
                "goals_for": row[f"{side}_goals"], "goals_against": row[f"{other}_goals"],
                "is_b_team": row[f"is_b_{side}"],
            })
    with (OUT / "gr2_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        writer.writeheader()
        writer.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
