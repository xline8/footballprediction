"""G-SAFD walk-forward evaluation and frozen preregistration gates."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "safd_matches.csv"
OUT = Path(__file__).resolve().parent
PREDICTIONS = OUT.parents[1] / "predictions" / "g_safd_virgin_predictions.csv"
DEV_SEASON = "2024/2025"
VIRGIN_SEASON = "2025/2026"
WARMUP = 90
ARMS = ("gate_zero", "shrink")


def load(seasons):
    rows = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons or r["phase"] != "regular" or r["awarded"] != "0":
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1.0 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _predict_block(train, target, arm):
    cutoff = min(r["date"] for r in target)
    model = DC().fit(train, cutoff)
    counts = match_counts(train)
    out = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
        out.append((r, lh, la, model.probs(lh, la)))
    return model, out


def _dev_predictions():
    rows = load({DEV_SEASON})
    assert len(rows) == 306, len(rows)
    scored = rows[WARMUP:]
    dates = sorted({r["date"] for r in scored})
    per_arm = {arm: [] for arm in ARMS}
    for d in dates:
        target = [r for r in scored if r["date"] == d]
        train = [r for r in rows if r["date"] < d]
        cp, co = _clim(train)
        clim_p = {"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co}
        for arm in ARMS:
            _, preds = _predict_block(train, target, arm)
            for r, lh, la, p in preds:
                per_arm[arm].append((r, lh, la, p, clim_p))
    return per_arm


def run_dev():
    per_arm = _dev_predictions()
    result = []
    for arm in ARMS:
        triples = per_arm[arm]
        met = _scores([t[0] for t in triples], [t[3] for t in triples])
        result.append({**met, "arm": arm, "season": "pooled", "kind": "model"})
        met = _scores([t[0] for t in triples], [t[4] for t in triples])
        result.append({**met, "arm": arm, "season": "pooled", "kind": "climatology"})
    scored_n = len(per_arm["gate_zero"])
    assert scored_n == 216, scored_n
    out = {"protocol": {"league": "SA-FirstDivision", "dev_season": DEV_SEASON,
                         "warmup_matches": WARMUP, "scored_n": scored_n,
                         "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"},
           "rows": result}
    (OUT / "results_dev.json").write_text(json.dumps(out, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        w.writerows({k: r.get(k) for k in fields} for r in result)
    fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
              "actual_home_goals", "actual_away_goals", "actual_target", "arm", "lambda_home",
              "lambda_away", "p_home", "p_draw", "p_away", "p_over_2_5", "baseline_p_home",
              "baseline_p_draw", "baseline_p_away", "baseline_p_over_2_5"]
    with (OUT / "predictions_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm in ARMS:
            for r, lh, la, p, cp in per_arm[arm]:
                w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(),
                            "home_team_id": r["hi"], "away_team_id": r["ai"], "home": r["home"], "away": r["away"],
                            "actual_home_goals": r["yh"], "actual_away_goals": r["ya"], "actual_target": r["yh"] + r["ya"],
                            "arm": arm, "lambda_home": lh, "lambda_away": la, "p_home": p["ph"], "p_draw": p["pd"],
                            "p_away": p["pa"], "p_over_2_5": p["over25"], "baseline_p_home": cp["ph"],
                            "baseline_p_draw": cp["pd"], "baseline_p_away": cp["pa"], "baseline_p_over_2_5": cp["over25"]})
    for r in result:
        print(f'{r["arm"]} {r["kind"]} n={r["n"]} ll={r["ll_1x2"]:.6f} rps={r["rps"]:.6f} oull={r["oull_2_5"]:.6f}')
    return out


def _dev_passing(dev):
    passing = []
    for arm in ARMS:
        model = next(x for x in dev["rows"] if x["arm"] == arm and x["kind"] == "model")
        clim = next(x for x in dev["rows"] if x["arm"] == arm and x["kind"] == "climatology")
        if model["ll_1x2"] < clim["ll_1x2"] and model["rps"] < clim["rps"] and model["oull_2_5"] < clim["oull_2_5"]:
            passing.append(arm)
    return passing


def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs)
    def diff_se(y, p):
        e = [a - b for a, b in zip(y, p)]
        d = sum(e) / len(e)
        return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** 0.5 / (len(e) ** 0.5)
    dh, seh = diff_se([int(r["yh"] > r["ya"]) for r in rows], [p["ph"] for p in probs])
    do, seo = diff_se([int(r["yh"] + r["ya"] > 2.5) for r in rows], [p["over25"] for p in probs])
    return {**scored, "calibration": {"home_win_diff": dh, "home_win_se": seh,
                                      "over25_diff": do, "over25_se": seo}}


def _calibration_status(diff, se):
    if abs(diff) <= 0.01:
        return "clean"
    if abs(diff) <= 0.01 + se:
        return "provisional"
    return "FAIL"


def _write_params(model, arm, train_n):
    params = {"arm": arm, "label": "Gate Zero" if arm == "gate_zero" else "SHRINK",
              "rho": model.rho, "home_advantage": model.h, "mu": model.mu,
              "training_rows": train_n, "attack": {str(k): v for k, v in model.a.items()},
              "defence": {str(k): v for k, v in model.d.items()},
              "team_names": {str(k): v for k, v in model.team_names.items()}}
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n")


def _write_predictions(target, model, pp, lams, arm):
    PREDICTIONS.parent.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a",
              "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "arm"]
    with PREDICTIONS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p, (lh, la) in zip(target, pp, lams):
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"],
                        "away_team": r["away"], "home_goals": r["yh"], "away_goals": r["ya"], "lam_h": lh,
                        "lam_a": la, "rho": model.rho, "ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
                        "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"],
                        "p_btts": p["btts"], "arm": arm})


def virgin():
    dev = json.loads((OUT / "results_dev.json").read_text())
    passing = _dev_passing(dev)
    if "gate_zero" not in passing:
        out = {"virgin_read": False, "reason": "Gate Zero failed dev gate"}
        (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
        _write_params(DC(), "gate_zero", 0)
        print("virgin_read=false reason=Gate Zero failed dev gate")
        return out
    rows = load({DEV_SEASON, VIRGIN_SEASON})
    train = [r for r in rows if r["season"] == DEV_SEASON]
    target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    assert len(train) == 306 and len(target) == 304, (len(train), len(target))
    out = {"virgin_read": True, "protocol": {"league": "SA-FirstDivision", "virgin_season": VIRGIN_SEASON,
           "n": len(target), "training_season": DEV_SEASON, "training_n": len(train), "scored_arms": passing,
           "sign_convention": "actual_minus_predicted"}, "arms": {}, "baselines": {}}
    predsets = {}
    for arm in passing:
        model, preds = _predict_block(train, target, arm)
        pp = [p for _, _, _, p in preds]
        predsets[arm] = (pp, model, [(lh, la) for _, lh, la, _ in preds])
        out["arms"][arm] = _virgin_metrics(target, pp)
    cp, co = _clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    out["baselines"]["climatology"] = _virgin_metrics(target, cprobs)
    dev_model = {a: next(x for x in dev["rows"] if x["arm"] == a and x["kind"] == "model") for a in ARMS}
    gz = out["arms"]["gate_zero"]
    for arm in passing:
        v = out["arms"][arm]
        cal = v["calibration"]
        legs = {"ll": v["ll_1x2"] <= gz["ll_1x2"] and v["ll_1x2"] <= out["baselines"]["climatology"]["ll_1x2"],
                "calibration": {k: {"diff": cal[k], "se": cal[k.replace("diff", "se")],
                                    "status": _calibration_status(cal[k], cal[k.replace("diff", "se")])}
                                for k in ("home_win_diff", "over25_diff")}}
        legs["calibration_pass"] = all(x["status"] != "FAIL" for x in legs["calibration"].values())
        legs["sign"] = arm == "gate_zero" or dev_model[arm]["ll_1x2"] <= dev_model["gate_zero"]["ll_1x2"]
        legs["passes"] = legs["ll"] and legs["calibration_pass"] and legs["sign"]
        out["arms"][arm]["gate_legs"] = legs
    eligible = [a for a in passing if out["arms"][a]["gate_legs"]["passes"]]
    chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        pp, model, lams = predsets[chosen]
        _write_predictions(target, model, pp, lams, chosen)
        _write_params(model, chosen, len(train))
    else:
        _write_params(predsets["gate_zero"][1], "gate_zero", len(train))
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"virgin_read": True, "shipped_arm": chosen,
                      "arms": {a: out["arms"][a]["ll_1x2"] for a in out["arms"]},
                      "climatology_ll": out["baselines"]["climatology"]["ll_1x2"]}, indent=2))
    return out


def virgin_predict():
    """Validate the prediction artifact produced during the single virgin pass."""
    result = json.loads((OUT / "results_virgin.json").read_text())
    if not result.get("virgin_read"):
        print("virgin prediction skipped: virgin was not read")
        return result
    shipped = result.get("shipped_arm")
    if shipped and not PREDICTIONS.exists():
        raise SystemExit("virgin metrics marked an arm shipped but prediction CSV is missing")
    print(f"virgin prediction artifact present={PREDICTIONS.exists()} shipped_arm={shipped}")
    return result
