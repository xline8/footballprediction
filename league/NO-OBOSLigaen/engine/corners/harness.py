"""C-J1 evaluation harness and frozen output writers."""
import csv
import json
import math
from pathlib import Path
from core import FeatureBuilder, attach_naive, baseline_prediction, load, model_prediction, over_prob, fit_params, pmf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "league" / "NO-OBOSLigaen" / "data" / "no_obos_matches.csv"
PRED = ROOT / "league" / "NO-OBOSLigaen" / "predictions" / "c_no_obos_virgin_predictions.csv"
DEV_SEASONS = ("2021", "2022", "2023", "2024", "2025")
TARGET_SEASONS = ("2022", "2023", "2024", "2025")


def feature_rows(seasons):
    return attach_naive(FeatureBuilder(load(DATA, set(seasons))).build())


def season_metrics(rows, predictions, season):
    rs = [r for r in rows if r["season"] == season]
    ps = [p for p in predictions if p["season"] == season]
    return metrics(rs, ps, season)


def metrics(rows, predictions, season):
    n = len(rows)
    vals = {"n": n, "season": season}
    for line in (9.5, 10.5, 11.5):
        probs = [p[line] for p in predictions]
        actual = [int(r["y"] > line) for r in rows]
        vals["ll_" + str(line)] = sum(-(y * math.log(max(p, 1e-12)) + (1-y) * math.log(max(1-p, 1e-12))) for p, y in zip(probs, actual)) / n
        vals["mean_p_" + str(line)] = sum(probs) / n
        vals["actual_over_" + str(line)] = sum(actual) / n
    if predictions and "active" in predictions[0]:
        vals["both_teams_active_share"] = sum(p["active"] for p in predictions) / n
        vals["active_with_nonzero_beta_share"] = sum(p["active_nonzero"] for p in predictions) / n
    return vals


def make_prediction(row, kind, params=None, arm=None):
    if kind == "model":
        mu, r = model_prediction(row, params, arm)
        active = row["both_poss_active"] if arm == "gate_zero" else False
        active_nonzero = active and any(abs(x) > 0 for x in params["beta"])
    else:
        mu, r = baseline_prediction(row, kind)
        active = active_nonzero = False
    return {"season": row["season"], "match_id": row["match_id"], "mu": mu, "r": r,
            **{line: over_prob(mu, r, line) for line in (9.5, 10.5, 11.5)},
            "active": active, "active_nonzero": active_nonzero}


def dev():
    all_rows = feature_rows(DEV_SEASONS)
    result = []
    for arm in ("gate_zero", "plain"):
        for season in TARGET_SEASONS:
            target = [r for r in all_rows if r["season"] == season]
            train = [r for r in all_rows if int(r["season"][:4]) < int(season[:4])]
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
            train = [r for r in all_rows if int(r["season"][:4]) < int(season[:4])]
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
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_9.5", "ll_10.5", "ll_11.5", "mean_p_10.5", "actual_over_10.5", "both_teams_active_share", "active_with_nonzero_beta_share"]
    with open(HERE / "results_dev.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows({k: x.get(k, "") for k in fields} for x in result)
    print_table(result, "dev")
    return result


def gate_passes(dev_result):
    out = {}
    for arm in ("gate_zero", "plain"):
        p = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        b1 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "league_base_rate")
        b2 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "naive_trailing_10")
        out[arm] = p["ll_10.5"] < b1["ll_10.5"] and p["ll_10.5"] < b2["ll_10.5"]
    return out


def virgin(arms, dev_result):
    gates = gate_passes(dev_result)
    refused = [a for a in arms if not gates.get(a, False)]
    if refused:
        raise SystemExit("virgin refused non-passing arm(s): " + ", ".join(refused))
    rows = feature_rows(("2021", "2022", "2023", "2024", "2025", "2026"))
    target = [r for r in rows if r["season"] == "2026"]
    train = [r for r in rows if r["season"] != "2026"]
    result = {}
    params_out = {}
    for arm in arms:
        params = fit_params(train, arm)
        preds = [make_prediction(r, "model", params, arm) for r in target]
        m = metrics(target, preds, "2026")
        cal = m["mean_p_10.5"] - m["actual_over_10.5"]
        errors = [p[10.5] - int(r["y"] > 10.5) for r, p in zip(target, preds)]
        mean_e = sum(errors) / len(errors)
        se = math.sqrt(sum((e - mean_e) ** 2 for e in errors) / (len(errors) - 1)) / math.sqrt(len(errors))
        m.update({"arm": arm, "calibration_diff": cal, "calibration_se": se, "params": params})
        result[arm] = m
        params_out[arm] = params
    # Baselines are evaluated on virgin for gate-leg reporting.
    for kind in ("league_base_rate", "naive_trailing_10"):
        preds = [make_prediction(r, kind) for r in target]
        result[kind] = metrics(target, preds, "2026")
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(params_out, indent=2) + "\n")
    print_table(list(result.values()), "virgin")
    return result, target


def print_table(rows, label):
    print(label)
    for x in rows:
        if "arm" in x:
            print(x.get("arm"), x.get("season"), x.get("kind", "model"), x.get("n"),
                  "LL10.5=" + format(x.get("ll_10.5", 0), ".6f"),
                  "P=" + format(x.get("mean_p_10.5", 0), ".6f"),
                  "A=" + format(x.get("actual_over_10.5", 0), ".6f"))


def write_predictions(arm, target, params):
    PRED.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "actual_corners_home", "actual_corners_away", "actual_corners_total", "arm", "mu", "r", "gamma", "beta", "p_over_9.5", "p_over_10.5", "p_over_11.5"]
    with open(PRED, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for row in target:
            mu, r = model_prediction(row, params, arm)
            out = {"match_id": row["match_id"], "date": row["date"].isoformat(), "home_team": row["home"], "away_team": row["away"], "actual_corners_home": row["ch"], "actual_corners_away": row["ca"], "actual_corners_total": row["y"], "arm": arm, "mu": mu, "r": r, "gamma": params["gamma"], "beta": json.dumps(params["beta"], separators=(",", ":"))}
            out.update({"p_over_" + str(line): over_prob(mu, r, line) for line in (9.5, 10.5, 11.5)})
            w.writerow(out)
