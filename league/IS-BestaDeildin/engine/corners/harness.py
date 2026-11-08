"""C-HR evaluation harness and frozen output writers (seeded from C-J1)."""
import csv
import json
import math
from pathlib import Path
from core import FeatureBuilder, attach_naive, baseline_prediction, load, model_prediction, over_prob, fit_params, pmf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "league" / "IS-BestaDeildin" / "data" / "is_matches.csv"
DEV_SEASONS = ("2023", "2024", "2025")
TARGET_SEASONS = ("2024", "2025")


def feature_rows(seasons):
    return attach_naive(FeatureBuilder(load(DATA, set(seasons))).build())


def season_metrics(rows, predictions, season):
    rs = [r for r in rows if r["season"] == season]
    ps = [p for p in predictions if p["season"] == season]
    return metrics(rs, ps, season)


def metrics(rows, predictions, season):
    n = len(rows)
    vals = {"n": n, "season": season}
    for line in (10.5, 11.5, 12.5):
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
        active = row["both_bt_active"] if arm == "x7" else row["both_poss_active"] and row["both_bc_active"]
        active_nonzero = active and any(abs(x) > 0 for x in params["beta"])
    else:
        mu, r = baseline_prediction(row, kind)
        active = active_nonzero = False
    return {"season": row["season"], "match_id": row["match_id"], "mu": mu, "r": r,
            **{line: over_prob(mu, r, line) for line in (10.5, 11.5, 12.5)},
            "active": active, "active_nonzero": active_nonzero}


def dev():
    all_rows = feature_rows(DEV_SEASONS)
    result = []
    for arm in ("gate_zero", "x7"):
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
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_10.5", "ll_11.5", "ll_12.5", "mean_p_11.5", "actual_over_11.5", "both_teams_active_share", "active_with_nonzero_beta_share"]
    with open(HERE / "results_dev.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows({k: x.get(k, "") for k in fields} for x in result)
    print_table(result, "dev")
    return result


def gate_passes(dev_result):
    out = {}
    for arm in ("gate_zero", "x7"):
        p = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        b1 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "league_base_rate")
        b2 = next(x for x in dev_result if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "naive_trailing_10")
        out[arm] = p["ll_11.5"] < b1["ll_11.5"] and p["ll_11.5"] < b2["ll_11.5"]
    return out


def print_table(rows, label):
    print(label)
    for x in rows:
        if "arm" in x:
            print(x.get("arm"), x.get("season"), x.get("kind", "model"), x.get("n"),
                  "LL11.5=" + format(x.get("ll_11.5", 0), ".6f"),
                  "P=" + format(x.get("mean_p_11.5", 0), ".6f"),
                  "A=" + format(x.get("actual_over_11.5", 0), ".6f"))

def virgin_metrics(rows):
    n = len(rows); out = {"n": n, "logloss": {}}
    for line in (10.5, 11.5, 12.5):
        ps = [p[line] for _, p in rows]; ys = [int(r["y"] > line) for r, _ in rows]
        out["logloss"][str(line)] = sum(-(y*math.log(max(p, 1e-12)) + (1-y)*math.log(max(1-p, 1e-12))) for p, y in zip(ps, ys)) / n
    ps = [p[11.5] for _, p in rows]; ys = [int(r["y"] > 11.5) for r, _ in rows]; d = [p-y for p, y in zip(ps, ys)]; mean = sum(d)/n
    out.update({"calibration_pp": mean*100, "calibration_se_pp": (sum((x-mean)**2 for x in d)/(n-1))**0.5/n**0.5*100, "actual_over_rate_pp": sum(ys)/n*100, "mean_pred_over_pp": sum(ps)/n*100})
    return out

def virgin(dev_result):
    all_rows = feature_rows(("2023", "2024", "2025", "2026")); target = [r for r in all_rows if r["season"] == "2026"]
    dev_pass = gate_passes(dev_result); passing = [a for a in ("gate_zero", "x7") if dev_pass[a]]
    params = {a: fit_params([r for r in all_rows if r["season"] != "2026"], a) for a in passing}
    runs = {a: [(r, make_prediction(r, "model", params[a], a)) for r in target] for a in passing}
    prior = [r for r in all_rows if r["season"] != "2026"]
    bases = {}
    for kind in ("league_base_rate", "naive_trailing_10"):
        if kind == "league_base_rate":
            q = {line: sum(int(r["y"] > line) for r in prior) / len(prior) for line in (10.5, 11.5, 12.5)}
            pairs = [(r, {line: q[line] for line in q}) for r in target]
        else:
            pairs = [(r, make_prediction(r, kind)) for r in target]
        bases[kind] = virgin_metrics(pairs)
    out = {"protocol": "C-IS frozen virgin", "virgin_season": "2026", "n": len(target), "read_arms": passing, "dev_pass": dev_pass, "arms": {a: virgin_metrics(v) for a, v in runs.items()}, "baselines": bases, "legs": {}}
    eligible = []
    for a, v in out["arms"].items():
        ref = out["arms"].get("gate_zero", v); leg1 = v["logloss"]["11.5"] <= ref["logloss"]["11.5"] and v["logloss"]["11.5"] <= min(x["logloss"]["11.5"] for x in bases.values())
        leg2 = abs(v["calibration_pp"]) <= 1.0 + v["calibration_se_pp"]
        leg3 = a == "gate_zero" or sum(next(x for x in dev_result if x["arm"] == a and x["season"] == s and x["kind"] == "model")["ll_11.5"] <= next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_11.5"] for s in ("2024", "2025")) >= 1
        out["legs"][a] = {"ll": leg1, "calibration": leg2, "dev_sign": leg3}
        if leg1 and leg2 and leg3: eligible.append(a)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["logloss"]["11.5"], 0 if a == "gate_zero" else 1)) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        write_predictions(runs[chosen], chosen, params[chosen])
        (HERE / "fitted_params_virgin.json").write_text(json.dumps({"arm": chosen, **params[chosen]}, indent=2) + "\n")
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    return out

def write_predictions(rows, arm, params):
    path = HERE / ".." / ".." / "predictions" / "c_is_virgin_predictions.csv"; path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["arm", "match_id", "date", "home", "away", "actual_total_corners", "pred_total_ft"] + [f"ft_p_over_{x}" for x in (10.5, 11.5, 12.5)] + [f"1h_p_over_{x}" for x in (5.0, 5.5, 6.0)] + [f"2h_p_over_{x}" for x in (5.5, 6.0, 6.5)]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for r, p in rows:
            mu = p["mu"]; q = {"arm": arm, "match_id": r["match_id"], "date": r["date"], "home": r["home"], "away": r["away"], "actual_total_corners": r["y"], "pred_total_ft": mu}
            for line in (10.5, 11.5, 12.5): q[f"ft_p_over_{line}"] = p[line]
            for line in (5.0, 5.5, 6.0): q[f"1h_p_over_{line}"] = over_prob(mu*.4707, params["r"], line)
            for line in (5.5, 6.0, 6.5): q[f"2h_p_over_{line}"] = over_prob(mu*.5293, params["r"], line)
            w.writerow(q)


