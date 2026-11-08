"""Build Bulgaria First League Phase A tables from the FotMob warehouse."""
import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WAREHOUSE = Path.home() / "workspace" / "footballprediction"
LEAGUE_ID = "270"
STAT_KEYS = (
    "BallPossesion", "expected_goals", "expected_goals_set_play", "total_shots",
    "ShotsOnTarget", "big_chance", "touches_opp_box", "corners", "yellow_cards",
    "red_cards", "fouls",
)
PERIODS = (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_"))


def number(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or []
                if len(vals) >= 2:
                    h, a = number(vals[0]), number(vals[1])
                    key = stat.get("key")
                    if key and (h is not None or a is not None):
                        out[(period, key)] = (h, a)
    return out


def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def count_card(event_list, card, home):
    return sum(1 for event in event_list
               if event.get("type") == "Card" and event.get("card") == card
               and bool(event.get("isHome")) == home)


def score(value):
    parts = (value or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def event_minute(event):
    value = event.get("time")
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split("+")[0])
    except (TypeError, ValueError):
        return None


def phase(league_name):
    if league_name == "First Professional League":
        return "regular"
    for suffix, value in ((" Championship Playoff", "championship_playoff"),
                          (" Relegation Group", "relegation_group"),
                          (" ECL Group", "ecl_group"),
                          (" ECL Playoff", "ecl_playoff")):
        if league_name.endswith(suffix):
            return value
    raise ValueError(f"unexpected leagueName: {league_name!r}")


def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    content = payload.get("content") or {}
    stats, event_list = flat_stats(content), events(content)
    home_team, away_team = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    home_goals, away_goals = score(status.get("scoreStr") or index_row.get("score"))
    row = {
        "match_id": index_row["match_id"], "league": "BG-FirstLeague",
        "season": index_row["season"], "date": index_row["date"],
        "round": str(general.get("matchRound") or ""), "phase": phase(general.get("leagueName") or ""),
        "home_team_id": home_team.get("id"), "home_team": home_team.get("name"),
        "away_team_id": away_team.get("id"), "away_team": away_team.get("name"),
        "home_goals": home_goals, "away_goals": away_goals,
    }
    goals = [e for e in event_list if e.get("type") == "Goal"
             and not e.get("isPenaltyShootoutEvent")]
    first_half_goals = [e for e in goals if (event_minute(e) or 999) <= 45]
    row["ht_home_goals"] = sum(1 for e in first_half_goals if e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in first_half_goals if not e.get("isHome"))
    row["ht_source"] = "events" if event_list else "none"
    for is_home in (True, False):
        side = "home" if is_home else "away"
        direct = count_card(event_list, "Yellow", is_home)
        yellowred = count_card(event_list, "YellowRed", is_home)
        row[f"ev_yellow_direct_{side}"] = direct
        row[f"ev_yellowred_{side}"] = yellowred
        row[f"ev_yellow_{side}"] = direct + yellowred
        row[f"ev_red_{side}"] = count_card(event_list, "Red", is_home) + yellowred
        row[f"ht_yellow_{side}"] = sum(1 for e in event_list
                                        if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed")
                                        and bool(e.get("isHome")) == is_home and (event_minute(e) or 999) <= 45)
    for key in STAT_KEYS:
        for period, prefix in PERIODS:
            home, away = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = home, away
    row["yellow_home"], row["yellow_away"] = row["ev_yellow_home"], row["ev_yellow_away"]
    row["red_home"], row["red_away"] = row["ev_red_home"], row["ev_red_away"]
    row["cards_source"] = "events"
    row["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {})
                       .get("Referee") or {}).get("text") or ""
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["has_stats_half"] = int(("FirstHalf", "corners") in stats and ("SecondHalf", "corners") in stats)
    row["has_events"] = int(bool(event_list))
    row["has_period_splits_content"] = int(any(period in ((content.get("stats") or {}).get("Periods") or {})
                                                for period in ("FirstHalf", "SecondHalf")))
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    regular_shots = [s for s in shots if s.get("period") != "PenaltyShootout"]
    row["has_shotmap"], row["n_shootout_shots"] = int(bool(regular_shots)), len(shots) - len(regular_shots)
    for side, team_id in (("home", home_team.get("id")), ("away", away_team.get("id"))):
        side_shots = [s for s in regular_shots if s.get("teamId") == team_id]
        row[f"sm_shots_{side}"] = len(side_shots) if regular_shots else None
        row[f"sm_sot_{side}"] = sum(1 for s in side_shots if s.get("isOnTarget") and not s.get("isBlocked")) if regular_shots else None
        row[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in side_shots), 4) if regular_shots else None
        xgot = [s.get("expectedGoalsOnTarget") for s in side_shots if s.get("expectedGoalsOnTarget") is not None]
        row[f"sm_xgot_{side}"] = round(sum(xgot), 4) if regular_shots else None
        row[f"sm_xgot_n_{side}"] = len(xgot) if regular_shots else None
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE)
    args = parser.parse_args()
    index_path = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    index_rows = [r for r in csv.DictReader(index_path.open()) if r["league_id"] == LEAGUE_ID]
    rows = []
    for index_row in index_rows:
        rows.append(build(index_row, args.warehouse_root))
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    expected_phases = {
        "2021/2022": {"regular": 182, "championship_playoff": 15, "relegation_group": 12, "ecl_group": 12, "ecl_playoff": 1},
        "2022/2023": {"regular": 240, "championship_playoff": 15, "ecl_group": 12, "relegation_group": 15, "ecl_playoff": 1},
        "2023/2024": {"regular": 240, "championship_playoff": 15, "ecl_group": 12, "relegation_group": 15, "ecl_playoff": 1},
        "2024/2025": {"regular": 240, "championship_playoff": 12, "ecl_group": 12, "relegation_group": 28, "ecl_playoff": 1},
        "2025/2026": {"regular": 240, "championship_playoff": 12, "ecl_group": 12, "relegation_group": 28, "ecl_playoff": 1},
        "2026/2027": {"regular": 97},
    }
    actual_phases = {}
    for row in rows:
        actual_phases.setdefault(row["season"], {})[row["phase"]] = actual_phases.setdefault(row["season"], {}).get(row["phase"], 0) + 1
    assert actual_phases == expected_phases, actual_phases
    assert len(rows) == 1471, len(rows)
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "bg_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)
    team_rows = []
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            item = {"match_id": row["match_id"], "season": row["season"], "date": row["date"],
                    "phase": row["phase"], "team_id": row[f"{side}_team_id"],
                    "team": row[f"{side}_team"], "venue": side,
                    "goals_for": row[f"{side}_goals"], "goals_against": row[f"{other}_goals"]}
            for key in STAT_KEYS:
                item[f"{key}_for"], item[f"{key}_against"] = row.get(f"{key}_{side}"), row.get(f"{key}_{other}")
            item["yellow_events_for"], item["yellow_events_against"] = row[f"ev_yellow_{side}"], row[f"ev_yellow_{other}"]
            team_rows.append(item)
    with (HERE / "bg_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]), extrasaction="ignore")
        writer.writeheader(); writer.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
