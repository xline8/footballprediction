import csv, json, math, os
import numpy as np
from collections import defaultdict
from model import Engine, load_matches, NB_R, ERA, LINES, nb_over

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "league", "DK-Superligaen", "data", "dk_matches.csv")
OUT = os.path.dirname(__file__)
ARMS = ("GZ", "RS", "X4")

def ll(p, y):
    p = min(max(p, 1e-12), 1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m, line): return 1.0 if m["sot_h"] + m["sot_a"] > line else 0.0

def run_dev():
    # Deliberately request only 2021-2025: the dev path never opens 2026 rows.
    ms = load_matches(DATA, {"2021/2022", "2022/2023", "2023/2024", "2024/2025"})
    scored = [m for m in ms if m["season"] in {"2022/2023", "2023/2024", "2024/2025"}]
    out = {"protocol": "S-J1 frozen prereg", "n": len(scored), "arms": {}, "baselines": {}}
    results = {}
    for arm in ARMS:
        eng = Engine(ms, arm); rows=[]
        for m in ms:
            if m["season"] in {"2022/2023", "2023/2024", "2024/2025"}:
                pred=eng.predict(m); rows.append((m,pred))
            eng.update(m)
        results[arm]=rows
        out["arms"][arm] = metrics(rows)
    # Baseline league rate and naive are scored on each arm's chronological rows; identical across arms.
    out["baselines"] = baseline_metrics(results["GZ"], ms)
    with open(os.path.join(OUT,"results_dev.json"),"w") as f: json.dump(out,f,indent=2,default=str)
    with open(os.path.join(OUT,"results_dev.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["scope","arm_or_baseline","season","ll_8.5","ll_9.5","ll_10.5","n"])
        for kind, block in [("arm",out["arms"]),("baseline",out["baselines"])]:
            for name, item in block.items():
                pooled = item["pooled"]
                w.writerow(["pooled",kind+":"+name,"pooled",pooled.get("ll_8.5"),pooled.get("ll_9.5"),pooled.get("ll_10.5"),item["n"]])
                for season,val in item.get("seasons",{}).items():
                    w.writerow(["season",kind+":"+name,season,val.get("ll_8.5"),val.get("ll_9.5"),val.get("ll_10.5"),val["n"]])
    return out, results, ms

def metrics(rows):
    ans={"pooled":{},"seasons":{}}
    for L in LINES:
        vals=[ll(x[1]["probs"][L],actual(x[0],L)) for x in rows]; ans["pooled"][f"ll_{L}"]=sum(vals)/len(vals) if vals else None
        for s in sorted({x[0]["season"] for x in rows}):
            z=[ll(x[1]["probs"][L],actual(x[0],L)) for x in rows if x[0]["season"]==s]; ans["seasons"].setdefault(s,{})[f"ll_{L}"]=sum(z)/len(z) if z else None; ans["seasons"][s]["n"]=len(z)
    ans["n"]=len(rows); return ans

def baseline_metrics(rows, all_ms, season=None):
    # League base rate is strictly prior to the scored season; naive is captured from each prediction.
    by={}
    seasons=sorted({x[0]["season"] for x in rows})
    for s in seasons:
        cutoff = min(m["date"] for m in all_ms if m["season"] == s)
        prior=[m for m in all_ms if m["date"] < cutoff]; rate=sum(actual(m,9.5) for m in prior)/len(prior)
        rs=[x for x in rows if x[0]["season"]==s]; by.setdefault("league_base_rate",[]).extend([(m,rate,None) for m,_ in rs])
    def block(which):
        vals=[]
        for m,p in rows:
            prob=p["naive_probs"][9.5] if which=="naive" else next(z[1] for z in by["league_base_rate"] if z[0] is m)
            vals.append((m,p,prob))
        ans={"pooled":{},"seasons":{},"n":len(vals)}
        for L in LINES:
            vv=[]
            for m,p,base in vals:
                prob=base if which=="league_base_rate" else p["naive_probs"][L]; vv.append(ll(prob,actual(m,L)))
            ans["pooled"][f"ll_{L}"]=sum(vv)/len(vv)
            for s in sorted({m["season"] for m,_,_ in vals}):
                    z=[ll((base if which=="league_base_rate" else p["naive_probs"][L]),actual(m,L)) for m,p,base in vals if m["season"]==s]; ans["seasons"].setdefault(s,{})[f"ll_{L}"]=sum(z)/len(z); ans["seasons"][s]["n"]=len(z)
        return ans
    return {k:block(k) for k in ("league_base_rate","naive")}

def virgin(dev, devrows, requested_arm=None):
    ms=load_matches(DATA, {"2021/2022","2022/2023","2023/2024","2024/2025","2025/2026"}); virgin_ms=[m for m in ms if m["season"]=="2025/2026"]
    passing=[]
    gz=dev["arms"]["GZ"]["pooled"]["ll_9.5"]
    gz_base = min(dev["baselines"]["league_base_rate"]["pooled"]["ll_9.5"], dev["baselines"]["naive"]["pooled"]["ll_9.5"])
    gz_dev_pass = gz < gz_base
    for a in ARMS:
        judged=dev["arms"][a]
        base=dev["baselines"]
        arm_base = min(base["league_base_rate"]["pooled"]["ll_9.5"],base["naive"]["pooled"]["ll_9.5"])
        sign = True if a == "GZ" else (
            sum(dev["arms"][a]["seasons"][s]["ll_9.5"] <= dev["arms"]["GZ"]["seasons"][s]["ll_9.5"] for s in ("2022/2023","2023/2024","2024/2025")) >= 2)
        if gz_dev_pass and judged["pooled"]["ll_9.5"] < arm_base and sign: passing.append(a)
    allrows={}; out={"n":len(virgin_ms),"arms":{},"read_arms":passing,"baselines":{}}
    for a in passing:
        eng=Engine(ms,a); rows=[]
        for m in ms:
            if m["season"]=="2025/2026": rows.append((m,eng.predict(m)))
            eng.update(m)
        allrows[a]=(rows,eng); out["arms"][a]=virgin_metrics(rows)
    if passing:
        # Baselines on virgin window, from GZ run's naive values and pre-2026 league rate.
        eng=Engine(ms,"GZ"); rows=[]
        for m in ms:
            if m["season"]=="2025/2026": rows.append((m,eng.predict(m)))
            eng.update(m)
        rate=sum(actual(m,9.5) for m in ms if m["season"]!="2025/2026")/sum(m["season"]!="2025/2026" for m in ms)
        out["baselines"]={"league_base_rate": metric_probs(rows,lambda p,L: rate),"naive":metric_probs(rows,lambda p,L:p["naive_probs"][L])}
    chosen=choose(out,dev)
    if requested_arm is not None and requested_arm in out["arms"]:
        chosen = requested_arm
    predrows, eng = allrows.get(chosen, allrows.get("GZ", (None,None)))
    if predrows is None:
        eng=Engine(ms,"GZ"); predrows=[]
        for m in ms:
            if m["season"]=="2025/2026": predrows.append((m,eng.predict(m)))
            eng.update(m)
        chosen="GZ"
    with open(os.path.join(OUT,"results_virgin.json"),"w") as f: json.dump(out,f,indent=2)
    write_predictions(predrows,chosen)
    league_means = {}
    for d in eng.reg.divs:
        mh, ma = eng.reg.means(d, virgin_ms[-1]["day"] + 1)
        league_means[d] = {"home": mh, "away": ma}
    with open(os.path.join(OUT,"fitted_params_virgin.json"),"w") as f:
        json.dump({"arm":chosen,"nb_r":NB_R,"league_means":league_means,"regression":{d:{"teams":x["teams"],"theta":x["theta"].tolist()} for d,x in eng.reg.divs.items()}},f,indent=2)
    return out

def virgin_metrics(rows):
    ps=[x[1]["probs"][9.5] for x in rows]; ys=[actual(x[0],9.5) for x in rows]; dif=[p-y for p,y in zip(ps,ys)]
    return {"ll_9.5":sum(ll(p,y) for p,y in zip(ps,ys))/len(ps),"calibration_diff":sum(dif)/len(dif),"calibration_se":(np.std(dif,ddof=1)/math.sqrt(len(dif))) if len(dif)>1 else 0,"n":len(rows)}
def metric_probs(rows, fn): return {"ll_9.5":sum(ll(fn(p,9.5),actual(m,9.5)) for m,p in rows)/len(rows),"calibration_diff":sum(fn(p,9.5)-actual(m,9.5) for m,p in rows)/len(rows),"n":len(rows)}
def choose(out,dev):
    candidates=[]
    for a,v in out["arms"].items():
        if v["ll_9.5"] <= out["arms"].get("GZ",v)["ll_9.5"] and v["ll_9.5"] <= min(x["ll_9.5"] for x in out["baselines"].values()) and abs(v["calibration_diff"]) <= .01 + v["calibration_se"]: candidates.append(a)
    return min(candidates,key=lambda a:(out["arms"][a]["ll_9.5"],ARMS.index(a))) if candidates else "GZ"
def write_predictions(rows,arm):
    path=os.path.join(OUT,"..","..","predictions","s_dk_virgin_predictions.csv"); os.makedirs(os.path.dirname(path),exist_ok=True)
    cols=["arm","match_id","date","home_team","away_team","actual_total_sot","exp_sot_home","exp_sot_away","exp_sot_total"]+[f"ft_p_over_{L}" for L in LINES]+[f"1h_p_over_{L}" for L in (3.5,4.5,5.5)]+[f"2h_p_over_{L}" for L in (4.5,5.5,6.5)]
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for m,p in rows:
            total=p["exp_h"]+p["exp_a"]; row={"arm":arm,"match_id":m["match_id"],"date":m["date"],"home_team":m["home"],"away_team":m["away"],"actual_total_sot":m["sot_h"]+m["sot_a"],"exp_sot_home":p["exp_h"],"exp_sot_away":p["exp_a"],"exp_sot_total":total}
            for L in LINES: row[f"ft_p_over_{L}"]=p["probs"][L]
            for L in (3.5,4.5,5.5): row[f"1h_p_over_{L}"]=nb_over(.462*total,NB_R,L)
            for L in (4.5,5.5,6.5): row[f"2h_p_over_{L}"]=nb_over(.538*total,NB_R,L)
            w.writerow(row)

