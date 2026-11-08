import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"is_matches.csv"
DEV=("2023","2024","2025"); SCORED=DEV[1:]
def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            key=(r["date"]+"T00:00:00Z",r["match_id"]); yh=int(float(r["stats_yellow_home"])); ya=int(float(r["stats_yellow_away"]))
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
        ss["pooled"]=scored(allr,rm); ss3=ss["pooled"]; out["arms"][a]={"r":rm,"seasons":ss,"dev_gate_pass":ss3["model"]["4.5"]["ll"]<ss3["base"]["4.5"]["ll"] and ss3["model"]["4.5"]["ll"]<ss3["naive"]["4.5"]["ll"],"x8_fallbacks":{s:fallback([p for _,p in sp[a][s]]) for s in SCORED},"referee_multiplier_active_share":{s:(sum(not p["fallback"] for _,p in sp[a][s])/len(sp[a][s])) for s in SCORED}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n")
    with (HERE/"results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["arm", "scope", "method", "line", "n", "ll", "mean_p", "actual_rate"])
        for arm, block in out["arms"].items():
            for scope, metrics_block in block["seasons"].items():
                for method, lines in metrics_block.items():
                    for line, x in lines.items():
                        w.writerow([arm, scope, method, line, x["n"], x["ll"], x["mean_p"], x["actual_rate"]])
    return out
