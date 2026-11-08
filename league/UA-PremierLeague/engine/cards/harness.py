"""K-UA harness — written for CN per PREREG_K_CN.md.

model.py is the copied production cards pattern (team yellow ratings +
NB count distribution + naive ensemble; referee used only by the x8
arm, which is NOT built here). Protocol:
- era 2023+ only; warm-up 2023 (predictions estimate the NB size r,
  never scored); dev scored 2024+2025 (n=480);
- virgin 2026 (n=240) read ONCE, only if Gate Zero passes dev; r
  re-estimated from all pre-virgin predictions, Online state
  continues through the virgin window;
- target: stats-feed yellows (frozen); the preregistered sensitivity
  recomputes virgin LL@3.5 + calibration against the event-feed
  target and reports it in results_virgin.json (not a gate leg).
Calibration = actual - predicted. Primary line 3.5.
"""
import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "ua_matches.csv"
PRED = HERE.parents[1] / "predictions" / "k_ua_virgin_predictions.csv"
DEV = ("2022/2023", "2023/2024", "2024/2025")
SCORED = DEV[1:]
VIRGIN_SEASON = "2025/2026"
ARM = "gate_zero"
LINES = (3.5, 4.5)
PRIMARY = 4.5
HALVES_YC_1H = 0.3290


def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["ev_yellow_home"] == "" or r["ev_yellow_away"] == "":
                continue
            key = (r["date"] + "T00:00:00Z", r["match_id"])
            yh, ya = int(float(r["ev_yellow_home"])), int(float(r["ev_yellow_away"]))  # UA: EVENT yellows are the frozen primary target (stats key absent)
            evh = int(float(r["yellow_cards_home"])) if r.get("yellow_cards_home") not in (None, "") else None  # stats sensitivity: absent in UA -> None
            eva = int(float(r["yellow_cards_away"])) if r.get("yellow_cards_away") not in (None, "") else None
            out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                        "kickoff_utc": key[0], "key": key,
                        "day": date.fromisoformat(r["date"]).toordinal(),
                        "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                        "home": r["home_team"], "away": r["away_team"], "yh": yh, "ya": ya,
                        "y": yh + ya, "ev_y": (evh + eva) if evh is not None and eva is not None else None,
                        "referee": r.get("referee", "")})
    out.sort(key=lambda x: x["key"])
    return out


def scored(rows, rm, target_key="y"):
    out = {}
    for method in ("model", "base", "naive"):
        out[method] = {}
        for line in LINES:
            ps = [nb_over(x[method], rm[method], line) for x in rows]
            ys = [int(x[target_key] > line) for x in rows]
            out[method][str(line)] = {"n": len(rows),
                                      "ll": sum(-(y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12))) for p, y in zip(ps, ys)) / len(rows),
                                      "mean_p": sum(ps) / len(ps), "actual_rate": sum(ys) / len(ys)}
    return out


def dev():
    rows = load(DEV)
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
    pl = str(PRIMARY)
    gate = metrics["pooled"]["model"][pl]["ll"] < metrics["pooled"]["base"][pl]["ll"] and \
        metrics["pooled"]["model"][pl]["ll"] < metrics["pooled"]["naive"][pl]["ll"]
    assert len(scored_rows) == 480, len(scored_rows)
    result = {"protocol": {"league": "UA-PremierLeague", "warmup": DEV[0], "scored": list(SCORED),
                           "dev_rows_loaded": len(rows), "scored_n": len(scored_rows),
                           "primary_line": PRIMARY, "target": "ev_yellow_home + ev_yellow_away (event-unified; stats key absent)",
                           "sign_convention": "actual_minus_predicted"},
              "arms": {ARM: {"r": rm, "seasons": metrics, "dev_gate_pass": gate}},
              "baselines": {"base": metrics["pooled"]["base"], "naive": metrics["pooled"]["naive"]}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_target", "arm", "predicted_mean", "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "baseline_base_p_over_3_5", "baseline_naive_p_over_3_5"]
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p in scored_rows:
            w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                        "home_team_id": r["home_id"], "away_team_id": r["away_id"],
                        "home": r["home"], "away": r["away"], "actual_target": r["y"], "arm": ARM,
                        "predicted_mean": p["model"],
                        "p_over_3_5": nb_over(p["model"], rm["model"], 3.5),
                        "p_over_4_5": nb_over(p["model"], rm["model"], 4.5),
                        "p_over_5_5": nb_over(p["model"], rm["model"], 5.5),
                        "baseline_base_p_over_3_5": nb_over(p["base"], rm["base"], 3.5),
                        "baseline_naive_p_over_3_5": nb_over(p["naive"], rm["naive"], 3.5)})
    return result


def virgin():
    d = json.loads((HERE / "results_dev.json").read_text())
    if not d["arms"][ARM]["dev_gate_pass"]:
        raise SystemExit("virgin refused: gate_zero did not pass the dev gate")
    rows = load(DEV + (VIRGIN_SEASON,))
    online = Online(); warm = []; target = []
    for row in rows:
        p = online.prediction(row, ARM)
        rec = {"y": row["y"], "ev_y": row["ev_y"], "model": p["model"], "base": p["base"],
               "naive": p["naive"], "row": row, "p": p}
        (target if row["season"] == VIRGIN_SEASON else warm).append(rec)
        online.update(row)
    assert len(target) == 240, len(target)
    rm = {m: estimate_r(warm, m) for m in ("model", "base", "naive")}
    metrics = scored([{k: x[k] for k in ("y", "model", "base", "naive")} for x in target], rm)
    pl = str(PRIMARY)
    cal = [int(x["y"] > PRIMARY) - nb_over(x["model"], rm["model"], PRIMARY) for x in target]
    mean_cal = sum(cal) / len(cal)
    se = (sum((x - mean_cal) ** 2 for x in cal) / (len(cal) - 1)) ** .5 / len(cal) ** .5
    # preregistered sensitivity (not a gate leg): event-feed target
    ev_rows = [{**{k: x[k] for k in ("model", "base", "naive")}, "y": x["ev_y"]}
               for x in target if x["ev_y"] is not None]
    ev_metrics = scored(ev_rows, rm) if ev_rows else None
    ev_cal = None
    if ev_rows:
        dif = [int(x["y"] > PRIMARY) - nb_over(x["model"], rm["model"], PRIMARY) for x in ev_rows]
        ev_cal = {"n": len(ev_rows), "diff": sum(dif) / len(dif),
                  "se": (sum((v - sum(dif) / len(dif)) ** 2 for v in dif) / (len(dif) - 1)) ** .5 / len(dif) ** .5}
    best_base = min(metrics["base"][pl]["ll"], metrics["naive"][pl]["ll"])
    leg_i = metrics["model"][pl]["ll"] <= best_base
    leg_ii = abs(mean_cal) <= 0.01 + se
    status = "clean" if abs(mean_cal) <= 0.01 else ("provisional" if leg_ii else "fail")
    shipped = ARM if (leg_i and leg_ii) else None
    out = {"protocol": {"league": "UA-PremierLeague", "virgin_season": VIRGIN_SEASON, "n": len(target),
                        "scored_arms": [ARM], "primary_line": PRIMARY,
                        "sign_convention": "actual_minus_predicted",
                        "r_handling": "fixed estimate_r from pre-virgin predictions; Online state continues through virgin"},
           "arms": {ARM: {"r": rm, "metrics": metrics,
                          "calibration": {"diff": mean_cal, "se": se, "status": status},
                          "legs": {"i_ll": bool(leg_i), "ii_calibration": bool(leg_ii)}}},
           "baselines": {"base": metrics["base"], "naive": metrics["naive"]},
           "sensitivity_event_target": {"metrics_model": ev_metrics["model"] if ev_metrics else None,
                                        "calibration": ev_cal},
           "shipped_arm": shipped}
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_target", "actual_event_target", "arm", "predicted_mean", "r",
              "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "baseline_base_p_over_3_5", "baseline_naive_p_over_3_5"]
    with (HERE / "predictions_virgin.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for x in target:
            r = x["row"]
            w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                        "home_team_id": r["home_id"], "away_team_id": r["away_id"],
                        "home": r["home"], "away": r["away"], "actual_target": x["y"],
                        "actual_event_target": x["ev_y"], "arm": ARM,
                        "predicted_mean": x["model"], "r": rm["model"],
                        "p_over_3_5": nb_over(x["model"], rm["model"], 3.5),
                        "p_over_4_5": nb_over(x["model"], rm["model"], 4.5),
                        "p_over_5_5": nb_over(x["model"], rm["model"], 5.5),
                        "baseline_base_p_over_3_5": nb_over(x["base"], rm["base"], 3.5),
                        "baseline_naive_p_over_3_5": nb_over(x["naive"], rm["naive"], 3.5)})
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(
        {"arm": ARM, "r": rm, "shipped_arm": shipped, "halves_yellow_cards_1h_share": HALVES_YC_1H},
        indent=2) + "\n")
    if shipped:
        PRED.parent.mkdir(parents=True, exist_ok=True)
        with open(PRED, "w", newline="", encoding="utf-8") as f:
            fields2 = ["match_id", "date", "home_team", "away_team", "actual_yellow_total",
                       "actual_event_yellow_total", "arm", "pred_yellow_total",
                       "p_over_3_5", "p_over_4_5", "pred_yellow_1h", "pred_yellow_2h"]
            w = csv.DictWriter(f, fieldnames=fields2); w.writeheader()
            for x in target:
                r = x["row"]
                w.writerow({"match_id": r["match_id"], "date": r["date"], "home_team": r["home"],
                            "away_team": r["away"], "actual_yellow_total": x["y"],
                            "actual_event_yellow_total": x["ev_y"], "arm": ARM,
                            "pred_yellow_total": x["model"],
                            "p_over_3_5": nb_over(x["model"], rm["model"], 3.5),
                            "p_over_4_5": nb_over(x["model"], rm["model"], 4.5),
                            "pred_yellow_1h": x["model"] * HALVES_YC_1H,
                            "pred_yellow_2h": x["model"] * (1 - HALVES_YC_1H)})
    return out
