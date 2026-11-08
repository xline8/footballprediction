"""Build UAE Pro League (FotMob id 538) tables from the FotMob world warehouse.

One row per played match. Targets:
- goals from header scoreStr (official).
- count stats from the stats feed Periods.All (100% coverage, all seasons).
- cards TARGET = stats-feed yellows (yellow_cards). The event feed carries
  plain Yellow events in 2021/2022-2023/2024 and 2026/2027 but collapses to
  ~0 in 2024/2025 and 2025/2026 (only YellowRed/Red survive), so an
  event-unified target cannot exist in the virgin window; event yellows are
  stored alongside (ev_yellow_*) for the artefact record only.
- HT goals / HT yellows from goal/card event minutes (goal events reproduce
  the FT score in 956/959; the 3 exceptions are flagged).
- period-split (FirstHalf) stats stored where present: none in 2021/2022,
  50/182 in 2022/2023, all matches from 2023/2024.
- awarded matches flagged (2) and excluded from fits/scoring by the engines.
"""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WAREHOUSE = Path.home() / "workspace" / "footballprediction"
LEAGUE_ID = "538"
STAT_KEYS = ("BallPossesion", "ShotsOnTarget", "corners", "total_shots",
             "big_chance", "touches_opp_box", "yellow_cards", "red_cards")

def number(value):
    if value in (None, ""):
        return None
    try:
        return float(str(value).split()[0].replace("%", "").replace("(", "").strip())
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
                    if stat.get("key") and (h is not None or a is not None):
                        out[(period, stat["key"])] = (h, a)
    return out

def event_list(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []

def event_minute(event):
    value = event.get("time")
    try:
        return float(value if isinstance(value, (int, float)) else str(value).split("+")[0])
    except (TypeError, ValueError):
        return None

def score(value):
    a, b = (value or "0 - 0").split("-")[:2]
    return int(a.strip()), int(b.strip())

def build(index_row, warehouse_root):
    path = warehouse_root / index_row["path"].rstrip("\r")
    payload = json.loads(path.read_text())
    general, header, content = payload.get("general") or {}, payload.get("header") or {}, payload.get("content") or {}
    status = header.get("status") or {}
    home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    ev = event_list(content)
    stats = flat_stats(content)
    awarded = int(bool(status.get("awarded")))
    row = {"match_id": index_row["match_id"], "league": "AE-ProLeague", "season": index_row["season"],
           "date": index_row["date"], "round": str(general.get("matchRound") or ""),
           "phase": "regular", "awarded": awarded,
           "home_team_id": home.get("id"), "home_team": home.get("name"),
           "away_team_id": away.get("id"), "away_team": away.get("name"),
           "home_goals": hg, "away_goals": ag}
    goals = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["goal_events_match_score"] = int(len(goals) == hg + ag)
    first_goals = [e for e in goals if (event_minute(e) or 999) <= 45]
    row["ht_home_goals"] = sum(bool(e.get("isHome")) for e in first_goals)
    row["ht_away_goals"] = sum(not bool(e.get("isHome")) for e in first_goals)
    row["ht_source"] = "events" if ev and row["goal_events_match_score"] else "unreliable"
    for is_home in (True, False):
        side = "home" if is_home else "away"
        ys = [e for e in ev if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and bool(e.get("isHome")) == is_home]
        row[f"ev_yellow_{side}"] = len(ys)
        row[f"ev_red_{side}"] = sum(e.get("card") == "Red" for e in ev if e.get("type") == "Card" and bool(e.get("isHome")) == is_home)
        row[f"ht_ev_yellow_{side}"] = sum((event_minute(e) or 999) <= 45 for e in ys)
    for key in STAT_KEYS:
        h, a = stats.get(("All", key), (None, None))
        row[f"{key}_home"], row[f"{key}_away"] = h, a
        h1, a1 = stats.get(("FirstHalf", key), (None, None))
        row[f"{key}_1h_home"], row[f"{key}_1h_away"] = h1, a1
    # cards target: stats feed (see module docstring)
    row["yellow_home"], row["yellow_away"] = row["yellow_cards_home"], row["yellow_cards_away"]
    row["red_home"], row["red_away"] = row["red_cards_home"], row["red_cards_away"]
    row["cards_source"] = "stats"
    ref = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {})
    row["referee"] = (ref.get("text") or "").strip()
    row["has_stats_all"] = int(all(("All", k) in stats for k in ("ShotsOnTarget", "corners", "total_shots")))
    row["has_events"] = int(bool(ev))
    row["has_period_splits"] = int(any(p in ((content.get("stats") or {}).get("Periods") or {}) for p in ("FirstHalf", "SecondHalf")))
    row["has_shotmap"] = int(bool(((content.get("shotmap") or {}).get("shots") or [])))
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE)
    args = ap.parse_args()
    index = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [build(r, args.warehouse_root) for r in csv.DictReader(index.open()) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    counts = {}
    for r in rows:
        counts[r["season"]] = counts.get(r["season"], 0) + 1
    expected = {"2021/2022": 182, "2022/2023": 182, "2023/2024": 182,
                "2024/2025": 182, "2025/2026": 182}
    # Completed seasons stay exact; the in-progress 2026/2027 season
    # (49 rows at build time, growing) and the total are floors so a
    # daily rebuild survives new played matches (AU/MLS/USLL1 trap
    # precedent).
    assert all(counts.get(s) == n for s, n in expected.items()), counts
    assert counts.get("2026/2027", 0) >= 49, counts
    assert len(rows) >= 959, len(rows)
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "ae_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "awarded": r["awarded"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"],
                 "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]}
            for k in STAT_KEYS:
                x[f"{k}_for"], x[f"{k}_against"] = r.get(f"{k}_{side}"), r.get(f"{k}_{other}")
            x["yellow_for"], x["yellow_against"] = r[f"yellow_{side}"], r[f"yellow_{other}"]
            x["ev_yellow_for"], x["ev_yellow_against"] = r[f"ev_yellow_{side}"], r[f"ev_yellow_{other}"]
            team_rows.append(x)
    with (HERE / "ae_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        w.writeheader(); w.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)} seasons={counts}")

if __name__ == "__main__":
    main()
