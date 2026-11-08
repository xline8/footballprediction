"""Data loading, walk-forward evaluation, and dev outputs."""
import csv, json, math
from collections import Counter
from datetime import date
from pathlib import Path
from dc import DC
from arms import x2_multipliers, adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
SE = ROOT / "data" / "is_matches.csv"
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
    mult = x2_multipliers([r for r in train if r["date"] < cutoff], target) if arm == "x2" else {}
    return model, movers, mult, match_counts([r for r in train if r["date"] < cutoff])


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
    rows = load(SE, {"2021", "2022", "2023", "2024", "2025"})
    result = []
    for arm in ("gate_zero", "shrink", "x2"):
        all_rows = []
        all_clim = []
        for season in ("2022", "2023", "2024", "2025"):
            target = [r for r in rows if r["season"] == season]
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, mult, counts = _fit_predict(train, target, arm)
            # SHRINK uses only matches already played in the target season;
            # this is the preregistered early-season-history arm, not a
            # lifetime-history rescaling of the fitted model.
            probs = [model.probs(*adjusted_lambdas(
                model, r["hi"], r["ai"], arm, movers, mult,
                match_counts([q for q in target if q["date"] < r["date"]])
                if arm in ("shrink", "x2") else counts)) for r in target]
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met); all_rows += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met); all_clim += list(zip(target, cprobs))
        met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        # Pooled climatology = pooled score of the per-season (expanding,
        # prior-seasons-only) climatology predictions, per the prereg.
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    gate_lambdas = {}
    for arm in ("gate_zero", "shrink", "x2"):
        gate_lambdas[arm] = {"differ_from_gate_zero": 0, "n": 0}
    x2_transitions = {}
    for season in ("2022", "2023", "2024", "2025"):
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        models = {}
        for arm in ("gate_zero", "shrink", "x2"):
            model, movers, mult, counts = _fit_predict(train, target, arm)
            models[arm] = [adjusted_lambdas(
                model, r["hi"], r["ai"], arm, movers, mult,
                match_counts([q for q in target if q["date"] < r["date"]])
                if arm in ("shrink", "x2") else counts) for r in target]
            if arm == "x2":
                x2_transitions[season] = {str(team): {"g": v["g"], "c": v["c"]} for team, v in sorted(mult.items())}
        for arm in ("gate_zero", "shrink", "x2"):
            gate_lambdas[arm]["n"] += len(target)
            if arm != "gate_zero":
                gate_lambdas[arm]["differ_from_gate_zero"] += sum(a != b for a, b in zip(models[arm], models["gate_zero"]))
    _write_dev(result)
    print(json.dumps({"lambda_differences_vs_gate_zero": gate_lambdas,
                      "x2_entrant_transitions": x2_transitions}, indent=2))
    _print_table(result, "dev")
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result)


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for a, r in data.items(): print(f'{a} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f} {r["climatology"]["ll_1x2"]:.6f} {r["calibration"]["home_win_diff"]:.6f} {r["calibration"]["over25_diff"]:.6f}')
