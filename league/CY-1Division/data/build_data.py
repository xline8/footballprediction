"""Build Cyprus 1. Division Phase A tables from the FotMob warehouse."""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WAREHOUSE = Path.home() / "workspace" / "footballprediction"
LEAGUE_ID = "136"
STAT_KEYS = ("BallPossesion", "ShotsOnTarget", "corners", "total_shots")

def number(value):
    if value in (None, ""): return None
    try: return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError): return None

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
    try: return float(value if isinstance(value, (int, float)) else str(value).split("+")[0])
    except (TypeError, ValueError): return None

def score(value):
    a, b = (value or "0 - 0").split("-")[:2]
    return int(a.strip()), int(b.strip())

def phase(name):
    name = (name or "").strip()
    for suffix, value in ((" Championship Playoff", "championship_playoff"),
                          (" Relegation Playoff", "relegation_playoff")):
        if name.endswith(suffix): return value
    if name in ("1. Division", "Cyprus League"): return "regular"
    raise ValueError(f"unexpected leagueName: {name!r}")

def build(index_row, warehouse_root):
    path = warehouse_root / index_row["path"].rstrip("\r")
    payload = json.loads(path.read_text())
    general, header, content = payload.get("general") or {}, payload.get("header") or {}, payload.get("content") or {}
    status = header.get("status") or {}
    home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    ev = event_list(content); stats = flat_stats(content)
    row = {"match_id": index_row["match_id"], "league": "CY-1Division", "season": index_row["season"],
           "date": index_row["date"], "round": str(general.get("matchRound") or ""),
           "phase": phase(general.get("leagueName")), "home_team_id": home.get("id"), "home_team": home.get("name"),
           "away_team_id": away.get("id"), "away_team": away.get("name"), "home_goals": hg, "away_goals": ag}
    goals = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    first_goals = [e for e in goals if (event_minute(e) or 999) <= 45]
    row["ht_home_goals"] = sum(bool(e.get("isHome")) for e in first_goals)
    row["ht_away_goals"] = sum(not bool(e.get("isHome")) for e in first_goals)
    row["ht_source"] = "events" if ev else "none"
    for is_home in (True, False):
        side = "home" if is_home else "away"
        ys = [e for e in ev if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and bool(e.get("isHome")) == is_home]
        direct = sum(e.get("card") == "Yellow" for e in ys); yr = sum(e.get("card") == "YellowRed" for e in ys)
        row[f"ev_yellow_direct_{side}"], row[f"ev_yellowred_{side}"] = direct, yr
        row[f"ev_yellow_{side}"] = direct + yr
        row[f"ev_red_{side}"] = sum(e.get("card") == "Red" for e in ev if e.get("type") == "Card" and bool(e.get("isHome")) == is_home) + yr
        row[f"ht_yellow_{side}"] = sum((event_minute(e) or 999) <= 45 for e in ys)
    for key in STAT_KEYS:
        h, a = stats.get(("All", key), (None, None))
        row[f"{key}_home"], row[f"{key}_away"] = h, a
    row["yellow_home"], row["yellow_away"] = row["ev_yellow_home"], row["ev_yellow_away"]
    row["red_home"], row["red_away"] = row["ev_red_home"], row["ev_red_away"]
    row["cards_source"] = "events"; row["referee"] = ""
    row["has_stats_all"] = int(any(("All", k) in stats for k in STAT_KEYS))
    row["has_stats_flag"] = int(str(index_row.get("has_stats", "")).lower() == "true")
    row["has_events"] = int(bool(ev))
    row["has_period_splits_content"] = int(any(p in (((content.get("stats") or {}).get("Periods") or {})) for p in ("FirstHalf", "SecondHalf")))
    row["has_shotmap"] = int(bool(((content.get("shotmap") or {}).get("shots") or [])))
    return row

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE); args = ap.parse_args()
    index = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [build(r, args.warehouse_root) for r in csv.DictReader(index.open()) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"])); expected = {
        "2021/2022":{"regular":132,"championship_playoff":30,"relegation_playoff":30},
        "2022/2023":{"regular":182,"championship_playoff":30,"relegation_playoff":56},
        "2023/2024":{"regular":182,"championship_playoff":30,"relegation_playoff":56},
        "2024/2025":{"regular":182,"championship_playoff":30,"relegation_playoff":28},
        "2025/2026":{"regular":182,"championship_playoff":30,"relegation_playoff":28},
        "2026/2027":{"regular":63}}
    actual = {}
    for r in rows: actual.setdefault(r["season"], {})[r["phase"]] = actual.setdefault(r["season"], {}).get(r["phase"], 0) + 1
    # Daily rebuilds: the world index grows as new 2026/2027 matches are
    # played, so the frozen build-time counts break on a live rebuild
    # (the AU/MLS trap). 1271 and the per-phase counts are floors now.
    assert len(rows) >= 1271, len(rows)
    for _season, _phases in expected.items():
        for _phase, _n in _phases.items():
            assert actual.get(_season, {}).get(_phase, 0) >= _n, (_season, _phase, actual)
    HERE.mkdir(parents=True, exist_ok=True)
    for name, output_rows in (("cy_matches.csv", rows), ("cy_team_matches.csv", [])):
        if name == "cy_team_matches.csv":
            for r in rows:
                for side, other in (("home","away"),("away","home")):
                    x={"match_id":r["match_id"],"season":r["season"],"date":r["date"],"phase":r["phase"],"team_id":r[f"{side}_team_id"],"team":r[f"{side}_team"],"venue":side,"goals_for":r[f"{side}_goals"],"goals_against":r[f"{other}_goals"]}
                    for k in STAT_KEYS: x[f"{k}_for"],x[f"{k}_against"] = r.get(f"{k}_{side}"),r.get(f"{k}_{other}")
                    x["yellow_events_for"],x["yellow_events_against"] = r[f"ev_yellow_{side}"],r[f"ev_yellow_{other}"]; output_rows.append(x)
        with (HERE / name).open("w", newline="") as fh:
            w=csv.DictWriter(fh, fieldnames=list(output_rows[0]), extrasaction="ignore"); w.writeheader(); w.writerows(output_rows)
    print(f"matches={len(rows)} team_rows={len(output_rows)}")

if __name__ == "__main__": main()
