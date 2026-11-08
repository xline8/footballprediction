"""Build the Türkiye 1. Lig match and team-match tables.

The index corpus is retained one-for-one, including administrative awarded
rows.  Downstream fitting and EDA apply the explicit awarded/phase rules.
"""
import csv
import json
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
PLAYOFF_ROUNDS = {"1/4", "1/2", "final"}


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).split(" ")[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or [None, None]
                h = _num(vals[0])
                a = _num(vals[1]) if len(vals) > 1 else None
                if h is not None or a is not None:
                    out[(period, stat.get("key"))] = (h, a)
    return out


def main():
    index = [r for r in csv.DictReader(open(INDEX, encoding="utf-8"))
             if r["league_id"] == "165"]
    index.sort(key=lambda r: (r["date"], r["match_id"]))
    out, awarded = [], {}
    for ix in index:
        d = json.load(open(MAIN_REPO / ix["path"], encoding="utf-8"))
        gen = d.get("general") or {}
        hdr = d.get("header") or {}
        status = hdr.get("status") or {}
        content = d.get("content") or {}
        fs = flat_stats(content)
        get = lambda period, key: fs.get((period, key), (None, None))
        match_round = str(gen.get("matchRound"))
        rec = {
            "match_id": ix["match_id"], "league": "TR-1Lig", "season": ix["season"],
            "date": ix["date"], "round": match_round,
            "phase": "playoff" if match_round in PLAYOFF_ROUNDS else "regular",
            "league_name_raw": gen.get("leagueName"),
            "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
            "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
            "coverage_level": gen.get("coverageLevel"),
            "finished": int(bool(status.get("finished"))),
            "awarded": int(bool(status.get("awarded"))),
        }
        if rec["awarded"]:
            awarded[ix["season"]] = awarded.get(ix["season"], 0) + 1
        score = (status.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"], rec["away_goals"] = int(score[0]), int(score[1])
        events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in events if e.get("type") == "Goal"]
        rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        rec["ht_source"] = "events" if events else "none"
        for card, value in (("yellow", "Yellow"), ("red", "Red"), ("yellowred", "YellowRed")):
            for side, is_home in (("home", True), ("away", False)):
                rec[f"ev_{card}_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == value and bool(e.get("isHome")) == is_home)
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                rec[f"{prefix}{key}_home"], rec[f"{prefix}{key}_away"] = get(period, key)
        rec["yellow_home"], rec["yellow_away"] = rec["yellow_cards_home"], rec["yellow_cards_away"]
        rec["red_home"], rec["red_away"] = rec["red_cards_home"], rec["red_cards_away"]
        if rec["yellow_home"] is None:
            rec["yellow_home"], rec["yellow_away"], rec["cards_source"] = rec["ev_yellow_home"], rec["ev_yellow_away"], "events"
        elif rec["yellow_home"] + rec["yellow_away"] == 0 and rec["ev_yellow_home"] + rec["ev_yellow_away"] > 0:
            rec["yellow_home"], rec["yellow_away"], rec["cards_source"] = rec["ev_yellow_home"], rec["ev_yellow_away"], "events_broken_stats"
        else:
            rec["cards_source"] = "stats"
        periods = list(((content.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"] = int(("All", "corners") in fs)
        rec["has_stats_half"] = int(("FirstHalf", "corners") in fs)
        rec["has_extra_time"] = int(any("Extra" in p for p in periods))
        shots = ((content.get("shotmap") or {}).get("shots") or [])
        regulation = [s for s in shots if s.get("period") != "PenaltyShootout"]
        rec["has_shotmap"], rec["n_shootout_shots"] = int(bool(regulation)), len(shots) - len(regulation)
        for side, tid in (("home", rec["home_team_id"]), ("away", rec["away_team_id"])):
            side_shots = [s for s in regulation if s.get("teamId") == tid]
            rec[f"sm_shots_{side}"] = len(side_shots)
            rec[f"sm_sot_{side}"] = sum(1 for s in side_shots if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in side_shots), 4)
            xgots = [s.get("expectedGoalsOnTarget") for s in side_shots if s.get("expectedGoalsOnTarget") is not None]
            rec[f"sm_xgot_{side}"], rec[f"sm_xgot_n_{side}"] = round(sum(xgots), 4), len(xgots)
            rec[f"sm_shots_fh_{side}"] = sum(1 for s in side_shots if s.get("period") == "FirstHalf")
        rec["has_events"] = int(bool(events))
        rec["referee"] = ((((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")) or ""
        out.append(rec)
    assert len(out) == len(index) and len({r["match_id"] for r in out}) == len(out)
    with open(OUT / "tr1_matches.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0])); writer.writeheader(); writer.writerows(out)
    team_rows = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"], "awarded": r["awarded"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]}
            for key in ("expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"):
                t[f"{key}_for"], t[f"{key}_against"] = r[f"{key}_{side}"], r[f"{key}_{opp}"]
            t["sm_xg_for"], t["sm_shots_for"] = r[f"sm_xg_{side}"], r[f"sm_shots_{side}"]
            team_rows.append(t)
    with open(OUT / "tr1_team_matches.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0])); writer.writeheader(); writer.writerows(team_rows)
    print("matches", len(out), "team_rows", len(team_rows), "awarded", dict(sorted(awarded.items())))


if __name__ == "__main__":
    main()
