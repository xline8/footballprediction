"""Build the Ireland First Division analysis tables from the FotMob warehouse.

League 218. Scores + events ONLY: no team stats, no shotmap, no named
referees in any of the 1,028 payloads (verified by content, not by the
index flags). Yellow cards do not exist in this corpus — the event feed
lists Red / YellowRed only, zero plain 'Yellow' events — so no unified
yellow target is built (yellow_* stays None, cards_source 'none');
ev_yellow_* audit columns count Yellow+YellowRed events only.

Scope: regular-season matches are the modelled population. Playoff
matches (two-legged semi-finals + final, 5 per season) are built into
the table with phase='playoff' but are EXCLUDED from every EDA/design
number and from all fitting and evaluation.
"""
import csv, json
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "expected_goals_non_penalty",
             "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance",
             "touches_opp_box", "corners", "yellow_cards", "red_cards",
             "fouls", "Offsides", "keeper_saves"]

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
    index_rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "218"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = []
    for ir in index_rows:
        d = json.load(open(MAIN_REPO / ir["path"]))
        gen = d.get("general") or {}; status = (d.get("header") or {}).get("status") or {}
        if not status.get("finished"): continue
        content = d.get("content") or {}; fs = flat_stats(content)
        def g(period, key): return fs.get((period, key), (None, None))
        rnd = str(gen.get("matchRound"))
        phase = "regular" if rnd.isdigit() else "playoff"
        rec = {
            "match_id": ir["match_id"], "league": "IE-FirstDivision", "season": ir["season"],
            "date": ir["date"], "round": rnd, "phase": phase,
            "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
            "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
            "coverage_level": gen.get("coverageLevel"),
        }
        score = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(score[0]), int(score[1])
        events = (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])
        goals = [e for e in events if e.get("type") == "Goal"]
        ev_gh = sum(1 for e in goals if e.get("isHome"))
        ev_ga = sum(1 for e in goals if not e.get("isHome"))
        rec["ev_goals_home"], rec["ev_goals_away"] = ev_gh, ev_ga
        rec["score_events_mismatch"] = int((ev_gh, ev_ga) != (rec["home_goals"], rec["away_goals"]) and len(events) > 0)
        # HT goals from goal events (time <= 45, credited side). Two
        # exceptions, both left NaN and flagged: the event-less 0-3
        # (Cabinteely-Galway 2021-04-09) and the side-flipped feed
        # (UCD-Wexford 2025-02-14, events say 0-3 vs official 3-0).
        # Event-less 0-0 matches have HT 0-0 by the FT score itself.
        if rec["score_events_mismatch"]:
            rec["ht_home_goals"], rec["ht_away_goals"] = None, None
            rec["ht_source"] = "mismatch"
        elif not events and (rec["home_goals"], rec["away_goals"]) == (0, 0):
            rec["ht_home_goals"], rec["ht_away_goals"] = 0, 0
            rec["ht_source"] = "inferred-0-0"
        elif not events:
            rec["ht_home_goals"], rec["ht_away_goals"] = None, None
            rec["ht_source"] = "none"
        else:
            rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
            rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
            rec["ht_source"] = "events"
        target_cards = {"Yellow", "YellowRed"}
        strict_cards = {"Yellow"}
        red_cards = {"Red", "YellowRed"}
        for label, cards in (("ev_yellow", target_cards), ("ev_yellow_strict", strict_cards), ("ev_red", red_cards)):
            rec[f"{label}_home"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in cards and e.get("isHome"))
            rec[f"{label}_away"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in cards and not e.get("isHome"))
        rec["ev_yellow_fh_home"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in target_cards and e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["ev_yellow_fh_away"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in target_cards and e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        for key in STAT_KEYS:
            h, a = g("All", key); rec[f"{key}_home"], rec[f"{key}_away"] = h, a
            h, a = g("FirstHalf", key); rec[f"fh_{key}_home"], rec[f"fh_{key}_away"] = h, a
            h, a = g("SecondHalf", key); rec[f"sh_{key}_home"], rec[f"sh_{key}_away"] = h, a
        # NO yellow target exists in this corpus (see module docstring).
        rec["yellow_home"], rec["yellow_away"] = None, None
        rec["red_home"], rec["red_away"] = rec["ev_red_home"], rec["ev_red_away"]
        rec["cards_source"] = "none"
        ref = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {})
        rec["referee"] = ref.get("text") or ""
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs)
        rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        halfs = status.get("halfs") or {}
        # Extra-half keys exist in EVERY match; only a non-empty
        # timestamp means extra time was actually played.
        rec["has_extra_time"] = int(any("Extra" in k and v for k, v in halfs.items()))
        reason = status.get("reason") or {}
        rec["has_shootout"] = int(reason.get("short") == "Pen")
        rec["shootout_winner"] = ""  # decided by penalties; regulation score is the target
        shots = ((content.get("shotmap") or {}).get("shots") or [])
        regulation = [s for s in shots if s.get("period") != "PenaltyShootout"]
        rec["has_shotmap"], rec["n_shootout_shots"] = int(bool(regulation)), len(shots) - len(regulation)
        for side, tid in (("home", rec["home_team_id"]), ("away", rec["away_team_id"])):
            ss = [s for s in regulation if s.get("teamId") == tid]
            rec[f"sm_shots_{side}"] = len(ss)
            rec[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4)
            xgots = [s.get("expectedGoalsOnTarget") for s in ss if s.get("expectedGoalsOnTarget") is not None]
            rec[f"sm_xgot_{side}"], rec[f"sm_xgot_n_{side}"] = round(sum(xgots), 4), len(xgots)
            rec[f"sm_shots_fh_{side}"] = sum(1 for s in ss if s.get("period") == "FirstHalf")
        rec["has_events"] = int(bool(events))
        rows.append(rec)
    assert len(rows) == 1028, len(rows)
    assert len({r["match_id"] for r in rows}) == len(rows)
    assert sum(1 for r in rows if r["phase"] == "regular") == 998, sum(1 for r in rows if r["phase"] == "regular")
    assert sum(1 for r in rows if r["phase"] == "playoff") == 30
    with open(OUT / "ie_first_division_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
                 "ht_goals_for": r["ht_home_goals"] if side == "home" else r["ht_away_goals"],
                 "ht_goals_against": r["ht_away_goals"] if side == "home" else r["ht_home_goals"]}
            team_rows.append(t)
    with open(OUT / "ie_first_division_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print(f"matches {len(rows)} regular {sum(1 for r in rows if r['phase']=='regular')} playoff {sum(1 for r in rows if r['phase']=='playoff')} team_rows {len(team_rows)}")

if __name__ == "__main__": main()
