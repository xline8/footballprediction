"""Build the Morocco Botola Pro tables from the FotMob warehouse.

Extraction only: no imputation, fitting, or feature windows. The
warehouse is the main footballprediction checkout; generated CSVs are
local gitignored artefacts. Teams are keyed on FotMob team ids (four
ids carry two name spellings each; names are never keys).
"""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
STAT_KEYS = ("BallPossesion", "total_shots", "ShotsOnTarget", "corners")

def number(value):
    if value in (None, ""): return None
    if isinstance(value, (int, float)): return float(value)
    try: return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError): return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                values = stat.get("stats") or []
                if len(values) < 2: continue
                h, a = number(values[0]), number(values[1])
                if h is not None or a is not None:
                    out[(period, stat.get("key"))] = (h, a)
    return out

def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []

def count_event(es, card, home):
    return sum(1 for e in es if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == home)

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
    row = {
        "match_id": index_row["match_id"], "league": "MA-BotolaPro",
        "season": index_row["season"], "date": index_row["date"],
        "round": str(general.get("matchRound") or ""), "phase": "regular",
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
    }
    goals = [e for e in es if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["goal_events"] = len(goals)
    row["ht_source"] = "events" if es else "none"
    row["ev_yellow_home"] = count_event(es, "Yellow", True)
    row["ev_yellow_away"] = count_event(es, "Yellow", False)
    row["ev_yellowred_home"] = count_event(es, "YellowRed", True)
    row["ev_yellowred_away"] = count_event(es, "YellowRed", False)
    row["ev_red_home"] = count_event(es, "Red", True)
    row["ev_red_away"] = count_event(es, "Red", False)
    # unified yellows = Yellow + YellowRed (RU-1Division convention)
    row["yellow_home"] = float(row["ev_yellow_home"] + row["ev_yellowred_home"])
    row["yellow_away"] = float(row["ev_yellow_away"] + row["ev_yellowred_away"])
    row["cards_source"] = "events"
    # 1H yellows from card event times (rich era only is meaningful)
    cards = [e for e in es if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed")]
    row["ht_yellows"] = sum(1 for e in cards if e.get("time") is not None and e["time"] <= 45)
    for key in STAT_KEYS:
        h, a = stats.get(("All", key), (None, None))
        row[f"{key}_home"], row[f"{key}_away"] = h, a
    periods = ((content.get("stats") or {}).get("Periods") or {})
    row["has_period_splits_content"] = int("FirstHalf" in periods or "SecondHalf" in periods)
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["rich_era"] = int(row["date"] >= "2024-11-01")
    row["has_events"] = int(bool(es))
    row["has_shotmap"] = 0
    row["referee"] = ((((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "")
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warehouse-root", type=Path, default=MAIN_REPO)
    args = parser.parse_args()
    warehouse = args.warehouse_root
    index = warehouse / "data_enrichment" / "fotmob_world_index.csv"
    source = [r for r in csv.DictReader(index.open()) if r["league_id"] == "530"]
    rows = [build(r, warehouse) for r in source]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1255, len(rows)
    with (HERE / "ma_botola_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                 "yellow_for": r[f"yellow_{side}"], "yellow_against": r[f"yellow_{other}"]}
            for key in STAT_KEYS:
                x[f"{key}_for"] = r.get(f"{key}_{side}")
                x[f"{key}_against"] = r.get(f"{key}_{other}")
            team.append(x)
    with (HERE / "ma_botola_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} team_rows={len(team)}")

if __name__ == "__main__":
    main()
