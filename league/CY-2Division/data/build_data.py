"""Build Cyprus 2. Division Phase A tables from the FotMob warehouse.

Scores + events corpus ONLY: no team-stats block, no shotmap, no lineups,
referee empty in every payload (verified by content scan of all 1,210
payloads). The event feed carries goals, Half markers and red-family
cards only -- plain Yellow cards are absent from the feed, so the
ev_yellow_* columns below count YellowRed dismissals only and are NOT
a valid yellow-cards target (see analysis/FEATURES.md).
"""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WAREHOUSE = Path.home() / "workspace" / "footballprediction"
LEAGUE_ID = "9100"


def event_minute(event):
    value = event.get("time")
    try:
        return float(value if isinstance(value, (int, float)) else str(value).split("+")[0])
    except (TypeError, ValueError):
        return None


def score(value):
    a, b = (value or "0 - 0").split("-")[:2]
    return int(a.strip()), int(b.strip())


def phase(name):
    name = (name or "").strip()
    if name == "2. Division":
        return "regular"
    if name == "2. Division Promotion Group":
        return "promotion"
    if name == "2. Division Relegation Group":
        return "relegation"
    raise ValueError(f"unexpected leagueName: {name!r}")


def build(index_row, warehouse_root):
    path = warehouse_root / index_row["path"].rstrip("\r")
    payload = json.loads(path.read_text())
    general, header, content = payload.get("general") or {}, payload.get("header") or {}, payload.get("content") or {}
    status = header.get("status") or {}
    home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    ev = (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
    row = {"match_id": index_row["match_id"], "league": "CY-2Division", "season": index_row["season"],
           "date": index_row["date"], "round": str(general.get("matchRound") or ""),
           "phase": phase(general.get("leagueName")), "home_team_id": home.get("id"), "home_team": home.get("name"),
           "away_team_id": away.get("id"), "away_team": away.get("name"), "home_goals": hg, "away_goals": ag}
    goals = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    first_goals = [e for e in goals if (event_minute(e) or 999) <= 45]
    # No events -> HT is unknown, never 0 (absent feed != zero).
    row["ht_home_goals"] = sum(bool(e.get("isHome")) for e in first_goals) if ev else ""
    row["ht_away_goals"] = sum(not bool(e.get("isHome")) for e in first_goals) if ev else ""
    row["ht_source"] = "events" if ev else "none"
    row["ev_goals_home"] = sum(bool(e.get("isHome")) for e in goals)
    row["ev_goals_away"] = sum(not bool(e.get("isHome")) for e in goals)
    row["score_events_mismatch"] = int(row["ev_goals_home"] != hg or row["ev_goals_away"] != ag) if ev else 0
    for is_home in (True, False):
        side = "home" if is_home else "away"
        ys = [e for e in ev if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and bool(e.get("isHome")) == is_home]
        direct = sum(e.get("card") == "Yellow" for e in ys)
        yr = sum(e.get("card") == "YellowRed" for e in ys)
        row[f"ev_yellow_direct_{side}"], row[f"ev_yellowred_{side}"] = direct, yr
        row[f"ev_yellow_{side}"] = direct + yr  # YellowRed only in practice; NOT a yellows target
        row[f"ev_red_{side}"] = sum(e.get("card") == "Red" for e in ev if e.get("type") == "Card" and bool(e.get("isHome")) == is_home) + yr
        row[f"ht_yellow_{side}"] = sum((event_minute(e) or 999) <= 45 for e in ys)
    row["yellow_home"], row["yellow_away"] = row["ev_yellow_home"], row["ev_yellow_away"]
    row["red_home"], row["red_away"] = row["ev_red_home"], row["ev_red_away"]
    row["cards_source"] = "events"
    row["referee"] = ""
    row["has_stats_all"] = 0
    row["has_stats_flag"] = int(str(index_row.get("has_stats", "")).lower() == "true")
    row["has_events"] = int(bool(ev))
    row["has_period_splits_content"] = 0
    row["has_shotmap"] = 0
    row["has_lineup"] = 0
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE)
    args = ap.parse_args()
    index = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [build(r, args.warehouse_root) for r in csv.DictReader(index.open()) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    expected = {
        "2021/2022": {"regular": 240},
        "2022/2023": {"regular": 120, "promotion": 56, "relegation": 42},
        "2023/2024": {"regular": 120, "promotion": 56, "relegation": 56},
        "2024/2025": {"regular": 120, "promotion": 56, "relegation": 56},
        "2025/2026": {"regular": 120, "promotion": 56, "relegation": 56},
        "2026/2027": {"regular": 56},
    }
    actual = {}
    for r in rows:
        actual.setdefault(r["season"], {})[r["phase"]] = actual.setdefault(r["season"], {}).get(r["phase"], 0) + 1
    assert actual == expected, actual
    assert len(rows) == 1210, len(rows)
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                "ht_goals_for": r[f"ht_{side}_goals"], "ht_goals_against": r[f"ht_{other}_goals"],
                "yellow_events_for": r[f"ev_yellow_{side}"], "yellow_events_against": r[f"ev_yellow_{other}"],
                "red_events_for": r[f"ev_red_{side}"], "red_events_against": r[f"ev_red_{other}"],
            })
    with (HERE / "cy2_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (HERE / "cy2_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        w.writeheader()
        w.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
