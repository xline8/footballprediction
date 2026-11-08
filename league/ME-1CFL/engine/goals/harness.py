"""Season-blocked G-ME development walk-forward harness."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import ARMS, adjusted_lambdas, match_counts
from dc import DC

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "me_matches.csv"
SEED = "2021/2022"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")


def start_year(season):
    return int(season.split("/")[0])


def load(path=DATA):
    rows = []
    with open(path, newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            # This filter is intentionally at the load boundary: dev cannot see virgin rows.
            if raw["season"] not in {SEED, *DEV_SEASONS}:
                continue
            rows.append({"match_id": raw["match_id"], "season": raw["season"],
                         "date": date.fromisoformat(raw["date"]),
                         "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]),
                         "home": raw["home_team"], "away": raw["away_team"],
                         "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"])})
    assert not any(r["season"] in {"2025/2026", "2026/2027"} for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _load_seasons(seasons, path=DATA):
    rows = []
    with open(path, newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            if raw["season"] not in seasons:
                continue
            rows.append({"match_id": raw["match_id"], "season": raw["season"],
                         "date": date.fromisoformat(raw["date"]),
                         "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]),
                         "home": raw["home_team"], "away": raw["away_team"],
                         "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"])})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _outcome(game):
    return (1, 0, 0) if game["yh"] > game["ya"] else ((0, 1, 0) if game["yh"] == game["ya"] else (0, 0, 1))


def score(rows, predictions):
    ll = rps = oull = 0.0
    for game, pred in zip(rows, predictions):
        y = _outcome(game); p = [pred["ph"], pred["pd"], pred["pa"]]
        ll -= math.log(max(p[y.index(1)], 1e-15))
        rps += 0.5 * ((p[0] - y[0]) ** 2 + (p[0] + p[1] - y[0] - y[1]) ** 2)
        over = game["yh"] + game["ya"] > 2.5
        oull -= math.log(max(pred["over25"] if over else 1 - pred["over25"], 1e-15))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def climatology(rows):
    if not rows:
        raise ValueError("climatology requires prior seasons")
    n = len(rows)
    home = sum(r["yh"] > r["ya"] for r in rows) / n
    draw = sum(r["yh"] == r["ya"] for r in rows) / n
    return {"outcome": [home, draw, 1.0 - home - draw],
            "over25": sum(r["yh"] + r["ya"] > 2.5 for r in rows) / n}


def _predictions(model, target, arm, counts):
    result = []
    for game in target:
        lh, la = adjusted_lambdas(model, game["hi"], game["ai"], arm, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        result.append(p)
    return result


def _direct_climatology(rows, season):
    # Deliberately independent from climatology(): direct CSV aggregation for the audit check.
    prior = [r for r in rows if start_year(r["season"]) < start_year(season)]
    n = len(prior)
    hw = sum(r["yh"] > r["ya"] for r in prior)
    dr = sum(r["yh"] == r["ya"] for r in prior)
    ov = sum(r["yh"] + r["ya"] > 2.5 for r in prior)
    return {"outcome": [hw / n, dr / n, 1.0 - hw / n - dr / n], "over25": ov / n}


def run_dev():
    rows = load()
    assert not any(r["season"] in {"2025/2026", "2026/2027"} for r in rows)
    predictions_by_arm = {arm: [] for arm in ARMS}
    scored_rows = []
    tables = []
    fit_trace = []
    season_payload = {}
    for season in DEV_SEASONS:
        target = [r for r in rows if r["season"] == season]
        first_date = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < first_date]
        assert not any(r["season"] == season or r["date"] >= first_date for r in train)
        prior = [r for r in rows if start_year(r["season"]) < start_year(season)]
        clim = climatology(prior)
        if season == "2024/2025":
            direct = _direct_climatology(rows, season)
            assert direct == clim, (direct, clim)
            print("climatology_check_2024_equivalent=PASS")
        model = DC().fit(train, first_date)
        counts = match_counts(train)
        fit_trace.append({"season": season, "h": model.h, "rho": model.rho,
                          "training_n": len(train), "cutoff": first_date.isoformat()})
        season_payload[season] = {"climatology": clim, "training_n": len(train), "scored_n": len(target)}
        clim_preds = [{"ph": clim["outcome"][0], "pd": clim["outcome"][1],
                       "pa": clim["outcome"][2], "over25": clim["over25"]} for _ in target]
        cmetrics = score(target, clim_preds)
        cmetrics.update({"arm": "climatology", "season": season, "kind": "climatology"})
        tables.append(cmetrics)
        for arm in ARMS:
            preds = _predictions(model, target, arm, counts)
            predictions_by_arm[arm].extend(preds)
            metrics = score(target, preds)
            metrics.update({"arm": arm, "season": season, "kind": "model"})
            tables.append(metrics)
            for game, pred in zip(target, preds):
                scored_rows.append((game, arm, pred, clim))

    pooled_rows = [r for r in rows if r["season"] in DEV_SEASONS]
    for arm in ARMS:
        metrics = score(pooled_rows, predictions_by_arm[arm])
        metrics.update({"arm": arm, "season": "pooled", "kind": "model"})
        tables.append(metrics)
    # One pooled climatology row is calculated from the season-specific baseline predictions.
    pooled_clim_preds = []
    for season in DEV_SEASONS:
        prior = [r for r in rows if start_year(r["season"]) < start_year(season)]
        c = climatology(prior)
        pooled_clim_preds.extend({"ph": c["outcome"][0], "pd": c["outcome"][1], "pa": c["outcome"][2], "over25": c["over25"]}
                                 for _ in range(sum(r["season"] == season for r in pooled_rows)))
    cm = score(pooled_rows, pooled_clim_preds)
    cm.update({"arm": "climatology", "season": "pooled", "kind": "climatology"})
    tables.append(cm)

    diffs = []
    gate = predictions_by_arm["gate_zero"]
    shrink = predictions_by_arm["shrink"]
    for g, a, b in zip(pooled_rows, gate, shrink):
        delta = max(abs(a[k] - b[k]) for k in ("ph", "pd", "pa", "over25"))
        diffs.append(delta)
    differing = sum(d > 1e-12 for d in diffs)
    # No assert here: SHRINK coincides with Gate Zero by construction in
    # this league (prereg). Thin teams are exactly the zero-count new ids,
    # whose SHRINK factor is 0 and whose Gate Zero prior is a = d = 0;
    # every other team has >= 6 training matches (factor 1). The
    # coincidence is recorded in "activity", not treated as a defect.
    activity = {"differing_predictions": differing, "max_abs_probability_delta": max(diffs)}
    dev_gate = {}
    clim_pool = next(x for x in tables if x["arm"] == "climatology" and x["season"] == "pooled")
    for arm in ARMS:
        p = next(x for x in tables if x["arm"] == arm and x["season"] == "pooled")
        dev_gate[arm] = {"pass": p["ll_1x2"] < clim_pool["ll_1x2"] and p["rps"] < clim_pool["rps"] and p["oull_2_5"] < clim_pool["oull_2_5"],
                         "ll_1x2": p["ll_1x2"] < clim_pool["ll_1x2"], "rps": p["rps"] < clim_pool["rps"], "oull_2_5": p["oull_2_5"] < clim_pool["oull_2_5"]}
    result = {"protocol": {"league": "ME-1CFL", "seed_season": SEED, "dev_seasons": list(DEV_SEASONS),
                            "dev_seasons_loaded": [SEED, *DEV_SEASONS], "scored_n": len(pooled_rows), "season_2025/2026_loaded": False,
                            "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"},
              "tables": tables, "season_payload": season_payload, "fits": fit_trace,
              "activity": activity, "dev_gate": dev_gate}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    _write_csv(scored_rows)
    _print(result)
    return result


def _calibration(actual, predicted):
    errors = [y - p for y, p in zip(actual, predicted)]
    diff = sum(errors) / len(errors)
    se = math.sqrt(sum((x - diff) ** 2 for x in errors) / (len(errors) - 1)) / math.sqrt(len(errors))
    return {"diff_pp": 100.0 * diff, "se_pp": 100.0 * se}


def _calibration_leg(cal):
    boundary_pp = 1.0
    excess_pp = max(0.0, abs(cal["diff_pp"]) - boundary_pp)
    if excess_pp == 0.0:
        status = "PASS"
    elif excess_pp <= cal["se_pp"]:
        status = "PROVISIONAL PASS"
    else:
        status = "FAIL"
    return {"status": status, "difference_pp": cal["diff_pp"], "se_pp": cal["se_pp"],
            "boundary_pp": boundary_pp, "breach_distance_pp": excess_pp,
            "arithmetic": f"abs({cal['diff_pp']:.15g}) <= 1.0pp; excess={excess_pp:.15g}pp <= SE {cal['se_pp']:.15g}pp"}


def _write_virgin_predictions(target, predictions, model, shipped_arm):
    destination = HERE.parents[1] / "predictions" / "g_me_virgin_predictions.csv"
    fields = ["season", "date", "match_id", "home_team_id", "home_team", "away_team_id", "away_team",
              "home_goals", "away_goals", "lambda_home", "lambda_away", "ph", "pd", "pa",
              "over15", "over25", "over35", "btts", "lambda_home_1h", "lambda_away_1h",
              "ph_1h", "pd_1h", "pa_1h", "over05_1h", "over15_1h", "over25_1h",
              "lambda_home_2h", "lambda_away_2h", "ph_2h", "pd_2h", "pa_2h",
              "over15_2h", "over25_2h", "over35_2h", "shipped_arm"]
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for game, pred in zip(target, predictions):
            lh1, la1 = pred["lh"] * 0.426643, pred["la"] * 0.426643
            lh2, la2 = pred["lh"] * 0.573357, pred["la"] * 0.573357
            p1 = model.probs(lh1, la1)
            p2 = model.probs(lh2, la2)
            writer.writerow({"season": game["season"], "date": game["date"].isoformat(), "match_id": game["match_id"],
                             "home_team_id": game["hi"], "home_team": game["home"], "away_team_id": game["ai"],
                             "away_team": game["away"], "home_goals": game["yh"], "away_goals": game["ya"],
                             "lambda_home": pred["lh"], "lambda_away": pred["la"], "ph": pred["ph"],
                             "pd": pred["pd"], "pa": pred["pa"], "over15": pred["over15"], "over25": pred["over25"],
                             "over35": pred["over35"], "btts": pred["btts"], "lambda_home_1h": lh1,
                             "lambda_away_1h": la1, "ph_1h": p1["ph"], "pd_1h": p1["pd"], "pa_1h": p1["pa"],
                             "over05_1h": p1["over05"], "over15_1h": p1["over15"], "over25_1h": p1["over25"],
                             "lambda_home_2h": lh2, "lambda_away_2h": la2, "ph_2h": p2["ph"], "pd_2h": p2["pd"],
                             "pa_2h": p2["pa"], "over15_2h": p2["over15"], "over25_2h": p2["over25"],
                             "over35_2h": p2["over35"], "shipped_arm": shipped_arm})


def run_virgin():
    seasons = {SEED, *DEV_SEASONS, "2025/2026"}
    rows = _load_seasons(seasons)
    assert not any(r["season"] == "2026/2027" for r in rows)
    target = [r for r in rows if r["season"] == "2025/2026"]
    assert len(target) == 180, len(target)
    cutoff = min(r["date"] for r in target)
    train = [r for r in rows if r["date"] < cutoff]
    assert len(train) == 718, len(train)
    assert all(r["season"] != "2025/2026" for r in train)
    model = DC().fit(train, cutoff)
    counts = match_counts(train)
    dev = json.loads((HERE / "results_dev.json").read_text(encoding="utf-8"))
    clim = climatology(train)
    clim_preds = [{"ph": clim["outcome"][0], "pd": clim["outcome"][1], "pa": clim["outcome"][2],
                   "over25": clim["over25"]} for _ in target]
    metrics = {"climatology": score(target, clim_preds)}
    metrics["climatology"]["calibration"] = {
        "home_win": _calibration([int(r["yh"] > r["ya"]) for r in target], [p["ph"] for p in clim_preds]),
        "over25": _calibration([int(r["yh"] + r["ya"] > 2.5) for r in target], [p["over25"] for p in clim_preds])}
    predictions = {}
    for arm in ARMS:
        predictions[arm] = _predictions(model, target, arm, counts)
        m = score(target, predictions[arm])
        m["calibration"] = {
            "home_win": _calibration([int(r["yh"] > r["ya"]) for r in target], [p["ph"] for p in predictions[arm]]),
            "over25": _calibration([int(r["yh"] + r["ya"] > 2.5) for r in target], [p["over25"] for p in predictions[arm]])}
        metrics[arm] = m

    dev_tables = dev["tables"]
    sign_checks = {}
    for arm in ARMS:
        checks = []
        for season in DEV_SEASONS:
            actual = next(r for r in dev_tables if r["arm"] == arm and r["season"] == season and r["kind"] == "model")
            gz = next(r for r in dev_tables if r["arm"] == "gate_zero" and r["season"] == season and r["kind"] == "model")
            checks.append({"season": season, "arm_ll": actual["ll_1x2"], "gate_zero_ll": gz["ll_1x2"],
                           "pass": actual["ll_1x2"] <= gz["ll_1x2"]})
        sign_checks[arm] = {"exempt": arm == "gate_zero", "seasons": checks,
                            "passing_seasons": sum(x["pass"] for x in checks),
                            "required_seasons": 2, "pass": arm == "gate_zero" or sum(x["pass"] for x in checks) >= 2}

    gates = {}
    for arm in ARMS:
        ll = metrics[arm]["ll_1x2"] <= metrics["gate_zero"]["ll_1x2"] and metrics[arm]["ll_1x2"] <= metrics["climatology"]["ll_1x2"]
        cal_home = _calibration_leg(metrics[arm]["calibration"]["home_win"])
        cal_over = _calibration_leg(metrics[arm]["calibration"]["over25"])
        gates[arm] = {
            "ll_leg": {"pass": ll, "arm_ll": metrics[arm]["ll_1x2"], "gate_zero_ll": metrics["gate_zero"]["ll_1x2"],
                       "climatology_ll": metrics["climatology"]["ll_1x2"],
                       "arithmetic": f"{metrics[arm]['ll_1x2']:.15g} <= {metrics['gate_zero']['ll_1x2']:.15g} AND <= {metrics['climatology']['ll_1x2']:.15g}"},
            "calibration_leg": {"home_win": cal_home, "over25": cal_over,
                                "pass": cal_home["status"] != "FAIL" and cal_over["status"] != "FAIL"},
            "dev_sign_check": sign_checks[arm],
            "dev_gate": dev["dev_gate"][arm],
        }
        gates[arm]["pass"] = (gates[arm]["dev_gate"]["pass"] and gates[arm]["ll_leg"]["pass"] and
                               gates[arm]["calibration_leg"]["pass"] and gates[arm]["dev_sign_check"]["pass"])

    eligible = [arm for arm in ARMS if gates[arm]["pass"]]
    shipped = min(eligible, key=lambda arm: (metrics[arm]["ll_1x2"], 0 if arm == "gate_zero" else 1)) if eligible else None
    prediction_arm = shipped or "gate_zero"
    params = {"h": model.h, "rho": model.rho, "mu": model.mu,
              "a": {str(k): v for k, v in model.a.items()}, "d": {str(k): v for k, v in model.d.items()},
              "team_names": {str(k): v for k, v in model.team_names.items()}, "cutoff": cutoff.isoformat(),
              "training_n": len(train), "target_season": "2025/2026", "target_n": len(target)}
    (HERE / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8")
    result = {"protocol": {"league": "ME-1CFL", "virgin_season": "2025/2026", "n": len(target),
                            "fit_cutoff": cutoff.isoformat(), "training_n": len(train),
                            "sign_convention": "actual_minus_predicted"},
              "metrics": metrics, "gates": gates, "shipped_arm": shipped}
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    _write_virgin_predictions(target, predictions[prediction_arm], model, shipped)
    _print_virgin(result)
    return result


def _print_virgin(result):
    for arm in ("gate_zero", "shrink", "climatology"):
        m = result["metrics"][arm]
        print(f"{arm} LL={m['ll_1x2']:.6f} RPS={m['rps']:.6f} OU25={m['oull_2_5']:.6f}")
        if arm != "climatology":
            for key in ("home_win", "over25"):
                c = m["calibration"][key]
                print(f"{arm} calibration_{key} diff_pp={c['diff_pp']:.6f} se_pp={c['se_pp']:.6f}")
            print("gates=" + json.dumps(result["gates"][arm], separators=(",", ":")))
    print("shipped_arm=" + json.dumps(result["shipped_arm"]))


def _write_csv(scored_rows):
    fields = ["season", "date", "match_id", "home_team_id", "away_team_id", "home_goals", "away_goals",
              "gate_zero_ph", "gate_zero_pd", "gate_zero_pa", "gate_zero_over25", "gate_zero_lambda_home", "gate_zero_lambda_away",
              "shrink_ph", "shrink_pd", "shrink_pa", "shrink_over25", "shrink_lambda_home", "shrink_lambda_away",
              "climatology_ph", "climatology_pd", "climatology_pa", "climatology_over25"]
    grouped = {}
    for game, arm, pred, clim in scored_rows:
        grouped.setdefault(game["match_id"], {"game": game, "clim": clim})[arm] = pred
    with (HERE / "results_dev.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for item in sorted(grouped.values(), key=lambda x: (x["game"]["date"], x["game"]["match_id"])):
            g = item["game"]; row = {"season": g["season"], "date": g["date"].isoformat(), "match_id": g["match_id"],
                   "home_team_id": g["hi"], "away_team_id": g["ai"], "home_goals": g["yh"], "away_goals": g["ya"],
                   "climatology_ph": item["clim"]["outcome"][0], "climatology_pd": item["clim"]["outcome"][1],
                   "climatology_pa": item["clim"]["outcome"][2], "climatology_over25": item["clim"]["over25"]}
            for arm in ARMS:
                p = item[arm]; prefix = arm
                row.update({f"{prefix}_ph": p["ph"], f"{prefix}_pd": p["pd"], f"{prefix}_pa": p["pa"],
                            f"{prefix}_over25": p["over25"], f"{prefix}_lambda_home": p["lh"], f"{prefix}_lambda_away": p["la"]})
            writer.writerow(row)


def _print(result):
    print("fit_trace=" + json.dumps(result["fits"], separators=(",", ":")))
    for row in result["tables"]:
        if row["season"] == "pooled":
            print(f'{row["arm"]} pooled LL={row["ll_1x2"]:.6f} RPS={row["rps"]:.6f} OU25={row["oull_2_5"]:.6f}')
    print("activity=" + json.dumps(result["activity"], separators=(",", ":")))
    print("dev_gate=" + json.dumps(result["dev_gate"], separators=(",", ":")))
