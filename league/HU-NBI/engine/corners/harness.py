"""HU-NBI corners dev harness using the copied possession-only Gate Zero core."""
import csv, json, math
from pathlib import Path
from core import FeatureBuilder, attach_naive, load, fit_params, model_prediction, baseline_prediction, over_prob

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"hu_nbi.csv"
DEV=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=DEV[1:]; LINE=9.5
def rows(): return attach_naive(FeatureBuilder(load(DATA,set(DEV))).build())
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def metrics(pairs):
    return {"n":len(pairs),"ll_9.5":sum(ll(p,int(r["y"]>LINE)) for r,p in pairs)/len(pairs),"mean_p":sum(p for r,p in pairs)/len(pairs),"actual_rate":sum(r["y"]>LINE for r,p in pairs)/len(pairs),"per_season":{s:{"n":len(z),"ll_9.5":sum(ll(p,int(r["y"]>LINE)) for r,p in z)/len(z)} for s in SCORED for z in [[x for x in pairs if x[0]["season"]==s]]}}
def dev():
    rs=rows(); out={"protocol":{"league":"HU-NBI","dev_seasons_loaded":list(DEV),"virgin_seasons_forbidden":["2025/2026","2026/2027"]},"primary_line":LINE,"arms":{},"baselines":{},"gate":{}}
    allp={}; fitted={}
    for arm in ("gate_zero","plain"):
        pairs=[]
        for s in SCORED:
            target=[r for r in rs if r["season"]==s]; train=[r for r in rs if int(r["season"][:4])<int(s[:4])]; params=fit_params(train,arm); fitted[(arm,s)]=params
            pairs += [(r,over_prob(*model_prediction(r,params,arm),LINE)) for r in target]
        allp[arm]=pairs; out["arms"][arm]=metrics(pairs)
    for name,kind in (("base_rate","league_base_rate"),("naive_trailing_10","naive_trailing_10")):
        pairs=[]
        for s in SCORED:
            target=[r for r in rs if r["season"]==s]; train=[r for r in rs if int(r["season"][:4])<int(s[:4])]
            pairs += [(r,over_prob(*baseline_prediction(r,kind),LINE)) for r in target]
        out["baselines"][name]=metrics(pairs)
    for arm in allp: out["gate"][arm]={"pooled_beats_base_rate":out["arms"][arm]["ll_9.5"]<out["baselines"]["base_rate"]["ll_9.5"],"pooled_beats_naive_trailing_10":out["arms"][arm]["ll_9.5"]<out["baselines"]["naive_trailing_10"]["ll_9.5"]}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    for arm,pairs in allp.items():
        with (HERE/f"dev_predictions_{arm}.csv").open("w",newline="",encoding="utf-8") as fh:
            fields=["match_id","season","date","home_id","away_id","expected","p_over","actual"]
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
            for r,p in pairs:
                mu,_=model_prediction(r,fitted[(arm,r["season"])],arm)
                w.writerow({"match_id":r["match_id"],"season":r["season"],"date":r["date"].isoformat(),"home_id":r["home_id"],"away_id":r["away_id"],"expected":mu,"p_over":p,"actual":r["y"]})
    return out
