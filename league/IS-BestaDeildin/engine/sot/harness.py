import csv, json, math, os
from collections import defaultdict
from model import Engine, load_matches, NB_R, ERA, LINES, nb_over

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "league", "IS-BestaDeildin", "data", "is_matches.csv")
OUT = os.path.dirname(__file__)
ARMS = ("GZ", "RS")

def ll(p, y):
    p = min(max(p, 1e-12), 1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m, line): return 1.0 if m["sot_h"] + m["sot_a"] > line else 0.0

def run_dev():
    ms = load_matches(DATA, {"2023", "2024", "2025"})
    scored = [m for m in ms if m["season"] in {"2024", "2025"}]
    out = {"protocol": "S-IS frozen prereg", "n": len(scored), "arms": {}, "baselines": {}}
    results = {}
    for arm in ARMS:
        eng = Engine(ms, arm); rows=[]
        for m in ms:
            if m["season"] in {"2024", "2025"}:
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

def virgin_metrics(rows):
    out = {"n": len(rows), "logloss": {}, "calibration_pp": None,
           "calibration_se_pp": None, "actual_over_rate_pp": None,
           "mean_pred_over_pp": None}
    for L in LINES:
        ys = [actual(m, L) for m, _ in rows]
        ps = [p["probs"][L] for _, p in rows]
        out["logloss"][str(L)] = sum(ll(p, y) for p, y in zip(ps, ys)) / len(ps)
    ps = [p["probs"][9.5] for _, p in rows]
    ys = [actual(m, 9.5) for m, _ in rows]
    dif = [p - y for p, y in zip(ps, ys)]
    mean = sum(dif) / len(dif)
    out["calibration_pp"] = mean * 100.0
    out["calibration_se_pp"] = (sum((x - mean) ** 2 for x in dif) / (len(dif) - 1)) ** 0.5 / len(dif) ** 0.5 * 100.0
    out["actual_over_rate_pp"] = sum(ys) / len(ys) * 100.0
    out["mean_pred_over_pp"] = sum(ps) / len(ps) * 100.0
    return out

def virgin(dev):
    all_ms = load_matches(DATA, {"2023", "2024", "2025", "2026"})
    virgin_ms = [m for m in all_ms if m["season"] == "2026"]
    dev_gz = dev["arms"]["GZ"]["pooled"]["ll_9.5"]
    best_dev_base = min(dev["baselines"][x]["pooled"]["ll_9.5"] for x in ("league_base_rate", "naive"))
    dev_pass = {a: dev["arms"][a]["pooled"]["ll_9.5"] < dev["baselines"]["league_base_rate"]["pooled"]["ll_9.5"] and dev["arms"][a]["pooled"]["ll_9.5"] < dev["baselines"]["naive"]["pooled"]["ll_9.5"] for a in ARMS}
    passing = [a for a in ARMS if dev_pass[a]]
    runs = {}
    for arm in passing:
        eng = Engine(all_ms, arm); rows = []
        for m in all_ms:
            if m["season"] == "2026": rows.append((m, eng.predict(m)))
            eng.update(m)
        runs[arm] = rows
    gz_eng = Engine(all_ms, "GZ"); gz_rows = []
    for m in all_ms:
        if m["season"] == "2026": gz_rows.append((m, gz_eng.predict(m)))
        gz_eng.update(m)
    prior = [m for m in all_ms if m["season"] != "2026"]
    rate = sum(actual(m, 9.5) for m in prior) / len(prior)
    baseline_rows = {"league_base_rate": [(m, p) for m, p in gz_rows], "naive": gz_rows}
    base_metrics = {}
    for name, rows in baseline_rows.items():
        vals = []
        for m, p in rows:
            q = {"probs": ({L: sum(actual(x, L) for x in prior) / len(prior) for L in LINES} if name == "league_base_rate" else p["naive_probs"])}
            vals.append((m, q))
        base_metrics[name] = virgin_metrics(vals)
    out = {"protocol": "S-IS frozen virgin", "virgin_season": "2026", "n": len(virgin_ms),
           "read_arms": passing, "dev_pass": dev_pass, "arms": {}, "baselines": base_metrics}
    for arm, rows in runs.items(): out["arms"][arm] = virgin_metrics(rows)
    eligible = []
    for arm, v in out["arms"].items():
        ref = out["arms"].get("GZ", v)
        leg1 = v["logloss"]["9.5"] <= ref["logloss"]["9.5"] and v["logloss"]["9.5"] <= min(x["logloss"]["9.5"] for x in base_metrics.values())
        leg2 = abs(v["calibration_pp"]) <= 1.0 + v["calibration_se_pp"]
        leg3 = arm == "GZ" or sum(dev["arms"][arm]["seasons"][s]["ll_9.5"] <= dev["arms"]["GZ"]["seasons"][s]["ll_9.5"] for s in ("2024", "2025")) >= 1
        out.setdefault("legs", {})[arm] = {"ll": leg1, "calibration": leg2, "dev_sign": leg3}
        if leg1 and leg2 and leg3: eligible.append(arm)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["logloss"]["9.5"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        write_predictions(runs[chosen], chosen)
        with open(os.path.join(OUT, "fitted_params_virgin.json"), "w") as f:
            json.dump({"arm": chosen, "nb_r": NB_R, "lines": list(LINES)}, f, indent=2)
    with open(os.path.join(OUT, "results_virgin.json"), "w") as f: json.dump(out, f, indent=2)
    return out

def write_predictions(rows, arm):
    path = os.path.join(OUT, "..", "..", "predictions", "s_is_virgin_predictions.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["arm", "match_id", "date", "home_team", "away_team", "actual_total_sot", "exp_sot_home", "exp_sot_away", "exp_sot_total"] + [f"ft_p_over_{L}" for L in LINES] + [f"1h_p_over_{L}" for L in (3.5, 4.5, 5.5)] + [f"2h_p_over_{L}" for L in (4.5, 5.5, 6.5)]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for m, p in rows:
            total = p["exp_h"] + p["exp_a"]; row = {"arm": arm, "match_id": m["match_id"], "date": m["date"], "home_team": m["home"], "away_team": m["away"], "actual_total_sot": m["sot_h"] + m["sot_a"], "exp_sot_home": p["exp_h"], "exp_sot_away": p["exp_a"], "exp_sot_total": total}
            for L in LINES: row[f"ft_p_over_{L}"] = p["probs"][L]
            for L in (3.5, 4.5, 5.5): row[f"1h_p_over_{L}"] = nb_over(.4644 * total, NB_R, L)
            for L in (4.5, 5.5, 6.5): row[f"2h_p_over_{L}"] = nb_over(.5356 * total, NB_R, L)
            w.writerow(row)


