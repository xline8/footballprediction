"""G-RU2 development and coordinator-controlled virgin evaluation."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "ru2_matches.csv"
OUT = Path(__file__).resolve().parent
SEED = "2021/2022"
DEV_FOLDS = ("2022/2023", "2023", "2023/2024", "2024", "2024/2025", "2025/2026")
EXPECTED = {SEED: 1126, "2022/2023": 1115, "2023": 512, "2023/2024": 362,
            "2024": 904, "2024/2025": 235, "2025/2026": 156}
VIRGIN_SEASONS = ("2026", "2026/2027")


def load(path, allowed):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] == "2025":
                continue
            if r["season"] not in allowed:
                continue
            if r["finished"] != "1" or r["awarded"] != "0":
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    assert all(r["season"] != "2025" for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    fit_rows = [r for r in train if r["date"] < cutoff]
    assert all(r["season"] != "2025" for r in fit_rows)
    model = DC().fit(fit_rows, cutoff)
    return model, set(), {}, match_counts(fit_rows)


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
    n = len(train); hw = sum(r["yh"] > r["ya"] for r in train) / n; dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _folds(rows):
    for season in DEV_FOLDS:
        target = [r for r in rows if r["season"] == season]
        assert len(target) == EXPECTED[season], (season, len(target), EXPECTED[season])
        cutoff = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < cutoff]
        assert all(r["season"] != "2025" for r in train)
        yield season, train, target


def _dev_gate(result, arm):
    rows = result["rows"]
    model = next(r for r in rows if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "model")
    clim = next(r for r in rows if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "climatology")
    return {"ll_1x2": model["ll_1x2"] < clim["ll_1x2"], "rps": model["rps"] < clim["rps"],
            "oull_2_5": model["oull_2_5"] < clim["oull_2_5"]}


def run_dev():
    rows = load(DATA, {SEED, *DEV_FOLDS})
    assert len([r for r in rows if r["season"] == SEED]) == EXPECTED[SEED]
    result = []
    prediction_rows = []
    for arm in ("gate_zero", "shrink"):
        all_rows = []; all_clim = []
        for season, train, target in _folds(rows):
            model, movers, mult, counts = _fit_predict(train, target, arm)
            probs = []
            lambdas = []
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts)
                lambdas.append((lh, la)); probs.append(model.probs(lh, la))
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met)
            all_rows += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met)
            all_clim += list(zip(target, cprobs))
            for r, p, (lh, la) in zip(target, probs, lambdas):
                prediction_rows.append(_prediction(r, arm, p, lh, la, cp, co))
        met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    result = {"protocol": {"league": "RU-SecondLeague", "dev_seasons_loaded": [SEED, *DEV_FOLDS],
                            "scored_n": 3284, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted",
                            "eligibility": "finished=1 AND awarded=0 AND season != '2025'"}, "rows": result,
              "dev_gate": {arm: _dev_gate({"rows": result}, arm) for arm in ("gate_zero", "shrink")}}
    _write_dev(result, prediction_rows)
    _print_table(result, "dev")
    return result


def _prediction(r, arm, p, lh, la, cp, co):
    return {"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"],
            "actual_home_goals": r["yh"], "actual_away_goals": r["ya"], "actual_target": r["yh"] + r["ya"], "arm": arm,
            "lambda_home": lh, "lambda_away": la, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"],
            "baseline_p_home": cp[0], "baseline_p_draw": cp[1], "baseline_p_away": cp[2], "baseline_p_over_2_5": co}


def _write_dev(result, prediction_rows):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result["rows"])
    fields = ["match_id", "season", "date", "home", "away", "actual_home_goals", "actual_away_goals", "actual_target", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over_2_5", "baseline_p_home", "baseline_p_draw", "baseline_p_away", "baseline_p_over_2_5"]
    with open(OUT / "predictions_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(prediction_rows)


def _print_table(data, label):
    print(label)
    print("arm season kind n ll_1x2 rps oull_2_5")
    for r in data["rows"]:
        print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')


def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs)
    hw = [int(r["yh"] > r["ya"]) for r in rows]; ov = [int(r["yh"] + r["ya"] > 2.5) for r in rows]
    def diff_se(y, p):
        e = [a - b for a, b in zip(y, p)]; d = sum(e) / len(e)
        return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** 0.5 / (len(e) ** 0.5)
    dh, seh = diff_se(hw, [p["ph"] for p in probs]); do, seo = diff_se(ov, [p["over25"] for p in probs])
    return {**scored, "calibration": {"home_win_diff": dh, "home_win_se": seh, "over25_diff": do, "over25_se": seo}}


def virgin(requested_arms=None):
    dev = json.loads((OUT / "results_dev.json").read_text())
    if not all(_dev_gate(dev, "gate_zero").values()):
        raise RuntimeError("Gate Zero failed the dev gate; virgin evaluation is prohibited")
    dev_pass = {a for a in ("gate_zero", "shrink") if all(_dev_gate(dev, a).values())}
    rows = load(DATA, {SEED, *DEV_FOLDS, *VIRGIN_SEASONS})
    target = [r for r in rows if r["season"] in VIRGIN_SEASONS]
    assert len(target) == 888
    cutoff = date(2026, 3, 28)
    train = [r for r in rows if r["date"] < cutoff and r["season"] not in VIRGIN_SEASONS]
    passing = [a for a in ("gate_zero", "shrink") if a in dev_pass and (requested_arms is None or a in requested_arms)]
    out = {"protocol": {"league": "RU-SecondLeague", "virgin_seasons": list(VIRGIN_SEASONS), "n": len(target), "scored_arms": passing, "training_rows": len(train)}, "arms": {}, "baselines": {}}
    predsets = {}
    for arm in passing:
        model, movers, mult, counts = _fit_predict(train, target, arm)
        pp = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts); p = model.probs(lh, la); p.update(_lambdas= (lh, la)); pp.append(p)
        predsets[arm] = (pp, model); out["arms"][arm] = _virgin_metrics(target, pp)
    cp, co = _clim(train); cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    out["baselines"]["climatology"] = _virgin_metrics(target, cprobs)
    gzll = out["arms"].get("gate_zero", {"ll_1x2": float("inf")})["ll_1x2"]
    climll = out["baselines"]["climatology"]["ll_1x2"]; eligible = []
    for arm in passing:
        v = out["arms"][arm]; cal = v["calibration"]
        sign = arm == "gate_zero" or sum(next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_1x2"] <= next(x for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_1x2"] for s in DEV_FOLDS) >= 3
        ll_pass = v["ll_1x2"] <= gzll and v["ll_1x2"] <= climll
        cal_pass = abs(cal["home_win_diff"]) <= .01 + cal["home_win_se"] and abs(cal["over25_diff"]) <= .01 + cal["over25_se"]
        out["arms"][arm]["eligibility"] = {"ll": ll_pass, "calibration": cal_pass, "dev_fold_sign": sign, "provisional_home_win": abs(cal["home_win_diff"]) > .01 and abs(cal["home_win_diff"]) <= .01 + cal["home_win_se"], "provisional_over25": abs(cal["over25_diff"]) > .01 and abs(cal["over25_diff"]) <= .01 + cal["over25_se"]}
        if ll_pass and cal_pass and sign: eligible.append(arm)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], ("gate_zero", "shrink").index(a))) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        pp, model = predsets[chosen]; ppath = OUT.parents[1] / "predictions" / "g_ru2_virgin_predictions.csv"; ppath.parent.mkdir(exist_ok=True)
        with ppath.open("w", newline="", encoding="utf-8") as f:
            fields = ["match_id", "date", "home_team", "away_team", "arm", "p_home", "p_draw", "p_away", "p_over_2_5", "actual_home_goals", "actual_away_goals"]; w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r, p in zip(target, pp): w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "arm": chosen, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
        (OUT / "fitted_params_virgin.json").write_text(json.dumps({"arm": chosen, "training_rows": len(train), "home_advantage": model.h, "rho": model.rho, "mu": model.mu, "attack": dict(model.a), "defence": dict(model.d)}, indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    return out
