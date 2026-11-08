import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "cy_matches.csv"
DEV = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = DEV[1:]
ARMS = ("gate_zero",)
LINES = (3.5, 4.5, 5.5)

def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] == "2026/2027": continue
            if r["season"] not in seasons or r["ev_yellow_home"] == "" or r["ev_yellow_away"] == "":
                continue
            key = (r["date"] + "T00:00:00Z", r["match_id"])
            yh, ya = int(float(r["ev_yellow_home"])), int(float(r["ev_yellow_away"]))
            out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "kickoff_utc": key[0], "key": key, "day": date.fromisoformat(r["date"]).toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"], "yh": yh, "ya": ya, "y": yh + ya, "referee": r.get("referee", "")})
    out.sort(key=lambda x: x["key"])
    return out

def scored(rows, rm):
    out = {}
    for method in ("model", "base", "naive"):
        out[method] = {}
        for line in LINES:
            ps = [nb_over(x[method], rm[method], line) for x in rows]
            ys = [int(x["y"] > line) for x in rows]
            out[method][str(line)] = {"n": len(rows), "ll": sum(-(y * math.log(max(p, 1e-12)) + (1-y) * math.log(max(1-p, 1e-12))) for p, y in zip(ps, ys)) / len(rows), "mean_p": sum(ps) / len(ps), "actual_rate": sum(ys) / len(ys)}
    return out

def dev():
    rows = load(DEV)
    online = Online(); warm = {a: [] for a in ARMS}; scored_rows = {a: [] for a in ARMS}
    for row in rows:
        for arm in ARMS:
            p = online.prediction(row, arm)
            rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
            (warm if row["season"] == DEV[0] else scored_rows)[arm].append(rec if row["season"] == DEV[0] else (row, p))
        online.update(row)
    rm = {a: {m: estimate_r(warm[a], m) for m in ("model", "base", "naive")} for a in ARMS}
    metrics = {}
    arms_out = {}
    for arm in ARMS:
        arm_metrics = {}
        for s in list(SCORED) + ["pooled"]:
            pairs = scored_rows[arm] if s == "pooled" else [(r, p) for r, p in scored_rows[arm] if r["season"] == s]
            arm_metrics[s] = scored([{**p, "y": r["y"]} for r, p in pairs], rm[arm])
        gate = arm_metrics["pooled"]["model"]["4.5"]["ll"] < arm_metrics["pooled"]["base"]["4.5"]["ll"] and arm_metrics["pooled"]["model"]["4.5"]["ll"] < arm_metrics["pooled"]["naive"]["4.5"]["ll"]
        arms_out[arm] = {"r": rm[arm], "seasons": arm_metrics, "dev_gate_pass": gate}
    assert len(rows) == 968 and sum(len(x) for x in scored_rows.values()) // len(ARMS) == 776
    result = {"protocol": {"league": "CY-1Division", "warmup": DEV[0], "scored": list(SCORED), "dev_rows_loaded": len(rows), "scored_n": sum(len(x) for x in scored_rows.values()) // len(ARMS), "primary_line": 4.5, "target": "ev_yellow_home + ev_yellow_away", "sign_convention": "actual_minus_predicted"}, "arms": arms_out, "baselines": {"base": arms_out[ARMS[0]]["seasons"]["pooled"]["base"], "naive": arms_out[ARMS[0]]["seasons"]["pooled"]["naive"]}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_3_5", "p_over_4_5", "p_over_5_5", "baseline_base_p_over_4_5", "baseline_naive_p_over_4_5"]
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm in ARMS:
            for r, p in scored_rows[arm]:
                w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "home": r["home"], "away": r["away"], "actual_target": r["y"], "arm": arm, "predicted_mean": p["model"], "p_over_3_5": nb_over(p["model"], rm[arm]["model"], 3.5), "p_over_4_5": nb_over(p["model"], rm[arm]["model"], 4.5), "p_over_5_5": nb_over(p["model"], rm[arm]["model"], 5.5), "baseline_base_p_over_4_5": nb_over(p["base"], rm[arm]["base"], 4.5), "baseline_naive_p_over_4_5": nb_over(p["naive"], rm[arm]["naive"], 4.5)})
    with (HERE / "results_dev_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["arm", "season", "kind", "n", "ll_3.5", "ll_4.5", "ll_5.5"])
        for s in list(SCORED) + ["pooled"]:
            for arm in ARMS:
                for kind in ("model", "base", "naive"):
                    x = arms_out[arm]["seasons"][s][kind]; w.writerow([arm, s, kind, x["4.5"]["n"], x["3.5"]["ll"], x["4.5"]["ll"], x["5.5"]["ll"]])
    import shutil
    shutil.copyfile(HERE / "predictions_dev.csv", HERE / "results_dev.csv")
    print(json.dumps({"scored_n": result["protocol"]["scored_n"], "dev_gate_pass": {a: arms_out[a]["dev_gate_pass"] for a in ARMS}, "pooled_ll_4_5": {a: arms_out[a]["seasons"]["pooled"]["model"]["4.5"]["ll"] for a in ARMS}}, indent=2))
    return result

def virgin():
    d=json.loads((HERE/"results_dev.json").read_text())
    if not d["arms"]["gate_zero"]["dev_gate_pass"]:
        raise SystemExit("virgin refused: Gate Zero failed the K-CY dev gate")
    rows = load(DEV + ("2025/2026",))
    target = [r for r in rows if r["season"] == "2025/2026"]
    online = Online(); warm=[]; virgin_rows=[]
    for row in rows:
        p = online.prediction(row, "gate_zero")
        if row["season"] == DEV[0]: warm.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        elif row["season"] == "2025/2026": virgin_rows.append((row,p))
        online.update(row)
    rm = {k: estimate_r(warm, k) for k in ("model", "base", "naive")}
    def block(which):
        ps=[nb_over(p[which], rm[which], line) for r,p in virgin_rows for line in ()]
        out={"n":len(virgin_rows)}
        for line in LINES:
            probs=[nb_over(p[which], rm[which], line) for r,p in virgin_rows]
            ys=[int(r["y"] > line) for r,p in virgin_rows]
            dif=[y-q for q,y in zip(probs,ys)]
            out[str(line)]={"ll":sum(-(y*math.log(max(q,1e-12))+(1-y)*math.log(max(1-q,1e-12))) for q,y in zip(probs,ys))/len(ys),"mean_p":sum(probs)/len(probs),"actual_rate":sum(ys)/len(ys)}
            if line == 4.5:
                mean=sum(dif)/len(dif); out["calibration_diff"]=mean; out["calibration_se"]=(sum((x-mean)**2 for x in dif)/(len(dif)-1))**0.5/(len(dif)**0.5)
        return out
    metrics={"gate_zero":block("model"),"base":block("base"),"naive":block("naive")}
    metrics["gate_zero"]["params"]={"r":rm["model"]}
    out={"protocol":{"league":"CY-1Division","virgin_season":"2025/2026","n":len(target),"scored_arms":["gate_zero"],"primary_line":4.5,"sign_convention":"actual_minus_predicted"},"arms":{"gate_zero":metrics["gate_zero"]},"baselines":{"base":metrics["base"],"naive":metrics["naive"]}}
    v=metrics["gate_zero"]
    best=min(metrics["base"]["4.5"]["ll"],metrics["naive"]["4.5"]["ll"])
    out["shipped_arm"]="gate_zero" if v["4.5"]["ll"] <= best and abs(v["calibration_diff"]) <= .01 + v["calibration_se"] else None
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n")
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arms":["gate_zero"],"shipped_arm":out["shipped_arm"],"r":rm},indent=2)+"\n")
    fields=["match_id","season","date","home","away","actual_target","arm","predicted_mean","p_over_3_5","p_over_4_5","p_over_5_5","baseline_base_p_over_4_5","baseline_naive_p_over_4_5"]
    with (HERE/"predictions_virgin.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r,p in virgin_rows:
            w.writerow({"match_id":r["match_id"],"season":r["season"],"date":r["date"],"home":r["home"],"away":r["away"],"actual_target":r["y"],"arm":"gate_zero","predicted_mean":p["model"],**{"p_over_"+str(line).replace('.','_'):nb_over(p["model"],rm["model"],line) for line in LINES},"baseline_base_p_over_4_5":nb_over(p["base"],rm["base"],4.5),"baseline_naive_p_over_4_5":nb_over(p["naive"],rm["naive"],4.5)})
    if out["shipped_arm"]:
        with (HERE.parents[1]/"predictions"/"k_cy_virgin_predictions.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["arm","match_id","date","home_team","away_team","actual_total_cards","pred_total_ft","ft_p_over_3.5","ft_p_over_4.5","ft_p_over_5.5"])
            for r,p in virgin_rows: w.writerow(["gate_zero",r["match_id"],r["date"],r["home"],r["away"],r["y"],p["model"],*[nb_over(p["model"],rm["model"],x) for x in LINES]])
    return out
            # Frozen CY half split (0.3693) is presentation-only; dev scoring is full time.
