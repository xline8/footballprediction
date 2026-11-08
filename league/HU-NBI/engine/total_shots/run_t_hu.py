#!/usr/bin/env python3
"""HU-NBI total-shots DEV runner; copied A/B/C mechanics, HU loader only."""
import csv,json
from datetime import date
from pathlib import Path
from model import ShotsRegressionStore, NaiveTracker, BaseRateTracker, LevelLayer, TrailingR, nb_over, logloss, M_BAR

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"hu_nbi.csv"
SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=SEASONS[1:]; LINE=19.5; LAM=100.0
CELLS=[(hl,s,k) for hl in (30.0,60.0,120.0) for s in (0.5,1.0) for k in (20.0,50.0)]
def load():
    assert set(SEASONS) <= {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}, "HU loader allow-list blocks virgin seasons"
    out=[]
    with DATA.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in SEASONS: continue
            if r["total_shots_h"] == "" or r["total_shots_a"] == "": continue
            d=date.fromisoformat(r["date"]); out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"day":d.toordinal(),"home_id":int(r["home_id"]),"away_id":int(r["away_id"]),"home":r["home_team"],"away":r["away_team"],"shots_h":float(r["total_shots_h"]),"shots_a":float(r["total_shots_a"])})
    return sorted(out,key=lambda x:(x["day"],x["match_id"]))
def over(mu,r): return nb_over(mu,r,LINE)
def score(xs): return {"n":len(xs),"ll_19.5":sum(logloss(x["p"],x["y"]>LINE) for x in xs)/len(xs),"per_season":{s:{"n":len(z),"ll_19.5":sum(logloss(x["p"],x["y"]>LINE) for x in z)/len(z)} for s in SCORED for z in [[x for x in xs if x["season"]==s]]}}
def pass_arm(rows,arm):
    reg=ShotsRegressionStore(rows,[LAM]); naive=NaiveTracker(); base=BaseRateTracker(); layer=LevelLayer([CELLS[0]]); trailing=TrailingR(40.0); out=[]
    for m in rows:
        eh,ea=reg.predict(m["home_id"],m["away_id"],m["day"],LAM); rh,ra=reg.league_mu(m["day"],LAM); nh,na=naive.predict(m["home_id"],m["away_id"],rh,ra); bh,ba=base.predict(m["day"]); lt,ln,lb=eh+ea,nh+na,bh+ba; f=layer.factor(0,m["day"]); rr=40.0 if arm in ("A","B") else trailing.value(m["day"]); mu=(lt+ln)/2*(f if arm=="B" else 1.0)
        p=.5*over(lt,rr)+.5*over(ln,rr) if arm!="B" else .5*over(lt*f,40.0)+.5*over(ln*f,40.0)
        if m["season"] in SCORED: out.append({"row":m,"season":m["season"],"y":m["shots_h"]+m["shots_a"],"p":p,"expected":mu})
        naive.update(m["home_id"],m["away_id"],m["shots_h"],m["shots_a"]); base.update(m["day"],m["shots_h"],m["shots_a"]); layer.update(0,m["day"],m["shots_h"]+m["shots_a"],mu); trailing.update(m["day"],m["shots_h"]+m["shots_a"])
    return out
def dev():
    rows=load(); assert all(x["season"] in SEASONS for x in rows)
    out={"protocol":{"league":"HU-NBI","dev_seasons_loaded":list(SEASONS),"virgin_seasons_forbidden":["2025/2026","2026/2027"]},"primary_line":LINE,"arms":{},"baselines":{},"gate":{}}
    allp={}
    for arm in ("A","B","C"):
        allp[arm]=pass_arm(rows,arm); out["arms"][arm]=score(allp[arm])
    for name,arm in (("base_rate","A"),("naive_trailing_10","B")):
        xs=allp[arm]; out["baselines"][name]=score([{**x,"p":(sum(z["shots_h"]+z["shots_a"]>LINE for z in rows if z["season"]<x["season"])/len([z for z in rows if z["season"]<x["season"]]) if name=="base_rate" else x["p"])} for x in xs])
    for arm in allp: out["gate"][arm]={"pooled_beats_base_rate":out["arms"][arm]["ll_19.5"]<out["baselines"]["base_rate"]["ll_19.5"],"pooled_beats_naive_trailing_10":out["arms"][arm]["ll_19.5"]<out["baselines"]["naive_trailing_10"]["ll_19.5"]}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    for arm,xs in allp.items():
        with (HERE/f"dev_predictions_{arm}.csv").open("w",newline="",encoding="utf-8") as fh:
            fields=["match_id","season","date","home_id","away_id","expected","p_over","actual"]
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
            for x in xs: w.writerow({"match_id":x["row"]["match_id"],"season":x["season"],"date":x["row"]["date"],"home_id":x["row"]["home_id"],"away_id":x["row"]["away_id"],"expected":x["expected"],"p_over":x["p"],"actual":x["y"]})
    return out
if __name__=="__main__": dev()
