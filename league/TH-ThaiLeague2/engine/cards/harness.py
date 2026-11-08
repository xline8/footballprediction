"""K-TH2 walk-forward evaluation (event-unified yellows, Gate Zero only).

Dev: within-season walk-forward over 2024/2025 regular. Warm-up = first
90 regular matches (state updates, never scored); scored = remaining
regular matches with an event feed (n = 182). Virgin: 2025/2026 regular
(n = 306), read ONCE and only if Gate Zero passes the dev gate; the
Online state continues through the virgin, and the NB size r is
re-estimated once from all pre-virgin predictions (sibling pattern).
"""
import csv, json, math
from datetime import date
from pathlib import Path
from model import Online, estimate_r, nb_over

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "th2_matches.csv"
DEV_SEASON = "2024/2025"
VIRGIN_SEASON = "2025/2026"
WARMUP = 90
ARM = "gate_zero"
LINES = (3.5, 4.5, 5.5)
HALVES_SHARE = 0.3322


def load(seasons):
    """All regular rows in order, with a cards_valid flag (event feed present)."""
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["phase"] != "regular":
                continue
            yh, ya = int(r["ev_yellow_home"]), int(r["ev_yellow_away"])
            out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                        "kickoff_utc": r["date"] + "T00:00:00Z",
                        "key": (r["date"] + "T00:00:00Z", r["match_id"]),
                        "day": date.fromisoformat(r["date"]).toordinal(),
                        "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                        "home": r["home_team"], "away": r["away_team"],
                        "yh": yh, "ya": ya, "y": yh + ya,
                        "referee": r.get("referee", ""),
                        "cards_valid": r["cards_source"] == "events"})
    out.sort(key=lambda x: x["key"])
    return out


def scored(rows, rm):
    out = {}
    for method in ("model", "base", "naive"):
        out[method] = {}
        for line in LINES:
            ps = [nb_over(x[method], rm[method], line) for x in rows]
            ys = [int(x["y"] > line) for x in rows]
            out[method][str(line)] = {"n": len(rows),
                                      "ll": sum(-(y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12))) for p, y in zip(ps, ys)) / len(rows),
                                      "mean_p": sum(ps) / len(ps), "actual_rate": sum(ys) / len(ys)}
    return out


def dev():
    rows = load({DEV_SEASON})
    assert len(rows) == 273, len(rows)
    online = Online(); warm = []; scored_rows = []
    for i, row in enumerate(rows):
        if not row["cards_valid"]:
            continue  # never scored, never updates the target state (prereg)
        p = online.prediction(row, ARM)
        if i < WARMUP:
            warm.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        else:
            scored_rows.append((row, p))
        online.update(row)
    rm = {m: estimate_r(warm, m) for m in ("model", "base", "naive")}
    metrics = scored([{**p, "y": r["y"]} for r, p in scored_rows], rm)
    gate = metrics["model"]["4.5"]["ll"] < metrics["base"]["4.5"]["ll"] and \
        metrics["model"]["4.5"]["ll"] < metrics["naive"]["4.5"]["ll"]
    assert len(scored_rows) == 182, len(scored_rows)
    result = {"protocol": {"league": "TH-ThaiLeague2", "warmup_matches": WARMUP,
                           "dev_season": DEV_SEASON, "dev_rows_loaded": len(rows),
                           "scored_n": len(scored_rows), "primary_line": 4.5,
                           "target": "ev_yellow_home + ev_yellow_away (event-unified)",
                           "sign_convention": "actual_minus_predicted"},
              "arms": {ARM: {"r": rm, "metrics": metrics, "dev_gate_pass": gate}},
              "baselines": {"base": metrics["base"], "naive": metrics["naive"]}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_target", "arm", "predicted_mean", "p_over_3_5", "p_over_4_5", "p_over_5_5",
              "baseline_base_p_over_4_5", "baseline_naive_p_over_4_5"]
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
                        "baseline_base_p_over_4_5": nb_over(p["base"], rm["base"], 4.5),
                        "baseline_naive_p_over_4_5": nb_over(p["naive"], rm["naive"], 4.5)})
    with (HERE / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["arm", "season", "kind", "n", "ll_3.5", "ll_4.5", "ll_5.5"])
        for kind in ("model", "base", "naive"):
            x = metrics[kind]
            w.writerow([ARM, "pooled", kind, x["4.5"]["n"], x["3.5"]["ll"], x["4.5"]["ll"], x["5.5"]["ll"]])
    print(json.dumps({"scored_n": len(scored_rows), "dev_gate_pass": gate,
                      "pooled_ll_4_5": metrics["model"]["4.5"]["ll"],
                      "base_ll_4_5": metrics["base"]["4.5"]["ll"],
                      "naive_ll_4_5": metrics["naive"]["4.5"]["ll"]}, indent=2))
    return result


def virgin():
    d = json.loads((HERE / "results_dev.json").read_text())
    if not d["arms"][ARM]["dev_gate_pass"]:
        raise SystemExit("virgin refused non-passing arm: gate_zero (virgin NOT read)")
    rows = load({DEV_SEASON, VIRGIN_SEASON})
    online = Online(); warm = []; target = []
    for row in rows:
        if not row["cards_valid"]:
            continue
        p = online.prediction(row, ARM)
        rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"],
               "row": row, "p": p}
        (target if row["season"] == VIRGIN_SEASON else warm).append(rec)
        online.update(row)
    assert len(target) == 306, len(target)
    rm = {m: estimate_r(warm, m) for m in ("model", "base", "naive")}
    metrics = scored([{k: x[k] for k in ("y", "model", "base", "naive")} for x in target], rm)
    cal = [int(x["y"] > 4.5) - nb_over(x["model"], rm["model"], 4.5) for x in target]
    se = (sum((x - sum(cal) / len(cal)) ** 2 for x in cal) / (len(cal) - 1)) ** .5 / len(cal) ** .5
    diff = sum(cal) / len(cal)
    best_base = min(metrics["base"]["4.5"]["ll"], metrics["naive"]["4.5"]["ll"])
    ll_ok = metrics["model"]["4.5"]["ll"] <= best_base
    cal_clean = abs(diff) <= 0.01
    cal_prov = abs(diff) - 0.01 <= se
    ships = bool(ll_ok and cal_prov)
    out = {"protocol": {"league": "TH-ThaiLeague2", "virgin_season": VIRGIN_SEASON,
                        "n": len(target), "scored_arms": [ARM], "primary_line": 4.5,
                        "sign_convention": "actual_minus_predicted",
                        "r_handling": "fixed estimate_r from all pre-virgin predictions; Online state continues through virgin"},
           "arms": {ARM: {"r": rm, "metrics": metrics,
                          "calibration": {"diff_4.5": diff, "se_4.5": se},
                          "ll_leg_pass": ll_ok, "calibration_clean": cal_clean,
                          "calibration_provisional": bool(cal_prov and not cal_clean)}},
           "baselines": {"base": metrics["base"], "naive": metrics["naive"]},
           "shipped_arm": ARM if ships else None}
    fields = ["match_id", "date", "home_team", "away_team", "actual_target", "arm",
              "predicted_mean", "r", "p_over_3_5", "p_over_4_5", "p_over_5_5"]
    with (HERE / "predictions_virgin_all.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for x in target:
            q = {"match_id": x["row"]["match_id"], "date": x["row"]["date"],
                 "home_team": x["row"]["home"], "away_team": x["row"]["away"],
                 "actual_target": x["y"], "arm": ARM, "predicted_mean": x["model"], "r": rm["model"]}
            q.update({"p_over_" + str(l).replace(".", "_"): nb_over(x["model"], rm["model"], l) for l in LINES})
            w.writerow(q)
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    if ships:
        day = date.fromisoformat("2026-04-25").toordinal()
        snap = online.state.snapshot(day)
        (HERE / "fitted_params_virgin.json").write_text(json.dumps(
            {"arm": ARM, "r": rm, "state_at_virgin_end": snap}, indent=2) + "\n")
        ppath = HERE.parents[1] / "predictions" / "k_th2_virgin_predictions.csv"
        ppath.parent.mkdir(exist_ok=True)
        fields = ["match_id", "date", "home_team", "away_team", "actual_target", "arm",
                  "expected_home", "expected_away", "expected_total",
                  "p_over_3_5", "p_over_4_5", "p_over_5_5",
                  "mean_1h", "mean_2h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5",
                  "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5"]
        with ppath.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for x in target:
                p = x["p"]; mu = x["model"]; mu1 = mu * HALVES_SHARE; mu2 = mu * (1 - HALVES_SHARE)
                w.writerow({"match_id": x["row"]["match_id"], "date": x["row"]["date"],
                            "home_team": x["row"]["home"], "away_team": x["row"]["away"],
                            "actual_target": x["y"], "arm": ARM,
                            "expected_home": p["eh"], "expected_away": p["ea"], "expected_total": mu,
                            "p_over_3_5": nb_over(mu, rm["model"], 3.5),
                            "p_over_4_5": nb_over(mu, rm["model"], 4.5),
                            "p_over_5_5": nb_over(mu, rm["model"], 5.5),
                            "mean_1h": mu1, "mean_2h": mu2,
                            "p_over_1h_0_5": nb_over(mu1, rm["model"], 0.5),
                            "p_over_1h_1_5": nb_over(mu1, rm["model"], 1.5),
                            "p_over_1h_2_5": nb_over(mu1, rm["model"], 2.5),
                            "p_over_2h_1_5": nb_over(mu2, rm["model"], 1.5),
                            "p_over_2h_2_5": nb_over(mu2, rm["model"], 2.5),
                            "p_over_2h_3_5": nb_over(mu2, rm["model"], 3.5)})
    print(json.dumps({"n": len(target), "ll_4_5": metrics["model"]["4.5"]["ll"],
                      "best_baseline_ll": best_base, "calibration_diff": diff, "se": se,
                      "shipped_arm": out["shipped_arm"]}, indent=2))
    return out
