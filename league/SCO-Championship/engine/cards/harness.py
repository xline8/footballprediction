import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "sco_championship_matches.csv"
DEV = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = DEV[1:]
ARM = "gate_zero"
LINES = (2.5, 3.5, 4.5)

def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["yellow_home"] == "" or r["yellow_away"] == "":
                continue
            key = (r["date"] + "T00:00:00Z", r["match_id"])
            yh, ya = int(float(r["yellow_home"])), int(float(r["yellow_away"]))
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
    assert len(rows) == 720, len(rows)
    assert not any(r["season"] in {"2025/2026", "2026/2027"} for r in rows)
    online = Online(); warm = []; scored_rows = []
    for row in rows:
        p = online.prediction(row, ARM)
        if row["season"] == DEV[0]:
            warm.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        else:
            scored_rows.append((row, p))
        online.update(row)
    rm = {m: estimate_r(warm, m) for m in ("model", "base", "naive")}
    metrics = {}
    for s in list(SCORED) + ["pooled"]:
        pairs = scored_rows if s == "pooled" else [(r, p) for r, p in scored_rows if r["season"] == s]
        metrics[s] = scored([{**p, "y": r["y"]} for r, p in pairs], rm)
    gate = metrics["pooled"]["model"]["3.5"]["ll"] < metrics["pooled"]["base"]["3.5"]["ll"] and metrics["pooled"]["model"]["3.5"]["ll"] < metrics["pooled"]["naive"]["3.5"]["ll"]
    result = {"protocol": {"league": "SCO-Championship", "warmup": DEV[0], "scored": list(SCORED), "dev_rows_loaded": len(rows), "scored_n": len(scored_rows), "primary_line": 3.5, "target": "yellow_home + yellow_away", "sign_convention": "predicted_minus_actual"}, "arms": {ARM: {"r": rm, "seasons": metrics, "dev_gate_pass": gate}}, "baselines": {"base": metrics["pooled"]["base"], "naive": metrics["pooled"]["naive"]}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_2_5", "p_over_3_5", "p_over_4_5", "baseline_base_p_over_3_5", "baseline_naive_p_over_3_5"]
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p in scored_rows:
            w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "home": r["home"], "away": r["away"], "actual_target": r["y"], "arm": ARM, "predicted_mean": p["model"], "p_over_2_5": nb_over(p["model"], rm["model"], 2.5), "p_over_3_5": nb_over(p["model"], rm["model"], 3.5), "p_over_4_5": nb_over(p["model"], rm["model"], 4.5), "baseline_base_p_over_3_5": nb_over(p["base"], rm["base"], 3.5), "baseline_naive_p_over_3_5": nb_over(p["naive"], rm["naive"], 3.5)})
    with (HERE / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["arm", "season", "kind", "n", "ll_2.5", "ll_3.5", "ll_4.5"])
        for s in list(SCORED) + ["pooled"]:
            for kind in ("model", "base", "naive"):
                x = metrics[s][kind]; w.writerow([ARM, s, kind, x["3.5"]["n"], x["2.5"]["ll"], x["3.5"]["ll"], x["4.5"]["ll"]])
    print(json.dumps({"scored_n": len(scored_rows), "dev_gate_pass": gate, "pooled_ll_3_5": metrics["pooled"]["model"]["3.5"]["ll"]}, indent=2))
    return result

def virgin():
    d=json.loads((HERE/"results_dev.json").read_text())
    if not d["arms"][ARM]["dev_gate_pass"]:
        raise SystemExit("virgin refused non-passing arm: gate_zero")
    rows=load(DEV+("2025/2026",)); online=Online(); warm=[]; target=[]
    for row in rows:
        p=online.prediction(row,ARM)
        rec={"y":row["y"],"model":p["model"],"base":p["base"],"naive":p["naive"],"row":row,"p":p}
        (target if row["season"]=="2025/2026" else warm).append(rec)
        online.update(row)
    # PL parity: r is estimated once from the pre-virgin warm-up predictions;
    # the Online model state itself continues and updates through virgin.
    rm={m:estimate_r(warm,m) for m in ("model","base","naive")}
    metrics=scored([{k:x[k] for k in ("y","model","base","naive")} for x in target],rm)
    cal=[]
    for x in target:
        cal.append(nb_over(x["model"],rm["model"],3.5)-int(x["y"]>3.5))
    se=(sum((x-sum(cal)/len(cal))**2 for x in cal)/(len(cal)-1))**.5/len(cal)**.5
    breach=sum(cal)/len(cal)
    pass_cal=abs(breach)<=.01
    best_base=min(metrics["base"]["3.5"]["ll"],metrics["naive"]["3.5"]["ll"])
    pass_ll=metrics["model"]["3.5"]["ll"]<=best_base
    shipped=ARM if pass_cal and pass_ll else None
    out={"protocol":{"league":"SCO-Championship","virgin_season":"2025/2026","n":len(target),"scored_arms":[ARM],"primary_line":3.5,"sign_convention":"predicted_minus_actual","r_handling":"fixed estimate_r from warm-up predictions; Online state continues through virgin"},"arms":{ARM:{"r":rm,"metrics":metrics,"calibration":{"breach_pp":100*breach,"se_pp":100*se,"status":"PASS" if pass_cal else ("PROVISIONAL PASS" if abs(breach)<=.01+se else "FAIL")},"legs":{"ll_le_best_baseline":pass_ll,"calibration":pass_cal}}},"baselines":{"base":metrics["base"],"naive":metrics["naive"]},"shipped_arm":shipped}
    fields=["match_id","date","home_team","away_team","actual_target","arm","predicted_mean","r","p_over_2_5","p_over_3_5","p_over_4_5"]
    with (HERE/"predictions_virgin.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for x in target:
            p=x["p"]; q={"match_id":x["row"]["match_id"],"date":x["row"]["date"],"home_team":x["row"]["home"],"away_team":x["row"]["away"],"actual_target":x["y"],"arm":ARM,"predicted_mean":x["model"],"r":rm["model"]}
            q.update({"p_over_"+str(l).replace(".","_"):nb_over(x["model"],rm["model"],l) for l in LINES}); w.writerow(q)
    (HERE/"results_virgin.json").write_text(json.dumps(out,indent=2)+"\n")
    (HERE/"fitted_params_virgin.json").write_text(json.dumps({"arm":ARM,"r":rm,"shipped_arm":shipped} if shipped else {},indent=2)+"\n")
    return out
            # Frozen RU half split is presentation-only; dev scoring is full time.
