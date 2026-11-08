"""Build the RO-LigaI analysis CSV from the FotMob world warehouse.

One row per played match (league_id 189, parent league). Adapted from
league/CH-SuperLeague/data/build_data.py + J1 preprocessing rules:
FT score from header.status.scoreStr, team stats from
content.stats.Periods (All/FirstHalf/SecondHalf), events from
content.matchFacts.events, referee from matchFacts.infoBox.

RO specifics (measured, see analysis/DATA_UNDERSTANDING.md):
- No shotmap shots and no expected_goals in ANY season -> sm_* are 0,
  xG columns are None throughout; goals model is goals-only.
- Stats feed is minimal in 2021/2022-2024/2025 (possession, total_shots,
  ShotsOnTarget, corners only) and rich from 2025/2026. yellow_cards /
  red_cards stats keys exist ONLY from 2025/2026.
- Cards target is EVENT-based for every season (the only all-era
  source): yellow_* = count of matchFacts events with card == "Yellow"
  (straight yellows). YellowRed and Red events are recorded separately.
  Stats-feed yellows are kept as stats_yellow_* for the artefact audit.
- Phase from general.leagueId sub-tournament: regular (240/season),
  championship (30), relegation (45), ecl_playoff (1-2, one-legged
  knockout; the only extra-time matches). Modelling inclusion rule
  (frozen in prereg): phase != "ecl_playoff".

Regenerate: .venv/bin/python league/RO-LigaI/data/build_data.py
Output (gitignored): league/RO-LigaI/data/ro_matches.csv (+ team table)
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

def phase_of(gen):
    name=(gen.get("leagueName") or "")
    if "Championship" in name: return "championship"
    if "Relegation" in name: return "relegation"
    if "ECL" in name or "Playoff" in name: return "ecl_playoff"
    return "regular"

def main():
    rows=[r for r in csv.DictReader(open(INDEX)) if r["league_id"]=="189"]
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
        rec={"match_id":r["match_id"],"league":"RO-LigaI","season":r["season"],
             "date":r["date"],"round":str(gen.get("matchRound")),
             "sub_league_id":gen.get("leagueId"),"phase":phase_of(gen),
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
        for card,tag in (("Yellow","yellow"),("YellowRed","yellowred"),("Red","red")):
            rec[f"ev_{tag}_home"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")==card and e.get("isHome"))
            rec[f"ev_{tag}_away"]=sum(1 for e in evs if e.get("type")=="Card" and e.get("card")==card and not e.get("isHome"))
        for k in STAT_KEYS:
            h,a=g("All",k); rec[f"{k}_home"]=h; rec[f"{k}_away"]=a
            fh,fa=g("FirstHalf",k); rec[f"fh_{k}_home"]=fh; rec[f"fh_{k}_away"]=fa
            sh,sa=g("SecondHalf",k); rec[f"sh_{k}_home"]=sh; rec[f"sh_{k}_away"]=sa
        rec["stats_yellow_home"]=rec["yellow_cards_home"]; rec["stats_yellow_away"]=rec["yellow_cards_away"]
        rec["stats_red_home"]=rec["red_cards_home"]; rec["stats_red_away"]=rec["red_cards_away"]
        # UNIFIED cards target: events, all eras (frozen; see prereg)
        rec["yellow_home"]=float(rec["ev_yellow_home"]); rec["yellow_away"]=float(rec["ev_yellow_away"])
        rec["red_home"]=float(rec["ev_red_home"]+rec["ev_yellowred_home"]); rec["red_away"]=float(rec["ev_red_away"]+rec["ev_yellowred_away"])
        rec["cards_source"]="events"
        ref=(((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        rec["referee"]=ref
        periods=list(((c.get("stats") or {}).get("Periods") or {}).keys())
        rec["has_stats_all"]=int(("All", "corners") in fs)
        rec["has_stats_half"]=int(("FirstHalf","corners") in fs)
        rec["has_extra_time"]=int(any("Extra" in p for p in periods))
        shots=((c.get("shotmap") or {}).get("shots") or [])
        rec["has_shotmap"]=int(len(shots)>0); rec["n_shotmap_shots"]=len(shots)
        rec["has_events"]=int(len(evs)>0)
        out.append(rec)
    assert len(out)==len(rows), (len(out),len(rows))
    ids=[r["match_id"] for r in out]; assert len(set(ids))==len(ids)
    with open(OUT/"ro_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm=[]
    for r in out:
        for side,opp in (("home","away"),("away","home")):
            t={"match_id":r["match_id"],"season":r["season"],"date":r["date"],"phase":r["phase"],
               "team_id":r[f"{side}_team_id"],"team":r[f"{side}_team"],"venue":side,
               "goals_for":r["home_goals"] if side=="home" else r["away_goals"],
               "goals_against":r["away_goals"] if side=="home" else r["home_goals"]}
            for k in ["total_shots","ShotsOnTarget","corners","BallPossesion"]:
                t[f"{k}_for"]=r.get(f"{k}_{side}"); t[f"{k}_against"]=r.get(f"{k}_{opp}")
            t["yellow_for"]=r[f"yellow_{side}"]; t["yellow_against"]=r[f"yellow_{opp}"]
            tm.append(t)
    with open(OUT/"ro_team_matches.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__=="__main__": main()
