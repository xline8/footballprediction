"""CO-PrimeraB loading, walk-forward evaluation, and output writers."""
import csv, json, math
from collections import defaultdict, deque
from datetime import date
from pathlib import Path
from arms import adjusted_lambdas, prior_match_counts
from dc import DC

ROOT = Path(__file__).resolve().parents[2]; DATA = ROOT / "data" / "co_primerab_matches.csv"; OUT = Path(__file__).resolve().parent
ARMS = ("gate_zero", "shrink", "x2"); DEV_SEASONS = tuple(str(y) for y in range(2021, 2025)); VIRGIN_SEASONS = set(DEV_SEASONS) | {"2025"}

def load(path=DATA, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if allowed is not None and raw["season"] not in allowed: continue
            rows.append({"match_id": raw["match_id"], "season": raw["season"], "date": date.fromisoformat(raw["date"]),
                         "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]), "home": raw["home_team"], "away": raw["away_team"],
                         "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"]),
                         "hm": raw["home_mover_down"].lower() == "true", "am": raw["away_mover_down"].lower() == "true"})
    return sorted(rows, key=lambda row: (row["date"], row["match_id"]))

def _scores(rows, probabilities):
    ll = rps = oull = 0.0
    for row, probability in zip(rows, probabilities):
        outcome = (1, 0, 0) if row["yh"] > row["ya"] else ((0, 1, 0) if row["yh"] == row["ya"] else (0, 0, 1))
        p = [probability["ph"], probability["pd"], probability["pa"]]; ll -= math.log(max(p[outcome.index(1)], 1e-12))
        rps += 0.5 * ((p[0] - outcome[0]) ** 2 + (p[0] + p[1] - outcome[0] - outcome[1]) ** 2)
        is_over = row["yh"] + row["ya"] > 2.5; oull -= math.log(max(probability["over25"] if is_over else 1 - probability["over25"], 1e-12))
    n = len(rows); return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}

def _climatology(train):
    n = len(train); home = sum(row["yh"] > row["ya"] for row in train) / n; draw = sum(row["yh"] == row["ya"] for row in train) / n
    return [home, draw, 1.0 - home - draw], sum(row["yh"] + row["ya"] > 2.5 for row in train) / n

def _fit_predict(train, target, arm):
    cutoff = min(row["date"] for row in target); fit_rows = [row for row in train if row["date"] < cutoff]
    model = DC().fit(fit_rows, cutoff); counts = prior_match_counts(fit_rows); probabilities = []
    for row in target:
        lh, la = adjusted_lambdas(model, row["hi"], row["ai"], arm, counts, row["hm"], row["am"]); p = model.probs(lh, la); p.update({"lh": lh, "la": la}); probabilities.append(p)
    return model, counts, probabilities

def _naive_probability(row, history, train):
    mu = sum(r["yh"] + r["ya"] for r in train) / (2 * len(train)); mu_h = sum(r["yh"] for r in train) / len(train); mu_a = sum(r["ya"] for r in train) / len(train)
    scored = defaultdict(list); conceded = defaultdict(list)
    for old in history:
        scored[old["hi"]].append(old["yh"]); scored[old["ai"]].append(old["ya"]); conceded[old["hi"]].append(old["ya"]); conceded[old["ai"]].append(old["yh"])
    def mean(values, fallback): return sum(values[-10:]) / len(values[-10:]) if values else fallback
    fallback_scored = defaultdict(list); fallback_conceded = defaultdict(list)
    for old in train:
        fallback_scored[old["hi"]].append(old["yh"]); fallback_scored[old["ai"]].append(old["ya"])
        fallback_conceded[old["hi"]].append(old["ya"]); fallback_conceded[old["ai"]].append(old["yh"])
    ah = mean(scored[row["hi"]], sum(fallback_scored[row["hi"]]) / max(1, len(fallback_scored[row["hi"]])))
    aa = mean(scored[row["ai"]], sum(fallback_scored[row["ai"]]) / max(1, len(fallback_scored[row["ai"]])))
    dh = mean(conceded[row["hi"]], sum(fallback_conceded[row["hi"]]) / max(1, len(fallback_conceded[row["hi"]])))
    da = mean(conceded[row["ai"]], sum(fallback_conceded[row["ai"]]) / max(1, len(fallback_conceded[row["ai"]])))
    return DC().probs(mu_h * (ah / mu) * (da / mu), mu_a * (aa / mu) * (dh / mu), rho=0.0)

def _evaluate_target(rows, target, arm):
    cutoff = min(row["date"] for row in target); train = [row for row in rows if row["date"] < cutoff]
    _, _, model_p = _fit_predict(train, target, arm); history = []
    naive_p = []
    for row in target:
        naive_p.append(_naive_probability(row, history, train)); history.extend(old for old in rows if old["date"] < row["date"] and old not in history)
    return train, model_p, naive_p

def run_dev():
    rows = load(allowed=set(DEV_SEASONS)); assert {r["season"] for r in rows} <= set(DEV_SEASONS); result = []
    for arm in ARMS:
        pooled = {"model": [], "climatology": [], "naive": []}
        for season in DEV_SEASONS[1:]:
            target = [r for r in rows if r["season"] == season]; train, model_p, naive_p = _evaluate_target(rows, target, arm); clim_p, clim_o = _climatology(train)
            clim = [{"ph": clim_p[0], "pd": clim_p[1], "pa": clim_p[2], "over25": clim_o} for _ in target]
            for kind, probs in (("model", model_p), ("climatology", clim), ("naive", naive_p)):
                metrics = _scores(target, probs); metrics.update({"arm": arm, "season": season, "kind": kind}); result.append(metrics); pooled[kind].extend(zip(target, probs))
        for kind, values in pooled.items():
            metrics = _scores([r for r, _ in values], [p for _, p in values]); metrics.update({"arm": arm, "season": "pooled", "kind": kind}); result.append(metrics)
    _write_dev(result); _print_table(result, "dev"); return result

def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as handle: csv.DictWriter(handle, fieldnames=fields).writeheader(); csv.DictWriter(handle, fieldnames=fields).writerows({k: r.get(k) for k in fields} for r in result)

def _params(model): return {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "league_mean_goals": model.mu}

def run_virgin(arms):
    rows = load(allowed=VIRGIN_SEASONS); assert {r["season"] for r in rows} <= VIRGIN_SEASONS; target = [r for r in rows if r["season"] == "2025"]; result = {}; fitted = {}
    for arm in arms:
        train, probabilities, naive = _evaluate_target(rows, target, arm); clim_p, clim_o = _climatology(train); metrics = _scores(target, probabilities); metrics.update({"arm": arm, "naive": _scores(target, naive), "climatology": _scores(target, [{"ph": clim_p[0], "pd": clim_p[1], "pa": clim_p[2], "over25": clim_o} for _ in target])}); result[arm] = metrics
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8"); _print_table(result, "virgin"); return result

def write_predictions(arm):
    rows = load(allowed=VIRGIN_SEASONS); target = [r for r in rows if r["season"] == "2025"]; train, probabilities, _ = _evaluate_target(rows, target, arm); model = DC().fit([r for r in train if r["date"] < min(x["date"] for x in target)], min(x["date"] for x in target)); fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a", "p_home", "p_draw", "p_away", "p_over15", "p_over25", "p_over35", "p_btts", "p_1h_over05", "p_1h_over15", "p_1h_over25", "p_2h_over15", "p_2h_over25", "p_2h_over35"]
    output = []
    for row, p in zip(target, probabilities):
        first_h, first_a = p["lh"] * .4875, p["la"] * .4875; second_h, second_a = p["lh"] * .5125, p["la"] * .5125; first, second = model.probs(first_h, first_a), model.probs(second_h, second_a)
        output.append({"match_id": row["match_id"], "date": row["date"].isoformat(), "home_team": row["home"], "away_team": row["away"], "home_goals": row["yh"], "away_goals": row["ya"], "lam_h": p["lh"], "lam_a": p["la"], "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over15": p["over15"], "p_over25": p["over25"], "p_over35": p["over35"], "p_btts": p["btts"], "p_1h_over05": model.over(first_h, first_a, .5), "p_1h_over15": first["over15"], "p_1h_over25": first["over25"], "p_2h_over15": second["over15"], "p_2h_over25": second["over25"], "p_2h_over35": second["over35"]})
    destination = ROOT / "predictions" / "g_co_virgin_predictions.csv"; destination.parent.mkdir(exist_ok=True)
    with open(destination, "w", newline="", encoding="utf-8") as handle: writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(output)

def _print_table(data, label):
    print(label); print("arm season kind n ll_1x2 rps oull_2_5") if label == "dev" else print("arm n ll_1x2 rps oull_2_5")
    if label == "dev":
        for row in data: print(f'{row["arm"]} {row["season"]} {row["kind"]} {row["n"]} {row["ll_1x2"]:.6f} {row["rps"]:.6f} {row["oull_2_5"]:.6f}')
    else:
        for arm, row in data.items(): print(f'{arm} {row["n"]} {row["ll_1x2"]:.6f} {row["rps"]:.6f} {row["oull_2_5"]:.6f}')
