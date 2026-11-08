"""Build the HR-HNL analysis CSV from the FotMob world warehouse.

One row per played match (league_id 252). Adapted from
league/FI-Veikkausliiga/data/build_data.py (itself from league/jleague_lib.py):
FT score from header.status.scoreStr, team stats from
content.stats.Periods (All/FirstHalf/SecondHalf), cards from BOTH the
stats feed (yellow_cards/red_cards keys, present in every season) and
the event feed (Card events, every season) so the stats-vs-events
artefact check can be run before the target is frozen. The modelling
target columns yellow_* are left as the STATS values here; the prereg
freezes the final target after the artefact check (see analysis/EDA.md
F6) — the builder records both sources and never merges them silently.
Referee name from content.matchFacts.infoBox.Referee.text. The league
was renamed mid-corpus: general.leagueName is "1. Division" in
2021/2022, mixed in 2022/2023, "HNL" from 2023/2024 — recorded per row
as league_name. All fixtures are regular-season quadruple round-robin
rounds (general.matchRound 1..36); there is no split/play-off phase in
this league, so phase is "regular" for every row. Team identity is
keyed on FotMob team id (id 10165 appears as both "NK Varazdin" and
"NK Varaždin" from 2025/2026 — a name variant, not two clubs).
1H goals / 1H yellows are counted from event times (time <= 45 = first
half, incl. 45+ stoppage). No shotmap exists in any season
(has_shotmap False for 964/964), so the sm_* columns are all zero/empty
by construction and no xG key exists in the stats feed.

Regenerate: .venv/bin/python league/HR-HNL/data/build_data.py
Output (gitignored): league/HR-HNL/data/hr_matches.csv (+ team table)
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")  # warehouse lives in main checkout (gitignored data)
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion","expected_goals","expected_goals_open_play","expected_goals_set_play",
 "expected_goals_non_penalty","total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots",
 "shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards",
 "red_cards","fouls","Offsides","keeper_saves"]

def _num(v):
    if v is None: return None
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,str):
        try: return float(v.split(" ")[0].replace("%",""))
        except ValueError: return None
    return None

def flat_stats(content):
    out={}
    periods=((content or {}).get("stats") or {}).get("Periods") or {}
    for period,block in periods.items():
        for group in (block or {}).get("stats",[]) or []:
            for s in group.get("stats",[]) or []:
                vals=s.get("stats") or [None,None]
                h=_num(vals[0]); a=_num(vals[1]) if len(vals)>1 else None
                if h is None and a is None: continue
                out[(period,s.get("key"))]=(h,a)
    return out

def main():
    rows=[r for r in csv.DictReader(open(INDEX)) if r["league_id"]=="252"]
    rows.sort(key=lambda r:(r["date"], r["match_id"]))
    out=[]
    for r in rows:
        d=json.load(open(MAIN_REPO/r["path"]))
        gen=d.get("general") or {}; hdr=d.get("header") or {}; st=hdr.get("status") or {}
        if not st.get("finished"): continue
        c=d.get("content") or {}
        fs=flat_stats(c)
        def g(period,key):
            v=fs.get((period,key)); return v if v else (None,None)
        rec={"match_id":r["match_id"],"league":"HR-HNL","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "phase":"regular","league_name":gen.get("leagueName"),
             "home_team_id":gen["homeTeam"]["id"],"home_team":gen["homeTeam"]["name"],
             "away_team_id":gen["awayTeam"]["id"],"away_team":gen["awayTeam"]["name"],
             "coverage_level":gen.get("coverageLevel")}
        ss=(st.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"]=int(ss[0]); rec["away_goals"]=int(ss[1])
        evs=((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals=[e for e in evs if e.get("type")=="Goal"]
        if evs:
            rec["ht_home_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and e.get("isHome"))
            rec["ht_away_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and not e.get("isHome"))
            rec["ht_source"]="events"
        else:
            rec["ht_home_goals"]=None; rec["ht_away_goals"]=None; rec["ht_source"]="none"
        rec["ev_yellow_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("isHome"))
        rec["ev_yellow_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and not e.get("isHome"))
        rec["ev_yellow_1h"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("time") is not None and e["time"]<=45)
        rec["goals_1h_total"]=(rec["ht_home_goals"] or 0)+(rec["ht_away_goals"] or 0)
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        # Modelling target = STATS yellows (keys exist in every season); the
        # event-derived columns above stay as the artefact-check comparison.
        sy_h,sy_a=g("All","yellow_cards"); rec["yellow_home"]=sy_h; rec["yellow_away"]=sy_a
        sr_h,sr_a=g("All","red_cards"); rec["red_home"]=sr_h; rec["red_away"]=sr_a
        rec["stats_yellow_home"]=sy_h; rec["stats_yellow_away"]=sy_a
        rec["stats_red_home"]=sr_h; rec["stats_red_away"]=sr_a
        rec["cards_source"]="stats" if sy_h is not None else "none"
        ref=(((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        rec["referee"]=ref
        periods=list(((c.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"]=int(("All", "corners") in fs)
        rec["has_stats_half"]=int(("FirstHalf","corners") in fs)
        rec["has_extra_time"]=int(any("Extra" in p for p in periods))
        shots=((c.get("shotmap") or {}).get("shots") or [])
        reg=[s for s in shots if s.get("period")!="PenaltyShootout"]
        rec["has_shotmap"]=int(len(reg)>0); rec["n_shootout_shots"]=len(shots)-len(reg)
        for side in ("home","away"):
            rec[f"sm_shots_{side}"]=0; rec[f"sm_sot_{side}"]=0; rec[f"sm_xg_{side}"]=0.0
            rec[f"sm_xgot_{side}"]=0.0; rec[f"sm_xgot_n_{side}"]=0; rec[f"sm_shots_fh_{side}"]=0
        rec["has_events"]=int(len(evs)>0)
        out.append(rec)
    assert len(out)==len(rows), (len(out),len(rows))
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"hr_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm=[]
    for r in out:
        for side,opp in (("home","away"),("away","home")):
            t={"match_id":r["match_id"],"season":r["season"],"date":r["date"],"phase":r["phase"],
               "team_id":r[f"{side}_team_id"],"team":r[f"{side}_team"],"venue":side,
               "goals_for":r["home_goals"] if side=="home" else r["away_goals"],
               "goals_against":r["away_goals"] if side=="home" else r["home_goals"]}
            for k in ["expected_goals","total_shots","ShotsOnTarget","corners","yellow_cards","touches_opp_box","big_chance","BallPossesion"]:
                t[f"{k}_for"]=r.get(f"{k}_{side}"); t[f"{k}_against"]=r.get(f"{k}_{opp}")
            t["sm_xg_for"]=r[f"sm_xg_{side}"]; t["sm_shots_for"]=r[f"sm_shots_{side}"]
            tm.append(t)
    with open(OUT/"hr_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
