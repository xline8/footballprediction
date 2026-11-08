import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"de3_matches.csv"; PRED=HERE.parents[1]/"predictions"/"k_de3_virgin_predictions.csv"
DEV=("2021/2022","2022/2023","2023/2024","2024/2025"); SCORED=DEV[1:]; VIRGIN="2025/2026"
def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            if r["yellow_home"] == "" or r["yellow_away"] == "": continue  # target absent (score-only match) — never imputed
            key=(r["date"]+"T00:00:00Z",r["match_id"]); yh=int(float(r["yellow_home"])); ya=int(float(r["yellow_away"]))
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":key[0],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_team_id"]),"away_id":int(r["away_team_id"]),"home":r["home_team"],"away":r["away_team"],"yh":yh,"ya":ya,"y":yh+ya,"referee":r.get("referee","")})
    out.sort(key=lambda x:x["key"]); return out
def scored(rs,rm):
    o={}
    for method in ("model","base","naive"):
        o[method]={}
        for line in (3.5,4.5,5.5):
            ps=[nb_over(x[method],rm[method],line) for x in rs]; ys=[int(x["y"]>line) for x in rs]; o[method][str(line)]={"n":len(rs),"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/len(rs),"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys)}
    return o
def rmap(rs): return {m:estimate_r(rs,m) for m in ("model","base","naive")}
def fallback(ps): return {k:sum(p["fallback_reason"]==k for p in ps) for k in ("unknown_identity","thin_history")}
def dev():
    rows=load(DEV); online=Online(); arms=("gate_zero","x8"); warm={a:[] for a in arms}; sp={a:{s:[] for s in SCORED} for a in arms}; cov={s:[0,0] for s in DEV}
    for row in rows:
        for a in arms:
            p=online.prediction(row,a); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]}; (warm if row["season"]==DEV[0] else sp)[a] [row["season"]].append((row,p)) if row["season"] in SCORED else warm[a].append(rec)
        cov[row["season"]][0]+=bool(row["referee"]); cov[row["season"]][1]+=1; online.update(row)
    out={"protocol":{"warmup":DEV[0],"scored":list(SCORED),"dev_rows_loaded":len(rows)},"arms":{},"referee_coverage":{s:{"known":v[0],"n":v[1],"fraction":v[0]/v[1]} for s,v in cov.items()}}
    for a in arms:
        rm=rmap(warm[a]); ss={}; allr=[]
        for s in SCORED:
            rr=[{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in sp[a][s]]; allr+=rr; ss[s]=scored(rr,rm)
        ss["pooled"]=scored(allr,rm); ss3=ss["pooled"]; out["arms"][a]={"r":rm,"seasons":ss,"dev_gate_pass":ss3["model"]["4.5"]["ll"]<ss3["base"]["4.5"]["ll"] and ss3["model"]["4.5"]["ll"]<ss3["naive"]["4.5"]["ll"],"x8_fallbacks":{s:fallback([p for _,p in sp[a][s]]) for s in SCORED}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); return out
def virgin_metrics(arms):
    d=json.loads((HERE/"results_dev.json").read_text()); passing=[a for a in arms if d["arms"].get(a,{}).get("dev_gate_pass")]
    if len(passing)!=len(arms): raise SystemExit("virgin refused non-passing arm(s): "+",".join(sorted(set(arms)-set(passing))))
    rows=load(DEV+(VIRGIN,)); online=Online(); fit={a:[] for a in arms}; tar={a:[] for a in arms}; cov=[0,0]
    for row in rows:
        for a in arms:
            p=online.prediction(row,a); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"],"row":row,"p":p}; (tar if row["season"]==VIRGIN else fit)[a].append(rec)
        if row["season"]==VIRGIN: cov[0]+=bool(row["referee"]); cov[1]+=1
        online.update(row)
    out={"protocol":{"rows":len(tar[arms[0]]) if arms else 0,"dead_arms_not_read":sorted(set(("gate_zero","x8"))-set(arms))},"arms":{},"referee_coverage":{"known":cov[0],"n":cov[1],"fraction":cov[0]/cov[1]}}
    for a in arms:
        rm=rmap([{"y":x["y"],"model":x["model"],"base":x["base"],"naive":x["naive"]} for x in fit[a]]); rr=[{"y":x["y"],"model":x["model"],"base":x["base"],"naive":x["naive"]} for x in tar[a]]; vals=[nb_over(x["model"],rm["model"],4.5) for x in tar[a]]; ys=[int(x["y"]>4.5) for x in tar[a]]; dif=sum(p-y for p,y in zip(vals,ys))/len(vals); se=(sum((p-y-dif)**2 for p,y in zip(vals,ys))/(len(vals)-1))**.5/len(vals)**.5; out["arms"][a]={"r":rm,"metrics":scored(rr,rm),"calibration":{"diff_4_5":dif,"se_4_5":se},"x8_fallbacks":fallback([x["p"] for x in tar[a]])}
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); return out
def predict(arm):
    rows=load(DEV+(VIRGIN,)); online=Online(); fit=[]; tar=[]
    for row in rows:
        p=online.prediction(row,arm); (tar if row["season"]==VIRGIN else fit).append((row,p)); online.update(row)
    rm=rmap([{"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for row,p in fit]); PRED.parent.mkdir(exist_ok=True); fields=["match_id","date","home_team","away_team","referee","referee_known","n_prior","multiplier","fallback","fallback_reason","expected_home","expected_away","expected_total","p_over_3_5","p_over_4_5","p_over_5_5","mean_1h","mean_2h","arm"]
    with PRED.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for row,p in tar:
            q={"match_id":row["match_id"],"date":row["date"],"home_team":row["home"],"away_team":row["away"],"referee":p["referee"],"referee_known":bool(p["referee"]),"n_prior":p["n_prior"],"multiplier":p["multiplier"],"fallback":p["fallback"],"fallback_reason":p["fallback_reason"],"expected_home":p["eh"],"expected_away":p["ea"],"expected_total":p["model"],"mean_1h":p["model"]*.361,"mean_2h":p["model"]*.639,"arm":arm}; q.update({f"p_over_{str(l).replace('.','_')}":nb_over(p["model"],rm["model"],l) for l in (3.5,4.5,5.5)}); w.writerow(q)
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":arm,"r":rm},indent=2)+"\n")
