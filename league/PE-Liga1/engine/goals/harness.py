"""G-PE tournament-blocked Dixon-Coles evaluation and outputs."""
import csv, json, math
from collections import defaultdict
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas

ROOT = Path(__file__).resolve().parents[2]; DATA = ROOT / "data" / "pe_liga1_matches.csv"; OUT = Path(__file__).resolve().parent
SEED = {"2021 - Fase 1", "2021 - Fase 2"}; DEV = ("2022 - Apertura", "2022 - Clausura", "2023 - Apertura", "2023 - Clausura", "2024 - Apertura", "2024 - Clausura"); VIRGIN = ("2025 - Apertura", "2025 - Clausura"); ARMS = ("gate_zero", "x2")

def load(seasons):
    rows = []
    with DATA.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            if raw["block"] in seasons and raw["phase"] == "regular" and raw["awarded"] == "0":
                rows.append({"match_id": raw["match_id"], "season": raw["block"], "date": date.fromisoformat(raw["date"]), "hi": int(raw["home_team_id"]), "ai": int(raw["away_team_id"]), "home": raw["home_team"], "away": raw["away_team"], "yh": int(raw["home_goals"]), "ya": int(raw["away_goals"]), "hm": raw["home_absent_prev"] == "1", "am": raw["away_absent_prev"] == "1"})
    return sorted(rows, key=lambda row: (row["date"], row["match_id"]))

def scores(rows, probabilities):
    ll = rps = oull = 0.0
    for row, p in zip(rows, probabilities):
        y = (1, 0, 0) if row["yh"] > row["ya"] else ((0, 1, 0) if row["yh"] == row["ya"] else (0, 0, 1)); q = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(q[y.index(1)], 1e-12)); rps += .5 * ((q[0] - y[0]) ** 2 + (q[0] + q[1] - y[0] - y[1]) ** 2)
        over = row["yh"] + row["ya"] > 2.5; oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    return {"n": len(rows), "ll_1x2": ll / len(rows), "rps": rps / len(rows), "oull_2_5": oull / len(rows)}

def clim(rows):
    n = len(rows); h = sum(r["yh"] > r["ya"] for r in rows) / n; d = sum(r["yh"] == r["ya"] for r in rows) / n
    return [h, d, 1 - h - d], sum(r["yh"] + r["ya"] > 2.5 for r in rows) / n

def fit_predict(train, target):
    cutoff = min(r["date"] for r in target); fit_rows = [r for r in train if r["date"] < cutoff]
    return DC().fit(fit_rows, cutoff), fit_rows

def naive_probability(row, history, fit_rows):
    mu = sum(r["yh"] + r["ya"] for r in fit_rows) / (2 * len(fit_rows)); mu_h = sum(r["yh"] for r in fit_rows) / len(fit_rows); mu_a = sum(r["ya"] for r in fit_rows) / len(fit_rows)
    scored = defaultdict(list); conceded = defaultdict(list)
    for old in history:
        scored[old["hi"]].append(old["yh"]); scored[old["ai"]].append(old["ya"]); conceded[old["hi"]].append(old["ya"]); conceded[old["ai"]].append(old["yh"])
    fallback_s = defaultdict(list); fallback_c = defaultdict(list)
    for old in fit_rows:
        fallback_s[old["hi"]].append(old["yh"]); fallback_s[old["ai"]].append(old["ya"]); fallback_c[old["hi"]].append(old["ya"]); fallback_c[old["ai"]].append(old["yh"])
    def mean(values, fallback): return sum(values[-10:]) / len(values[-10:]) if values else fallback
    def fallback(values): return sum(values) / len(values) if values else mu
    ah = mean(scored[row["hi"]], fallback(fallback_s[row["hi"]])); aa = mean(scored[row["ai"]], fallback(fallback_s[row["ai"]])); dh = mean(conceded[row["hi"]], fallback(fallback_c[row["hi"]])); da = mean(conceded[row["ai"]], fallback(fallback_c[row["ai"]]))
    return DC().probs(mu_h * ah / mu * da / mu, mu_a * aa / mu * dh / mu, rho=0.0)

def _clim_probs(rows, p, o): return [{"ph": p[0], "pd": p[1], "pa": p[2], "over25": o} for _ in rows]

def run_dev():
    rows = load(SEED | set(DEV)); assert not any(r["season"].startswith(("2025", "2026")) for r in rows); result = []
    for arm in ARMS:
        pooled = {"model": [], "climatology": [], "naive": []}
        for season in DEV:
            target = [r for r in rows if r["season"] == season]; train = [r for r in rows if r["date"] < min(x["date"] for x in target)]; model, fit_rows = fit_predict(train, target)
            model_p = []
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, r["hm"], r["am"]); q = model.probs(lh, la); q.update(lh=lh, la=la); model_p.append(q)
            history = [r for r in rows if r["date"] < min(x["date"] for x in target)]; naive_p = []
            for r in target:
                naive_p.append(naive_probability(r, history, fit_rows)); history.append(r)
            cp, co = clim(train); probs = {"model": model_p, "climatology": _clim_probs(target, cp, co), "naive": naive_p}
            for kind, ps in probs.items():
                x = scores(target, ps); x.update(arm=arm, season=season, kind=kind); result.append(x); pooled[kind].extend(zip(target, ps))
        for kind, pairs in pooled.items():
            x = scores([r for r, _ in pairs], [p for _, p in pairs]); x.update(arm=arm, season="pooled", kind=kind); result.append(x)
    write_dev(result); print_table(result, "dev"); return result

def write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows({k: r.get(k) for k in fields} for r in result)

def se(values):
    mean = sum(values) / len(values); return (sum((x - mean) ** 2 for x in values) / (len(values) - 1)) ** .5 / len(values) ** .5

def print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for x in data: print(x["arm"], x["season"], x["kind"], x["n"], f'{x["ll_1x2"]:.6f}', f'{x["rps"]:.6f}', f'{x["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 climatology_ll_1x2 home_win_diff over25_diff")
        for arm, x in data.items(): print(arm, x["n"], f'{x["ll_1x2"]:.6f}', f'{x["rps"]:.6f}', f'{x["oull_2_5"]:.6f}', f'{x["climatology"]["ll_1x2"]:.6f}', f'{x["calibration"]["home_win_diff"]:.6f}', f'{x["calibration"]["over25_diff"]:.6f}')

def virgin_metrics(arms):
    dev = json.loads((OUT / "results_dev.json").read_text()); get = lambda a, k: next(x for x in dev if x["arm"] == a and x["season"] == "pooled" and x["kind"] == k)
    base = get("gate_zero", "climatology"); gates = {a: get(a, "model")["ll_1x2"] < base["ll_1x2"] and get(a, "model")["rps"] < base["rps"] and get(a, "model")["oull_2_5"] < base["oull_2_5"] for a in arms}
    if not gates["gate_zero"]:
        out = {"virgin_read": False, "verdict": "FAIL", "shipped_arm": None, "legs": {"dev_gate": gates}}
        (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); print("virgin not read: Gate Zero failed dev gate"); return out
    rows = load(SEED | set(DEV) | set(VIRGIN)); assert not any(r["season"].startswith("2026") for r in rows)
    target = [r for r in rows if r["season"] in VIRGIN]; train = [r for r in rows if r["season"] not in VIRGIN]; cutoff = min(r["date"] for r in target); model, fit_rows = fit_predict(train, target); cp, co = clim(train); result = {}; dev_season_ll = {}
    for arm in arms:
        if not gates[arm]: continue
        ps = []; naive = []; history = [r for r in train if r["date"] < cutoff]
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, r["hm"], r["am"]); q = model.probs(lh, la); q.update(lh=lh, la=la); ps.append(q); naive.append(naive_probability(r, history, fit_rows)); history.append(r)
        home_diffs = [q["ph"] - (r["yh"] > r["ya"]) for q, r in zip(ps, target)]; over_diffs = [q["over25"] - (r["yh"] + r["ya"] > 2.5) for q, r in zip(ps, target)]
        calibration = {"home_win_diff": sum(home_diffs) / len(home_diffs), "over25_diff": sum(over_diffs) / len(over_diffs), "home_win_se": se(home_diffs), "over25_se": se(over_diffs)}
        result[arm] = {**scores(target, ps), "arm": arm, "climatology": scores(target, _clim_probs(target, cp, co)), "naive": scores(target, naive), "calibration": calibration, "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm}}
        for season in DEV:
            dev_season_ll.setdefault(arm, {})[season] = get(arm, "model")["ll_1x2"] if False else next(x["ll_1x2"] for x in dev if x["arm"] == arm and x["season"] == season and x["kind"] == "model")
    legs = {"dev_gate": gates, "arms": {}}
    for arm, x in result.items():
        c = x["calibration"]; clean = abs(c["home_win_diff"]) <= .01 and abs(c["over25_diff"]) <= .01; provisional = abs(c["home_win_diff"]) <= .01 + c["home_win_se"] and abs(c["over25_diff"]) <= .01 + c["over25_se"]
        leg3 = True if arm == "gate_zero" else sum(next(y["ll_1x2"] for y in dev if y["arm"] == arm and y["season"] == s and y["kind"] == "model") <= next(y["ll_1x2"] for y in dev if y["arm"] == "gate_zero" and y["season"] == s and y["kind"] == "model") for s in DEV) >= (len(DEV) + 1) // 2
        legs["arms"][arm] = {"dev": gates[arm], "i": x["ll_1x2"] <= result["gate_zero"]["ll_1x2"] and x["ll_1x2"] <= x["climatology"]["ll_1x2"], "ii": provisional, "ii_status": "clean" if clean else ("provisional" if provisional else "fail"), "iii": leg3}
    eligible = [a for a, l in legs["arms"].items() if all(l[k] for k in ("dev", "i", "ii", "iii"))]; ship = min(eligible, key=lambda a: (result[a]["ll_1x2"], a != "gate_zero")) if eligible else None
    out = {**result, "virgin_read": True, "verdict": "PASS" if ship else "FAIL", "shipped_arm": ship, "legs": legs}; (OUT / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n"); print_table(result, "virgin"); print("verdict", out["verdict"], "shipped", ship)
    if ship: write_predictions(ship, model, target, result[ship]["params"])
    return out

def write_predictions(arm, model, target, params):
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "lam_h", "lam_a", "p_home", "p_draw", "p_away", "p_over15", "p_over25", "p_over35", "p_btts", "p_1h_over05", "p_1h_over15", "p_1h_over25", "p_2h_over15", "p_2h_over25", "p_2h_over35", "mean_1h", "mean_2h", "rho", "arm"]
    with (ROOT / "predictions" / "g_pe_virgin_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, r["hm"], r["am"]); q = model.probs(lh, la); first = model.probs(lh * .4377, la * .4377); second = model.probs(lh * .5623, la * .5623)
            writer.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "home_team": r["home"], "away_team": r["away"], "home_goals": r["yh"], "away_goals": r["ya"], "lam_h": lh, "lam_a": la, "p_home": q["ph"], "p_draw": q["pd"], "p_away": q["pa"], "p_over15": q["over15"], "p_over25": q["over25"], "p_over35": q["over35"], "p_btts": q["btts"], "p_1h_over05": model.over(lh * .4377, la * .4377, .5), "p_1h_over15": first["over15"], "p_1h_over25": first["over25"], "p_2h_over15": second["over15"], "p_2h_over25": second["over25"], "p_2h_over35": second["over35"], "mean_1h": .4377 * (lh + la), "mean_2h": .5623 * (lh + la), "rho": model.rho, "arm": arm})
    (OUT / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2) + "\n")
