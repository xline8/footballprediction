"""C-QASD walk-forward harness; stdlib only."""
import csv, json, math
from collections import defaultdict
from pathlib import Path
from core import FeatureBuilder, attach_naive, fit_params, load, model_prediction, over_prob

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "qasd_matches.csv"
DEV = "2025/2026"; VIRGIN = "2026/2027"; ARMS = ("gate_zero",)
LINES = (8.5, 9.5, 10.5)

def rows_for(seasons):
    return attach_naive(FeatureBuilder(load(str(DATA), set(seasons))).build())

def pred(row, kind, params=None, arm=None):
    if kind == "model": mu, r = model_prediction(row, params, arm)
    elif kind == "league_base_rate": mu, r = row["base_mu"], row["r_base"]
    else: mu, r = (row["naive_home"] + row["naive_away"]) / 2.0, row["r_base"]
    return {"mu": mu, "r": r, **{str(x): over_prob(mu, r, x) for x in LINES}}

def metrics(target, ps, season, arm=None, kind=None):
    n=len(target); out={"season":season,"n":n}
    for line in LINES:
        vals=[p[str(line)] for p in ps]; ys=[int(r["y"]>line) for r in target]
        out[f"ll_{line}"]=sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(vals,ys))/n
        out[f"mean_p_{line}"]=sum(vals)/n; out[f"actual_over_{line}"]=sum(ys)/n
    if arm: out.update({"arm":arm,"kind":kind or "model"})
    return out

def param_cache(rows, target, arm):
    cache={}
    for r in target:
        key=r["date"]
        if key not in cache:
            train=[x for x in rows if x["date"] < r["date"]]
            cache[key]=fit_params(train, arm)
    return cache

def evaluate(rows, target, arms):
    out=[]
    caches={a:param_cache(rows,target,a) for a in arms}
    for arm in arms:
        ps=[pred(r,"model",caches[arm][r["date"]],arm) for r in target]
        out.append(metrics(target,ps,target[0]["season"],arm,"model"))
    for kind in ("league_base_rate","naive_trailing_10"):
        out.append(metrics(target,[pred(r,kind) for r in target],target[0]["season"],"baseline",kind))
    return out,caches

def gate(dev):
    result={}
    for a in ARMS:
        p=next(x for x in dev if x.get("arm")==a and x["season"]=="pooled")
        b1=next(x for x in dev if x["kind"]=="league_base_rate" and x["season"]=="pooled")
        b2=next(x for x in dev if x["kind"]=="naive_trailing_10" and x["season"]=="pooled")
        result[a]=p["ll_9.5"]<b1["ll_9.5"] and p["ll_9.5"]<b2["ll_9.5"]
    return result

def dev():
    rows=rows_for(("2024/2025", DEV)); assert sum(r["season"]=="2024/2025" for r in rows)==38; assert sum(r["season"]==DEV for r in rows)==56
    warm=[r for r in rows if r["season"]==DEV and 1<=r["round"]<=7]; target=[r for r in rows if r["season"]==DEV and 8<=r["round"]<=14]; assert len(warm)==28 and len(target)==28
    result=[]; allpairs={a:[] for a in ARMS}; caches={a:param_cache(rows,target,a) for a in ARMS}
    for a in ARMS:
        ps=[pred(r,"model",caches[a][r["date"]],a) for r in target]
        result.append(metrics(target,ps,"pooled",a,"model")); allpairs[a]=list(zip(target,ps))
    for kind in ("league_base_rate","naive_trailing_10"):
        result.append(metrics(target,[pred(r,kind) for r in target],"pooled","baseline",kind))
    passes=gate(result)
    payload={"protocol":{"loaded_seasons":["2024/2025",DEV],"warmup_n":28,"scored_n":28,"virgin_loaded":False,"primary_line":9.5},"metrics":result,"dev_pass":passes}
    (HERE/"results_dev.json").write_text(json.dumps(payload,indent=2)+"\n")
    with (HERE/"predictions_dev.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["arm","match_id","date","home_team","away_team","actual_total_corners","p_over_8.5","p_over_9.5","p_over_10.5","baseline_league_p","baseline_naive_p"]); w.writeheader()
        for r,p in allpairs["gate_zero"]:
            w.writerow({"arm":"gate_zero","match_id":r["match_id"],"date":r["date"].isoformat(),"home_team":r["home"],"away_team":r["away"],"actual_total_corners":r["y"],"p_over_8.5":p["8.5"],"p_over_9.5":p["9.5"],"p_over_10.5":p["10.5"],"baseline_league_p":pred(r,"league_base_rate")["9.5"],"baseline_naive_p":pred(r,"naive")["9.5"]})
    fields=["arm","kind","season","n","ll_8.5","ll_9.5","ll_10.5","mean_p_9.5","actual_over_9.5"]
    with (HERE/"results_dev.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:x.get(k,"") for k in fields} for x in result)
    print(json.dumps({"scored_n":28,"dev_pass":passes,"pooled_ll_9.5":{x.get("arm",x.get("kind")):x["ll_9.5"] for x in result}},sort_keys=True))

def virgin_metrics():
    d=json.loads((HERE/"results_dev.json").read_text()); passing=[a for a in ARMS if d["dev_pass"].get(a)]
    if not passing:
        stub={"virgin_read":False,"reason":"Gate Zero failed dev gate","dead_arms":[a for a in ARMS if not d["dev_pass"].get(a)]}
        (HERE/"results_virgin.json").write_text(json.dumps(stub,indent=2)+"\n")
        (HERE/"fitted_params_virgin.json").write_text(json.dumps({"virgin_read":False,"training_rows":0,"params":{}},indent=2)+"\n")
        print(json.dumps(stub)); return
    rows=rows_for(("2024/2025",DEV,VIRGIN)); assert sum(r["season"]==DEV for r in rows)==56; assert sum(r["season"]==VIRGIN for r in rows)==29
    target=[r for r in rows if r["season"]==VIRGIN]; result=[]; params_out={}
    for a in passing:
        cache=param_cache(rows,target,a); ps=[pred(r,"model",cache[r["date"]],a) for r in target]
        m=metrics(target,ps,VIRGIN,a,"model"); es=[p["9.5"]-int(r["y"]>9.5) for r,p in zip(target,ps)]; mean=sum(es)/len(es)
        m.update({"calibration_diff":mean,"calibration_se":math.sqrt(sum((e-mean)**2 for e in es)/(len(es)-1))/math.sqrt(len(es)),"params":cache[target[-1]["date"]]}); result.append(m); params_out[a]=cache[target[-1]["date"]]
    for k in ("league_base_rate","naive_trailing_10"): result.append(metrics(target,[pred(r,k) for r in target],VIRGIN,"baseline",k))
    bestbase=min(x["ll_9.5"] for x in result if x["kind"] in ("league_base_rate","naive_trailing_10")); gz=next(x for x in result if x.get("arm")=="gate_zero"); eligible=[]
    for x in result:
        if x.get("arm") not in passing: continue
        sign=True if x["arm"]=="gate_zero" else next(y for y in d["metrics"] if y.get("arm")=="x7")["ll_9.5"]<=next(y for y in d["metrics"] if y.get("arm")=="gate_zero")["ll_9.5"]
        if x["ll_9.5"]<=gz["ll_9.5"] and x["ll_9.5"]<=bestbase and abs(x["calibration_diff"])<=0.01+x["calibration_se"] and sign: eligible.append(x["arm"])
    shipped=min(eligible,key=lambda a:(next(x for x in result if x.get("arm")==a)["ll_9.5"],0 if a=="gate_zero" else 1)) if eligible else None
    payload={"virgin_read":True,"transitional":True,"n":29,"metrics":result,"dev_pass":d["dev_pass"],"shipped_arm":shipped,"eligible_arms":eligible}
    (HERE/"results_virgin.json").write_text(json.dumps(payload,indent=2)+"\n"); (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":shipped or "reference_label_only_gate_zero","training_rows":56,"params":params_out.get(shipped or passing[0],{})},indent=2)+"\n")
    print(json.dumps({"virgin_read":True,"n":29,"shipped_arm":shipped,"eligible":eligible,"ll_9.5":{x.get("arm",x.get("kind")):x["ll_9.5"] for x in result}},sort_keys=True))

def virgin_predict():
    v=json.loads((HERE/"results_virgin.json").read_text()); arm=v.get("shipped_arm")
    if not arm: print("no prediction CSV: no PASS"); return
    rows=rows_for(("2024/2025",DEV,VIRGIN)); target=[r for r in rows if r["season"]==VIRGIN]; cache=param_cache(rows,target,arm)
    fields=["match_id","date","home_team","away_team","arm","mu","r","gamma","beta","p_over_8.5","p_over_9.5","p_over_10.5","mu_1h","p_1h_over_3.5","p_1h_over_4.5","p_1h_over_5.5","mu_2h","p_2h_over_4.5","p_2h_over_5.5","p_2h_over_6.5","actual_corners_total"]
    out=HERE.parents[1]/"predictions"/"c_qasd_virgin_predictions.csv"; out.parent.mkdir(exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in target:
            p=cache[r["date"]]; mu,rr=model_prediction(r,p,arm); m1,m2=.4495*mu,(1-.4495)*mu; q={"match_id":r["match_id"],"date":r["date"].isoformat(),"home_team":r["home"],"away_team":r["away"],"arm":arm,"mu":mu,"r":rr,"gamma":p["gamma"],"beta":json.dumps(p["beta"]),"mu_1h":m1,"mu_2h":m2,"actual_corners_total":r["y"]}
            q.update({"p_over_"+str(x):over_prob(mu,rr,x) for x in LINES}); q.update({"p_1h_over_"+str(x):over_prob(m1,rr,x) for x in (3.5,4.5,5.5)}); q.update({"p_2h_over_"+str(x):over_prob(m2,rr,x) for x in (4.5,5.5,6.5)}); w.writerow(q)

