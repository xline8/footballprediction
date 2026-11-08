"""Build the played-match table for FotMob league 264 (BE First Division B)."""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
RESERVE_IDS = {1173026, 1378462, 1378463, 1378461, 1379188}
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
 "expected_goals_set_play", "expected_goals_non_penalty", "total_shots",
 "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box",
 "shots_outside_box", "big_chance", "touches_opp_box", "corners",
 "yellow_cards", "red_cards"]

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split()[0].replace('%', ''))
    except (ValueError, IndexError): return None

def flat_stats(content):
    out = {}
    for period, block in (((content or {}).get("stats") or {}).get("Periods") or {}).items():
        for group in (block or {}).get("stats", []) or []:
            for item in group.get("stats", []) or []:
                vals = item.get("stats") or []
                h, a = (num(vals[0]) if vals else None), (num(vals[1]) if len(vals) > 1 else None)
                if h is not None or a is not None: out[(period, item.get("key"))] = (h, a)
    return out

def phase(name):
    n = (name or "").lower()
    if "relegation" in n: return "relegation_group"
    if "promotion playoff" in n or "promotion play-off" in n: return "promotion_playoff"
    if "promotion group" in n: return "promotion_group"
    return "regular"

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "264"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for ix in rows:
        d = json.load(open(MAIN_REPO / ix["path"])); g = d.get("general") or {}
        st = (d.get("header") or {}).get("status") or {}
        if not st.get("finished"): continue
        c = d.get("content") or {}; fs = flat_stats(c)
        home, away = g["homeTeam"], g["awayTeam"]
        rec = {"match_id": ix["match_id"], "league": "BE-FirstDivisionB", "season": ix["season"],
               "date": ix["date"], "round": str(g.get("matchRound")),
               "phase": phase(g.get("leagueName")), "league_name_raw": g.get("leagueName"),
               "home_team_id": home["id"], "home_team": home["name"],
               "away_team_id": away["id"], "away_team": away["name"],
               "is_reserve_home": int(home["id"] in RESERVE_IDS),
               "is_reserve_away": int(away["id"] in RESERVE_IDS),
               "coverage_level": g.get("coverageLevel")}
        score = (st.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(score[0]), int(score[1])
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in evs if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
        for side, home_flag in (("home", True), ("away", False)):
            rec[f"ht_{side}_goals"] = sum(1 for e in goals if e.get("isHome") == home_flag and e.get("time") is not None and e["time"] <= 45)
            rec[f"ev_yellow_{side}"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") == home_flag)
            rec[f"ev_red_{side}"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and e.get("isHome") == home_flag)
            rec[f"ev_yellowred_{side}"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") == "YellowRed" and e.get("isHome") == home_flag)
        rec["ht_source"] = "events" if evs else "none"
        def get(period, key): return fs.get((period, key), (None, None))
        for key in STAT_KEYS:
            h, a = get("All", key); rec[f"{key}_home"], rec[f"{key}_away"] = h, a
            h, a = get("FirstHalf", key); rec[f"fh_{key}_home"], rec[f"fh_{key}_away"] = h, a
            h, a = get("SecondHalf", key); rec[f"sh_{key}_home"], rec[f"sh_{key}_away"] = h, a
        rec["yellow_home"], rec["yellow_away"] = rec["yellow_cards_home"], rec["yellow_cards_away"]
        rec["red_home"], rec["red_away"] = rec["red_cards_home"], rec["red_cards_away"]
        if rec["yellow_home"] is not None: rec["cards_source"] = "stats"
        elif evs:
            rec["yellow_home"], rec["yellow_away"] = rec["ev_yellow_home"], rec["ev_yellow_away"]; rec["cards_source"] = "events"
        else: rec["cards_source"] = "none"
        rec["referee"] = (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        rec["has_stats_all"] = int(("All", "corners") in fs); rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        rec["has_events"] = int(bool(evs))
        shots = ((c.get("shotmap") or {}).get("shots") or []); shots = [s for s in shots if s.get("period") != "PenaltyShootout"]
        rec["has_shotmap"] = int(bool(shots)); rec["n_shootout_shots"] = 0
        for side, tid in (("home", home["id"]), ("away", away["id"])):
            ss = [s for s in shots if s.get("teamId") == tid]
            rec[f"sm_shots_{side}"] = len(ss); rec[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4)
            rec[f"sm_xgot_{side}"] = round(sum(s.get("expectedGoalsOnTarget") or 0 for s in ss if s.get("expectedGoalsOnTarget") is not None), 4)
            rec[f"sm_xgot_n_{side}"] = sum(1 for s in ss if s.get("expectedGoalsOnTarget") is not None)
        out.append(rec)
    assert len(out) == 1114, len(out); assert len({r["match_id"] for r in out}) == len(out)
    with open(OUT / "beb_matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side in ("home", "away"):
            opp = "away" if side == "home" else "home"
            tm.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
              "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
              "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]})
    with open(OUT / "beb_team_matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tm[0])); w.writeheader(); w.writerows(tm)
    from collections import Counter
    print("matches", len(out), "team_rows", len(tm)); print("rows_per_season", dict(Counter(r["season"] for r in out)))

if __name__ == "__main__": main()
