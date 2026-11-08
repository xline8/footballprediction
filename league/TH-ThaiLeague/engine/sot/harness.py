import csv, json, math, os
import numpy as np
from collections import defaultdict
from model import Engine, load_matches, NB_R, ERA, LINES, nb_over

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data", "th_matches.csv")
OUT = os.path.dirname(__file__)
ARMS = ("GZ", "RS")

def ll(p, y):
    p = min(max(p, 1e-12), 1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m, line): return 1.0 if m["sot_h"] + m["sot_a"] > line else 0.0

def run_dev():
    # Deliberately request only 2021-2025: the dev path never opens 2026 rows.
    ms = load_matches(DATA, {"2022/2023", "2023/2024", "2024/2025"})
    scored = [m for m in ms if m["season"] in {"2023/2024", "2024/2025"}]
    assert len(scored) == 480, len(scored)
    out = {"protocol": {"league": "TH-ThaiLeague", "dev_seasons_loaded": ["2022/2023", "2023/2024", "2024/2025"], "n": len(scored), "scored_n": len(scored), "primary_line": 9.5, "sign_convention": "actual_minus_predicted"}, "n": len(scored), "arms": {}, "baselines": {}}
    results = {}
    for arm in ARMS:
        eng = Engine(ms, arm); rows=[]
        for m in ms:
            if m["season"] in {"2023/2024", "2024/2025"}:
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
    with open(os.path.join(OUT, "predictions_dev.csv"), "w", newline="") as f:
        fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_8_5", "p_over_9_5", "p_over_10_5", "baseline_league_p_over_9_5", "baseline_naive_p_over_9_5"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm, rows in results.items():
            for m, p in rows:
                prior = [x for x in ms if x["date"] < min(y["date"] for y in ms if y["season"] == m["season"])]
                rate = sum(actual(x, 9.5) for x in prior) / len(prior)
                q = {"match_id": m["match_id"], "season": m["season"], "date": m["date"].isoformat(), "home_team_id": m["home_id"], "away_team_id": m["away_id"], "home": m["home"], "away": m["away"], "actual_target": m["sot_h"] + m["sot_a"], "arm": arm, "predicted_mean": p["exp_h"] + p["exp_a"]}
                q.update({f"p_over_{str(L).replace('.', '_')}": p["probs"][L] for L in LINES})
                q["baseline_league_p_over_9_5"] = rate; q["baseline_naive_p_over_9_5"] = p["naive_probs"][9.5]
                w.writerow(q)
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
    passing = list(ARMS)
    allrows={}; out={"protocol":{"league":"RU-1Division","virgin_season":"2025/2026","n":len(virgin_ms),"scored_arms":passing,"sign_convention":"actual_minus_predicted"},"n":len(virgin_ms),"arms":{},"read_arms":passing,"baselines":{}}
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
        rate=sum(actual(m,7.5) for m in ms if m["season"]!="2025/2026")/sum(m["season"]!="2025/2026" for m in ms)
        out["baselines"]={"league_base_rate": metric_probs(rows,lambda p,L: rate),"naive":metric_probs(rows,lambda p,L:p["naive_probs"][L])}
    chosen=choose(out,dev)
    if requested_arm is not None and requested_arm in out["arms"]:
        chosen = requested_arm
    predrows, eng = allrows.get(chosen, allrows["GZ"])
    out["shipped_arm"] = chosen if chosen in out["arms"] else None
    with open(os.path.join(OUT,"results_virgin.json"),"w") as f: json.dump(out,f,indent=2)
    with open(os.path.join(OUT,"predictions_virgin.csv"),"w",newline="") as f:
        cols=["match_id", "season", "date", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_6_5", "p_over_7_5", "p_over_8_5", "baseline_league_p_over_7_5", "baseline_naive_p_over_7_5"]
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for a,(rs,_) in allrows.items():
            for m,p in rs:
                q={"match_id":m["match_id"],"season":m["season"],"date":m["date"].isoformat(),"home":m["home"],"away":m["away"],"actual_target":m["sot_h"]+m["sot_a"],"arm":a,"predicted_mean":p["exp_h"]+p["exp_a"]}
                q.update({f"p_over_{str(L).replace('.', '_')}":p["probs"][L] for L in LINES})
                q["baseline_league_p_over_7_5"] = rate; q["baseline_naive_p_over_7_5"] = p["naive_probs"][7.5]; w.writerow(q)
    league_means = {}
    for d in eng.reg.divs:
        mh, ma = eng.reg.means(d, virgin_ms[-1]["day"] + 1)
        league_means[d] = {"home": mh, "away": ma}
    with open(os.path.join(OUT,"fitted_params_virgin.json"),"w") as f:
        json.dump({"arms":passing,"shipped_arm":chosen,"nb_r":NB_R,"league_means":league_means,"regression":{d:{"teams":x["teams"],"theta":x["theta"].tolist()} for d,x in eng.reg.divs.items()}},f,indent=2)
    if chosen is not None:
        write_predictions(predrows, chosen)
    return out

def virgin_metrics(rows):
    out={"n":len(rows)}
    for line in LINES:
        ps=[x[1]["probs"][line] for x in rows]; ys=[actual(x[0],line) for x in rows]; dif=[y-p for p,y in zip(ps,ys)]
        out[f"ll_{line}"]=sum(ll(p,y) for p,y in zip(ps,ys))/len(ps)
        out[f"mean_p_{line}"]=sum(ps)/len(ps); out[f"actual_over_{line}"]=sum(ys)/len(ys)
        out[f"calibration_diff_{line}"]=sum(dif)/len(dif); out[f"calibration_se_{line}"]=(np.std(dif,ddof=1)/math.sqrt(len(dif))) if len(dif)>1 else 0
    out["calibration_diff"]=out["calibration_diff_7.5"]; out["calibration_se"]=out["calibration_se_7.5"]; return out
def metric_probs(rows, fn):
    out={"n":len(rows)}
    for line in LINES:
        ps=[fn(p,line) for m,p in rows]; ys=[actual(m,line) for m,p in rows]; dif=[y-q for q,y in zip(ps,ys)]
        out[f"ll_{line}"]=sum(ll(q,y) for q,y in zip(ps,ys))/len(ps); out[f"mean_p_{line}"]=sum(ps)/len(ps); out[f"actual_over_{line}"]=sum(ys)/len(ys)
        out[f"calibration_diff_{line}"]=sum(dif)/len(dif); out[f"calibration_se_{line}"]=np.std(dif,ddof=1)/math.sqrt(len(dif))
    out["calibration_diff"]=out["calibration_diff_7.5"]; out["calibration_se"]=out["calibration_se_7.5"]; return out
def choose(out,dev):
    candidates=[]
    for a,v in out["arms"].items():
        if v["ll_7.5"] <= out["arms"].get("GZ",v)["ll_7.5"] and v["ll_7.5"] <= min(x["ll_7.5"] for x in out["baselines"].values()) and abs(v["calibration_diff_7.5"]) <= .01 + v["calibration_se_7.5"]: candidates.append(a)
    return min(candidates,key=lambda a:(out["arms"][a]["ll_7.5"],ARMS.index(a))) if candidates else None
def write_predictions(rows,arm):
    path=os.path.join(OUT,"..","..","predictions","s_ru1_virgin_predictions.csv"); os.makedirs(os.path.dirname(path),exist_ok=True)
    cols=["arm","match_id","date","home_team","away_team","actual_total_sot","exp_sot_home","exp_sot_away","exp_sot_total"]+[f"ft_p_over_{L}" for L in LINES]
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for m,p in rows:
            total=p["exp_h"]+p["exp_a"]; row={"arm":arm,"match_id":m["match_id"],"date":m["date"],"home_team":m["home"],"away_team":m["away"],"actual_total_sot":m["sot_h"]+m["sot_a"],"exp_sot_home":p["exp_h"],"exp_sot_away":p["exp_a"],"exp_sot_total":total}
            for L in LINES: row[f"ft_p_over_{L}"]=p["probs"][L]
            w.writerow(row)

