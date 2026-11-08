"""Build Scotland League One Phase-A extraction tables.

Extraction only: no imputation, fitting, or feature windows.  The warehouse
is the main footballprediction checkout; generated CSVs are local artefacts.
"""
import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
STAT_KEYS = (
    "BallPossesion", "total_shots", "ShotsOnTarget", "corners",
    "expected_goals", "expected_goals_open_play", "expected_goals_set_play",
    "expected_goals_non_penalty", "ShotsOffTarget", "blocked_shots",
    "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box",
    "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
)


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
                values = stat.get("stats") or []
                if len(values) >= 2:
                    h, a = number(values[0]), number(values[1])
                    if h is not None or a is not None:
                        out[(period, stat.get("key"))] = (h, a)
    return out


def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def count_card(es, card, home, first_half=False):
    return sum(1 for e in es if e.get("type") == "Card" and e.get("card") == card
               and bool(e.get("isHome")) == home
               and (not first_half or (e.get("time") is not None and e["time"] <= 45)))


def score(value):
    parts = (value or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general = payload.get("general") or {}
    status = ((payload.get("header") or {}).get("status") or {})
    content = payload.get("content") or {}
    stats, es = flat_stats(content), events(content)
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    row = {"match_id": index_row["match_id"], "league": "SCO-LeagueOne",
           "season": index_row["season"], "date": index_row["date"],
           "round": str(general.get("matchRound") or ""), "phase": "regular",
           "home_team_id": home.get("id"), "home_team": home.get("name"),
           "away_team_id": away.get("id"), "away_team": away.get("name"),
           "home_goals": hg, "away_goals": ag}
    goals = [e for e in es if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["ht_source"] = "events" if es else "none"
    for side, home_flag in (("home", True), ("away", False)):
        row[f"ev_yellow_{side}"] = count_card(es, "Yellow", home_flag)
        row[f"ev_yellowred_{side}"] = count_card(es, "YellowRed", home_flag)
        row[f"ev_red_{side}"] = count_card(es, "Red", home_flag) + row[f"ev_yellowred_{side}"]
        row[f"ht_yellow_{side}"] = count_card(es, "Yellow", home_flag, True)
        row[f"ht_red_{side}"] = count_card(es, "Red", home_flag, True) + count_card(es, "YellowRed", home_flag, True)
    for key in STAT_KEYS:
        for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
            h, a = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = h, a
    stats_yh, stats_ya = row["yellow_cards_home"], row["yellow_cards_away"]
    row["yellow_home"] = stats_yh if stats_yh is not None else float(row["ev_yellow_home"])
    row["yellow_away"] = stats_ya if stats_ya is not None else float(row["ev_yellow_away"])
    row["red_home"] = row["red_cards_home"] if row["red_cards_home"] is not None else float(row["ev_red_home"])
    row["red_away"] = row["red_cards_away"] if row["red_cards_away"] is not None else float(row["ev_red_away"])
    row["cards_source"] = "stats" if stats_yh is not None and stats_ya is not None else "events"
    info = (content.get("matchFacts") or {}).get("infoBox") or {}
    row["referee"] = (info.get("Referee") or {}).get("text") or ""
    periods = ((content.get("stats") or {}).get("Periods") or {})
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["has_stats_half"] = int(("FirstHalf", "corners") in stats and ("SecondHalf", "corners") in stats)
    row["has_period_splits_content"] = int("FirstHalf" in periods or "SecondHalf" in periods)
    row["has_events"] = int(bool(es))
    row["has_shotmap"] = 0
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warehouse-root", type=Path, default=MAIN_REPO)
    args = parser.parse_args()
    index = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    source = [r for r in csv.DictReader(index.open()) if r["league_id"] == "124"]
    rows = sorted((build(r, args.warehouse_root) for r in source), key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 969, len(rows)
    with (HERE / "sco_league_one_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    team = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                 "phase": r["phase"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"],
                 "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                 "yellow_events_for": r[f"ev_yellow_{side}"], "yellow_events_against": r[f"ev_yellow_{other}"],
                 "red_events_for": r[f"ev_red_{side}"], "red_events_against": r[f"ev_red_{other}"]}
            for key in ("BallPossesion", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "red_cards", "touches_opp_box", "big_chance"):
                x[f"{key}_for"], x[f"{key}_against"] = r.get(f"{key}_{side}"), r.get(f"{key}_{other}")
            team.append(x)
    with (HERE / "sco_league_one_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team[0])); writer.writeheader(); writer.writerows(team)
    print(f"matches={len(rows)} team_rows={len(team)}")


if __name__ == "__main__":
    main()
