import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"py_matches.csv"; PRED=HERE.parents[1]/"predictions"/"k_py_virgin_predictions.csv"
DEV=("2025 - Apertura","2025 - Clausura","2026 - Apertura"); SCORED=DEV[1:]; VIRGIN="2026 - Clausura"
def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            missing=r["ev_yellow_inc2nd_home"] in (None,"") or r["ev_yellow_inc2nd_away"] in (None,"") or r.get("has_stats")=="0"
            yh,ya=(None,None) if missing else (int(float(r["ev_yellow_inc2nd_home"])),int(float(r["ev_yellow_inc2nd_away"]))); key=(r["date"]+"T00:00:00Z",r["match_id"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":key[0],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":r["home_team_id"],"away_id":r["away_team_id"],"home":r["home_team"],"away":r["away_team"],"yh":yh,"ya":ya,"y":None if missing else yh+ya,"referee":""})
    return sorted(out,key=lambda x:x["key"])
def scored(rs,rm):
    out={}
    for method in ("model","base","naive"):
        out[method]={}
        for line in (3.5,4.5,5.5):
            pairs=[x for x in rs if x["y"] is not None]; ps=[nb_over(x[method],rm[method],line) for x in pairs]; ys=[int(x["y"]>line) for x in pairs]; out[method][str(line)]={"n":len(pairs),"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/len(ps),"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys)}
    return out
def rmap(rs): return {m:estimate_r(rs,m) for m in ("model","base","naive")}
def dev():
    rows=load(DEV); assert not any(r["season"]==VIRGIN for r in rows); online=Online(); warm=[]; sp={s:[] for s in SCORED}
    for row in rows:
        p=online.prediction(row,"gate_zero"); rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]}; (warm if row["season"]==DEV[0] else sp[row["season"]]).append(rec if row["season"]==DEV[0] else (row,p));
        if row["y"] is not None: online.update(row)
    rm=rmap([{**x,"model":x["model"]} for x in warm]); seasons={}; allr=[]
    for s in SCORED:
        rr=[{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in sp[s]]; allr+=rr; seasons[s]=scored(rr,rm)
    seasons["pooled"]=scored(allr,rm); gate=seasons["pooled"]["model"]["4.5"]["ll"]<seasons["pooled"]["base"]["4.5"]["ll"] and seasons["pooled"]["model"]["4.5"]["ll"]<seasons["pooled"]["naive"]["4.5"]["ll"]
    out={"protocol":{"warmup":DEV[0],"scored":list(SCORED),"dev_rows_loaded":len(rows)},"arms":{"gate_zero":{"r":rm,"seasons":seasons,"dev_gate_pass":gate}},"referee_coverage":{s:{"known":0,"n":len([r for r in rows if r["season"]==s]),"fraction":0.0} for s in DEV}}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); print_table(out,"dev"); return out
def virgin_metrics(arms=("gate_zero",)):
    d=json.loads((HERE/"results_dev.json").read_text());
    if not d["arms"]["gate_zero"]["dev_gate_pass"]:
        out={"verdict":"FAIL","shipped_arm":None,"legs":{"dev_gate":False,"virgin_read":False}}; (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print("virgin not read: Gate Zero failed dev gate"); return out
    rows=load(DEV+(VIRGIN,)); online=Online(); fit=[]; tar=[]
    for row in rows:
        p=online.prediction(row,"gate_zero"); (tar if row["season"]==VIRGIN else fit).append((row,p));
        if row["y"] is not None: online.update(row)
    rm=rmap([{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in fit if r["y"] is not None]); rr=[{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in tar]; met=scored(rr,rm); scored_tar=[(r,p) for r,p in tar if r["y"] is not None]; vals=[nb_over(p["model"],rm["model"],4.5) for _,p in scored_tar]; ys=[int(r["y"]>4.5) for r,_ in scored_tar]; dif=sum(p-y for p,y in zip(vals,ys))/len(vals); se=(sum((p-y-dif)**2 for p,y in zip(vals,ys))/(len(vals)-1))**.5/len(vals)**.5; base=met["base"]["4.5"]["ll"]; ll=met["model"]["4.5"]["ll"]; leg1=ll<=base; leg2=abs(dif)<=.01+se; status="PASS" if abs(dif)<=.01 else ("PROVISIONAL" if leg2 else "FAIL"); verdict="PASS" if leg1 and leg2 else "FAIL"; out={"arms":{"gate_zero":{"r":rm,"metrics":met,"calibration":{"diff_4_5":dif,"se_4_5":se}}},"verdict":verdict,"shipped_arm":"gate_zero" if verdict=="PASS" else None,"legs":{"dev_gate":True,"i":leg1,"ii":leg2,"calibration_status":status}}
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print_table(out,"virgin"); print("verdict",verdict,"shipped",out["shipped_arm"])
    if verdict=="PASS": predict(tar,fit,rm)
    return out
def predict(tar,fit,rm):
    PRED.parent.mkdir(exist_ok=True); fields=["match_id","date","home_team","away_team","referee","referee_known","n_prior","multiplier","fallback","fallback_reason","expected_home","expected_away","expected_total","p_over_3_5","p_over_4_5","p_over_5_5","mean_1h","mean_2h","arm"]
    with PRED.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for row,p in tar:
            q={"match_id":row["match_id"],"date":row["date"],"home_team":row["home"],"away_team":row["away"],"referee":"","referee_known":False,"n_prior":0,"multiplier":1.0,"fallback":False,"fallback_reason":"","expected_home":p["eh"],"expected_away":p["ea"],"expected_total":p["model"],"mean_1h":p["model"]*.327,"mean_2h":p["model"]*.673,"arm":"gate_zero"}; q.update({f"p_over_{str(l).replace('.','_')}":nb_over(p["model"],rm["model"],l) for l in (3.5,4.5,5.5)}); w.writerow(q)
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":"gate_zero","r":rm},indent=2)+"\n")
def print_table(out,label):
    print(label)
    if label=="dev":
        for s,x in out["arms"]["gate_zero"]["seasons"].items(): print("gate_zero",s,"model",x["model"]["4.5"]["n"],f'{x["model"]["4.5"]["ll"]:.6f}',f'{x["model"]["4.5"]["mean_p"]:.6f}',f'{x["model"]["4.5"]["actual_rate"]:.6f}')
    else:
        x=out["arms"]["gate_zero"]["metrics"]; print("gate_zero",x["model"]["4.5"]["n"],f'{x["model"]["4.5"]["ll"]:.6f}',f'{x["model"]["4.5"]["mean_p"]:.6f}',f'{x["model"]["4.5"]["actual_rate"]:.6f}')
