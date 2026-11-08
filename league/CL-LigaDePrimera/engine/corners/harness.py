"""C-CL development-only evaluation harness."""
import csv
import json
import math
from pathlib import Path
from core import FeatureBuilder, attach_naive, baseline_prediction, load, model_prediction, over_prob, fit_params, pmf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "data" / "cl_matches.csv"
PRED = HERE.parents[1] / "predictions" / "c_cl_virgin_predictions.csv"
DEV_SEASONS = ("2021", "2022", "2023", "2024")
TARGET_SEASONS = ("2022", "2023", "2024")


def feature_rows(seasons):
    return attach_naive(FeatureBuilder(load(DATA, set(seasons))).build())


def season_metrics(rows, predictions, season):
    rs = [r for r in rows if r["season"] == season]
    ps = [p for p in predictions if p["season"] == season]
    return metrics(rs, ps, season)


def metrics(rows, predictions, season):
    n = len(rows)
    vals = {"n": n, "season": season}
    for line in (8.5, 9.5, 10.5):
        probs = [p[line] for p in predictions]
        actual = [int(r["y"] > line) for r in rows]
        vals["ll_" + str(line)] = sum(-(y * math.log(max(p, 1e-12)) + (1-y) * math.log(max(1-p, 1e-12))) for p, y in zip(probs, actual)) / n
        vals["mean_p_" + str(line)] = sum(probs) / n
        vals["actual_over_" + str(line)] = sum(actual) / n
    if predictions and "active" in predictions[0]:
        vals["both_teams_active_share"] = sum(p["active"] for p in predictions) / n
        vals["active_with_nonzero_beta_share"] = sum(p["active_nonzero"] for p in predictions) / n
    if n:
        e=[p[9.5]-int(r["y"]>9.5) for r,p in zip(rows,predictions)]; mean_e=sum(e)/n
        vals["calibration_diff"]= -mean_e; vals["calibration_se"]=(sum((x-mean_e)**2 for x in e)/(n-1))**0.5/(n**0.5) if n>1 else 0
    return vals


def make_prediction(row, kind, params=None, arm=None):
    if kind == "model":
        mu, r = model_prediction(row, params, arm)
        active = row["both_poss_active"]
        active_nonzero = active and any(abs(x) > 0 for x in params["beta"])
    else:
        mu, r = baseline_prediction(row, kind)
        active = active_nonzero = False
    return {"season": row["season"], "match_id": row["match_id"], "mu": mu, "r": r,
            **{line: over_prob(mu, r, line) for line in (8.5, 9.5, 10.5)},
            "active": active, "active_nonzero": active_nonzero}


def dev():
    all_rows = feature_rows(DEV_SEASONS)
    result = []
    for arm in ("gate_zero", "boxtouch"):
        for season in TARGET_SEASONS:
            target = [r for r in all_rows if r["season"] == season]
            train = [r for r in all_rows if r["season"] < season]
            params = fit_params(train, arm)
            for kind in ("model", "league_base_rate", "naive_trailing_10"):
                preds = [make_prediction(r, kind, params, arm) if kind == "model" else make_prediction(r, kind) for r in target]
                row = metrics(target, preds, season)
                row.update({"arm": arm, "kind": kind})
                result.append(row)
        # pooled is the exact pooled row of season-specific predictions.
        pooled_rows = []
        for season in TARGET_SEASONS:
            target = [r for r in all_rows if r["season"] == season]
            train = [r for r in all_rows if r["season"] < season]
            params = fit_params(train, arm)
            for r in target:
                pooled_rows.append((r, make_prediction(r, "model", params, arm)))
        for kind in ("model", "league_base_rate", "naive_trailing_10"):
            pairs = []
            for season in TARGET_SEASONS:
                target = [r for r in all_rows if r["season"] == season]
                train = [r for r in all_rows if r["season"] < season]
                params = fit_params(train, arm)
                pairs.extend((r, make_prediction(r, kind, params, arm) if kind == "model" else make_prediction(r, kind)) for r in target)
            row = metrics([x[0] for x in pairs], [x[1] for x in pairs], "pooled")
            row.update({"arm": arm, "kind": kind})
            result.append(row)
    result = {"protocol": {"league": "CL-LigaDePrimera", "dev_seasons_loaded": list(DEV_SEASONS), "scored_n": sum(x["n"] for x in result if x["season"] == "pooled" and x["kind"] == "model"), "primary_line": 9.5, "sign_convention": "actual_minus_predicted"}, "rows": result}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_8.5", "ll_9.5", "ll_10.5", "mean_p_9.5", "actual_over_9.5", "both_teams_active_share", "active_with_nonzero_beta_share"]
    with open(HERE / "results_dev.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows({k: x.get(k, "") for k in fields} for x in result["rows"])
    with (HERE / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["match_id", "season", "date", "home", "away", "actual_target", "arm", "predicted_mean", "p_over_8_5", "p_over_9_5", "p_over_10_5", "baseline_league_p_over_9_5", "baseline_naive_p_over_9_5"]
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for arm in ("gate_zero", "boxtouch"):
            for season in TARGET_SEASONS:
                target = [r for r in all_rows if r["season"] == season]; train = [r for r in all_rows if r["season"] < season]; params = fit_params(train, arm)
                for r in target:
                    mu, rr = model_prediction(r, params, arm)
                    bl, br = baseline_prediction(r, "league_base_rate"); bn, bnr = baseline_prediction(r, "naive_trailing_10")
                    w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"], "actual_target": r["y"], "arm": arm, "predicted_mean": mu, "p_over_8_5": over_prob(mu, rr, 7.5), "p_over_9_5": over_prob(mu, rr, 9.5), "p_over_10_5": over_prob(mu, rr, 9.5), "baseline_league_p_over_9_5": over_prob(bl, br, 9.5), "baseline_naive_p_over_9_5": over_prob(bn, bnr, 9.5)})
    print_table(result, "dev")
    return result


def gate_passes(dev_result):
    out = {}
    for arm in ("gate_zero", "boxtouch"):
        p = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        b1 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "league_base_rate")
        b2 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "naive_trailing_10")
        out[arm] = p["ll_9.5"] < b1["ll_9.5"] and p["ll_9.5"] < b2["ll_9.5"]
    return out


def virgin(arms, dev_result):
    gates = gate_passes(dev_result)
    refused = [a for a in arms if not gates.get(a, False)]
    if refused:
        raise SystemExit("virgin refused non-passing arm(s): " + ", ".join(refused))
    rows = feature_rows(DEV_SEASONS + ("2025",))
    target = [r for r in rows if r["season"] == "2025"]
    train = [r for r in rows if r["season"] != "2025"]
    result = {"protocol":{"league":"CL-LigaDePrimera","virgin_season":"2025","n":len(target),"scored_arms":list(arms),"primary_line":9.5,"sign_convention":"actual_minus_predicted"}}
    params_out = {}
    for arm in arms:
        params = fit_params(train, arm)
        preds = [make_prediction(r, "model", params, arm) for r in target]
        m = metrics(target, preds, "2025")
        cal = m["actual_over_9.5"] - m["mean_p_9.5"]
        errors = [int(r["y"] > 9.5) - p[9.5] for r, p in zip(target, preds)]
        mean_e = sum(errors) / len(errors)
        se = math.sqrt(sum((e - mean_e) ** 2 for e in errors) / (len(errors) - 1)) / math.sqrt(len(errors))
        m.update({"arm": arm, "calibration_diff": cal, "calibration_se": se, "params": params})
        result[arm] = m
        params_out[arm] = params
    # Baselines are evaluated on virgin for gate-leg reporting.
    for kind in ("league_base_rate", "naive_trailing_10"):
        preds = [make_prediction(r, kind) for r in target]
        result[kind] = metrics(target, preds, "2025")
    best_base = min(result["league_base_rate"]["ll_9.5"], result["naive_trailing_10"]["ll_9.5"])
    eligible = []
    for arm in arms:
        v = result[arm]
        sign = arm == "gate_zero" or sum(next(x for x in dev_result if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_9.5"] <= next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_9.5"] for s in TARGET_SEASONS) >= 2
        if v["ll_9.5"] <= result.get("gate_zero", v)["ll_9.5"] and v["ll_9.5"] <= best_base and abs(v["calibration_diff"] * 1.0) <= .01 + v["calibration_se"] and sign:
            eligible.append(arm)
    result["shipped_arm"] = min(eligible, key=lambda a: (result[a]["ll_9.5"], ("gate_zero", "boxtouch").index(a))) if eligible else None
    all_fields = ["match_id","season","date","home","away","actual_target","arm","predicted_mean","p_over_8_5","p_over_9_5","p_over_10_5","baseline_league_p_over_9_5","baseline_naive_p_over_9_5"]
    with (HERE / "predictions_virgin_all.csv").open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=all_fields); w.writeheader()
        for arm in arms:
            params=params_out[arm]
            for row in target:
                mu,r=model_prediction(row,params,arm)
                bl, br = baseline_prediction(row, "league_base_rate"); bn, bnr = baseline_prediction(row, "naive_trailing_10")
                q={"match_id":row["match_id"],"season":row["season"],"date":row["date"].isoformat(),"home":row["home"],"away":row["away"],"actual_target":row["y"],"arm":arm,"predicted_mean":mu,"p_over_8_5":over_prob(mu,r,7.5),"p_over_9_5":over_prob(mu,r,9.5),"p_over_10_5":over_prob(mu,r,9.5),"baseline_league_p_over_9_5":over_prob(bl,br,9.5),"baseline_naive_p_over_9_5":over_prob(bn,bnr,9.5)}; w.writerow(q)
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(params_out, indent=2) + "\n")
    if result["shipped_arm"]:
        write_predictions(result["shipped_arm"], target, params_out[result["shipped_arm"]])
    print_table(list(result.values()), "virgin")
    return result, target


def print_table(rows, label):
    print(label)
    for x in rows:
        if isinstance(x, dict) and "arm" in x:
            print(x.get("arm"), x.get("season"), x.get("kind", "model"), x.get("n"),
                  "LL9.5=" + format(x.get("ll_10.5", 0), ".6f"),
                  "P=" + format(x.get("mean_p_9.5", 0), ".6f"),
                  "A=" + format(x.get("actual_over_10.5", 0), ".6f"))


def write_predictions(arm, target, params):
    PRED.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "actual_corners_home", "actual_corners_away", "actual_corners_total", "arm", "mu", "r", "gamma", "beta", "p_over_8.5", "p_over_9.5", "p_over_10.5"]
    with open(PRED, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for row in target:
            mu, r = model_prediction(row, params, arm)
            out = {"match_id": row["match_id"], "date": row["date"].isoformat(), "home_team": row["home"], "away_team": row["away"], "actual_corners_home": row["ch"], "actual_corners_away": row["ca"], "actual_corners_total": row["y"], "arm": arm, "mu": mu, "r": r, "gamma": params["gamma"], "beta": json.dumps(params["beta"], separators=(",", ":"))}
            out.update({"p_over_" + str(line): over_prob(mu, r, line) for line in (8.5, 9.5, 10.5)})
            w.writerow(out)
