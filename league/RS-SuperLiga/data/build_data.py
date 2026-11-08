"""Build the RS-SuperLiga analysis CSV from the FotMob world warehouse slice.

One row per played match (league_id 182). Adapted from the FI-Veikkausliiga
reference build script in inbox-muse2/_shared/reference/: FT score from
header.status.scoreStr, team stats from content.stats.Periods
(All/FirstHalf/SecondHalf), shotmap aggregates over regulation shots only
(shotmap is 0% in this league — columns recorded, all zero), cards recorded
BOTH as stats-feed yellows (exist ONLY 2025/2026+2026/2027) and event-derived
yellows (Card events Yellow/YellowRed). Modelling target yellow_* is the
EVENT-derived unified yellows, as in FI.

Era structure (measured 2026-11-10, pre-EDA): stats feed ABSENT in
2021/2022–2024/2025 (no Periods at all), RICH in 2025/2026 (36 keys) and
2026/2027. No expected_goals key in ANY season; no shotmap in ANY season.
Event feed in 2021–2025 carries only Goal/Card/Half types and Card events
are near-absent there (41–66/season vs 1422 in 2025/2026) — see EDA.md.
Phase is taken from general.matchRound (robust to the 2025/2026 leagueName
rename 'Super Liga' -> 'Serbian Super Liga'): 'Championship Round' ->
championship, 'Relegation Round' -> relegation, 'Qualification' ->
qualification, else regular. 1H goals / 1H yellows counted from event
times (time <= 45 = first half, incl. 45+ stoppage).

Regenerate: python3 league/RS-SuperLiga/data/build_data.py
  (run from ~/workspace/league-work/RS-SuperLiga)
Output: league/RS-SuperLiga/data/rs_matches.csv (+ team table)
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # ~/workspace/league-work/RS-SuperLiga
WORK = ROOT / "work"                        # extracted tar: work/Serbia/Super Liga/<season>/<id>.json
INDEX = ROOT / "league" / "RS-SuperLiga" / "data" / "index_182.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion","Offsides","ShotsOffTarget","ShotsOnTarget",
 "accurate_crosses","accurate_passes","aerials_won","big_chance",
 "big_chance_missed_title","blocked_shots","clearances","corners","defense",
 "discipline","dribbles_succeeded","duel_won","duels","fouls",
 "ground_duels_won","interceptions","keeper_saves","long_balls_accurate",
 "matchstats.headers.tackles","opposition_half_passes","own_half_passes",
 "passes","player_throws","red_cards","shot_blocks","shots",
 "shots_inside_box","shots_outside_box","shots_woodwork","total_shots",
 "touches_opp_box","yellow_cards"]

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

def phase_of(gen):
    # leagueName carries the phase in 2021-2025 ('Super Liga Championship
    # Group'); matchRound carries it in 2025/2026 after the rename to
    # 'Serbian Super Liga' ('Championship Round - Round 1').
    for src in (gen.get("leagueName") or "", gen.get("matchRound") or ""):
        s = str(src)
        if "Championship" in s: return "championship"
        if "Relegation" in s: return "relegation"
        if "Qualification" in s: return "qualification"
    return "regular"

def main():
    rows=list(csv.DictReader(open(INDEX)))
    rows.sort(key=lambda r:(r["date"], r["match_id"]))
    out=[]
    skipped=[]
    for r in rows:
        # index path: data_enrichment/fotmob_world/Serbia/Super Liga/<season>/<id>.json
        rel = r["path"].split("fotmob_world/",1)[1]
        p = WORK / rel
        d=json.load(open(p))
        gen=d.get("general") or {}; hdr=d.get("header") or {}; st=hdr.get("status") or {}
        if not st.get("finished"):
            skipped.append(r["match_id"]); continue
        c=d.get("content") or {}
        fs=flat_stats(c)
        def g(period,key):
            v=fs.get((period,key)); return v if v else (None,None)
        rec={"match_id":r["match_id"],"league":"RS-SuperLiga","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "phase":phase_of(gen),
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
        rec["goals_1h_total"]=(rec["ht_home_goals"] or 0)+(rec["ht_away_goals"] or 0) if evs else None
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        rec["yellow_home"]=rec["ev_yellow_home"]; rec["yellow_away"]=rec["ev_yellow_away"]
        rec["red_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and e.get("isHome"))
        rec["red_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and not e.get("isHome"))
        sy_h,sy_a=g("All","yellow_cards"); rec["stats_yellow_home"]=sy_h; rec["stats_yellow_away"]=sy_a
        sr_h,sr_a=g("All","red_cards"); rec["stats_red_home"]=sr_h; rec["stats_red_away"]=sr_a
        rec["cards_source"]="events" if evs else "none"
        ref=(((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        rec["referee"]=ref
        periods=list(((c.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"]=int(("All", "corners") in fs)
        rec["has_stats_half"]=int(("FirstHalf","corners") in fs)
        rec["has_extra_time"]=int(any("Extra" in p for p in periods))
        shots=((c.get("shotmap") or {}).get("shots") or [])
        reg=[s for s in shots if s.get("period")!="PenaltyShootout"]
        rec["has_shotmap"]=int(len(reg)>0); rec["n_shootout_shots"]=len(shots)-len(reg)
        for side,tid in (("home",rec["home_team_id"]),("away",rec["away_team_id"])):
            ss_=[s for s in reg if s.get("teamId")==tid]
            rec[f"sm_shots_{side}"]=len(ss_)
            rec[f"sm_sot_{side}"]=sum(1 for s in ss_ if s.get("isOnTarget") and not s.get("isBlocked"))
            rec[f"sm_xg_{side}"]=round(sum(s.get("expectedGoals") or 0 for s in ss_),4)
            xgots=[s.get("expectedGoalsOnTarget") for s in ss_ if s.get("expectedGoalsOnTarget") is not None]
            rec[f"sm_xgot_{side}"]=round(sum(xgots),4); rec[f"sm_xgot_n_{side}"]=len(xgots)
            rec[f"sm_shots_fh_{side}"]=sum(1 for s in ss_ if s.get("period")=="FirstHalf")
        rec["has_events"]=int(len(evs)>0)
        out.append(rec)
    print(f"index rows {len(rows)} built {len(out)} skipped-not-finished {skipped}")
    assert len(out)+len(skipped)==len(rows)
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"rs_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm=[]
    for r in out:
        for side,opp in (("home","away"),("away","home")):
            t={"match_id":r["match_id"],"season":r["season"],"date":r["date"],"phase":r["phase"],
               "team_id":r[f"{side}_team_id"],"team":r[f"{side}_team"],"venue":side,
               "goals_for":r["home_goals"] if side=="home" else r["away_goals"],
               "goals_against":r["away_goals"] if side=="home" else r["home_goals"]}
            for k in ["total_shots","ShotsOnTarget","corners","yellow_cards","touches_opp_box","big_chance","BallPossesion"]:
                t[f"{k}_for"]=r.get(f"{k}_{side}"); t[f"{k}_against"]=r.get(f"{k}_{opp}")
            t["sm_xg_for"]=r[f"sm_xg_{side}"]; t["sm_shots_for"]=r[f"sm_shots_{side}"]
            tm.append(t)
    with open(OUT/"rs_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
