"""C-AU evaluation harness and frozen output writers."""
import csv
import json
import math
from pathlib import Path
from core import FeatureBuilder, attach_naive, baseline_prediction, load, model_prediction, over_prob, fit_params, pmf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "league" / "AU-ALeagueWomen" / "data" / "auw_matches.csv"
PRED = ROOT / "league" / "AU-ALeagueWomen" / "predictions" / "c_auw_virgin_predictions.csv"
DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
TARGET_SEASONS = ("2022/2023", "2023/2024", "2024/2025")


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
            **{line: over_prob(mu, r, line) for line in (8.5, 9.5, 10.5)},
            "active": active, "active_nonzero": active_nonzero}


def dev():
    all_rows = feature_rows(DEV_SEASONS)
    result = []
    detail = []
    for arm in ("gate_zero", "x7"):
        for season in TARGET_SEASONS:
            target = [r for r in all_rows if r["season"] == season]
            train = [r for r in all_rows if r["season"] < season]
            params = fit_params(train, arm)
            for kind in ("model", "league_base_rate", "naive_trailing_10"):
                preds = [make_prediction(r, kind, params, arm) if kind == "model" else make_prediction(r, kind) for r in target]
                for r, p in zip(target, preds):
                    detail.append({"match_id": r["match_id"], "season": season, "date": r["date"].isoformat(), "home": r["home"], "away": r["away"], "arm": arm if kind == "model" else kind, "p_over_primary": p[9.5], "actual_total": r["y"], "actual_over_primary": int(r["y"] > 9.5)})
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
    (HERE / "results_dev.json").write_text(json.dumps({"protocol":{"regular_only":True,"dev_n":369,"primary_line":9.5,"ladder":[8.5,9.5,10.5],"halves":[.480,.520]},"metrics":result,"calibration_inputs":detail}, indent=2) + "\n")
    fields = list(detail[0])
    with open(HERE / "results_dev.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(detail)
    print_table(result, "dev")
    return result


def gate_passes(dev_result):
    out = {}
    for arm in ("gate_zero", "x7"):
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
    rows = feature_rows(DEV_SEASONS + ("2025/2026",))
    target = [r for r in rows if r["season"] == "2025/2026"]
    train = [r for r in rows if r["season"] != "2025/2026"]
    result = {}
    params_out = {}
    for arm in arms:
        params = fit_params(train, arm)
        preds = [make_prediction(r, "model", params, arm) for r in target]
        m = metrics(target, preds, "2025/2026")
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
        result[kind] = metrics(target, preds, "2025/2026")
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
    fields = ["match_id", "date", "home_team", "away_team", "actual_corners_home", "actual_corners_away", "actual_corners_total", "arm", "mu", "r", "gamma", "beta", "p_over_9.5", "p_over_10.5", "p_over_11.5", "mu_1h", "p_1h_over_3.5", "p_1h_over_4.5", "p_1h_over_5.5", "mu_2h", "p_2h_over_4.5", "p_2h_over_5.5", "p_2h_over_6.5"]
    with open(PRED, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for row in target:
            mu, r = model_prediction(row, params, arm)
            m1, m2 = 0.480 * mu, 0.520 * mu
            out = {"match_id": row["match_id"], "date": row["date"].isoformat(), "home_team": row["home"], "away_team": row["away"], "actual_corners_home": row["ch"], "actual_corners_away": row["ca"], "actual_corners_total": row["y"], "arm": arm, "mu": mu, "r": r, "gamma": params["gamma"], "beta": json.dumps(params["beta"], separators=(",", ":"))}
            out.update({"p_over_" + str(line): over_prob(mu, r, line) for line in (9.5, 10.5, 11.5)})
            out["mu_1h"] = m1
            out.update({"p_1h_over_" + str(line): over_prob(m1, r, line) for line in (3.5, 4.5, 5.5)})
            out["mu_2h"] = m2
            out.update({"p_2h_over_" + str(line): over_prob(m2, r, line) for line in (4.5, 5.5, 6.5)})
            w.writerow(out)

def virgin_read():
    rows = feature_rows(DEV_SEASONS + ("2025/2026",))
    target = [r for r in rows if r["season"] == "2025/2026"]
    train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
    assert len(target) == 110 and len(train) == 439
    dev = json.loads((HERE / "results_dev.json").read_text())
    arms = ("gate_zero", "x7")
    detail=[]; results={}; params={}
    for arm in arms:
        pp=fit_params(train, arm); params[arm]=pp; ps=[make_prediction(r,"model",pp,arm) for r in target]
        for r,p in zip(target,ps): detail.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"].isoformat(),"home":r["home"],"away":r["away"],"arm":arm,"p_over_primary":p[9.5],"actual_total":r["y"],"actual_over_primary":int(r["y"]>9.5)})
        m=metrics(target,ps,"2025/2026"); e=[p[9.5]-int(r["y"]>9.5) for r,p in zip(target,ps)]; mean=sum(e)/len(e); se=(sum((z-mean)**2 for z in e)/(len(e)-1))**.5/(len(e)**.5); m.update({"arm":arm,"calibration_diff":mean,"calibration_se":se}); results[arm]=m
    for kind in ("league_base_rate","naive_trailing_10"):
        ps=[make_prediction(r,kind) for r in target];
        for r,p in zip(target,ps): detail.append({"match_id":r["match_id"],"season":r["season"],"date":r["date"].isoformat(),"home":r["home"],"away":r["away"],"arm":"baseline_"+kind.replace("league_base_rate","league").replace("naive_trailing_10","naive"),"p_over_primary":p[9.5],"actual_total":r["y"],"actual_over_primary":int(r["y"]>9.5)})
        results[kind]=metrics(target,ps,"2025/2026")
    gzdev={s:next(x for x in dev["metrics"] if x["arm"]=="gate_zero" and x["season"]==s)["ll_9.5"] for s in TARGET_SEASONS}; var={s:next(x for x in dev["metrics"] if x["arm"]=="x7" and x["season"]==s)["ll_9.5"]<=gzdev[s] for s in TARGET_SEASONS}; results["x7"]["sign_check"]=sum(var.values())>=2; results["gate_zero"]["sign_check"]=True
    best=min(results[x]["ll_9.5"] for x in ("league_base_rate","naive_trailing_10")); gz=results["gate_zero"]["ll_9.5"]
    for a in arms:
        results[a]["leg_i"]=results[a]["ll_9.5"]<=gz and results[a]["ll_9.5"]<=best; results[a]["leg_ii"]=abs(results[a]["calibration_diff"])<=.01+results[a]["calibration_se"]; results[a]["eligible"]=results[a]["leg_i"] and results[a]["leg_ii"] and results[a]["sign_check"]
    eligible=[a for a in arms if results[a]["eligible"]]; ship=min(eligible,key=lambda a:(results[a]["ll_9.5"],0 if a=="gate_zero" else 1)) if eligible else None
    payload={"protocol":{"regular_only":True,"train_n":len(train),"virgin_n":len(target),"primary_line":9.5,"ladder":[8.5,9.5,10.5],"halves":[.480,.520]},"metrics":[{"arm":a,**results[a]} for a in arms]+[{"arm":"baseline_league",**results["league_base_rate"]},{"arm":"baseline_naive",**results["naive_trailing_10"]}],"dev_sign_check":var,"ship_arm":ship,"calibration_inputs":detail}
    (HERE/"results_virgin.json").write_text(json.dumps(payload,indent=2)+"\n")
    with (HERE/"results_virgin.csv").open("w",newline="",encoding="utf-8") as fh: w=csv.DictWriter(fh,fieldnames=list(detail[0])); w.writeheader(); w.writerows(detail)
    if ship:
        (HERE/"fitted_params_virgin.json").write_text(json.dumps({ship:params[ship]},indent=2)+"\n"); write_predictions(ship,target,params[ship])
