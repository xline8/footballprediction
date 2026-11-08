import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "bg_matches.csv"
DEV = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = DEV[1:]
ARMS = ("gate_zero", "x8")
LINES = (3.5, 4.5, 5.5)

def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
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
    assert len(rows) == 1081 and sum(len(x) for x in scored_rows.values()) // len(ARMS) == 859
    result = {"protocol": {"league": "BG-FirstLeague", "warmup": DEV[0], "scored": list(SCORED), "dev_rows_loaded": len(rows), "scored_n": sum(len(x) for x in scored_rows.values()) // len(ARMS), "primary_line": 4.5, "target": "ev_yellow_home + ev_yellow_away", "sign_convention": "actual_minus_predicted"}, "arms": arms_out, "baselines": {"base": arms_out[ARMS[0]]["seasons"]["pooled"]["base"], "naive": arms_out[ARMS[0]]["seasons"]["pooled"]["naive"]}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_3_5", "p_over_4_5", "p_over_5_5", "baseline_base_p_over_4_5", "baseline_naive_p_over_4_5"]
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm in ARMS:
            for r, p in scored_rows[arm]:
                w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "home": r["home"], "away": r["away"], "actual_target": r["y"], "arm": arm, "predicted_mean": p["model"], "p_over_3_5": nb_over(p["model"], rm[arm]["model"], 3.5), "p_over_4_5": nb_over(p["model"], rm[arm]["model"], 4.5), "p_over_5_5": nb_over(p["model"], rm[arm]["model"], 5.5), "baseline_base_p_over_4_5": nb_over(p["base"], rm[arm]["base"], 4.5), "baseline_naive_p_over_4_5": nb_over(p["naive"], rm[arm]["naive"], 4.5)})
    with (HERE / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["arm", "season", "kind", "n", "ll_3.5", "ll_4.5", "ll_5.5"])
        for s in list(SCORED) + ["pooled"]:
            for arm in ARMS:
                for kind in ("model", "base", "naive"):
                    x = arms_out[arm]["seasons"][s][kind]; w.writerow([arm, s, kind, x["4.5"]["n"], x["3.5"]["ll"], x["4.5"]["ll"], x["5.5"]["ll"]])
    print(json.dumps({"scored_n": result["protocol"]["scored_n"], "dev_gate_pass": {a: arms_out[a]["dev_gate_pass"] for a in ARMS}, "pooled_ll_4_5": {a: arms_out[a]["seasons"]["pooled"]["model"]["4.5"]["ll"] for a in ARMS}}, indent=2))
    return result

def virgin():
    # PREREG_K_BG mechanical rule: Gate Zero dev failure => variants moot,
    # verdict FAIL, virgin NOT read. Gate Zero failed the BG dev gate
    # (pooled LL@4.5 0.6855 vs league base rate 0.6804), so this function
    # refuses unconditionally for this league; it exists only so the CLI
    # fails closed instead of reading the virgin window.
    d=json.loads((HERE/"results_dev.json").read_text())
    if not d["arms"]["gate_zero"]["dev_gate_pass"]:
        raise SystemExit("virgin refused: Gate Zero failed the K-BG dev gate; "
                         "per PREREG_K_BG the virgin is NOT read")
    raise SystemExit("virgin refused: K-BG virgin path not built; Gate Zero "
                     "dev failure already decided the verdict")
            # Frozen BG half split (0.3183) is presentation-only; dev scoring is full time.
