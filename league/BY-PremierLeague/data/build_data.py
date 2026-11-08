"""Build the BY-PremierLeague analysis CSV from the FotMob world warehouse.

One row per played match (league_id 263, Belarus Premier League, tier 1).
Adapted from the FR-Ligue3 scores-only build (same pattern): FT score from
header.status.scoreStr; team stats from content.stats.Periods (All /
FirstHalf / SecondHalf where present) — the stats feed is ABSENT in
every season here (0/1394 matches carry any Periods key), so every
stats column stays empty (missing, never zero) and has_stats_all /
has_stats_half are 0 throughout. Shotmap is likewise absent (0/1394).
Cards: the stats feed carries no yellow_cards/red_cards keys in any
season; the event feed carries Card events, but plain Yellow events
exist in NO season at all (2021-2026: Red/YellowRed only, 0 plain
Yellow in 1394 matches) — the event-derived yellow_* columns therefore
count YellowRed only, and the K candidate is NOT-BUILDABLE in this
league (see EDA F5 / the K verdict): no yellows target exists in any
era and referee coverage is 0% in every season. 1H goals / 1H yellows
are counted from event times (time <= 45, incl. 45+ stoppage).
Naming: general.leagueName is 'Premier League' in all 1394 matches;
coverageLevel 'lower' in all 1394. Calendar-year seasons 2021-2026
(240/musim 2021-2022; 210 in 2023; 240 in 2024-2025; 224 in 2026,
in progress). Single group every season, so phase is 'main' for all
rows. 17 awarded matches (15 in 2021, 1 in 2022, 1 in 2023) — kept
as ordinary rows with the awarded flag. All logic keys by FotMob
team id.

Regenerate: python3 league/BY-PremierLeague/data/build_data.py
(from ~/workspace/league-work/BY-PremierLeague)
Output: league/BY-PremierLeague/data/by_matches.csv (+ team table)
"""
import csv, json
from pathlib import Path

WORK = Path(__file__).resolve().parents[3]  # ~/workspace/league-work/BY-PremierLeague
INDEX = Path("/home/hatch/league-remote/inbox-muse2/BY-PremierLeague/index_263.csv")
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["BallPossesion","expected_goals","expected_goals_open_play","expected_goals_set_play",
 "expected_goals_non_penalty","total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots",
 "shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards",
 "red_cards","fouls","Offsides","keeper_saves"]

PHASE = {"Premier League": "main"}

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
    rows=[r for r in csv.DictReader(open(INDEX)) if r["league_id"]=="263"]
    rows.sort(key=lambda r:(r["date"], r["match_id"]))
    out=[]
    for r in rows:
        d=json.load(open(WORK/r["path"]))
        gen=d.get("general") or {}; hdr=d.get("header") or {}; st=hdr.get("status") or {}
        if not st.get("finished"): continue
        c=d.get("content") or {}
        fs=flat_stats(c)
        def g(period,key):
            v=fs.get((period,key)); return v if v else (None,None)
        rec={"match_id":r["match_id"],"league":"BY-PremierLeague","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "league_name":gen.get("leagueName"),
             "phase":PHASE.get(gen.get("leagueName"),"unknown"),
             "home_team_id":gen["homeTeam"]["id"],"home_team":gen["homeTeam"]["name"],
             "away_team_id":gen["awayTeam"]["id"],"away_team":gen["awayTeam"]["name"],
             "coverage_level":gen.get("coverageLevel"),
             "awarded":bool(st.get("awarded"))}
        ss=(st.get("scoreStr") or "0 - 0").split("-")
        rec["home_goals"]=int(ss[0]); rec["away_goals"]=int(ss[1])
        evs=((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        rec["has_events"]=int(len(evs)>0)
        goals=[e for e in evs if e.get("type")=="Goal"]
        rec["ev_goals_home"]=sum(1 for e in goals if e.get("isHome"))
        rec["ev_goals_away"]=sum(1 for e in goals if not e.get("isHome"))
        rec["score_events_mismatch"]=bool(evs and (rec["ev_goals_home"],rec["ev_goals_away"])!=(rec["home_goals"],rec["away_goals"]))
        if evs:
            rec["ht_home_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and e.get("isHome"))
            rec["ht_away_goals"]=sum(1 for e in goals if e.get("time") is not None and e["time"]<=45 and not e.get("isHome"))
            rec["ht_source"]="events"
        else:
            rec["ht_home_goals"]=None; rec["ht_away_goals"]=None; rec["ht_source"]="none"
        rec["ev_yellow_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("isHome"))
        rec["ev_yellow_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and not e.get("isHome"))
        rec["ev_yellowred_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="YellowRed" and e.get("isHome"))
        rec["ev_yellowred_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")=="YellowRed" and not e.get("isHome"))
        rec["ev_red_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and e.get("isHome"))
        rec["ev_red_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Red","YellowRed") and not e.get("isHome"))
        rec["ht_yellow_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("time") is not None and e["time"]<=45 and e.get("isHome"))
        rec["ht_yellow_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card") in ("Yellow","YellowRed") and e.get("time") is not None and e["time"]<=45 and not e.get("isHome"))
        rec["ht_cards_source"]="events" if evs else "none"
        rec["ev_cards_complete"]=int(any(e.get("type")=="Card" and e.get("card")=="Yellow" for e in evs))
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        rec["yellow_home"]=rec["ev_yellow_home"]; rec["yellow_away"]=rec["ev_yellow_away"]
        rec["red_home"]=rec["ev_red_home"]; rec["red_away"]=rec["ev_red_away"]
        sy_h,sy_a=g("All","yellow_cards"); rec["stats_yellow_home"]=sy_h; rec["stats_yellow_away"]=sy_a
        sr_h,sr_a=g("All","red_cards"); rec["stats_red_home"]=sr_h; rec["stats_red_away"]=sr_a
        rec["cards_source"]="events" if evs else "none"
        ref=(((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        rec["referee"]=ref
        rec["has_referee"]=int(bool(ref))
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
    assert len(out)==len(rows), (len(out),len(rows))
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"by_matches.csv","w",newline="") as fh:
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
    with open(OUT/"by_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
