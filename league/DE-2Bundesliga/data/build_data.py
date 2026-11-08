"""Build the DE-2Bundesliga analysis CSV from the FotMob world warehouse.

One row per played match (league_id 146). Adapted from league/jleague_lib.py
+ league/J1 preprocessing rules: FT score from header.status.scoreStr,
team stats from content.stats.Periods (All/FirstHalf/SecondHalf), shotmap
aggregates over regulation shots only, cards = stats feed with event fallback
(the stats-vs-events agreement is measured in the EDA, before any fitting),
referee from matchFacts.infoBox. Phase: a 'qualification' flag exists
for the relegation play-off (leagueName '2. Bundesliga Qualification')
as a guard, but the verified corpus contains ZERO such matches — FotMob
files that play-off outside league_id 146 (all 1,629 files carry
leagueName '2. Bundesliga'; checked twice, independently). If a future
pull ever adds one, the frozen rule is: flagged and EXCLUDED from every
fit and scored window (its opponent is not a member of this league).

Regenerate: .venv/bin/python league/DE-2Bundesliga/data/build_data.py
Output (gitignored): league/DE-2Bundesliga/data/de2_matches.csv (+ team table)
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
    rows=[r for r in csv.DictReader(open(INDEX)) if r["league_id"]=="146"]
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
        rec={"match_id":r["match_id"],"league":"DE-2Bundesliga","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "phase":(("qualification" if "Qualification" in (gen.get("leagueName") or "")
                       else "regular")),
             "league_name_raw":gen.get("leagueName"),
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
        rec["ev_red_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and e.get("isHome"))
        rec["ev_red_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and not e.get("isHome"))
        rec["ev_yellowred_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="YellowRed" and e.get("isHome"))
        rec["ev_yellowred_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="YellowRed" and not e.get("isHome"))
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        rec["yellow_home"]=rec["yellow_cards_home"]; rec["yellow_away"]=rec["yellow_cards_away"]
        rec["red_home"]=rec["red_cards_home"]; rec["red_away"]=rec["red_cards_away"]
        if rec["yellow_home"] is None:  # stats feed lacks the cards block; events carry the cards
            rec["yellow_home"]=float(rec["ev_yellow_home"]); rec["yellow_away"]=float(rec["ev_yellow_away"])
            rec["cards_source"]="events"
        else:
            rec["cards_source"]="stats"
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
        if not rec["has_events"] and not rec["has_shotmap"]:
            # Score-only match: the stats feed is a stub (50/50 possession, 0 shots)
            # or null, the event feed is empty and there is no shotmap — only the
            # score is real. Null every stats-derived field; targets are absent,
            # never zero. (Rule carried from BE; applies if such a row exists.)
            for k in STAT_KEYS:
                for pfx in ("", "fh_", "sh_"):
                    rec[f"{pfx}{k}_home"]=None; rec[f"{pfx}{k}_away"]=None
            rec["yellow_home"]=None; rec["yellow_away"]=None
            rec["red_home"]=None; rec["red_away"]=None
            rec["cards_source"]="none"
            for side in ("home","away"):
                for f_ in ("sm_shots_","sm_sot_","sm_xg_","sm_xgot_","sm_xgot_n_","sm_shots_fh_"):
                    rec[f"{f_}{side}"]=None
        out.append(rec)
    assert len(out)==len(rows), (len(out),len(rows))
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"de2_matches.csv","w",newline="") as fh:
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
    with open(OUT/"de2_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
