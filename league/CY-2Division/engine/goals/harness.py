"""G-CY2 development walk-forward and one-shot virgin evaluation."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts, mover_ids

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "cy2_matches.csv"
CY1 = ROOT / "data" / "cy1_team_seasons.json"
OUT = Path(__file__).resolve().parent
SEED = "2021/2022"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
ARMS = ("gate_zero", "x2", "shrink")
TIE_ORDER = {a: i for i, a in enumerate(ARMS)}

def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed: continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]), "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))

def _fit_predict(train, target, arm, cy2_rows, cy1):
    cutoff = min(r["date"] for r in target)
    fit_rows = [r for r in train if r["date"] < cutoff]
    model = DC().fit(fit_rows, cutoff)
    movers = mover_ids(target[0]["season"], cy2_rows, cy1) if arm == "x2" else set()
    return model, movers, match_counts(fit_rows)

def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1)); pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12)); rps += .5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5; oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows); return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}

def _clim(train):
    n = len(train); hw = sum(r["yh"] > r["ya"] for r in train) / n; dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n

def _probs(model, rows, arm, movers, counts):
    return [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts)) for r in rows]

def run_dev():
    rows = load(DATA, {SEED, *DEV_SEASONS}); cy1 = json.loads(CY1.read_text()); result = []
    assert not any(r["season"] in {"2025/2026", "2026/2027"} for r in rows)
    for arm in ARMS:
        all_model = []; all_clim = []
        for season in DEV_SEASONS:
            target = [r for r in rows if r["season"] == season]; train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, counts = _fit_predict(train, target, arm, rows, cy1); probs = _probs(model, target, arm, movers, counts)
            m = _scores(target, probs); m.update({"arm": arm, "season": season, "kind": "model"}); result.append(m); all_model += list(zip(target, probs))
            cp, co = _clim(train); cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            m = _scores(target, cprobs); m.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(m); all_clim += list(zip(target, cprobs))
        m = _scores([x[0] for x in all_model], [x[1] for x in all_model]); m.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(m)
        m = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); m.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(m)
    scored_n = next(r["n"] for r in result if r["arm"] == "gate_zero" and r["season"] == "pooled" and r["kind"] == "model")
    assert scored_n == 682, scored_n
    out = {"protocol": {"league": "CY-2Division", "dev_seasons_loaded": [SEED, *DEV_SEASONS], "scored_n": scored_n, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"}, "rows": result}
    (OUT / "results_dev.json").write_text(json.dumps(out, indent=2) + "\n"); _write_dev_csv(result); _print_table(out, "dev"); return out

def _write_dev_csv(rows):
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in rows)

def _dev_pool(dev, arm, kind="model"):
    return next(r for r in dev["rows"] if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == kind)

def _diff_se(y, p):
    e = [a - b for a, b in zip(y, p)]; d = sum(e) / len(e)
    return d, (sum((x - d) ** 2 for x in e) / (len(e) - 1)) ** .5 / math.sqrt(len(e))

def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs); hw, ov = [int(r["yh"] > r["ya"]) for r in rows], [int(r["yh"] + r["ya"] > 2.5) for r in rows]
    dh, seh = _diff_se(hw, [p["ph"] for p in probs]); do, seo = _diff_se(ov, [p["over25"] for p in probs])
    scored["calibration"] = {"home_win_diff": dh, "home_win_se": seh, "over25_diff": do, "over25_se": seo}; return scored

def _cal_leg(diff, se):
    limit = .01
    return {"difference": diff, "se": se, "status": "PASS" if abs(diff) <= limit else ("PROVISIONAL PASS" if abs(diff) <= limit + se else "FAIL")}

def _write_predictions(rows, preds, arm, model, movers):
    dest = ROOT / "predictions"; dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over_1_5", "p_over_2_5", "p_over_3_5", "p_btts", "p_home_1h", "p_draw_1h", "p_away_1h", "p_over_1_5_1h", "p_over_2_5_1h", "p_home_2h", "p_draw_2h", "p_away_2h", "p_over_2_5_2h", "p_over_3_5_2h", "actual_home_goals", "actual_away_goals"]
    with open(dest / "g_cy2_virgin_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r, p in zip(rows, preds):
            q1 = model.probs(p["lh"] * .4351, p["la"] * .4351); q2 = model.probs(p["lh"] * .5649, p["la"] * .5649)
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "arm": arm, "lambda_home": p["lh"], "lambda_away": p["la"], "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_1_5": p["over15"], "p_over_2_5": p["over25"], "p_over_3_5": p["over35"], "p_btts": p["btts"], "p_home_1h": q1["ph"], "p_draw_1h": q1["pd"], "p_away_1h": q1["pa"], "p_over_1_5_1h": q1["over15"], "p_over_2_5_1h": q1["over25"], "p_home_2h": q2["ph"], "p_draw_2h": q2["pd"], "p_away_2h": q2["pa"], "p_over_2_5_2h": q2["over25"], "p_over_3_5_2h": q2["over35"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
    params = {"a": {str(k): v for k, v in model.a.items()}, "d": {str(k): v for k, v in model.d.items()}, "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "movers": sorted(movers)}
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n")

def virgin(requested_arms=None):
    dev = json.loads((OUT / "results_dev.json").read_text()); passing = []
    for arm in ARMS:
        p, c = _dev_pool(dev, arm), _dev_pool(dev, arm, "climatology")
        if p["ll_1x2"] < c["ll_1x2"] and p["rps"] < c["rps"] and p["oull_2_5"] < c["oull_2_5"] and (requested_arms is None or arm in requested_arms): passing.append(arm)
    if not passing or "gate_zero" not in passing:
        out = {"virgin_read": False, "protocol": {"league": "CY-2Division", "virgin_season": "2025/2026", "virgin_read": False, "scored_arms": passing}, "arms": {}, "baselines": {}, "eligibility": {}, "shipped_arm": None}
        (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); print("virgin_read=false; not reading 2025/2026"); return out
    cy1 = json.loads(CY1.read_text()); rows = load(DATA, {SEED, *DEV_SEASONS, "2025/2026"}); target = [r for r in rows if r["season"] == "2025/2026"]; train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
    out = {"virgin_read": True, "protocol": {"league": "CY-2Division", "virgin_season": "2025/2026", "virgin_read": True, "n": len(target), "scored_arms": passing}, "arms": {}, "baselines": {}, "eligibility": {}, "shipped_arm": None}; predsets = {}
    cp, co = _clim(train); base = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]; out["baselines"]["climatology"] = _virgin_metrics(target, base)
    for arm in passing:
        model, movers, counts = _fit_predict(train, target, arm, rows, cy1); pp = _probs(model, target, arm, movers, counts); pp = [dict(p, lh=adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts)[0], la=adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts)[1]) for r, p in zip(target, pp)]
        predsets[arm] = (pp, model, movers); out["arms"][arm] = _virgin_metrics(target, pp)
    for arm in passing:
        v = out["arms"][arm]; gz = out["arms"]["gate_zero"]; ll_leg = v["ll_1x2"] <= gz["ll_1x2"] and v["ll_1x2"] <= out["baselines"]["climatology"]["ll_1x2"]
        calh, calo = _cal_leg(v["calibration"]["home_win_diff"], v["calibration"]["home_win_se"]), _cal_leg(v["calibration"]["over25_diff"], v["calibration"]["over25_se"])
        sign = arm == "gate_zero" or sum(next(r for r in dev["rows"] if r["arm"] == arm and r["season"] == s and r["kind"] == "model")["ll_1x2"] <= next(r for r in dev["rows"] if r["arm"] == "gate_zero" and r["season"] == s and r["kind"] == "model")["ll_1x2"] for s in DEV_SEASONS) >= 2
        out["eligibility"][arm] = {"ll_leg": ll_leg, "calibration_home": calh, "calibration_over25": calo, "sign_check": sign, "passes": ll_leg and calh["status"] != "FAIL" and calo["status"] != "FAIL" and sign}
    eligible = [a for a in passing if out["eligibility"][a]["passes"]]; chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], TIE_ORDER[a])) if eligible else None; out["shipped_arm"] = chosen
    if chosen:
        pp, model, movers = predsets[chosen]; _write_predictions(target, pp, chosen, model, movers); out["arms"][chosen]["movers"] = sorted(movers)
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); _print_table(out, "virgin"); return out

def _print_table(data, label):
    print(label); print("arm season kind n ll_1x2 rps oull_2_5")
    for r in data["rows"] if label == "dev" else []: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
