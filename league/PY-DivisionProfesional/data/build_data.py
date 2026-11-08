"""Build the PY-DivisionProfesional analysis CSV from the FotMob world warehouse.

One row per played match (league_id 199). Adapted from the SA-ProLeague
builder / league/jleague_lib.py rules: FT score from header.status.scoreStr,
team stats from content.stats.Periods (All/FirstHalf/SecondHalf), referee
from matchFacts.infoBox.

Paraguay specifics (measured, see analysis/DATA_UNDERSTANDING.md):
- Stats feed exists ONLY from 2025 - Apertura onward (0% 2021-2024,
  ~100% 2025+). Shotmap is EMPTY in every season (0%) -> NO xG anywhere.
- Split calendar: each year has an Apertura and a Clausura tournament
  (season label carries the phase; `phase` column = apertura/clausura).
  2021 tournaments had 10 teams (90 matches); 2022+ have 12 (132).
- Cards are captured BOTH ways (stats-feed yellow_cards and event-derived
  yellows incl. second-yellow) so the feed check in EDA can pick the target
  on dev-era evidence only.

Regenerate: .venv/bin/python league/PY-DivisionProfesional/data/build_data.py
Output (gitignored): league/PY-DivisionProfesional/data/py_matches.csv (+ team table)
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")  # warehouse lives in main checkout (gitignored data)
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion", "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box", "corners",
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
                h = _num(vals[0]); a = _num(vals[1]) if len(vals) > 1 else None
                if h is None and a is None: continue
                out[(period, s.get("key"))] = (h, a)
    return out

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "199"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(MAIN_REPO / r["path"]))
        gen = d.get("general") or {}; hdr = d.get("header") or {}; st = hdr.get("status") or {}
        if not st.get("finished"): continue
        c = d.get("content") or {}
        fs = flat_stats(c)
        def g(period, key):
            v = fs.get((period, key)); return v if v else (None, None)
        phase = "apertura" if "Apertura" in r["season"] else "clausura"
        rec = {"match_id": r["match_id"], "league": "PY-DivisionProfesional", "season": r["season"],
               "phase": phase, "date": r["date"], "round": str(gen.get("matchRound")),
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "coverage_level": gen.get("coverageLevel")}
        ss = (st.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"] = int(ss[0]); rec["away_goals"] = int(ss[1])
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in evs if e.get("type") == "Goal"]
        if evs:
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
        for k in STAT_KEYS:
            for per, suf in (("All", ""), ("FirstHalf", "_1h"), ("SecondHalf", "_2h")):
                h, a = g(per, k)
                rec[f"{k.lower()}_home{suf}"] = h; rec[f"{k.lower()}_away{suf}"] = a
        ref = (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
        rec["referee"] = ref
        rec["has_stats"] = int(c.get("stats") is not None and fs.get(("All", "total_shots")) is not None)
        rec["has_period_splits"] = int(fs.get(("FirstHalf", "total_shots")) is not None)
        rec["n_shotmap"] = len(((c.get("shotmap") or {}).get("shots") or []))
        out.append(rec)
    # Canonical team names: FotMob name strings vary by era for the same
    # team_id (Guarani/Guaraní, Luqueno/Luqueño, Cerro Porteno/Porteño,
    # Atletico/Atlético Tembetary). Identity is team_id; the display name
    # is the id's most frequent spelling.
    from collections import Counter
    names = {}
    for r in out:
        for side in ("home", "away"):
            names.setdefault(r[f"{side}_team_id"], Counter())[r[f"{side}_team"]] += 1
    canon = {tid: c.most_common(1)[0][0] for tid, c in names.items()}
    for r in out:
        r["home_team"] = canon[r["home_team_id"]]; r["away_team"] = canon[r["away_team_id"]]
    assert len(out) == 1480, len(out)  # all index rows are played matches (verified Step 1)
    ids = [r["match_id"] for r in out]; assert len(set(ids)) == len(ids)
    with open(OUT / "py_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            tm.append({"match_id": r["match_id"], "season": r["season"], "phase": r["phase"], "date": r["date"],
                       "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                       "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
                       "sot_for": r[f"shotsontarget_{side}"], "sot_against": r[f"shotsontarget_{opp}"],
                       "corners_for": r[f"corners_{side}"], "corners_against": r[f"corners_{opp}"],
                       "shots_for": r[f"total_shots_{side}"], "shots_against": r[f"total_shots_{opp}"],
                       "yellow_for": r[f"yellow_cards_{side}"], "yellow_against": r[f"yellow_cards_{opp}"]})
    with open(OUT / "py_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__ == "__main__":
    main()
