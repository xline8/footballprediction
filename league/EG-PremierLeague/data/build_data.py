"""Build Egypt Premier League match and team-match tables from FotMob."""
import csv, json
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
 "expected_goals_set_play", "expected_goals_non_penalty", "total_shots",
 "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box",
 "shots_outside_box", "big_chance", "touches_opp_box", "corners",
 "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves"]

def _num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        try: return float(v.split(" ")[0].replace("%", ""))
        except ValueError: return None
    return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                vals = s.get("stats") or [None, None]
                h, a = _num(vals[0]), _num(vals[1]) if len(vals) > 1 else None
                if h is not None or a is not None: out[(period, s.get("key"))] = (h, a)
    return out

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "519"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for idx in rows:
        d = json.load(open(MAIN_REPO / idx["path"]))
        gen, hdr = d.get("general") or {}, d.get("header") or {}
        status = hdr.get("status") or {}
        if not status.get("finished"): continue
        content = d.get("content") or {}; fs = flat_stats(content)
        def g(period, key): return fs.get((period, key), (None, None))
        rec = {"match_id": idx["match_id"], "league": "EG-PremierLeague", "season": idx["season"],
               "date": idx["date"], "round": str(gen.get("matchRound")),
               "phase": "regular" if idx["season"] in ("2021/2022", "2022/2023", "2023/2024") else "split_pooled",
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "coverage_level": gen.get("coverageLevel")}
        score = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(score[0]), int(score[1])
        events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in events if e.get("type") == "Goal"]
        timed_goals = [e for e in goals if isinstance(e.get("time"), (int, float))]
        rec["goal_event_time_coverage"] = int(len(timed_goals) == len(goals)) if goals else 1
        rec["ht_home_goals"] = sum(1 for e in goals if isinstance(e.get("time"), (int, float)) and e["time"] <= 45 and e.get("isHome"))
        rec["ht_away_goals"] = sum(1 for e in goals if isinstance(e.get("time"), (int, float)) and e["time"] <= 45 and not e.get("isHome"))
        rec["ht_source"] = "events" if events else "none"
        for side in ("home", "away"):
            rec[f"ev_yellow_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "Yellow" and bool(e.get("isHome")) == (side == "home"))
            rec[f"ev_yellowred_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "YellowRed" and bool(e.get("isHome")) == (side == "home"))
            rec[f"fh_ev_yellow_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and isinstance(e.get("time"), (int, float)) and e["time"] <= 45 and bool(e.get("isHome")) == (side == "home"))
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                h, a = g(period, key); rec[f"{prefix}{key}_home"], rec[f"{prefix}{key}_away"] = h, a
        rec["yellow_home"], rec["yellow_away"] = rec["yellow_cards_home"], rec["yellow_cards_away"]
        rec["red_home"], rec["red_away"] = rec["red_cards_home"], rec["red_cards_away"]
        rec["cards_source"] = "stats"
        rec["stats_zero_contradicted_by_events"] = int((rec["yellow_home"] or 0) == 0 and (rec["yellow_away"] or 0) == 0 and (rec["ev_yellow_home"] + rec["ev_yellowred_home"] + rec["ev_yellow_away"] + rec["ev_yellowred_away"]) > 0)
        rec["referee"] = ((((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text"))
        stad = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Stadium") or {})
        rec.update({"stadium_name": stad.get("name"), "stadium_city": stad.get("city"), "stadium_lat": stad.get("lat")})
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs); rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        shots = ((content.get("shotmap") or {}).get("shots") or []); reg = [s for s in shots if s.get("period") != "PenaltyShootout"]
        rec["has_shotmap"], rec["n_shootout_shots"] = int(bool(reg)), len(shots) - len(reg)
        for side in ("home", "away"):
            tid = rec[f"{side}_team_id"]; ss = [s for s in reg if s.get("teamId") == tid]
            rec[f"sm_shots_{side}"] = len(ss); rec[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4)
            xgots = [s.get("expectedGoalsOnTarget") for s in ss if s.get("expectedGoalsOnTarget") is not None]
            rec[f"sm_xgot_{side}"], rec[f"sm_xgot_n_{side}"] = round(sum(xgots), 4), len(xgots)
            rec[f"sm_shots_fh_{side}"] = sum(1 for s in ss if s.get("period") == "FirstHalf")
        rec["has_events"] = int(bool(events)); out.append(rec)
    print(f"index rows {len(rows)} finished kept {len(out)} skipped {len(rows)-len(out)}")
    canon = {}
    for idk, namek in (("home_team_id", "home_team"), ("away_team_id", "away_team")):
        counts = {}
        for r in out: counts.setdefault(r[idk], Counter())[r[namek]] += 1
        for tid, c in counts.items(): canon[tid] = c.most_common(1)[0][0]
    for r in out: r["home_team"], r["away_team"] = canon[r["home_team_id"]], canon[r["away_team_id"]]
    with open(OUT / "eg_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side in ("home", "away"):
            opp = "away" if side == "home" else "home"
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]}
            for key in ("expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"):
                t[f"{key}_for"], t[f"{key}_against"] = r.get(f"{key}_{side}"), r.get(f"{key}_{opp}")
            t["sm_xg_for"], t["sm_shots_for"] = r[f"sm_xg_{side}"], r[f"sm_shots_{side}"]; tm.append(t)
    with open(OUT / "eg_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0])); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__ == "__main__": main()
