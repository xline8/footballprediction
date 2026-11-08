"""Season-blocked G-LT development walk-forward harness."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import ARMS, adjusted_lambdas, match_counts
from dc import DC

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "lt_matches.csv"
SEED = "2021"
DEV_SEASONS = ("2022", "2023", "2024", "2025")


def load(path=DATA):
    rows = []
    with open(path, newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            # This filter is intentionally at the load boundary: dev cannot see virgin rows.
            if raw["season"] == "2026":
                continue
            if raw["season"] not in {SEED, *DEV_SEASONS}:
                continue
            rows.append({"match_id": raw["match_id"], "season": raw["season"],
                         "date": date.fromisoformat(raw["date"]),
                         "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]),
                         "home": raw["home_team"], "away": raw["away_team"],
                         "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"])})
    assert not any(r["season"] == "2026" for r in rows)
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
    prior = [r for r in rows if int(r["season"]) < int(season)]
    n = len(prior)
    hw = sum(r["yh"] > r["ya"] for r in prior)
    dr = sum(r["yh"] == r["ya"] for r in prior)
    ov = sum(r["yh"] + r["ya"] > 2.5 for r in prior)
    return {"outcome": [hw / n, dr / n, 1.0 - hw / n - dr / n], "over25": ov / n}


def run_dev():
    rows = load()
    assert all(r["season"] != "2026" for r in rows)
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
        prior = [r for r in rows if int(r["season"]) < int(season)]
        clim = climatology(prior)
        if season == "2024":
            direct = _direct_climatology(rows, season)
            assert direct == clim, (direct, clim)
            print("climatology_check_2024=PASS")
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
        prior = [r for r in rows if int(r["season"]) < int(season)]
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
    result = {"protocol": {"league": "LT-Toplyga", "seed_season": SEED, "dev_seasons": list(DEV_SEASONS),
                            "dev_seasons_loaded": [SEED, *DEV_SEASONS], "scored_n": len(pooled_rows), "season_2026_loaded": False,
                            "primary_line": "OU2.5", "sign_convention": "actual_minus_predicted"},
              "tables": tables, "season_payload": season_payload, "fits": fit_trace,
              "activity": activity, "dev_gate": dev_gate}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    _write_csv(scored_rows)
    _print(result)
    return result


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
