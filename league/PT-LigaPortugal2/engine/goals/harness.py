"""G-PT2 walk-forward evaluation and preregistered output writer."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pt2_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
PRE_VIRGIN = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
VIRGIN = "2025/2026"


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            # This assertion makes the reserved confirmatory season unreachable.
            assert r["season"] != "2026/2027", "reserved 2026/2027 data must never be read"
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_id"]), "ai": int(r["away_id"]), "home": r["home_team"], "away": r["away_team"],
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
    model = DC().fit(prior, cutoff)
    return model, match_counts(prior)


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
    assert set(r["season"] for r in rows).issubset(set(PRE_VIRGIN))
    result = []
    for arm in ("gate_zero", "shrink"):
        pooled_rows, pooled_probs = [], []
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, counts = _fit_predict(train, target, arm)
            probs = _predict(target, model, counts, arm)
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met)
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met)
            pooled_rows.extend(target); pooled_probs.extend(probs)
        met = _scores(pooled_rows, pooled_probs); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        # The pooled dev baseline is the target-season prior-season climatology for each block.
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


def virgin_metrics(arms, write_predictions_arm=None):
    rows = load(allowed=PRE_VIRGIN + (VIRGIN,))
    train = [r for r in rows if r["season"] in PRE_VIRGIN]
    target = [r for r in rows if r["season"] == VIRGIN]
    assert all(r["season"] != "2026/2027" for r in rows)
    cp, co = _clim(train); result = {}
    for arm in arms:
        model, counts = _fit_predict(train, target, arm)
        preds = _predict(target, model, counts, arm)
        met = _scores(target, preds)
        cal_hw = sum(p["ph"] for p in preds) / len(preds) - sum(r["yh"] > r["ya"] for r in target) / len(target)
        cal_ou = sum(p["over25"] for p in preds) / len(preds) - sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)
        def se(vals):
            m = sum(vals) / len(vals)
            return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 / math.sqrt(len(vals))
        met.update({"climatology": _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]),
                    "calibration": {"home_win_diff": cal_hw, "home_win_se": se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)]),
                                    "over25_diff": cal_ou, "over25_se": se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)])},
                    "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "match_counts": dict(counts)}})
        result[arm] = met
        if arm == write_predictions_arm:
            _write_predictions(target, preds, arm)
            (OUT / "fitted_params_virgin.json").write_text(json.dumps(met["params"], indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def _write_predictions(rows, preds, arm):
    dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home", "away", "exp_home_goals", "exp_away_goals", "p_home", "p_draw", "p_away", "p_over25", "p_btts"]
    with open(dest / "g_pt2_virgin_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p in zip(rows, preds):
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home": r["home"], "away": r["away"],
                        "exp_home_goals": p["lh"], "exp_away_goals": p["la"], "p_home": p["ph"], "p_draw": p["pd"],
                        "p_away": p["pa"], "p_over25": p["over25"], "p_btts": p["btts"]})
