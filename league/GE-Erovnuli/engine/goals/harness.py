"""GE-Erovnuli loading, walk-forward evaluation, metrics, and output writers."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from arms import adjusted_lambdas, prior_match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "ge_matches.csv"
OUT = Path(__file__).resolve().parent
ARMS = ("gate_zero", "shrink")
DEV_SEASONS = ("2021", "2022", "2023", "2024")


def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if allowed is not None and raw["season"] not in allowed:
                continue
            rows.append({"match_id": raw["match_id"], "season": raw["season"],
                         "date": date.fromisoformat(raw["date"]),
                         "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]),
                         "home": raw["home_team"], "away": raw["away_team"],
                         "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"])})
    return sorted(rows, key=lambda row: (row["date"], row["match_id"]))


def _scores(rows, probabilities):
    ll = rps = oull = 0.0
    for row, probability in zip(rows, probabilities):
        outcome = (1, 0, 0) if row["yh"] > row["ya"] else ((0, 1, 0) if row["yh"] == row["ya"] else (0, 0, 1))
        p = [probability["ph"], probability["pd"], probability["pa"]]
        ll -= math.log(max(p[outcome.index(1)], 1e-12))
        rps += 0.5 * ((p[0] - outcome[0]) ** 2 + (p[0] + p[1] - outcome[0] - outcome[1]) ** 2)
        is_over = row["yh"] + row["ya"] > 2.5
        oull -= math.log(max(probability["over25"] if is_over else 1 - probability["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _climatology(train):
    n = len(train)
    home = sum(row["yh"] > row["ya"] for row in train) / n
    draw = sum(row["yh"] == row["ya"] for row in train) / n
    over = sum(row["yh"] + row["ya"] > 2.5 for row in train) / n
    return [home, draw, 1.0 - home - draw], over


def _fit_predict(train, target, arm):
    cutoff = min(row["date"] for row in target)
    fit_rows = [row for row in train if row["date"] < cutoff]
    model = DC().fit(fit_rows, cutoff)
    counts = prior_match_counts(fit_rows)
    probabilities = []
    for row in target:
        lh, la = adjusted_lambdas(model, row["hi"], row["ai"], arm, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        probabilities.append(p)
    return model, counts, probabilities


def run_dev():
    rows = load(allowed=set(DEV_SEASONS))
    assert {row["season"] for row in rows} <= set(DEV_SEASONS)
    result = []
    for arm in ARMS:
        pooled_model_rows = []
        pooled_clim_rows = []
        for season in DEV_SEASONS[1:]:
            target = [row for row in rows if row["season"] == season]
            cutoff = min(row["date"] for row in target)
            train = [row for row in rows if row["date"] < cutoff]
            model, _, probabilities = _fit_predict(train, target, arm)
            metrics = _scores(target, probabilities)
            metrics.update({"arm": arm, "season": season, "kind": "model"})
            result.append(metrics)
            pooled_model_rows.extend(zip(target, probabilities))
            clim_p, clim_over = _climatology(train)
            clim_probabilities = [{"ph": clim_p[0], "pd": clim_p[1], "pa": clim_p[2], "over25": clim_over}
                                  for _ in target]
            metrics = _scores(target, clim_probabilities)
            metrics.update({"arm": arm, "season": season, "kind": "climatology"})
            result.append(metrics)
            pooled_clim_rows.extend(zip(target, clim_probabilities))
        metrics = _scores([row for row, _ in pooled_model_rows], [p for _, p in pooled_model_rows])
        metrics.update({"arm": arm, "season": "pooled", "kind": "model"})
        result.append(metrics)
        metrics = _scores([row for row, _ in pooled_clim_rows], [p for _, p in pooled_clim_rows])
        metrics.update({"arm": arm, "season": "pooled", "kind": "climatology"})
        result.append(metrics)
    _write_dev(result)
    _print_table(result, "dev")
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in result)


def _calibration(values):
    mean = sum(values) / len(values)
    se = (sum((value - mean) ** 2 for value in values) / (len(values) - 1)) ** 0.5 / math.sqrt(len(values))
    return mean, se


def run_virgin(arms):
    rows = load(allowed={"2021", "2022", "2023", "2024", "2025"})
    assert {row["season"] for row in rows} <= {"2021", "2022", "2023", "2024", "2025"}
    target = [row for row in rows if row["season"] == "2025"]
    cutoff = min(row["date"] for row in target)
    train = [row for row in rows if row["date"] < cutoff]
    clim_p, clim_over = _climatology(train)
    result = {}
    fitted = {}
    for arm in arms:
        model, counts, probabilities = _fit_predict(train, target, arm)
        metrics = _scores(target, probabilities)
        clim_probabilities = [{"ph": clim_p[0], "pd": clim_p[1], "pa": clim_p[2], "over25": clim_over}
                              for _ in target]
        home_diff, home_se = _calibration([p["ph"] - (row["yh"] > row["ya"]) for row, p in zip(target, probabilities)])
        over_diff, over_se = _calibration([p["over25"] - (row["yh"] + row["ya"] > 2.5) for row, p in zip(target, probabilities)])
        metrics.update({"arm": arm, "climatology": _scores(target, clim_probabilities),
                        "calibration": {"home_win_diff": home_diff, "home_win_se": home_se,
                                        "over25_diff": over_diff, "over25_se": over_se},
                        "params": _params(model)})
        result[arm] = metrics
        fitted[arm] = _params(model)
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(fitted, indent=2) + "\n", encoding="utf-8")
    _print_table(result, "virgin")
    return result


def _params(model):
    return {"a": dict(model.a), "d": dict(model.d), "h": model.h,
            "rho": model.rho, "league_mean_goals": model.mu}


def write_predictions(arm):
    rows = load(allowed={"2021", "2022", "2023", "2024", "2025"})
    target = [row for row in rows if row["season"] == "2025"]
    cutoff = min(row["date"] for row in target)
    train = [row for row in rows if row["date"] < cutoff]
    model, counts, probabilities = _fit_predict(train, target, arm)
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals",
              "lam_h", "lam_a", "p_home", "p_draw", "p_away", "p_over15", "p_over25", "p_over35", "p_btts",
              "p_1h_over05", "p_1h_over15", "p_1h_over25", "p_2h_over15", "p_2h_over25", "p_2h_over35"]
    output = []
    for row, p in zip(target, probabilities):
        first_h = p["lh"] * 0.4516; first_a = p["la"] * 0.4516
        second_h = p["lh"] * (1.0 - 0.4516); second_a = p["la"] * (1.0 - 0.4516)
        first = model.probs(first_h, first_a)
        second = model.probs(second_h, second_a)
        output.append({"match_id": row["match_id"], "date": row["date"].isoformat(),
                       "home_team": row["home"], "away_team": row["away"],
                       "home_goals": row["yh"], "away_goals": row["ya"],
                       "lam_h": p["lh"], "lam_a": p["la"], "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"],
                       "p_over15": p["over15"], "p_over25": p["over25"], "p_over35": p["over35"], "p_btts": p["btts"],
                       "p_1h_over05": model.over(first_h, first_a, 0.5), "p_1h_over15": first["over15"],
                       "p_1h_over25": first["over25"], "p_2h_over15": second["over15"],
                       "p_2h_over25": second["over25"], "p_2h_over35": second["over35"]})
    destination = ROOT / "predictions" / "g_ge_virgin_predictions.csv"
    destination.parent.mkdir(exist_ok=True)
    with open(destination, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(output)


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for row in data:
            print(f'{row["arm"]} {row["season"]} {row["kind"]} {row["n"]} {row["ll_1x2"]:.6f} {row["rps"]:.6f} {row["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for arm, row in data.items():
            print(f'{arm} {row["n"]} {row["ll_1x2"]:.6f} {row["rps"]:.6f} {row["oull_2_5"]:.6f} '
                  f'{row["climatology"]["ll_1x2"]:.6f} {row["calibration"]["home_win_diff"]:.6f} {row["calibration"]["over25_diff"]:.6f}')
