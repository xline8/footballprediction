"""Build the Germany 3. Liga FotMob analysis tables (league_id 208).

The warehouse has no shotmap and no xG fields.  Goals are therefore the only
goals-model observation, while the stats-feed count targets remain available.
Cards use event-unified yellow counts: the raw stats yellow total is retained
as a cross-check, but event yellows are the target because the corpus check
shows the stats block undercounts them.  A Qualification league label is a
guard and is excluded if it ever appears; the present corpus contains none.
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion", "total_shots", "ShotsOnTarget", "ShotsOffTarget",
             "blocked_shots", "shots_inside_box", "shots_outside_box",
             "big_chance", "touches_opp_box", "corners", "yellow_cards",
             "red_cards", "fouls", "Offsides", "keeper_saves"]

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
                h = _num(vals[0]); a = _num(vals[1]) if len(vals) > 1 else None
                if h is not None or a is not None:
                    out[(period, s.get("key"))] = (h, a)
    return out

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "208"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(MAIN_REPO / r["path"]))
        gen = d.get("general") or {}; hdr = d.get("header") or {}
        status = hdr.get("status") or {}
        if not status.get("finished"): continue
        content = d.get("content") or {}; fs = flat_stats(content)
        def g(period, key): return fs.get((period, key), (None, None))
        league_name = gen.get("leagueName") or ""
        phase = "qualification" if "Qualification" in league_name else "regular"
        if phase == "qualification": continue
        rec = {"match_id": r["match_id"], "league": "DE-3Liga", "season": r["season"],
               "date": r["date"], "round": str(gen.get("matchRound")),
               "phase": phase, "league_name_raw": league_name,
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "coverage_level": gen.get("coverageLevel")}
        score = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"] = int(score[0]); rec["away_goals"] = int(score[1])
        events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in events if e.get("type") == "Goal"]
        rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        rec["ht_source"] = "events" if events else "none"
        for side, home in (("home", True), ("away", False)):
            rec[f"ev_yellow_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") == home)
            rec[f"ev_red_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and e.get("isHome") == home)
            rec[f"ev_yellowred_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "YellowRed" and e.get("isHome") == home)
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                h, a = g(period, key); rec[f"{prefix}{key}_home"] = h; rec[f"{prefix}{key}_away"] = a
        rec["stats_yellow_home"] = rec["yellow_cards_home"]; rec["stats_yellow_away"] = rec["yellow_cards_away"]
        rec["yellow_home"] = float(rec["ev_yellow_home"]); rec["yellow_away"] = float(rec["ev_yellow_away"])
        rec["cards_source"] = "events" if events else "none"
        rec["red_home"] = rec["red_cards_home"]; rec["red_away"] = rec["red_cards_away"]
        rec["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs); rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        rec["has_extra_time"] = int(any("Extra" in p for p in periods)); rec["has_shotmap"] = 0
        rec["n_shootout_shots"] = 0; rec["has_events"] = int(bool(events))
        for side in ("home", "away"):
            for name in ("sm_shots", "sm_sot", "sm_xg", "sm_xgot", "sm_xgot_n", "sm_shots_fh"):
                rec[f"{name}_{side}"] = None
        out.append(rec)
    assert len(out) == len(rows)
    assert len({r["match_id"] for r in out}) == len(out)
    with open(OUT / "de3_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]}
            for k in ["total_shots", "ShotsOnTarget", "corners", "touches_opp_box", "big_chance", "BallPossesion"]:
                t[f"{k}_for"] = r.get(f"{k}_{side}"); t[f"{k}_against"] = r.get(f"{k}_{opp}")
            t["yellow_for"] = r[f"yellow_{side}"]; t["yellow_against"] = r[f"yellow_{opp}"]
            tm.append(t)
    with open(OUT / "de3_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0])); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__ == "__main__": main()
