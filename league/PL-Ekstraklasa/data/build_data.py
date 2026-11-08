"""Build the PL-Ekstraklasa Stage 1 analysis tables from the world warehouse.

The builder deliberately keeps feed provenance in the match table.  In
particular, yellow cards use the stats feed when present (the reference
unified target), with an events fallback only when the stats card is absent;
stats-vs-events is measured by the EDA before that target is consumed.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = [
    "BallPossesion", "expected_goals", "expected_goals_open_play",
    "expected_goals_set_play", "expected_goals_non_penalty", "total_shots",
    "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box",
    "shots_outside_box", "big_chance", "touches_opp_box", "corners",
    "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
]


def number(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split(" ")[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    result = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                values = stat.get("stats") or []
                home = number(values[0]) if values else None
                away = number(values[1]) if len(values) > 1 else None
                if home is not None or away is not None:
                    result[(period, stat.get("key"))] = (home, away)
    return result


def events_block(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def event_count(events, card, home):
    return sum(1 for e in events if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == home)


def parse_score(score):
    parts = (score or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def build_match(index_row):
    payload = json.loads((ROOT / index_row["path"]).read_text())
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    content = payload.get("content") or {}
    stats = flat_stats(content)
    events = events_block(content)
    home_goals, away_goals = parse_score(status.get("scoreStr") or index_row.get("score"))
    home_team = general.get("homeTeam") or {}
    away_team = general.get("awayTeam") or {}
    row = {
        "match_id": index_row["match_id"], "league": "PL-Ekstraklasa",
        "season": index_row["season"], "date": index_row["date"],
        "round": str(general.get("matchRound") or ""), "phase": "regular",
        "league_name_raw": general.get("leagueName"),
        "parent_league_id": general.get("parentLeagueId"),
        "home_team_id": home_team.get("id"), "home_team": home_team.get("name"),
        "away_team_id": away_team.get("id"), "away_team": away_team.get("name"),
        "coverage_level": general.get("coverageLevel"),
        "home_goals": home_goals, "away_goals": away_goals,
    }
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["ht_source"] = "events" if events else "none"
    for side in (True, False):
        prefix = "home" if side else "away"
        row[f"ev_yellow_{prefix}"] = event_count(events, "Yellow", side)
        row[f"ev_yellowred_{prefix}"] = event_count(events, "YellowRed", side)
        row[f"ev_red_{prefix}"] = event_count(events, "Red", side) + row[f"ev_yellowred_{prefix}"]
    for key in STAT_KEYS:
        for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
            home, away = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"] = home
            row[f"{prefix}{key}_away"] = away
    row["yellow_home"] = row["yellow_cards_home"]
    row["yellow_away"] = row["yellow_cards_away"]
    row["red_home"] = row["red_cards_home"]
    row["red_away"] = row["red_cards_away"]
    if row["yellow_home"] is None or row["yellow_away"] is None:
        row["yellow_home"] = float(row["ev_yellow_home"])
        row["yellow_away"] = float(row["ev_yellow_away"])
        row["cards_source"] = "events"
    else:
        row["cards_source"] = "stats"
    info = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
    row["referee"] = info.get("text") or ""
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["has_stats_half"] = int(("FirstHalf", "corners") in stats)
    row["has_events"] = int(bool(events))
    row["has_period_splits_content"] = int(any(p in ((content.get("stats") or {}).get("Periods") or {}) for p in ("FirstHalf", "SecondHalf")))

    shots = ((content.get("shotmap") or {}).get("shots") or [])
    regular_shots = [s for s in shots if s.get("period") != "PenaltyShootout"]
    row["has_shotmap"] = int(bool(regular_shots))
    row["n_shootout_shots"] = len(shots) - len(regular_shots)
    for side, team_id in (("home", home_team.get("id")), ("away", away_team.get("id"))):
        side_shots = [s for s in regular_shots if s.get("teamId") == team_id]
        row[f"sm_shots_{side}"] = len(side_shots)
        row[f"sm_sot_{side}"] = sum(1 for s in side_shots if s.get("isOnTarget") and not s.get("isBlocked"))
        row[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in side_shots), 4)
        xgot = [s.get("expectedGoalsOnTarget") for s in side_shots if s.get("expectedGoalsOnTarget") is not None]
        row[f"sm_xgot_{side}"] = round(sum(xgot), 4)
        row[f"sm_xgot_n_{side}"] = len(xgot)
        row[f"sm_shots_fh_{side}"] = sum(1 for s in side_shots if s.get("period") == "FirstHalf")
    # Score-only payloads must not masquerade as zero-valued stat matches.
    if not row["has_events"] and not row["has_shotmap"]:
        for key in STAT_KEYS:
            for prefix in ("", "fh_", "sh_"):
                row[f"{prefix}{key}_home"] = None
                row[f"{prefix}{key}_away"] = None
        row["yellow_home"] = row["yellow_away"] = None
        row["red_home"] = row["red_away"] = None
        row["cards_source"] = "none"
        for side in ("home", "away"):
            for key in ("sm_shots", "sm_sot", "sm_xg", "sm_xgot", "sm_xgot_n", "sm_shots_fh"):
                row[f"{key}_{side}"] = None
    return row


def main():
    index_rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "196"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = [build_match(r) for r in index_rows]
    # 1654 is the frozen build-time count (2021/2022–2025/2026 complete at 306 each plus 124 played of 2026/2027); live rebuilds only grow it.
    assert len(rows) >= 1654, len(rows)
    assert len({r["match_id"] for r in rows}) == len(rows)
    with (OUT / "pl_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    team_rows = []
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            item = {"match_id": row["match_id"], "season": row["season"], "date": row["date"],
                    "phase": row["phase"], "team_id": row[f"{side}_team_id"],
                    "team": row[f"{side}_team"], "venue": side,
                    "goals_for": row[f"{side}_goals"], "goals_against": row[f"{other}_goals"]}
            for key in ("expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards",
                        "touches_opp_box", "big_chance", "BallPossesion"):
                item[f"{key}_for"] = row.get(f"{key}_{side}")
                item[f"{key}_against"] = row.get(f"{key}_{other}")
            item["sm_xg_for"] = row.get(f"sm_xg_{side}")
            item["sm_shots_for"] = row.get(f"sm_shots_{side}")
            item["sm_xgot_for"] = row.get(f"sm_xgot_{side}")
            item["sm_xgot_n_for"] = row.get(f"sm_xgot_n_{side}")
            team_rows.append(item)
    with (OUT / "pl_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        writer.writeheader(); writer.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
