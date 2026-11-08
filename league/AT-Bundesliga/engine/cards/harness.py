import csv, json, math
from datetime import datetime
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent; J1=HERE.parents[1]/"data"/"at_matches.csv"; PRED=HERE.parents[1]/"predictions"/"k_at_virgin_predictions.csv"
DEV_SEASONS=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=("2022/2023","2023/2024","2024/2025")

def load(seasons):
    out=[]
    with open(J1, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            key=datetime.fromisoformat(r["kickoff_utc"].replace("Z","+00:00")); referee=(r.get("referee") or "").strip()
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":r["kickoff_utc"],"key":(r["kickoff_utc"],r["match_id"]),"day":key.date().toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":int(float(r["yellow_home"])),"ya":int(float(r["yellow_away"])),"y":int(float(r["yellow_home"]))+int(float(r["yellow_away"])),"referee":referee})
    out.sort(key=lambda x:x["key"])
    for a,b in zip(out,out[1:]): assert a["key"] < b["key"], "processing order is not strictly chronological"
    return out

def scored(records, rmap):
    result={}
    for method in ("model","base","naive"):
        vals={}
        for line in (3.5,4.5,5.5):
            ps=[nb_over(x[method],rmap[method],line) for x in records]; ys=[int(x["y"]>line) for x in records]; n=len(ys)
            vals[str(line)]={"n":n,"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/n,"mean_p":sum(ps)/n,"actual_rate":sum(ys)/n}
        result[method]=vals
    return result

def _rmap(records): return {m:estimate_r(records,m) for m in ("model","base","naive")}

def _fallback(preds):
    return {k:sum(1 for p in preds if p["fallback_reason"]==k) for k in ("unknown_identity","thin_history")}

def dev():
    rows=load(DEV_SEASONS); online=Online(); by={a:[] for a in ("gate_zero","x8")}; warm={a:[] for a in by}; season_preds={a:{s:[] for s in SCORED} for a in by}; refs={s:[0,0] for s in DEV_SEASONS}
    for row in rows:
        for arm in by:
            p=online.prediction(row,arm); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]}; (warm if row["season"]=="2021" else by)[arm].append(rec)
            if row["season"] in SCORED: season_preds[arm][row["season"]].append((row,p))
        refs[row["season"]][1]+=1; refs[row["season"]][0]+=bool(row["referee"]); online.update(row)
    rmap={a:_rmap(warm[a]) for a in by}; out={"protocol":{"warmup":"2021","scored":list(SCORED),"dev_rows_loaded":len(rows)},"arms":{},"referee_coverage":{s:{"known":v[0],"n":v[1],"fraction":v[0]/v[1]} for s,v in refs.items()}}
    for arm in by:
        seasons={}
        allr=[]
        for s in SCORED:
            rr=[{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in season_preds[arm][s]]; allr+=rr; seasons[s]=scored(rr,rmap[arm])
        seasons["pooled"]=scored(allr,rmap[arm]); out["arms"][arm]={"r":rmap[arm],"seasons":seasons,"x8_fallbacks":{s:_fallback([p for _,p in season_preds[arm][s]]) for s in SCORED}}
    for arm in by:
        m=out["arms"][arm]["seasons"]["pooled"]["model"]["4.5"]["ll"]; b=out["arms"][arm]["seasons"]["pooled"]["base"]["4.5"]["ll"]; n=out["arms"][arm]["seasons"]["pooled"]["naive"]["4.5"]["ll"]; out["arms"][arm]["dev_gate_pass"]=m<b and m<n
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with open(HERE/"results_dev.csv","w",newline="",encoding="utf-8") as f:
        fields=["arm","season","method","n","ll_3_5","ll_4_5","ll_5_5","mean_p_over_4_5","actual_over_4_5"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for a,x in out["arms"].items():
            for s,z in x["seasons"].items():
                for meth,q in z.items(): w.writerow({"arm":a,"season":s,"method":meth,"n":q["4.5"]["n"],"ll_3_5":q["3.5"]["ll"],"ll_4_5":q["4.5"]["ll"],"ll_5_5":q["5.5"]["ll"],"mean_p_over_4_5":q["4.5"]["mean_p"],"actual_over_4_5":q["4.5"]["actual_rate"]})
    _print_dev(out); return out

def virgin_metrics():
    devres=json.loads((HERE/"results_dev.json").read_text()); arms=[a for a,x in devres["arms"].items() if x["dev_gate_pass"]]
    rows=load(DEV_SEASONS+("2025/2026",)); online=Online(); fit={a:[] for a in arms}; virgin={a:[] for a in arms}; coverage=[0,0]
    for row in rows:
        for a in arms:
            p=online.prediction(row,a); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"],"row":row,"p":p}; (fit if row["season"]!="2025/2026" else virgin)[a].append(rec)
        if row["season"]=="2025/2026": coverage[1]+=1; coverage[0]+=bool(row["referee"])
        online.update(row)
    result={"protocol":{"rows":195,"dead_arms_not_read":sorted(set(("gate_zero","x8"))-set(arms))},"arms":{},"referee_coverage":{"known":coverage[0],"n":coverage[1],"fraction":coverage[0]/coverage[1]}}
    chosen=[]
    for a in arms:
        rmap=_rmap(fit[a]); rr=[{"y":x["y"],"model":x["model"],"base":x["base"],"naive":x["naive"]} for x in virgin[a]]; metric=scored(rr,rmap); vals=[nb_over(x["model"],rmap["model"],4.5) for x in virgin[a]]; ys=[int(x["y"]>4.5) for x in virgin[a]]; dif=sum(vals)/len(vals)-sum(ys)/len(ys); se=(sum((p-y-dif)**2 for p,y in zip(vals,ys))/(len(vals)-1))**.5/len(vals)**.5
        result["arms"][a]={"r":rmap,"metrics":metric,"calibration":{"diff_4_5":dif,"se_4_5":se},"x8_fallbacks":_fallback([x["p"] for x in virgin[a]])}; chosen.append((metric["model"]["4.5"]["ll"],a))
    (HERE/"results_virgin.json").write_text(json.dumps(result,indent=2)+"\n"); _write_verdict(devres,result); return result

def predict(arm):
    result=json.loads((HERE/"results_virgin.json").read_text()); assert arm in result["arms"], "arm did not survive dev gate"
    rows=load(DEV_SEASONS+("2025/2026",)); online=Online(); fit=[]; targets=[]
    cutoff_state=None
    for row in rows:
        p=online.prediction(row,arm)
        if row["season"]!="2025/2026": fit.append({"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]})
        else:
            if cutoff_state is None: cutoff_state=online.state.snapshot(row["day"])
            targets.append((row,p))
        online.update(row)
    rmap=_rmap(fit); PRED.parent.mkdir(exist_ok=True)
    fields=["match_id","date","home_team","away_team","referee","referee_known","n_prior","multiplier","fallback","fallback_reason","expected_home","expected_away","expected_total","p_over_1_5","p_over_2_5","p_over_3_5","p_over_4_5","mean_1h","mean_2h","p_over_1h_0_5","p_over_1h_1_5","p_over_1h_2_5","p_over_2h_1_5","p_over_2h_2_5","p_over_2h_3_5","arm"]
    with open(PRED,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for row,p in targets:
            q={"match_id":row["match_id"],"date":row["date"],"home_team":row["home"],"away_team":row["away"],"referee":p["referee"],"referee_known":bool(p["referee"]),"n_prior":p["n_prior"],"multiplier":p["multiplier"],"fallback":p["fallback"],"fallback_reason":p["fallback_reason"],"expected_home":p["eh"],"expected_away":p["ea"],"expected_total":p["model"]}
            for L in (3.5,4.5,5.5): q[f"p_over_{str(L).replace('.','_')}"]=nb_over(p["model"],rmap["model"],L)
            q.update({"mean_1h":p["model"]*.316,"mean_2h":p["model"]*.684,"p_over_1h_0_5":nb_over(p["model"]*.316,rmap["model"],.5),"p_over_1h_1_5":nb_over(p["model"]*.316,rmap["model"],1.5),"p_over_1h_2_5":nb_over(p["model"]*.316,rmap["model"],2.5),"p_over_2h_1_5":nb_over(p["model"]*.684,rmap["model"],1.5),"p_over_2h_2_5":nb_over(p["model"]*.684,rmap["model"],2.5),"p_over_2h_3_5":nb_over(p["model"]*.684,rmap["model"],3.5),"arm":arm}); w.writerow(q)
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"HL":270,"K_PRIOR":8,"K_REF":8,"r":rmap,"arm":arm,"cutoff_state":cutoff_state},indent=2)+"\n")

def _print_dev(o):
    for a,x in o["arms"].items():
        q=x["seasons"]["pooled"]; print(a,"gate",x["dev_gate_pass"],"r",x["r"],"LL",q["model"]["4.5"]["ll"],q["base"]["4.5"]["ll"],q["naive"]["4.5"]["ll"])

def _write_verdict(d,v):
    legs={}
    best_base=min(min(v["arms"][a]["metrics"]["base"]["4.5"]["ll"],v["arms"][a]["metrics"]["naive"]["4.5"]["ll"]) for a in v["arms"]) if v["arms"] else None
    for a,x in d["arms"].items():
        vx=v["arms"].get(a); sign=(a=="gate_zero" or sum(x["seasons"][s]["model"]["4.5"]["ll"] <= d["arms"]["gate_zero"]["seasons"][s]["model"]["4.5"]["ll"] for s in SCORED)>=2)
        if vx:
            diff=vx["calibration"]["diff_4_5"]; se=vx["calibration"]["se_4_5"]
            legs[a]={"dev_gate":x["dev_gate_pass"],"virgin_ll_le_gate_zero":vx["metrics"]["model"]["4.5"]["ll"]<=v["arms"]["gate_zero"]["metrics"]["model"]["4.5"]["ll"],"virgin_ll_le_best_baseline":vx["metrics"]["model"]["4.5"]["ll"]<=best_base,"calibration_pass_or_provisional":abs(diff)<=.01+se,"calibration_diff":diff,"calibration_se":se,"x8_sign_check":sign}
        else: legs[a]={"dev_gate":False,"virgin_read":False}
    lines=["# K-AT verdict","","Dev and virgin results are recorded in the JSON outputs.","","## Operational referee check","",f"Referee identity coverage is {d['referee_coverage']} in dev and {v['referee_coverage']} in virgin.","Warehouse records are post-match snapshots and contain no publication timestamp; historical records cannot prove appointments were public before kickoff.","The shipped operating rule is unknown or thin-history referee → Gate Zero for that fixture; no imputation.","","## Gate status","",json.dumps(legs,indent=2),"","The mechanical virgin LL leg compares against both Gate Zero and the best baseline; no arm is marked shipped here unless all preregistered legs pass."]
    (HERE.parents[1]/"reports"/"K_AT_VERDICT.md").write_text("\n".join(lines)+"\n")
