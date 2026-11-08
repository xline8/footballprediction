"""G-PT3 expanding walk-forward harness and frozen virgin gate."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pt3_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
PRE_VIRGIN = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
VIRGIN = "2025/2026"
RESERVED = "2026/2027"


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            assert r["season"] != RESERVED, "reserved 2026/2027 data must never be read"
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_id"]), "ai": int(r["away_id"]), "home": r["home"], "away": r["away"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
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


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    prior = [r for r in train if r["date"] < cutoff]
    assert prior and max(r["date"] for r in prior) < cutoff
    model = DC().fit(prior, cutoff)
    return model, match_counts(prior), max(r["date"] for r in prior)


def _predict(target, model, counts, arm):
    out = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        out.append(p)
    return out


def run_dev():
    rows = load(allowed=PRE_VIRGIN)
    assert set(r["season"] for r in rows) == set(PRE_VIRGIN)
    result = []
    for arm in ("gate_zero", "shrink"):
        pooled_rows, pooled_probs = [], []
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, counts, max_train_date = _fit_predict(train, target, arm)
            print(f"dev {arm} {season}: max train date {max_train_date}")
            probs = _predict(target, model, counts, arm)
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met)
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met)
            pooled_rows.extend(target); pooled_probs.extend(probs)
        met = _scores(pooled_rows, pooled_probs); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        clim_rows, clim_probs = [], []
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            cp, co = _clim(train)
            clim_rows.extend(target); clim_probs.extend({"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target)
        met = _scores(clim_rows, clim_probs); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    _write_dev(result)
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result)


def dev_passes(result, arm):
    model = next(r for r in result if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "model")
    base = next(r for r in result if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "climatology")
    return model["ll_1x2"] < base["ll_1x2"] and model["rps"] < base["rps"] and model["oull_2_5"] < base["oull_2_5"]


def _se(values):
    m = sum(values) / len(values)
    return (sum((x - m) ** 2 for x in values) / (len(values) - 1)) ** 0.5 / math.sqrt(len(values))


def virgin_metrics(arms, dev_result):
    rows = load(allowed=PRE_VIRGIN + (VIRGIN,))
    train = [r for r in rows if r["season"] in PRE_VIRGIN]
    target = [r for r in rows if r["season"] == VIRGIN]
    assert all(r["season"] != RESERVED for r in rows)
    cp, co = _clim(train)
    clim = _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target])
    result = {"virgin_read": True, "n": len(target), "arms": {}, "winner": None, "verdict": "FAIL"}
    eval_arms = tuple(dict.fromkeys(("gate_zero",) + tuple(arms)))
    for arm in eval_arms:
        model, counts, max_train_date = _fit_predict(train, target, arm)
        assert max_train_date < min(r["date"] for r in target)
        preds = _predict(target, model, counts, arm)
        met = _scores(target, preds)
        actual_hw = sum(r["yh"] > r["ya"] for r in target) / len(target)
        actual_ou = sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)
        cal_hw = sum(p["ph"] for p in preds) / len(preds) - actual_hw
        cal_ou = sum(p["over25"] for p in preds) / len(preds) - actual_ou
        hw_se = _se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)])
        ou_se = _se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)])
        season_sign = {}
        for season in DEV_SEASONS:
            row = next(r for r in dev_result if r["arm"] == arm and r["season"] == season and r["kind"] == "model")
            base = next(r for r in dev_result if r["arm"] == "gate_zero" and r["season"] == season and r["kind"] == "model")
            season_sign[season] = {"arm_ll": row["ll_1x2"], "gate_zero_ll": base["ll_1x2"], "no_worse": row["ll_1x2"] <= base["ll_1x2"]}
        leg1 = met["ll_1x2"] <= result.get("gate_zero_ll", float("inf")) and met["ll_1x2"] <= clim["ll_1x2"]
        if "gate_zero_ll" not in result:
            result["gate_zero_ll"] = met["ll_1x2"]
            leg1 = met["ll_1x2"] <= clim["ll_1x2"]
        clean_hw = abs(cal_hw) <= 0.01; provisional_hw = abs(cal_hw) <= hw_se
        clean_ou = abs(cal_ou) <= 0.01; provisional_ou = abs(cal_ou) <= ou_se
        calibration_pass = (clean_hw or provisional_hw) and (clean_ou or provisional_ou)
        leg3 = arm == "gate_zero" or sum(x["no_worse"] for x in season_sign.values()) >= 2
        result["arms"][arm] = {"metrics": met, "climatology": clim, "max_train_date": max_train_date.isoformat(),
            "calibration": {"home_win_diff": cal_hw, "home_win_se": hw_se, "home_win_clean": clean_hw, "home_win_provisional": provisional_hw,
                             "over25_diff": cal_ou, "over25_se": ou_se, "over25_clean": clean_ou, "over25_provisional": provisional_ou},
            "legs": {"leg_1_1x2_vs_gate_zero_and_climatology": leg1, "leg_2_calibration": calibration_pass, "leg_3_dev_season_sign": leg3},
            "dev_season_sign": season_sign,
            "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "match_counts": dict(counts)}}
    # Correct Gate Zero comparison now that both arms have been evaluated.
    gz = result["arms"]["gate_zero"]["metrics"]["ll_1x2"]
    for arm, info in result["arms"].items():
        info["legs"]["leg_1_1x2_vs_gate_zero_and_climatology"] = info["metrics"]["ll_1x2"] <= gz and info["metrics"]["ll_1x2"] <= clim["ll_1x2"]
    passing = [a for a, x in result["arms"].items() if all(x["legs"].values())]
    if passing:
        winner = min(passing, key=lambda a: (result["arms"][a]["metrics"]["ll_1x2"], 0 if a == "gate_zero" else 1))
        result["winner"] = winner; result["verdict"] = "PASS"
        _write_predictions(target, _predict(target, DC_from_params(result["arms"][winner]["params"]), result["arms"][winner]["params"]["match_counts"], winner))
        (OUT / "fitted_params_virgin.json").write_text(json.dumps(result["arms"][winner]["params"], indent=2) + "\n")
    for info in result["arms"].values(): info.pop("params", None)
    result["climatology"] = clim
    result["gate_zero_virgin_ll"] = gz
    result.pop("gate_zero_ll", None)
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def DC_from_params(params):
    m = DC(); m.a.update(params["a"]); m.d.update(params["d"]); m.h = params["h"]; m.rho = params["rho"]; m.mu = params["mu"]; return m


def _write_predictions(rows, preds):
    dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home", "away", "exp_home_goals", "exp_away_goals", "p_home", "p_draw", "p_away", "p_over25", "p_btts"]
    with open(dest / "g_pt3_virgin_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p in zip(rows, preds):
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"],
                        "exp_home_goals": p["lh"], "exp_away_goals": p["la"], "p_home": p["ph"], "p_draw": p["pd"],
                        "p_away": p["pa"], "p_over25": p["over25"], "p_btts": p["btts"]})
