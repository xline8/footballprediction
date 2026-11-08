"""DEV-only walk-forward harness for G-BEB."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, match_counts, mover_ids
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
BE = ROOT / "data" / "beb_matches.csv"
PARENT = Path(__file__).resolve().parents[2].parent / "BE-FirstDivisionA" / "data" / "be_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
EVAL_SEASONS = DEV_SEASONS[1:]
FORBIDDEN_SEASONS = {"2025/2026", "2026/2027"}
HALVES_CONSTANT = 0.434014


def load(path, allowed):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in allowed:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert not any(x["season"] in FORBIDDEN_SEASONS for x in rows)
    return sorted(rows, key=lambda x: (x["date"], x["match_id"]))


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = r["yh"] + r["ya"] > 2.5
        oull -= math.log(max(p["over25"] if over else 1.0 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _rates(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1.0 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _baseline_probs(train, kind):
    one_x_two, over = _rates(train)
    if kind == "climatology":
        return {"ph": one_x_two[0], "pd": one_x_two[1], "pa": one_x_two[2], "over25": over}
    if kind == "base_rate":
        return {"ph": one_x_two[0], "pd": one_x_two[1], "pa": one_x_two[2], "over25": over}
    raise ValueError(kind)


def _predict(train, target, all_b_rows, parent, arm):
    cutoff = min(x["date"] for x in target)
    fit = [x for x in train if x["date"] < cutoff]
    model = DC().fit(fit, cutoff)
    movers = mover_ids(parent, all_b_rows, target[0]["season"])
    counts = match_counts(fit)
    predictions = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        predictions.append(p)
    return model, movers, predictions


def _prediction_rows(target, arm, predictions):
    for r, p in zip(target, predictions):
        yield {"match_id": r["match_id"], "season": r["season"], "arm": arm,
               "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"],
               "p_over25": p["over25"], "lambda_home": p["lh"], "lambda_away": p["la"]}


def run_dev():
    rows = load(BE, set(DEV_SEASONS))
    parent = load(PARENT, set(DEV_SEASONS))
    assert {x["season"] for x in rows} <= set(DEV_SEASONS)
    metrics = []
    mover_sets = {}
    all_predictions = []
    for season in EVAL_SEASONS:
        target = [x for x in rows if x["season"] == season]
        train = [x for x in rows if x["date"] < min(t["date"] for t in target)]
        movers = mover_ids(parent, rows, season)
        mover_sets[season] = sorted(movers)
        baselines = {}
        for kind in ("climatology", "base_rate"):
            probs = [_baseline_probs(train, kind)] * len(target)
            score = _scores(target, probs)
            score.update({"arm": kind, "season": season, "kind": kind})
            metrics.append(score)
            baselines[kind] = probs[0]
        for arm in ("gate_zero", "shrink", "x2"):
            model, _, probs = _predict(train, target, rows, parent, arm)
            score = _scores(target, probs)
            score.update({"arm": arm, "season": season, "kind": "model", "movers": sorted(movers)})
            metrics.append(score)
            all_predictions.extend(_prediction_rows(target, arm, probs))
    for arm in ("gate_zero", "shrink", "x2"):
        target_rows = [x for x in rows if x["season"] in EVAL_SEASONS]
        model_scores = [x for x in metrics if x["arm"] == arm and x["kind"] == "model"]
        pooled = _scores(target_rows, [
            {"ph": p["p_home"], "pd": p["p_draw"], "pa": p["p_away"], "over25": p["p_over25"]}
            for p in all_predictions if p["arm"] == arm])
        pooled.update({"arm": arm, "season": "pooled", "kind": "model"})
        metrics.append(pooled)
    for kind in ("climatology", "base_rate"):
        pairs = []
        for season in EVAL_SEASONS:
            target = [x for x in rows if x["season"] == season]
            train = [x for x in rows if x["date"] < min(t["date"] for t in target)]
            pairs.append((target, [_baseline_probs(train, kind)] * len(target)))
        flat_rows = [r for target, _ in pairs for r in target]
        flat_probs = [p for _, probs in pairs for p in probs]
        score = _scores(flat_rows, flat_probs)
        score.update({"arm": kind, "season": "pooled", "kind": kind})
        metrics.append(score)
    by_key = {(x["arm"], x["season"]): x for x in metrics if x["kind"] == "model"}
    sign_checks = []
    for arm in ("shrink", "x2"):
        for season in EVAL_SEASONS:
            variant = by_key[(arm, season)]["ll_1x2"]
            gz = by_key[("gate_zero", season)]["ll_1x2"]
            sign_checks.append({"arm": arm, "season": season, "arm_ll": variant,
                                "gate_zero_ll": gz, "ll_delta_vs_gate_zero": variant - gz,
                                "pass": variant <= gz})
    dev_gate = {}
    clim = next(x for x in metrics if x["arm"] == "climatology" and x["season"] == "pooled")
    base = next(x for x in metrics if x["arm"] == "base_rate" and x["season"] == "pooled")
    for arm in ("gate_zero", "shrink", "x2"):
        pooled = by_key[(arm, "pooled")]
        checks = [pooled["ll_1x2"] < clim["ll_1x2"], pooled["rps"] < clim["rps"],
                  pooled["oull_2_5"] < base["oull_2_5"]]
        arm_signs = [x for x in sign_checks if x["arm"] == arm]
        dev_gate[arm] = {"legs": {"1x2_ll_beats_climatology": checks[0],
                                   "rps_beats_climatology": checks[1],
                                   "ou2_5_ll_beats_base_rate": checks[2]},
                         "pass": all(checks) and (sum(x["pass"] for x in arm_signs) >= 2 if arm_signs else True)}
    result = {"pooled_n": len([x for x in rows if x["season"] in EVAL_SEASONS]),
              "dev_seasons": list(EVAL_SEASONS), "halves_constant": HALVES_CONSTANT,
              "mover_sets": mover_sets, "metrics": metrics, "sign_checks": sign_checks,
              "dev_gate": dev_gate, "virgin_read": False}
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["match_id", "season", "arm", "p_home", "p_draw", "p_away", "p_over25", "lambda_home", "lambda_away"]
    with open(OUT / "predictions_dev.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(all_predictions)
    _print(result)
    return result


def _print(result):
    print("mover_sets", json.dumps(result["mover_sets"], sort_keys=True))
    print("arm season kind n ll_1x2 rps oull_2_5")
    for x in result["metrics"]:
        print(f"{x['arm']} {x['season']} {x['kind']} {x['n']} {x['ll_1x2']:.6f} {x['rps']:.6f} {x['oull_2_5']:.6f}")
    print("sign_checks", json.dumps(result["sign_checks"], sort_keys=True))
    print("dev_gate", json.dumps(result["dev_gate"], sort_keys=True))


def virgin():
    raise RuntimeError("virgin mode is coordinator-run only and is disabled in this DEV-only phase")
