"""Build the CO-PrimeraA analysis CSVs from the FotMob world warehouse.

One row per played match (league_id 274). Adapted from the
PY-DivisionProfesional builder / league/jleague_lib.py rules: FT score
from header, team stats from content.stats.Periods (All/FirstHalf),
events from matchFacts, referee + stadium from matchFacts.infoBox.

Colombia Primera A specifics (measured 2026-11-09, see
analysis/DATA_UNDERSTANDING.md):
- Index n = 2,582 and EVERY indexed file is finished at build time
  (verified twice through independent paths). There are NO unfinished
  0-0 placeholder files in the 2021-2025 corpus -- the Primera B trap
  does not occur here. The played corpus is therefore all 2,582 rows,
  EXCLUDING the in-progress 2026 - Clausura only at the modelling
  layer (it is in the CSV, flagged by its season label).
- Split calendar: Apertura + Clausura tournaments per calendar year,
  each regular phase -> quadrangular semi-finals (Grp A/B) -> finals.
  `phase` = regular / quadrangular / final from the payload's
  Tournament name + round string (frozen phase rule: all phases are
  modelled, phase flagged, no phase filter/feature -- the CO-PrimeraB
  precedent, judged on this league's own data in EDA).
- Stats feed (SOT / corners / total shots / yellows / touches) exists
  in ~100% of matches from 2021. Period splits exist only from
  2023 - Clausura onward (with a handful of earlier exceptions).
- Stats-feed xG (expected_goals family) and the shotmap exist ONLY
  from 2025 - Clausura onward -- an era that starts AT the virgin
  boundary, so no xG feature can be fitted or gated on dev data
  (the ES-LaLiga2 lesson). Both are captured here for the record.
- Cards are captured BOTH ways (stats-feed yellow_cards and
  event-derived yellows incl. second-yellow) so the EDA feed check
  can pick the target on dev-era evidence only.
- Movers: clubs are promoted from Primera B (league_id 9125) each
  year. home/away_mover_up flags a club absent from Primera A in the
  previous calendar year but present in Primera B that year;
  home/away_absent_prev flags absence from A regardless of source.

Regenerate: .venv/bin/python league/CO-PrimeraA/data/build_data.py
Outputs (gitignored): co_primeraa_matches.csv + co_primeraa_team_matches.csv
"""
import csv, json
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")  # warehouse lives in main checkout (gitignored data)
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "274"
B_ID = "9125"

STAT_KEYS = ["BallPossesion", "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box", "corners",
             "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
             "expected_goals", "expected_goals_set_play", "expected_goals_open_play",
             "expected_goals_non_penalty", "expected_goals_on_target"]

EXPECTED_COUNTS = {"2021 - Apertura": 185, "2021 - Clausura": 226, "2022 - Apertura": 226,
                   "2022 - Clausura": 226, "2023 - Apertura": 226, "2023 - Clausura": 226,
                   "2024 - Apertura": 216, "2024 - Clausura": 216, "2025 - Apertura": 226,
                   "2025 - Clausura": 226, "2026 - Apertura": 204, "2026 - Clausura": 179}


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
                if h is None and a is None: continue
                out[(period, s.get("key"))] = (h, a)
    return out


def load(row):
    return json.load(open(MAIN_REPO / row["path"], encoding="utf-8"))


def b_teams_by_year(index_rows):
    """Finished Primera B team ids per calendar year (B seasons are year labels)."""
    teams = {}
    for row in index_rows:
        if row["league_id"] != B_ID:
            continue
        d = load(row)
        if not d["header"]["status"].get("finished"):
            continue
        gen = d["general"]
        teams.setdefault(row["season"], set()).update((gen["homeTeam"]["id"], gen["awayTeam"]["id"]))
    return teams


def main():
    index_rows = list(csv.DictReader(open(INDEX, encoding="utf-8")))
    rows = [r for r in index_rows if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    b_teams = b_teams_by_year(index_rows)

    # Pass 1 (streaming): A membership by calendar year + finished assert.
    a_teams_by_year = {}
    for r in rows:
        d = load(r)
        hdr = d.get("header") or {}; st = hdr.get("status") or {}
        assert st.get("finished"), f"unfinished file in corpus: {r['match_id']} {r['season']}"
        gen = d.get("general") or {}
        year = r["season"][:4]
        a_teams_by_year.setdefault(year, set()).update((gen["homeTeam"]["id"], gen["awayTeam"]["id"]))
        del d

    # Pass 2 (streaming): one payload at a time, never retained.
    out = []
    for r in rows:
        d = load(r)
        gen = d.get("general") or {}; hdr = d.get("header") or {}; st = hdr.get("status") or {}
        c = d.get("content") or {}
        fs = flat_stats(c)
        def g(period, key):
            v = fs.get((period, key)); return v if v else (None, None)
        info = ((c.get("matchFacts") or {}).get("infoBox") or {})
        tourn = (info.get("Tournament") or {}).get("leagueName", "")
        phase_text = f"{tourn} {gen.get('leagueRoundName') or ''} {gen.get('matchRound') or ''}"
        if "Quadrangular" in phase_text or "Playoff" in phase_text:
            phase = "quadrangular"
        elif "Final" in phase_text:
            phase = "final"
        else:
            phase = "regular"
        rec = {"match_id": r["match_id"], "league": "CO-PrimeraA", "season": r["season"],
               "tournament": "apertura" if "Apertura" in r["season"] else "clausura",
               "phase": phase, "date": r["date"], "round": str(gen.get("matchRound")),
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "coverage_level": gen.get("coverageLevel")}
        rec["home_goals"] = int(hdr["teams"][0]["score"]); rec["away_goals"] = int(hdr["teams"][1]["score"])
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in evs if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent", False)]
        rec["events_exact"] = int(len(goals) == rec["home_goals"] + rec["away_goals"])
        if rec["events_exact"]:
            rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
            rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
            rec["ht_source"] = "events"
        else:
            rec["ht_home_goals"] = None; rec["ht_away_goals"] = None; rec["ht_source"] = "none"
        for nm, cardset in (("ev_yellow", ("Yellow",)), ("ev_yellow_inc2nd", ("Yellow", "YellowRed"))):
            rec[nm + "_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in cardset and e.get("isHome"))
            rec[nm + "_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in cardset and not e.get("isHome"))
        rec["ev_red_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and e.get("isHome"))
        rec["ev_red_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and not e.get("isHome"))
        rec["fh_ev_yellow_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["fh_ev_yellow_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        rec["n_events"] = len(evs)
        for k in STAT_KEYS:
            for per, suf in (("All", ""), ("FirstHalf", "_1h")):
                h, a = g(per, k)
                rec[f"{k.lower()}_home{suf}"] = h; rec[f"{k.lower()}_away{suf}"] = a
        # Shotmap aggregates (regulation periods only; own goals credited
        # to the opponent, per the jleague_lib rule).
        shots = ((c.get("shotmap") or {}).get("shots") or [])
        home_id = gen["homeTeam"]["id"]
        agg = {"sm_shots_home": 0, "sm_shots_away": 0, "sm_xg_home": 0.0, "sm_xg_away": 0.0,
               "sm_xgot_home": 0.0, "sm_xgot_away": 0.0, "sm_xgot_n_home": 0, "sm_xgot_n_away": 0}
        for s in shots:
            if s.get("period") not in ("FirstHalf", "SecondHalf"):
                continue
            credited_home = (s.get("teamId") == home_id) != bool(s.get("isOwnGoal"))
            side = "home" if credited_home else "away"
            agg[f"sm_shots_{side}"] += 1
            if s.get("expectedGoals") is not None: agg[f"sm_xg_{side}"] += float(s["expectedGoals"])
            if s.get("expectedGoalsOnTarget") is not None:
                agg[f"sm_xgot_{side}"] += float(s["expectedGoalsOnTarget"]); agg[f"sm_xgot_n_{side}"] += 1
        rec.update(agg)
        rec["n_shotmap"] = len(shots)
        rec["referee"] = ((info.get("Referee") or {}).get("text") or "")
        stadium = info.get("Stadium") or {}
        rec["stadium"] = stadium.get("name", ""); rec["stadium_city"] = stadium.get("city", "")
        rec["has_stats"] = int(fs.get(("All", "total_shots")) is not None)
        rec["has_period_splits"] = int(fs.get(("FirstHalf", "total_shots")) is not None)
        rec["has_xg"] = int(fs.get(("All", "expected_goals")) is not None)
        # Mover flags vs the previous CALENDAR year (promotion enters at Apertura).
        year = r["season"][:4]; prev = str(int(year) - 1)
        prev_a = a_teams_by_year.get(prev, set()); prev_b = b_teams.get(prev, set())
        for side in ("home", "away"):
            tid = rec[f"{side}_team_id"]
            rec[f"{side}_absent_prev"] = int(year != "2021" and tid not in prev_a)
            rec[f"{side}_mover_up"] = int(year != "2021" and tid not in prev_a and tid in prev_b)
        out.append(rec)

    names = {}
    for r in out:
        for side in ("home", "away"):
            names.setdefault(r[f"{side}_team_id"], Counter())[r[f"{side}_team"]] += 1
    canon = {tid: cnt.most_common(1)[0][0] for tid, cnt in names.items()}
    for r in out:
        r["home_team"] = canon[r["home_team_id"]]; r["away_team"] = canon[r["away_team_id"]]

    counts = Counter(r["season"] for r in out)
    # The daily runner rebuilds after incremental finished additions, so build-time counts are floors.
    assert all(counts[season] >= expected for season, expected in EXPECTED_COUNTS.items()), dict(counts)
    assert len(out) >= 2582, len(out)
    ids = [r["match_id"] for r in out]; assert len(set(ids)) == len(ids)

    with open(OUT / "co_primeraa_matches.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            tm.append({"match_id": r["match_id"], "season": r["season"], "tournament": r["tournament"],
                       "phase": r["phase"], "date": r["date"],
                       "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                       "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
                       "sot_for": r[f"shotsontarget_{side}"], "sot_against": r[f"shotsontarget_{opp}"],
                       "corners_for": r[f"corners_{side}"], "corners_against": r[f"corners_{opp}"],
                       "shots_for": r[f"total_shots_{side}"], "shots_against": r[f"total_shots_{opp}"],
                       "yellow_for": r[f"yellow_cards_{side}"], "yellow_against": r[f"yellow_cards_{opp}"],
                       "ev_yellow_for": r[f"ev_yellow_inc2nd_{side}"], "ev_yellow_against": r[f"ev_yellow_inc2nd_{opp}"]})
    with open(OUT / "co_primeraa_team_matches.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")
    print("per-season:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
