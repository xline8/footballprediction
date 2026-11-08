"""Build the ENG-LeagueOne analysis CSV from the FotMob world warehouse.

One row per played match (league_id 108). Adapted from league/jleague_lib.py
+ league/J1 preprocessing rules: FT score from header.status.scoreStr,
team stats from content.stats.Periods (All/FirstHalf/SecondHalf), shotmap
aggregates over regulation shots only, unified cards = stats feed (present
for every ENG-LeagueOne match), referee from matchFacts.infoBox.

Regenerate: .venv/bin/python league/ENG-LeagueOne/data/build_data.py
Output (gitignored): league/ENG-LeagueOne/data/engl1_matches.csv (+ team table)
"""
import csv, json, sys
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
    rows=[r for r in csv.DictReader(open(INDEX)) if r["league_id"]=="108"]
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
        rec={"match_id":r["match_id"],"league":"ENG-LeagueOne","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "phase":("playoff" if str(gen.get("matchRound")) in ("1/2","final") else "regular"),
             "home_team_id":gen["homeTeam"]["id"],"home_team":gen["homeTeam"]["name"],
             "away_team_id":gen["awayTeam"]["id"],"away_team":gen["awayTeam"]["name"],
             "coverage_level":gen.get("coverageLevel")}
        ss=(st.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"]=int(ss[0]); rec["away_goals"]=int(ss[1])
        # HT from events
        evs=((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals=[e for e in evs if e.get("type")=="Goal"]
        if evs:
            rec["ht_home_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and e.get("isHome"))
            rec["ht_away_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and not e.get("isHome"))
            rec["ht_source"]="events"
        else:
            rec["ht_home_goals"]=None; rec["ht_away_goals"]=None; rec["ht_source"]="none"
        rec["ev_yellow_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="Yellow" and e.get("isHome"))
        rec["ev_yellow_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="Yellow" and not e.get("isHome"))
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        rec["yellow_home"]=rec["yellow_cards_home"]; rec["yellow_away"]=rec["yellow_cards_away"]
        rec["red_home"]=rec["red_cards_home"]; rec["red_away"]=rec["red_cards_away"]
        rec["cards_source"]="stats" if rec["yellow_home"] is not None else "none"
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
    # Daily rebuilds: the world index grows as new matches are played and
    # rows whose details are not finished are skipped above, so the old
    # hard equality len(out)==len(rows) breaks on a live rebuild (the same
    # trap NL's builder had). 2943 is the frozen build-time count; assert it
    # as a floor instead.
    assert len(out) >= 2943, len(out)
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"engl1_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    # team-match table
    tm=[]
    for r in out:
        for side,opp in (("home","away"),("away","home")):
            t={"match_id":r["match_id"],"season":r["season"],"date":r["date"],"phase":r["phase"],
               "team_id":r[f"{side}_team_id"],"team":r[f"{side}_team"],"venue":side,
               "goals_for":r[f"{opp.replace('home','away') if False else side}_goals"] if False else r[f"{'home' if side=='home' else 'away'}_goals"],
               "goals_against":r[f"{'away' if side=='home' else 'home'}_goals"]}
            t["goals_for"]=r["home_goals"] if side=="home" else r["away_goals"]
            t["goals_against"]=r["away_goals"] if side=="home" else r["home_goals"]
            for k in ["expected_goals","total_shots","ShotsOnTarget","corners","yellow_cards","touches_opp_box","big_chance","BallPossesion"]:
                t[f"{k}_for"]=r.get(f"{k}_{side}"); t[f"{k}_against"]=r.get(f"{k}_{opp}")
            t["sm_xg_for"]=r[f"sm_xg_{side}"]; t["sm_shots_for"]=r[f"sm_shots_{side}"]
            tm.append(t)
    with open(OUT/"engl1_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
