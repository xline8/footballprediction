"""G-LV development and virgin goals harness."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "lv_virsliga_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_SEASONS = ("2022", "2023", "2024", "2025")
DEV_LOADED = ("2021", "2022", "2023", "2024", "2025")
ALL_ARMS = ("gate_zero", "shrink")


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            rows.append({
                "match_id": r["match_id"], "season": r["season"],
                "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                "home": r["home_team"], "away": r["away_team"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                "xgh": None, "xga": None,
            })
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    fit_rows = [r for r in train if r["date"] < cutoff]
    model = DC().fit(fit_rows, cutoff)
    return model, match_counts(fit_rows), fit_rows


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


def _predict(model, counts, rows, arm):
    return [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, counts=counts)) for r in rows]


def run_dev():
    rows = load(DATA, set(DEV_LOADED))
    assert set(r["season"] for r in rows) <= set(DEV_LOADED)
    assert not any(r["season"] == "2026" for r in rows)
    scored = [r for r in rows if r["season"] in DEV_SEASONS]
    assert len(scored) == 720
    result_rows = []
    fit_params = {}
    prediction_sets = []
    for season in DEV_SEASONS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        clim = _scores(target, cprobs)
        for arm in ALL_ARMS:
            result_rows.append({**clim, "arm": arm, "season": season, "kind": "climatology"})
        for arm in ALL_ARMS:
            model, counts, fit_rows = _fit_predict(train, target, arm)
            probs = _predict(model, counts, target, arm)
            met = _scores(target, probs)
            result_rows.append({**met, "arm": arm, "season": season, "kind": "model"})
            fit_params[f"{arm}:{season}"] = {
                "training_rows": len(fit_rows), "a": dict(model.a), "d": dict(model.d),
                "h": model.h, "rho": model.rho, "mu": model.mu, "match_counts": dict(counts),
            }
            prediction_sets.append((arm, target, probs, cp, co))
    for arm in ALL_ARMS:
        model_sets = []
        for a, target, probs, _, _ in prediction_sets:
            if a == arm:
                model_sets.extend(zip(target, probs))
        clim_sets = []
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            cp, co = _clim(train)
            clim_sets.extend((r, {"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co}) for r in target)
        result_rows.append({**_scores([r for r, _ in model_sets], [p for _, p in model_sets]), "arm": arm, "season": "pooled", "kind": "model"})
        result_rows.append({**_scores([r for r, _ in clim_sets], [p for _, p in clim_sets]), "arm": arm, "season": "pooled", "kind": "climatology"})
    result = {"protocol": {"league": "LV-Virsliga", "dev_seasons_loaded": list(DEV_LOADED), "training_seed": "2021", "scored_seasons": list(DEV_SEASONS), "scored_n": 720, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"}, "rows": result_rows}
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "fitted_params.json").write_text(json.dumps(fit_params, indent=2) + "\n")
    with open(OUT / "predictions_dev.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["match_id", "season", "date", "home", "away", "arm", "p_home", "p_draw", "p_away", "p_over25", "actual_home_goals", "actual_away_goals"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm, target, probs, _, _ in prediction_sets:
            for r, p in zip(target, probs):
                w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"], "arm": arm, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over25": p["over25"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
    _print_table(result)
    return result


def _diff_se(y, p):
    e = [a - b for a, b in zip(y, p)]
    d = sum(e) / len(e)
    return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** 0.5 / math.sqrt(len(e))


def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs)
    dh, seh = _diff_se([int(r["yh"] > r["ya"]) for r in rows], [p["ph"] for p in probs])
    do, seo = _diff_se([int(r["yh"] + r["ya"] > 2.5) for r in rows], [p["over25"] for p in probs])
    return {**scored, "calibration": {"home_win_diff": dh, "home_win_se": seh, "over25_diff": do, "over25_se": seo}}


def virgin(requested_arms, predict_arm=False):
    rows = load(DATA, {"2021", "2022", "2023", "2024", "2025", "2026"})
    target = [r for r in rows if r["season"] == "2026"]
    assert len(target) == 179
    cutoff = min(r["date"] for r in target)
    train = [r for r in rows if r["date"] < cutoff]
    out = {"protocol": {"league": "LV-Virsliga", "virgin_season": "2026", "n": len(target), "arms_requested": requested_arms, "fit_cutoff": cutoff.isoformat()}, "arms": {}, "baselines": {}}
    predsets = {}
    for arm in requested_arms:
        model, counts, fit_rows = _fit_predict(train, target, arm)
        probs = _predict(model, counts, target, arm)
        predsets[arm] = (model, counts, probs, fit_rows)
        out["arms"][arm] = _virgin_metrics(target, probs)
    cp, co = _clim([r for r in rows if r["season"] in DEV_LOADED])
    out["baselines"]["climatology"] = _virgin_metrics(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target])
    if predict_arm:
        model, counts, probs, fit_rows = predsets[predict_arm]
        path = OUT.parents[1] / "predictions" / "g_lv_virgin_predictions.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            fields = ["match_id", "date", "home", "away", "arm", "p_home", "p_draw", "p_away", "p_over25", "actual_home_goals", "actual_away_goals"]
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r, p in zip(target, probs):
                w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"], "arm": predict_arm, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over25": p["over25"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
        out["shipped_arm"] = predict_arm
        (OUT / "fitted_params_virgin.json").write_text(json.dumps({"arm": predict_arm, "training_rows": len(fit_rows), "a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "match_counts": dict(counts), "halves_constant": 0.4569}, indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


def _print_table(result):
    print("arm season kind n ll_1x2 rps oull_2_5")
    for r in result["rows"]:
        print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
