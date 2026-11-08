"""G-PL development-only walk-forward evaluation."""
import csv, json, math
from collections import Counter
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pl_matches.csv"
OUT = Path(__file__).resolve().parent


def _num(x):
    return None if x in (None, "") else float(x)


def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed: continue
            rows.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": _num(r["expected_goals_home"]), "xga": _num(r["expected_goals_away"]),
                         "oph": _num(r["expected_goals_open_play_home"]), "opa": _num(r["expected_goals_open_play_away"]),
                         "sph": _num(r["expected_goals_set_play_home"]), "spa": _num(r["expected_goals_set_play_away"])})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    model = DC().fit([r for r in train if r["date"] < cutoff], cutoff)
    movers = set()
    return model, set(), {}, match_counts([r for r in train if r["date"] < cutoff])


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
    rows = load(DATA, {"2021/2022", "2022/2023", "2023/2024", "2024/2025"})
    result = []
    for arm in ("gate_zero", "shrink"):
        all_rows = []
        all_clim = []
        for season in ("2022/2023", "2023/2024", "2024/2025"):
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, mult, counts = _fit_predict(train, target, arm)
            probs = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts)) for r in target]
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met); all_rows += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met); all_clim += list(zip(target, cprobs))
        met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        # Pooled climatology = pooled score of the per-season (expanding,
        # prior-seasons-only) climatology predictions, per the prereg.
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    result = {"protocol": {"league": "PL-Ekstraklasa", "dev_seasons_loaded": ["2021/2022", "2022/2023", "2023/2024", "2024/2025"], "scored_n": 918, "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"}, "rows": result}
    _write_dev(result)
    _print_table(result, "dev")
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result["rows"])


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data["rows"]: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for a, r in data.items(): print(f'{a} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f} {r["climatology"]["ll_1x2"]:.6f} {r["calibration"]["home_win_diff"]:.6f} {r["calibration"]["over25_diff"]:.6f}')


def _virgin_metrics(rows, probs):
    scored = _scores(rows, probs[0])
    hw = [int(r["yh"] > r["ya"]) for r in rows]
    ov = [int(r["yh"] + r["ya"] > 2.5) for r in rows]
    hp = [p["ph"] for p in probs[0]]; op = [p["over25"] for p in probs[0]]
    def diff_se(y, p):
        e = [a-b for a,b in zip(y,p)]; d = sum(e)/len(e)
        return d, (sum((x-d)**2 for x in e)/(len(e)-1))**0.5/(len(e)**0.5)
    dh, seh = diff_se(hw, hp); do, seo = diff_se(ov, op)
    return {**scored, "calibration": {"home_win_diff": dh, "home_win_se": seh,
             "over25_diff": do, "over25_se": seo}}


def virgin(requested_arms=None):
    dev = json.loads((OUT / "results_dev.json").read_text())
    rows = load(DATA, {"2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"})
    target = [r for r in rows if r["season"] == "2025/2026"]
    train = [r for r in rows if r["season"] != "2025/2026"]
    passing = []
    for arm in ("gate_zero", "shrink"):
        pool = next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        clim = next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "climatology")
        if pool["ll_1x2"] < clim["ll_1x2"] and pool["rps"] < clim["rps"] and pool["oull_2_5"] < clim["oull_2_5"] and (requested_arms is None or arm in requested_arms):
            passing.append(arm)
    out = {"protocol": {"league": "PL-Ekstraklasa", "virgin_season": "2025/2026", "n": len(target), "scored_arms": passing, "dev_rows_loaded": len(rows)}, "arms": {}, "baselines": {}}
    predsets = {}
    for arm in passing:
        model, movers, mult, counts = _fit_predict(train, target, arm)
        pp = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts)) for r in target]
        predsets[arm] = (pp, model)
        out["arms"][arm] = _virgin_metrics(target, (pp, target))
    cp, co = _clim(train)
    cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
    out["baselines"]["climatology"] = _virgin_metrics(target, (cprobs, target))
    eligible = []
    best_base = out["baselines"]["climatology"]["ll_1x2"]
    for arm in passing:
        v = out["arms"][arm]; sign = arm == "gate_zero" or sum(next(x for x in dev["rows"] if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_1x2"] <= next(x for x in dev["rows"] if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_1x2"] for s in ("2022/2023", "2023/2024", "2024/2025")) >= 2
        cal = v["calibration"]
        if v["ll_1x2"] <= best_base and abs(cal["home_win_diff"]) <= .01 + cal["home_win_se"] and abs(cal["over25_diff"]) <= .01 + cal["over25_se"] and sign:
            eligible.append(arm)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], ("gate_zero", "shrink").index(a))) if eligible else None
    out["shipped_arm"] = chosen
    if chosen:
        pp, model = predsets[chosen]
        ppath = OUT.parents[1] / "predictions" / "g_pl_virgin_predictions.csv"; ppath.parent.mkdir(exist_ok=True)
        with ppath.open("w", newline="", encoding="utf-8") as f:
            fields = ["match_id", "date", "home_team", "away_team", "arm", "p_home", "p_draw", "p_away", "p_over_2_5", "actual_home_goals", "actual_away_goals"]
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r,p in zip(target,pp):
                w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "arm": chosen, "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over_2_5": p["over25"], "actual_home_goals": r["yh"], "actual_away_goals": r["ya"]})
        (OUT / "fitted_params_virgin.json").write_text(json.dumps({"arm": chosen, "training_rows": len(train)}, indent=2) + "\n")
    (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    return out
