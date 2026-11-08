"""Build Ukraine Premier League Phase A tables from the FotMob warehouse."""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_WAREHOUSE = Path.home() / "workspace" / "footballprediction"
MAIN_REPO = DEFAULT_WAREHOUSE
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
STAT_KEYS = ("BallPossesion", "expected_goals", "expected_goals_set_play", "total_shots",
             "ShotsOnTarget", "big_chance", "touches_opp_box", "corners",
             "yellow_cards", "red_cards")

def number(v):
    if v in (None, ""): return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split()[0].replace("%", ""))
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
                    if h is not None or a is not None: out[(period, stat.get("key"))] = (h, a)
    return out

def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []

def count_card(es, card, home):
    return sum(1 for e in es if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == home)

def score(s):
    p = (s or "0 - 0").split("-"); return int(p[0].strip()), int(p[1].strip())

def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general, header = payload.get("general") or {}, payload.get("header") or {}
    status, content = header.get("status") or {}, payload.get("content") or {}
    stats, es = flat_stats(content), events(content)
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    ht, at = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    row = {"match_id": index_row["match_id"], "league": "UA-PremierLeague", "season": index_row["season"],
           "date": index_row["date"], "round": str(general.get("matchRound") or ""), "phase": "regular",
           "home_team_id": ht.get("id"), "home_team": ht.get("name"), "away_team_id": at.get("id"),
           "away_team": at.get("name"), "home_goals": hg, "away_goals": ag}
    goals = [e for e in es if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["ht_ev_yellow_home"] = sum(1 for e in es if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_ev_yellow_away"] = sum(1 for e in es if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["ht_source"] = "events" if es else "none"
    for side in (True, False):
        p = "home" if side else "away"
        direct, second = count_card(es, "Yellow", side), count_card(es, "YellowRed", side)
        row[f"ev_yellow_direct_{p}"], row[f"ev_yellowred_{p}"] = direct, second
        row[f"ev_yellow_{p}"] = direct + second
        row[f"ev_red_{p}"] = count_card(es, "Red", side) + second
    for key in STAT_KEYS:
        for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
            h, a = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = h, a
    row["yellow_home"], row["yellow_away"] = row["yellow_cards_home"], row["yellow_cards_away"]
    row["red_home"], row["red_away"] = row["red_cards_home"], row["red_cards_away"]
    if row["yellow_home"] is None or row["yellow_away"] is None:
        row["yellow_home"], row["yellow_away"], row["cards_source"] = float(row["ev_yellow_home"]), float(row["ev_yellow_away"]), "events"
    else: row["cards_source"] = "stats"
    row["stadium"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Stadium") or {}).get("name") or ""
    row["finished"] = int(bool(status.get("finished")))
    row["cancelled"] = int(bool(status.get("cancelled")))
    row["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["has_stats_half"] = int(("FirstHalf", "corners") in stats and ("SecondHalf", "corners") in stats)
    row["has_events"] = int(bool(es))
    row["has_period_splits_content"] = int(any(p in ((content.get("stats") or {}).get("Periods") or {}) for p in ("FirstHalf", "SecondHalf")))
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    regular = [s for s in shots if s.get("period") != "PenaltyShootout"]
    row["has_shotmap"], row["n_shootout_shots"] = int(bool(regular)), len(shots) - len(regular)
    for side, tid in (("home", ht.get("id")), ("away", at.get("id"))):
        ss = [s for s in regular if s.get("teamId") == tid]
        row[f"sm_shots_{side}"] = len(ss) if regular else None
        row[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked")) if regular else None
        row[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4) if regular else None
        xgot = [s.get("expectedGoalsOnTarget") for s in ss if s.get("expectedGoalsOnTarget") is not None]
        row[f"sm_xgot_{side}"] = round(sum(xgot), 4) if regular else None
        row[f"sm_xgot_n_{side}"] = len(xgot) if regular else None
    return row

def main():
    rows = [build(r, MAIN_REPO) for r in csv.DictReader(INDEX.open()) if r["league_id"] == "441"]
    rows.sort(key=lambda r: (r["date"], r["match_id"])); assert len(rows) >= 1191
    out = HERE; out.mkdir(parents=True, exist_ok=True)
    with (out / "ua_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]}
            for k in ("expected_goals", "expected_goals_set_play", "total_shots", "ShotsOnTarget", "corners",
                      "yellow_cards", "red_cards", "touches_opp_box", "big_chance", "BallPossesion"):
                x[f"{k}_for"], x[f"{k}_against"] = r.get(f"{k}_{side}"), r.get(f"{k}_{other}")
            x["yellow_events_for"], x["yellow_events_against"] = r[f"ev_yellow_{side}"], r[f"ev_yellow_{other}"]
            team.append(x)
    with (out / "ua_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} team_rows={len(team)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--warehouse-root", type=Path)
    args = ap.parse_args()
    if args.warehouse_root is not None:
        MAIN_REPO = args.warehouse_root
        INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
    main()

