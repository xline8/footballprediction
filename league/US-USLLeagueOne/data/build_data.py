"""Build USL League One match and team-match tables from the FotMob warehouse."""
import csv, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WAREHOUSE_REPO = REPO if (REPO / "data_enrichment" / "fotmob_world" / "United States").exists() else Path.home() / "workspace" / "footballprediction"
sys.path.insert(0, str(REPO / "league"))
from jleague_lib import events_of, flat_stats, goal_events, ht_from_events, load, shots_of

OUT = Path(__file__).parent; INDEX = WAREHOUSE_REPO / "data_enrichment" / "fotmob_world_index.csv"; LEAGUE_ID = "9296"
ALL_KEYS = ["total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots","shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards","red_cards","fouls","Offsides","keeper_saves","BallPossesion","expected_goals","expected_goals_open_play","expected_goals_set_play","expected_goals_non_penalty"]
HALF_KEYS = ["total_shots","ShotsOnTarget","corners","yellow_cards","red_cards","fouls","expected_goals"]

def phase(name): return "playoff" if str(name or "").endswith("Playoff") else "regular"

def parse(ir):
    path=WAREHOUSE_REPO/ir["path"]; d=load(path); gen=d.get("general") or {}; hdr=d.get("header") or {}; c=d.get("content") or {}; st=hdr.get("status") or {}; fs=flat_stats(c)
    home=gen.get("homeTeam") or {}; away=gen.get("awayTeam") or {}; score=st.get("scoreStr") or ""; hg=ag=None
    if " - " in score:
        try: hg,ag=(int(x) for x in score.split(" - "))
        except ValueError: pass
    def val(per,key,side):
        x=fs.get((per,key)); return None if x is None else x[side]
    info=((c.get("matchFacts") or {}).get("infoBox") or {}); ref=(info.get("Referee") or {}).get("text") or None
    r={"match_id":int(gen.get("matchId") or path.stem),"league":"US-USLLeagueOne","season":ir["season"],"season_start":int(ir["season"]),"date":(gen.get("matchTimeUTCDate") or "")[:10],"kickoff_utc":gen.get("matchTimeUTCDate"),"round":gen.get("matchRound"),"phase":phase(gen.get("leagueName")),"fotmob_league_name":gen.get("leagueName"),"home_team_id":home.get("id"),"home_team":home.get("name"),"away_team_id":away.get("id"),"away_team":away.get("name"),"home_goals":hg,"away_goals":ag,"coverage_level":gen.get("coverageLevel"),"referee":ref,"awarded":bool(st.get("awarded")),"has_events":bool(events_of(c))}
    ge=goal_events(c); r["ev_goals_home"]=sum(bool(e.get("isHome")) for e in ge); r["ev_goals_away"]=sum(e.get("isHome") is False for e in ge); r["score_events_mismatch"]=bool(r["has_events"] and hg is not None and (r["ev_goals_home"],r["ev_goals_away"])!=(hg,ag))
    ht=ht_from_events(c); r["ht_home_goals"],r["ht_away_goals"]=ht if ht else (None,None); r["ht_source"]="events" if ht else "none"
    cards=[e for e in events_of(c) if e.get("type")=="Card"]
    for k,col in (("Yellow","ev_yellow"),("YellowRed","ev_yellowred"),("Red","ev_red")): r[col+"_home"]=sum(e.get("card")==k and e.get("isHome") for e in cards); r[col+"_away"]=sum(e.get("card")==k and e.get("isHome") is False for e in cards)
    for k in ALL_KEYS: r[k+"_home"]=val("All",k,0); r[k+"_away"]=val("All",k,1)
    r["has_stats_all"]=("All","total_shots") in fs or ("All","corners") in fs
    for per,pre in (("FirstHalf","fh"),("SecondHalf","sh")):
        for k in HALF_KEYS: r[pre+"_"+k+"_home"]=val(per,k,0); r[pre+"_"+k+"_away"]=val(per,k,1)
    r["has_stats_half"]=("FirstHalf","corners") in fs; periods=((c.get("stats") or {}).get("Periods") or {}); r["has_extra_time"]=any("ExtraHalf" in p for p in periods)
    shots=shots_of(c); reg=[s for s in shots if s.get("period")!="PenaltyShootout"]; r["n_shootout_shots"]=len(shots)-len(reg); r["has_shootout"]=bool(r["n_shootout_shots"]); r["has_shotmap"]=bool(reg); hid=home.get("id")
    def credited(s): return (s.get("teamId")==hid)!=bool(s.get("isOwnGoal"))
    for side,want in (("home",True),("away",False)):
        mine=[s for s in reg if (s.get("teamId")==hid)==want]; r["sm_shots_"+side]=len(mine) if reg else None; r["sm_sot_"+side]=sum(s.get("isOnTarget") and not s.get("isBlocked") for s in mine) if reg else None; r["sm_sot_incl_blocked_"+side]=sum(bool(s.get("isOnTarget")) for s in mine) if reg else None; r["sm_goals_"+side]=sum(s.get("eventType")=="Goal" and credited(s)==want for s in reg) if reg else None; r["sm_xg_"+side]=round(sum(s.get("expectedGoals") or 0 for s in mine),4) if reg else None; xgot=[s.get("expectedGoalsOnTarget") for s in mine if s.get("expectedGoalsOnTarget") is not None]; r["sm_xgot_"+side]=round(sum(xgot),4) if reg and xgot else None; r["sm_xgot_n_"+side]=len(xgot) if reg else None; r["sm_pen_"+side]=sum(s.get("situation")=="Penalty" for s in mine) if reg else None
    for side in ("home","away"): r["yellow_"+side]=r["yellow_cards_"+side]; r["red_"+side]=r["red_cards_"+side]
    r["cards_source"]="stats"
    # Artefact freeze (see PREPROCESSING.md): stats-feed yellows are broken in
    # 2021-22 (means 0.89/1.49, 72-80% zero-card matches) and the event feed
    # carries no card events at all in 2021-2025, so no valid card target
    # exists before 2023. Stats yellows are plausible from 2023 (4.78+).
    r["cards_target_valid"]=bool(ir["season"]>="2023" and r["yellow_cards_home"] is not None)
    r["finished"]=bool(st.get("finished"))
    return r

def team_rows(m, source):
    out=[]
    for venue,side,opp in (("H","home","away"),("A","away","home")):
        gf,ga=m[side+"_goals"],m[opp+"_goals"]; r={"match_id":m["match_id"],"league":m["league"],"season":m["season"],"season_start":m["season_start"],"date":m["date"],"phase":m["phase"],"team_id":m[side+"_team_id"],"team":m[side+"_team"],"opponent_id":m[opp+"_team_id"],"opponent":m[opp+"_team"],"venue":venue,"goals_for":gf,"goals_against":ga,"ht_goals_for":m["ht_"+side+"_goals"],"ht_goals_against":m["ht_"+opp+"_goals"],"result":"W" if gf>ga else ("D" if gf==ga else "L"),"points":3 if gf>ga else (1 if gf==ga else 0),"xg_for":m["expected_goals_"+side],"xg_against":m["expected_goals_"+opp],"shots_for":m["total_shots_"+side],"shots_against":m["total_shots_"+opp],"sot_for":m["ShotsOnTarget_"+side],"sot_against":m["ShotsOnTarget_"+opp],"corners_for":m["corners_"+side],"corners_against":m["corners_"+opp],"yellow_for":m["yellow_"+side],"red_for":m["red_"+side],"fouls_for":m["fouls_"+side],"possession":m["BallPossesion_"+side],"box_touches_for":m["touches_opp_box_"+side],"box_touches_against":m["touches_opp_box_"+opp],"big_chance_for":m["big_chance_"+side],"fh_shots_for":m["fh_total_shots_"+side],"sh_shots_for":m["sh_total_shots_"+side],"fh_sot_for":m["fh_ShotsOnTarget_"+side],"sh_sot_for":m["sh_ShotsOnTarget_"+side],"fh_corners_for":m["fh_corners_"+side],"sh_corners_for":m["sh_corners_"+side],"fh_yellow_for":m["fh_yellow_cards_"+side],"has_shotmap":m["has_shotmap"],"has_stats_all":m["has_stats_all"],"has_stats_half":m["has_stats_half"]}; out.append(r)
    return out

def main():
    idx=[r for r in csv.DictReader(INDEX.open()) if r["league_id"]==LEAGUE_ID]; rows=[]; seen=set()
    for ir in idx:
        r=parse(ir); assert r["match_id"] not in seen; seen.add(r["match_id"]); rows.append(r)
    rows.sort(key=lambda r:(r["date"],r["match_id"]))
    # Corpus-mutation guard (CO-PrimeraA lesson): every indexed row must be a
    # finished match with a score; unfinished 0-0 placeholders must never
    # enter the corpus silently.
    bad=[r["match_id"] for r in rows if not r["finished"] or r["home_goals"] is None]
    assert not bad, f"unfinished/scoreless rows in corpus: {bad}"
    # Card artefact table (frozen target decision in PREPROCESSING.md).
    for s in sorted(set(r["season"] for r in rows)):
        q=[r for r in rows if r["season"]==s]; tot=[(r["yellow_cards_home"] or 0)+(r["yellow_cards_away"] or 0) for r in q]; ev=[r["ev_yellow_home"]+r["ev_yellow_away"] for r in q]; zero=sum(t==0 for t in tot)/len(tot)
        print(f"cards {s}: stats_mean={sum(tot)/len(tot):.2f} zero_share={zero:.3f} events_mean={sum(ev)/len(ev):.2f}")
    with (OUT/"usll1_matches.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    tr=[x for r in rows for x in team_rows(r,"stats")]
    with (OUT/"usll1_team_matches.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(tr[0])); w.writeheader(); w.writerows(tr)
    assert len(rows)>=1174 and len(tr)==2*len(rows)
    print(f"USLL1: {len(rows)} matches, {len(tr)} team rows")
if __name__=="__main__": main()
