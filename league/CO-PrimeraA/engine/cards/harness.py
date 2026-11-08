import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[1]/"data"/"co_primeraa_matches.csv"
PRED=HERE.parents[1]/"predictions"/"k_coa_virgin_predictions.csv"
DEV=("2023 - Apertura","2023 - Clausura","2024 - Apertura","2024 - Clausura","2025 - Apertura","2025 - Clausura")
SCORED=DEV[1:]; VIRGIN="2026 - Apertura"; ARMS=("gate_zero","x8"); LINES=(3.5,4.5,5.5,6.5); GATE="5.5"


def load(seasons):
    allowed=set(DEV+(VIRGIN,)); assert set(seasons) <= allowed
    out=[]
    with DATA.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            yh, ya = r["ev_yellow_inc2nd_home"], r["ev_yellow_inc2nd_away"]
            missing=yh in (None,"") or ya in (None,"")
            yh,ya=(None,None) if missing else (int(float(yh)),int(float(ya)))
            key=(r["date"]+"T00:00:00Z",r["match_id"])
            out.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"kickoff_utc":key[0],"key":key,"day":date.fromisoformat(r["date"]).toordinal(),"home_id":r["home_team_id"],"away_id":r["away_team_id"],"home":r["home_team"],"away":r["away_team"],"yh":yh,"ya":ya,"y":None if missing else yh+ya,"referee":r.get("referee","").strip()})
    out=sorted(out,key=lambda x:x["key"])
    for a,b in zip(out,out[1:]): assert a["key"] < b["key"]
    assert {x["season"] for x in out} <= allowed
    return out


def scored(records, rmap):
    result={}
    for method in ("model","base","naive"):
        result[method]={}
        for line in LINES:
            pairs=[x for x in records if x["y"] is not None]; ps=[nb_over(x[method],rmap[method],line) for x in pairs]; ys=[int(x["y"]>line) for x in pairs]; n=len(ys)
            result[method][str(line)]={"n":n,"ll":sum(-(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12))) for p,y in zip(ps,ys))/n,"mean_p":sum(ps)/n,"actual_rate":sum(ys)/n}
    return result


def rmap(records): return {m:estimate_r(records,m) for m in ("model","base","naive")}
def records(rows, preds): return [{"y":r["y"],"model":p["model"],"base":p["base"],"naive":p["naive"]} for r,p in zip(rows,preds)]
def coverage(rows):
    return {s:{"known":sum(bool(r["referee"]) for r in rows if r["season"]==s),"n":sum(r["season"]==s for r in rows),"fraction":sum(bool(r["referee"]) for r in rows if r["season"]==s)/sum(r["season"]==s for r in rows)} for s in sorted({r["season"] for r in rows})}


def run_arm(rows, arm, split):
    online=Online(); warm=[]; scored_rows={s:[] for s in SCORED}; virgin=[]
    for row in rows:
        p=online.prediction(row,arm)
        if row["season"]==DEV[0]: warm.append((row,p))
        elif row["season"] in SCORED: scored_rows[row["season"]].append((row,p))
        elif row["season"]==VIRGIN: virgin.append((row,p))
        if row["y"] is not None: online.update(row)
    if split=="dev":
        rm=rmap(records([r for r,p in warm],[p for r,p in warm])); seasons={}; allr=[]
        for s in SCORED:
            rr=records([r for r,p in scored_rows[s]],[p for r,p in scored_rows[s]]); allr+=rr; seasons[s]=scored(rr,rm)
        seasons["pooled"]=scored(allr,rm); return {"r":rm,"seasons":seasons,"preds":scored_rows}
    fit=[]
    for s in DEV:
        if s==DEV[0]: fit += warm
        else: fit += scored_rows[s]
    rm=rmap(records([r for r,p in fit],[p for r,p in fit])); rr=records([r for r,p in virgin],[p for r,p in virgin])
    return {"r":rm,"metrics":scored(rr,rm),"preds":virgin,"fit":fit}


def dev():
    rows=load(DEV); assert {r["season"] for r in rows}==set(DEV); arms={}; refs=coverage(rows)
    for arm in ARMS:
        x=run_arm(rows,arm,"dev"); q=x["seasons"]["pooled"]["model"][GATE]; b=x["seasons"]["pooled"]["base"][GATE]; n=x["seasons"]["pooled"]["naive"][GATE]
        arms[arm]={"r":x["r"],"seasons":x["seasons"],"dev_gate_pass":q["ll"]<b["ll"] and q["ll"]<n["ll"]}
    out={"protocol":{"warmup":DEV[0],"scored":list(SCORED),"dev_rows_loaded":len(rows),"seasons_loaded":list(DEV),"lines":list(LINES),"primary_line":5.5},"arms":arms,"referee_coverage":refs}
    (HERE/"results_dev.json").write_text(json.dumps(out,indent=2)+"\n"); print_dev(out); return out


def virgin_metrics():
    d=json.loads((HERE/"results_dev.json").read_text())
    if not d["arms"]["gate_zero"]["dev_gate_pass"]:
        out={"protocol":{"virgin_read":False,"dead_arms_not_read":list(ARMS)},"arms":{},"referee_coverage":{"dev":d["referee_coverage"],"virgin":{}},"verdict":"FAIL","shipped_arm":None,"legs":{"dev_gate":False,"virgin_read":False}}
        (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print("virgin_read false: Gate Zero failed dev gate"); return out
    rows=load(DEV+(VIRGIN,)); passed=[a for a in ARMS if d["arms"][a]["dev_gate_pass"]]; outarms={}; armdata={}
    for arm in passed:
        x=run_arm(rows,arm,"virgin"); met=x["metrics"]; vals=[nb_over(p["model"],x["r"]["model"],5.5) for r,p in x["preds"]]; ys=[int(r["y"]>5.5) for r,p in x["preds"]]; dif=sum(y-p for p,y in zip(vals,ys))/len(vals); se=(sum((y-p-dif)**2 for p,y in zip(vals,ys))/(len(vals)-1))**.5/len(vals)**.5
        outarms[arm]={"r":x["r"],"metrics":met,"calibration":{"diff_5_5":dif,"se_5_5":se},"referee_fallbacks":{"unknown_identity":sum(p["fallback_reason"]=="unknown_identity" for r,p in x["preds"]),"thin_history":sum(p["fallback_reason"]=="thin_history" for r,p in x["preds"])}}
        armdata[arm]=x
    best_base=min((x["metrics"]["base"][GATE]["ll"] for x in outarms.values()),default=None); legs={}
    for arm,x in outarms.items():
        diff=x["calibration"]["diff_5_5"]; se=x["calibration"]["se_5_5"]; ll=x["metrics"]["model"][GATE]["ll"]; gate_ll=d["arms"]["gate_zero"]["seasons"]["pooled"]["model"][GATE]["ll"]
        leg1=ll<=outarms["gate_zero"]["metrics"]["model"][GATE]["ll"] and ll<=x["metrics"]["base"][GATE]["ll"] and ll<=x["metrics"]["naive"][GATE]["ll"]
        sign=arm=="gate_zero" or sum(d["arms"][arm]["seasons"][s]["model"][GATE]["ll"]<=d["arms"]["gate_zero"]["seasons"][s]["model"][GATE]["ll"] for s in SCORED)>=3
        cal=abs(diff)<=.01+se
        legs[arm]={"dev_gate":d["arms"][arm]["dev_gate_pass"],"virgin_ll_le_gate_zero":ll<=outarms["gate_zero"]["metrics"]["model"][GATE]["ll"],"virgin_ll_le_baselines":ll<=x["metrics"]["base"][GATE]["ll"] and ll<=x["metrics"]["naive"][GATE]["ll"],"calibration_pass_or_provisional":cal,"calibration_status":"PASS" if abs(diff)<=.01 else ("PROVISIONAL" if cal else "FAIL"),"x8_sign_check":sign,"all_legs":leg1 and cal and sign}
    eligible=[a for a in legs if legs[a]["all_legs"]]; shipped=min(eligible,key=lambda a:(outarms[a]["metrics"]["model"][GATE]["ll"],0 if a=="gate_zero" else 1)) if eligible else None
    out={"protocol":{"virgin_read":True,"virgin_season":VIRGIN,"virgin_rows_loaded":len([r for r in rows if r["season"]==VIRGIN]),"dead_arms_not_read":sorted(set(ARMS)-set(passed))},"arms":outarms,"referee_coverage":{"dev":d["referee_coverage"],"virgin":coverage([r for r in rows if r["season"]==VIRGIN])},"legs":legs,"verdict":"PASS" if shipped else "FAIL","shipped_arm":shipped}
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n"); print_virgin(out)
    if shipped: predict(armdata[shipped],shipped)
    return out


def predict(x, arm):
    PRED.parent.mkdir(exist_ok=True); fields=["match_id","date","home_team","away_team","referee","referee_known","n_prior","multiplier","fallback","fallback_reason","expected_home","expected_away","expected_total","p_over_3_5","p_over_4_5","p_over_5_5","p_over_6_5","mean_1h","mean_2h","arm"]
    with PRED.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for row,p in x["preds"]:
            q={"match_id":row["match_id"],"date":row["date"],"home_team":row["home"],"away_team":row["away"],"referee":p["referee"],"referee_known":bool(p["referee"]),"n_prior":p["n_prior"],"multiplier":p["multiplier"],"fallback":p["fallback"],"fallback_reason":p["fallback_reason"],"expected_home":p["eh"],"expected_away":p["ea"],"expected_total":p["model"],"mean_1h":p["model"]*.3543,"mean_2h":p["model"]*.6457,"arm":arm}
            q.update({f"p_over_{str(l).replace('.','_')}":nb_over(p["model"],x["r"]["model"],l) for l in LINES}); w.writerow(q)
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":arm,"r":x["r"]},indent=2)+"\n")


def print_dev(o):
    for a,x in o["arms"].items():
        q=x["seasons"]["pooled"]; print("dev",a,"model/base/naive",q["model"][GATE]["ll"],q["base"][GATE]["ll"],q["naive"][GATE]["ll"],"gate",x["dev_gate_pass"])
def print_virgin(o):
    for a,x in o["arms"].items(): print("virgin",a,"model/base/naive",x["metrics"]["model"][GATE]["ll"],x["metrics"]["base"][GATE]["ll"],x["metrics"]["naive"][GATE]["ll"],"cal",x["calibration"])
    print("verdict",o["verdict"],"shipped",o["shipped_arm"])
