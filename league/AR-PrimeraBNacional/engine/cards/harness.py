"""Chronological BNAC cards dev and virgin harness."""
import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,nb_over,R
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data"/"bnac_matches.csv"; PRED=HERE.parents[1]/"predictions"/"k_bnac_virgin_predictions.csv"
DEV_SEASONS=("2023","2024","2025"); SCORED=("2024","2025"); VIRGIN="2026"; HALF_1=.390091; HALF_2=1-HALF_1

def load(seasons):
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            assert r["season"] not in ("2021","2022") and r["yellow_home"]!="nan" and r["yellow_away"]!="nan"
            yh,ya=int(float(r["yellow_home"])),int(float(r["yellow_away"]))
            out.append({"match_id":r["match_id"],"season":r["season"],"date":date.fromisoformat(r["date"]),"key":(r["date"],r["match_id"]),"day":date.fromisoformat(r["date"]).toordinal(),"home_id":int(r["home_id"]),"away_id":int(r["away_id"]),"home":r["home_name"],"away":r["away_name"],"yh":yh,"ya":ya,"y":yh+ya,"referee":r.get("referee","")})
    out.sort(key=lambda r:r["key"]); assert all(a["key"]<b["key"] for a,b in zip(out,out[1:])); return out

def metric(records,line,field):
    ps=[nb_over(x[field],line) for x in records]; ys=[int(x["y"]>line) for x in records]; n=len(ys); ll=sum(-(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15))) for p,y in zip(ps,ys))/n
    return {"n":n,"ll":ll,"mean_p":sum(ps)/n,"actual_rate":sum(ys)/n}
def metrics(records,field): return {str(line):metric(records,line,field) for line in (4.5,5.5)}
def binary_metric(records,line,p):
    ys=[int(x["y"]>line) for x in records]; n=len(ys); ll=sum(-(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15))) for y in ys)/n
    return {"n":n,"ll":ll,"mean_p":p,"actual_rate":sum(ys)/n}
def binary_metric_records(records,line):
    ps=[x["base_p"][str(line)] for x in records]; ys=[int(x["y"]>line) for x in records]; n=len(ys); ll=sum(-(y*math.log(max(p,1e-15))+(1-y)*math.log(max(1-p,1e-15))) for p,y in zip(ps,ys))/n
    return {"n":n,"ll":ll,"mean_p":sum(ps)/n,"actual_rate":sum(ys)/n}

def _walk(rows,arms):
    online=Online(); preds={a:{s:[] for s in DEV_SEASONS} for a in arms}
    for row in rows:
        for arm in arms:
            p=online.prediction(row,arm); preds[arm][row["season"]].append({"y":row["y"],"row":row,"p":p,"model":p["model"],"base":p["base"],"naive":p["naive"]})
        online.update(row)
    return preds

def run_dev():
    rows=load(DEV_SEASONS); assert len(rows)==1982; arms=("gate_zero","x8"); preds=_walk(rows,arms); out={"protocol":{"loaded_seasons":list(DEV_SEASONS),"scored_seasons":list(SCORED),"loaded_n":len(rows),"scored_n":1334,"rows_2021_2022_seen":0},"arms":{}}
    for arm in arms:
        seasons={}
        for s in SCORED:
            prior=[x for x in rows if x["season"] in DEV_SEASONS and x["season"]<s]
            for x in preds[arm][s]: x["base_p"]={str(line):sum(z["y"]>line for z in prior)/len(prior) for line in (4.5,5.5)}
            seasons[s]={"model":metrics(preds[arm][s],"model"),"base":{str(line):binary_metric_records(preds[arm][s],line) for line in (4.5,5.5)},"naive":metrics(preds[arm][s],"naive")}
        allr=[x for s in SCORED for x in preds[arm][s]]
        seasons["pooled"]={"model":metrics(allr,"model"),"base":{str(line):binary_metric_records(allr,line) for line in (4.5,5.5)},"naive":metrics(allr,"naive")}; out["arms"][arm]={"seasons":seasons}
        out["arms"][arm]["gate_zero_sign"]={s:{"arm_ll":seasons[s]["model"]["4.5"]["ll"],"gate_zero_ll":seasons[s]["model"]["4.5"]["ll"] if arm=="gate_zero" else out["arms"]["gate_zero"]["seasons"][s]["model"]["4.5"]["ll"],"ll_le_gate_zero":arm=="gate_zero" or seasons[s]["model"]["4.5"]["ll"]<=out["arms"]["gate_zero"]["seasons"][s]["model"]["4.5"]["ll"]} for s in SCORED}
        p=seasons["pooled"]; g={"beats_league_base":p["model"]["4.5"]["ll"]<p["base"]["4.5"]["ll"],"beats_naive_trailing10":p["model"]["4.5"]["ll"]<p["naive"]["4.5"]["ll"]}; g["pass"]=all(g.values()); g["margins"]={"vs_league_base":p["base"]["4.5"]["ll"]-p["model"]["4.5"]["ll"],"vs_naive":p["naive"]["4.5"]["ll"]-p["model"]["4.5"]["ll"]}; out["arms"][arm]["dev_gate"]=g
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); return out

def _assert_dev(devres,preds):
    for arm in ("gate_zero","x8"):
        got=metric([x for s in SCORED for x in preds[arm][s]],4.5,"model")["ll"]; want=devres["arms"][arm]["seasons"]["pooled"]["model"]["4.5"]["ll"]; assert got==want,f"dev divergence for {arm}: {got!r} != {want!r}"; assert round(got,6)=={"gate_zero":.680252,"x8":.659605}[arm]
def _calibration(records):
    ps=[nb_over(x["model"],4.5) for x in records]; ys=[int(x["y"]>4.5) for x in records]; d=sum(p-y for p,y in zip(ps,ys))/len(ys); se=math.sqrt(sum((p-y-d)**2 for p,y in zip(ps,ys))/(len(ys)-1))/math.sqrt(len(ys)); return {"mean_p":sum(ps)/len(ps),"actual_rate":sum(ys)/len(ys),"diff":d,"se":se,"abs_diff_pp":abs(d)*100,"breach_pp":max(0,abs(d)-.01)*100}
def _csv_row(row,p,arm):
    fallback=arm=="x8" and (not row["referee"] or p["ref_prior"]<8); reason="" if not fallback else ("unknown_identity" if not row["referee"] else "thin_history"); q={"match_id":row["match_id"],"date":row["date"],"home_team":row["home"],"away_team":row["away"],"referee":row["referee"],"referee_known":bool(row["referee"]),"n_prior":p["ref_prior"],"multiplier":p["ref_factor"],"fallback":fallback,"fallback_reason":reason,"expected_home":p["eh"],"expected_away":p["ea"],"expected_total":p["model"],"actual_yellows":row["y"]}
    for line in (3.5,4.5,5.5): q[f"p_over_{str(line).replace('.','_')}"]=nb_over(p["model"],line)
    q.update({"mean_1h":p["model"]*HALF_1,"mean_2h":p["model"]*HALF_2,"p_over_1h_0_5":nb_over(p["model"]*HALF_1,.5),"p_over_1h_1_5":nb_over(p["model"]*HALF_1,1.5),"p_over_1h_2_5":nb_over(p["model"]*HALF_1,2.5),"p_over_2h_1_5":nb_over(p["model"]*HALF_2,1.5),"p_over_2h_2_5":nb_over(p["model"]*HALF_2,2.5),"p_over_2h_3_5":nb_over(p["model"]*HALF_2,3.5),"arm":arm}); return q

def virgin():
    devres=json.loads((HERE/"results_dev.json").read_text()); passing=[a for a in ("gate_zero","x8") if devres["arms"][a]["dev_gate"]["pass"]]; read_arms=passing or ["gate_zero"]; rows=load(("2023","2024","2025","2026")); assert len(rows)==2630 and sum(r["season"]==VIRGIN for r in rows)==648
    online=Online(); dev_preds={a:{s:[] for s in DEV_SEASONS} for a in read_arms}; vp={a:[] for a in read_arms}; prior=[]
    for row in rows:
        for arm in read_arms:
            p=online.prediction(row,arm); x={"y":row["y"],"row":row,"p":p,"model":p["model"],"base":p["base"],"naive":p["naive"]}
            if row["season"]==VIRGIN: vp[arm].append(x)
            else: dev_preds[arm][row["season"]].append(x)
        if row["season"]!=VIRGIN: prior.append(row["y"]>4.5)
        online.update(row)
    _assert_dev(devres,dev_preds); base_p=sum(prior)/len(prior); result={"protocol":{"loaded_seasons":["2023","2024","2025","2026"],"loaded_n":len(rows),"virgin_season":"2026","virgin_n":648,"read_arms":read_arms,"dead_arms_not_read":sorted(set(("gate_zero","x8"))-set(read_arms)),"rows_2021_2022_seen":0,"dev_reproduction":"exact"},"baselines":{},"arms":{}}
    for arm in read_arms: result["arms"][arm]={"metrics":{m:metrics(vp[arm],m) for m in ("model","base","naive")},"calibration":_calibration(vp[arm]),"x8_fallbacks":{"unknown_identity":sum(not x["row"]["referee"] for x in vp[arm]),"thin_history":sum(bool(x["row"]["referee"]) and x["p"]["ref_prior"]<8 for x in vp[arm])}}
    ys=[int(x["y"]>4.5) for x in vp[read_arms[0]]]; base_ll=sum(-(y*math.log(base_p)+(1-y)*math.log(1-base_p)) for y in ys)/len(ys)
    result["baselines"]={"league_base_rate":{"p_over_4_5":base_p,"n_prior":len(prior),"ll_4_5":base_ll},"naive_trailing10":{"ll_4_5":result["arms"][read_arms[0]]["metrics"]["naive"]["4.5"]["ll"],"r":R}}
    for arm in read_arms:
        x=result["arms"][arm]; d=x["calibration"]["diff"]; se=x["calibration"]["se"]; x["gate_legs"]={"dev_gate_pass":devres["arms"][arm]["dev_gate"]["pass"],"virgin_ll_le_gate_zero":x["metrics"]["model"]["4.5"]["ll"]<=result["arms"]["gate_zero"]["metrics"]["model"]["4.5"]["ll"],"virgin_ll_le_best_baseline":x["metrics"]["model"]["4.5"]["ll"]<=min(result["baselines"]["league_base_rate"]["ll_4_5"],result["baselines"]["naive_trailing10"]["ll_4_5"]),"calibration_pass":abs(d)<=.01,"calibration_provisional":abs(d)<=.01+se,"calibration_diff":d,"calibration_se":se,"dev_sign_pass":arm=="gate_zero" or sum(devres["arms"][arm]["gate_zero_sign"][s]["ll_le_gate_zero"] for s in SCORED)>=1}
    eligible=[a for a in read_arms if all(result["arms"][a]["gate_legs"][k] for k in ("dev_gate_pass","virgin_ll_le_gate_zero","virgin_ll_le_best_baseline","calibration_provisional","dev_sign_pass"))]; shipped=min(eligible,key=lambda a:(result["arms"][a]["metrics"]["model"]["4.5"]["ll"],a!="gate_zero")) if eligible else "gate_zero"; result["shipped_arm"]=shipped; result["nothing_ships"]=not eligible
    (HERE/"results_virgin.json").write_text(json.dumps(result,indent=2)+"\n"); fields="match_id date home_team away_team referee referee_known n_prior multiplier fallback fallback_reason expected_home expected_away expected_total actual_yellows p_over_3_5 p_over_4_5 p_over_5_5 mean_1h mean_2h p_over_1h_0_5 p_over_1h_1_5 p_over_1h_2_5 p_over_2h_1_5 p_over_2h_2_5 p_over_2h_3_5 arm".split(); PRED.parent.mkdir(exist_ok=True)
    with PRED.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in vp[shipped]: w.writerow(_csv_row(x["row"],x["p"],shipped))
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"HL":270,"K_PRIOR":8,"K_REF":8,"r":R,"shipped_arm":shipped,"cutoff_state":online.state.snapshot(rows[-1]["day"])},indent=2)+"\n"); return result
