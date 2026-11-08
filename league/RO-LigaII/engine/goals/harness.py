"""Data loading, walk-forward evaluation, virgin metrics, and outputs."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import mover_ids, adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
RO = ROOT / "data" / "rl2_matches.csv"
OUT = Path(__file__).resolve().parent
HALF_1 = 0.457419
HALF_2 = 0.542581
DEV_SEASONS = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}


def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            if r["phase"] == "relegation_playoff":
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    fit = [r for r in train if r["date"] < cutoff]
    return DC().fit(fit, cutoff), set(), match_counts(fit)


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


def run_dev():
    rows = load(RO, DEV_SEASONS)
    assert {r["season"] for r in rows} <= DEV_SEASONS
    result = []
    for arm in ("gate_zero", "shrink"):
        all_rows = []; all_clim = []
        for season in ("2022/2023", "2023/2024", "2024/2025"):
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, counts = _fit_predict(train, target, arm)
            probs = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts)) for r in target]
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met); all_rows += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met); all_clim += list(zip(target, cprobs))
        met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    _write_dev(result); _print_table(result, "dev")
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result)


def virgin_metrics(arms=("gate_zero", "shrink"), write_predictions_arm=None):
    rows = load(RO, {"2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"})
    train = [r for r in rows if r["season"] != "2025/2026"]; target = [r for r in rows if r["season"] == "2025/2026"]
    cp, co = _clim(train); result = {}
    for arm in arms:
        model, movers, counts = _fit_predict(train, target, arm); preds = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts); p = model.probs(lh, la); p.update({"lh": lh, "la": la}); preds.append(p)
        met = _scores(target, preds)
        cal_hw = sum(p["ph"] for p in preds) / len(preds) - sum(r["yh"] > r["ya"] for r in target) / len(target)
        cal_ou = sum(p["over25"] for p in preds) / len(preds) - sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)
        def se(vals):
            m = sum(vals) / len(vals); return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 / math.sqrt(len(vals))
        met.update({"climatology": _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]),
                    "calibration": {"home_win_diff": cal_hw, "home_win_se": se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)]), "over25_diff": cal_ou, "over25_se": se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)])},
                    "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "movers": sorted(movers)}})
        result[arm] = met
        if arm == write_predictions_arm:
            _write_predictions(target, preds, arm, model)
            (OUT / "fitted_params_virgin.json").write_text(json.dumps({"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "movers": sorted(movers), "match_counts": counts}, indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n"); _print_table(result, "virgin"); return result


def _write_predictions(rows, preds, arm, model):
    dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a", "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "lam_h_1h", "lam_a_1h", "p_over_1h_0_5", "p_over_1h_1_5", "p_over_1h_2_5", "lam_h_2h", "lam_a_2h", "p_over_2h_1_5", "p_over_2h_2_5", "p_over_2h_3_5", "arm"]
    out = []
    for r, p in zip(rows, preds):
        q1 = model.probs(p["lh"] * HALF_1, p["la"] * HALF_1); q2 = model.probs(p["lh"] * HALF_2, p["la"] * HALF_2)
        out.append({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "home_goals": r["yh"], "away_goals": r["ya"], "lam_h": p["lh"], "lam_a": p["la"], "rho": model.rho, "ph": p["ph"], "pd": p["pd"], "pa": p["pa"], "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"], "p_btts": p["btts"], "lam_h_1h": p["lh"] * HALF_1, "lam_a_1h": p["la"] * HALF_1, "p_over_1h_0_5": model.over(p["lh"] * HALF_1, p["la"] * HALF_1, .5), "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"], "lam_h_2h": p["lh"] * HALF_2, "lam_a_2h": p["la"] * HALF_2, "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"], "p_over_2h_3_5": q2["over35"], "arm": arm})
    with open(dest / "g_rl2_virgin_predictions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for a, r in data.items(): print(f'{a} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f} {r["climatology"]["ll_1x2"]:.6f} {r["calibration"]["home_win_diff"]:.6f} {r["calibration"]["over25_diff"]:.6f}')
