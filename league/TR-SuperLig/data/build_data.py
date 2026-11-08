"""Build the Türkiye Süper Lig phase-1 match and team-match tables.

Only finished, played matches are emitted. FotMob rows marked
``header.status.awarded`` are administrative 3-0/0-3 results and are excluded
from every analysis table, regardless of team name. Team identity is always
the FotMob team id.
"""
import csv, json
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion","expected_goals","expected_goals_open_play","expected_goals_set_play",
 "expected_goals_non_penalty","total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots",
 "shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards",
 "red_cards","fouls","Offsides","keeper_saves"]

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
    index = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "71"]
    index.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    awarded = {}
    for ix in index:
        d = json.load(open(MAIN_REPO / ix["path"]))
        gen = d.get("general") or {}; hdr = d.get("header") or {}; status = hdr.get("status") or {}
        if status.get("awarded"):
            awarded[ix["season"]] = awarded.get(ix["season"], 0) + 1
            continue
        if not status.get("finished"): continue
        content = d.get("content") or {}; fs = flat_stats(content)
        def g(period, key): return fs.get((period, key), (None, None))
        rec = {"match_id": ix["match_id"], "league": "TR-SuperLig", "season": ix["season"],
               "date": ix["date"], "round": str(gen.get("matchRound")), "phase": "regular",
               "league_name_raw": gen.get("leagueName"),
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "coverage_level": gen.get("coverageLevel")}
        score = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(score[0]), int(score[1])
        events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in events if e.get("type") == "Goal"]
        if events:
            rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
            rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
            rec["ht_source"] = "events"
        else:
            rec["ht_home_goals"] = rec["ht_away_goals"] = None; rec["ht_source"] = "none"
        rec["ev_yellow_home"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome"))
        rec["ev_yellow_away"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "Yellow" and not e.get("isHome"))
        rec["ev_red_home"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and e.get("isHome"))
        rec["ev_red_away"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and not e.get("isHome"))
        rec["ev_yellowred_home"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "YellowRed" and e.get("isHome"))
        rec["ev_yellowred_away"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == "YellowRed" and not e.get("isHome"))
        for key in STAT_KEYS:
            rec[f"{key}_home"], rec[f"{key}_away"] = g("All", key)
            rec[f"fh_{key}_home"], rec[f"fh_{key}_away"] = g("FirstHalf", key)
            rec[f"sh_{key}_home"], rec[f"sh_{key}_away"] = g("SecondHalf", key)
        rec["yellow_home"], rec["yellow_away"] = rec["yellow_cards_home"], rec["yellow_cards_away"]
        rec["red_home"], rec["red_away"] = rec["red_cards_home"], rec["red_cards_away"]
        if rec["yellow_home"] is None:
            rec["yellow_home"], rec["yellow_away"] = float(rec["ev_yellow_home"]), float(rec["ev_yellow_away"])
            rec["cards_source"] = "events"
        elif rec["yellow_home"] + rec["yellow_away"] == 0 and (rec["ev_yellow_home"] + rec["ev_yellow_away"]) > 0:
            # Broken stats discipline block (frozen rule, dev-era evidence):
            # stats yellows zeroed while the event feed records yellows in the
            # same match (47 matches warehouse-wide, 43 in 2021/2022; other
            # stat keys in those matches are intact, and 3 even carry stats
            # reds > 0). Unified target falls back to event yellows, exactly
            # like the stats-absent fallback above.
            rec["yellow_home"], rec["yellow_away"] = float(rec["ev_yellow_home"]), float(rec["ev_yellow_away"])
            rec["cards_source"] = "events_broken_stats"
        else: rec["cards_source"] = "stats"
        rec["referee"] = ((((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text"))
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs)
        rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        rec["has_extra_time"] = int(any("Extra" in p for p in periods))
        shots = ((content.get("shotmap") or {}).get("shots") or [])
        reg = [s for s in shots if s.get("period") != "PenaltyShootout"]
        rec["has_shotmap"], rec["n_shootout_shots"] = int(bool(reg)), len(shots) - len(reg)
        for side, tid in (("home", rec["home_team_id"]), ("away", rec["away_team_id"])):
            side_shots = [s for s in reg if s.get("teamId") == tid]
            rec[f"sm_shots_{side}"] = len(side_shots)
            rec[f"sm_sot_{side}"] = sum(1 for s in side_shots if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in side_shots), 4)
            xgots = [s.get("expectedGoalsOnTarget") for s in side_shots if s.get("expectedGoalsOnTarget") is not None]
            rec[f"sm_xgot_{side}"], rec[f"sm_xgot_n_{side}"] = round(sum(xgots), 4), len(xgots)
            rec[f"sm_shots_fh_{side}"] = sum(1 for s in side_shots if s.get("period") == "FirstHalf")
        rec["has_events"] = int(bool(events))
        if not rec["has_events"] and not rec["has_shotmap"]:
            for key in STAT_KEYS:
                for pfx in ("", "fh_", "sh_"):
                    rec[f"{pfx}{key}_home"] = rec[f"{pfx}{key}_away"] = None
            rec["yellow_home"] = rec["yellow_away"] = rec["red_home"] = rec["red_away"] = None
            rec["cards_source"] = "none"
            for side in ("home", "away"):
                for prefix in ("sm_shots_", "sm_sot_", "sm_xg_", "sm_xgot_", "sm_xgot_n_", "sm_shots_fh_"):
                    rec[f"{prefix}{side}"] = None
        out.append(rec)
    assert len(set(r["match_id"] for r in out)) == len(out)
    with open(OUT / "tr_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]}
            for key in ["expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"]:
                t[f"{key}_for"], t[f"{key}_against"] = r.get(f"{key}_{side}"), r.get(f"{key}_{opp}")
            t["sm_xg_for"], t["sm_shots_for"] = r[f"sm_xg_{side}"], r[f"sm_shots_{side}"]
            tm.append(t)
    with open(OUT / "tr_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0])); w.writeheader(); w.writerows(tm)
    print("matches", len(out), "team_rows", len(tm), "awarded", dict(sorted(awarded.items())))

if __name__ == "__main__": main()
