"""Build the Iceland Besta deildin Phase A analysis CSV.

The FotMob warehouse is in the main checkout, as in the HR-HNL builder.
This file is deliberately a data builder only: it creates match/team CSVs
and contains no modelling or walk-forward code.
"""
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

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split(" ")[0].replace("%", ""))
    except (TypeError, ValueError): return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or [None, None]
                h = num(vals[0]); a = num(vals[1]) if len(vals) > 1 else None
                if h is not None or a is not None:
                    out[(period, stat.get("key"))] = (h, a)
    return out

def phase(general):
    name = general.get("leagueName") or ""
    round_name = general.get("leagueRoundName") or ""
    if "Championship Group" in name or "Championship Round" in round_name:
        return "championship"
    if "Relegation Group" in name or "Relegation Round" in round_name:
        return "relegation"
    return "regular"

def main():
    index_rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "215"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    matches = []
    for ir in index_rows:
        d = json.load(open(MAIN_REPO / ir["path"]))
        general = d.get("general") or {}; status = (d.get("header") or {}).get("status") or {}
        if not status.get("finished"): continue
        content = d.get("content") or {}; fs = flat_stats(content)
        def get(period, key): return fs.get((period, key), (None, None))
        rec = {"match_id": ir["match_id"], "league": "IS-BestaDeildin",
               "season": ir["season"], "date": ir["date"],
               "round": str(general.get("matchRound")),
               "league_round_name": general.get("leagueRoundName"),
               "phase": phase(general), "league_name": general.get("leagueName"),
               "home_team_id": general["homeTeam"]["id"], "home_team": general["homeTeam"]["name"],
               "away_team_id": general["awayTeam"]["id"], "away_team": general["awayTeam"]["name"],
               "coverage_level": general.get("coverageLevel")}
        goals = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(goals[0]), int(goals[1])
        events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goal_events = [e for e in events if e.get("type") == "Goal"]
        rec["ht_home_goals"] = sum(1 for e in goal_events if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["ht_away_goals"] = sum(1 for e in goal_events if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        rec["ht_source"] = "events" if events else "none"
        yellow = lambda e: e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed")
        rec["ev_yellow_home"] = sum(1 for e in events if yellow(e) and e.get("isHome"))
        rec["ev_yellow_away"] = sum(1 for e in events if yellow(e) and not e.get("isHome"))
        rec["ev_yellow_1h"] = sum(1 for e in events if yellow(e) and e.get("time") is not None and e["time"] <= 45)
        rec["goals_1h_total"] = rec["ht_home_goals"] + rec["ht_away_goals"]
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                h, a = get(period, key)
                rec[f"{prefix}{key}_home"] = h; rec[f"{prefix}{key}_away"] = a
        syh, sya = get("All", "yellow_cards"); srh, sra = get("All", "red_cards")
        rec.update(yellow_home=syh, yellow_away=sya, stats_yellow_home=syh,
                   stats_yellow_away=sya, red_home=srh, red_away=sra,
                   stats_red_home=srh, stats_red_away=sra,
                   cards_source="stats" if syh is not None or sya is not None else "none")
        rec["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs)
        rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        rec["has_extra_time"] = int(any("Extra" in p for p in periods))
        shots = ((content.get("shotmap") or {}).get("shots") or [])
        rec["has_shotmap"] = int(bool(shots)); rec["n_shootout_shots"] = 0
        for side in ("home", "away"):
            for k, default in (("sm_shots", 0), ("sm_sot", 0), ("sm_xg", 0.0), ("sm_xgot", 0.0), ("sm_xgot_n", 0), ("sm_shots_fh", 0)):
                rec[f"{k}_{side}"] = default
        rec["has_events"] = int(bool(events)); matches.append(rec)
    assert len(matches) == len(index_rows) >= 942
    assert len({r["match_id"] for r in matches}) == len(matches)
    fields = list(matches[0])
    with open(OUT / "is_matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(matches)
    team_rows = []
    for r in matches:
        for side, other in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]}
            for k in ("expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"):
                t[f"{k}_for"] = r.get(f"{k}_{side}"); t[f"{k}_against"] = r.get(f"{k}_{other}")
            team_rows.append(t)
    with open(OUT / "is_team_matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print("matches", len(matches), "team_rows", len(team_rows))
    print("season_counts", dict(Counter(r["season"] for r in matches)))
    print("phase_counts", dict(Counter(r["phase"] for r in matches)))

if __name__ == "__main__": main()
