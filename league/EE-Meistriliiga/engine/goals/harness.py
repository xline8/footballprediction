"""Season-blocked Phase B walk-forward harness; deliberately has no virgin path."""
import csv
import json
import math
from datetime import date
from pathlib import Path

from fit import DC, HALF_LIFE, pois
from predict import adjusted_lambdas, entrant_ids, match_counts

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "ee_matches.csv"
SEASONS = ("2021", "2022", "2023", "2024", "2025")
TARGETS = ("2022", "2023", "2024", "2025")
ARMS = ("gate_zero", "shrink", "x2")


def load_rows(path=DATA):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            season = str(r["season"])
            if season not in SEASONS:
                continue
            rows.append({"match_id": r["match_id"], "season": season,
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert all(r["season"] in SEASONS for r in rows), "2026 row loaded into dev harness"
    assert not any(r["season"] == "2026" for r in rows), "2026 row loaded into dev harness"
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def scores(rows, predictions):
    ll = rps = oull = 0.0
    for r, p in zip(rows, predictions):
        outcome = 0 if r["yh"] > r["ya"] else 1 if r["yh"] == r["ya"] else 2
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[outcome], 1e-12))
        cumulative = pp[0] + pp[1]
        observed = (1.0, 1.0) if outcome == 0 else (0.0, 1.0) if outcome == 1 else (0.0, 0.0)
        rps += 0.5 * ((pp[0] - observed[0]) ** 2 + (cumulative - observed[1]) ** 2)
        over = r["yh"] + r["ya"] > 2
        q = p["over25"] if over else 1 - p["over25"]
        oull -= math.log(max(q, 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def base_rates(train):
    n = len(train)
    return ([sum(r["yh"] > r["ya"] for r in train) / n,
             sum(r["yh"] == r["ya"] for r in train) / n,
             sum(r["yh"] < r["ya"] for r in train) / n],
            sum(r["yh"] + r["ya"] > 2 for r in train) / n)


def run_dev():
    rows = load_rows()
    sign_check = synthetic_sign_checks()
    all_predictions = []
    summaries = []
    fit_info = {}
    for season in TARGETS:
        target = [r for r in rows if r["season"] == season]
        cutoff = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < cutoff]
        assert train and max(r["date"] for r in train) < cutoff
        model = DC().fit(train, cutoff)
        counts = match_counts(train)
        preceding = str(int(season) - 1)
        entrants = entrant_ids(rows, season, preceding)
        fit_info[season] = {"cutoff": cutoff.isoformat(), "n_train": len(train),
                            "max_train_date": model.max_train_date.isoformat(),
                            "rho": model.rho, "home_advantage": model.h,
                            "mu": model.mu, "entrants": sorted(entrants)}
        cp, co = base_rates(train)
        clim = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        summaries.append({"arm": "climatology", "season": season, **scores(target, clim)})
        for arm in ARMS:
            ps = []
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts, entrants, model.mu, season)
                p = model.probs(lh, la); p.update({"match_id": r["match_id"], "season": season, "arm": arm, "lh": lh, "la": la})
                ps.append(p)
                all_predictions.append({"match_id": r["match_id"], "season": season, "arm": arm,
                                        "ph": p["ph"], "pd": p["pd"], "pa": p["pa"], "over25": p["over25"],
                                        "home_goals": r["yh"], "away_goals": r["ya"]})
            summaries.append({"arm": arm, "season": season, **scores(target, ps)})
    for arm in ARMS:
        rr = [r for r in all_predictions if r["arm"] == arm]
        actual = [{"yh": r["home_goals"], "ya": r["away_goals"]} for r in rr]
        pp = [{k: r[k] for k in ("ph", "pd", "pa", "over25")} for r in rr]
        summaries.append({"arm": arm, "season": "pooled", **scores(actual, pp)})
    clim_rows = []
    for season in TARGETS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        cp, co = base_rates(train)
        clim_rows.extend((r, {"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co}) for r in target)
    summaries.append({"arm": "climatology", "season": "pooled", **scores([r for r, _ in clim_rows], [p for _, p in clim_rows])})
    naive_predictions = run_naive(rows)
    for season in TARGETS:
        target = [r for r in rows if r["season"] == season]
        np = [p for p in naive_predictions if p["season"] == season]
        summaries.append({"arm": "naive_trailing10", "season": season, **scores(target, np)})
    summaries.append({"arm": "naive_trailing10", "season": "pooled",
                      **scores([r for r in rows if r["season"] in TARGETS], naive_predictions)})
    by = {(r["arm"], r["season"]): r for r in summaries}
    gate = {}
    clim_pool = by[("climatology", "pooled")]
    for arm in ARMS:
        x = by[(arm, "pooled")]
        gate[arm] = {"verdict": "PASS" if x["ll_1x2"] < clim_pool["ll_1x2"] and x["rps"] < clim_pool["rps"] and x["oull_2_5"] < clim_pool["oull_2_5"] else "FAIL",
                     "comparisons": {"ll_1x2": {"arm": x["ll_1x2"], "climatology": clim_pool["ll_1x2"], "beats": x["ll_1x2"] < clim_pool["ll_1x2"]},
                                     "rps": {"arm": x["rps"], "climatology": clim_pool["rps"], "beats": x["rps"] < clim_pool["rps"]},
                                     "oull_2_5": {"arm": x["oull_2_5"], "base_rate_baseline": clim_pool["oull_2_5"], "beats": x["oull_2_5"] < clim_pool["oull_2_5"]}}}
    pred_csv = HERE / "predictions_dev.csv"
    with pred_csv.open("w", newline="") as f:
        fields = list(all_predictions[0]); w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(all_predictions)
    rederive = independent_gate_zero_2022(pred_csv, rows, by[("gate_zero", "2022")]["ll_1x2"])
    naive = [r for r in summaries if r["arm"] == "naive_trailing10"]
    shrink_delta = max(max(abs(a[k] - b[k]) for k in ("ph", "pd", "pa", "over25"))
                       for a, b in zip([r for r in all_predictions if r["arm"] == "gate_zero"], [r for r in all_predictions if r["arm"] == "shrink"]))
    result = {"spec": {"data": str(DATA), "seasons_loaded": list(SEASONS), "target_seasons": list(TARGETS), "half_life": 270, "maxg": 10, "smoothing": 0.25, "damping": 0.7},
              "fits": fit_info, "metrics": summaries, "naive_trailing10": naive, "dev_gate": gate,
              "checks": {"shrink_max_abs_probability_delta": shrink_delta, "shrink_identity": shrink_delta == 0.0,
                          "independent_gate_zero_2022": rederive, "no_2026_loaded": True, "defence_sign": sign_check}}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (HERE / "results_dev.csv").open("w", newline="") as f:
        fields = ["arm", "season", "n", "ll_1x2", "rps", "oull_2_5"]; w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in summaries)
    return result


def independent_gate_zero_2022(pred_csv, rows, harness):
    target_ids = {r["match_id"]: r for r in rows if r["season"] == "2022"}
    ll = 0.0; n = 0
    with pred_csv.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["arm"] == "gate_zero" and r["season"] == "2022":
                actual = target_ids[r["match_id"]]
                outcome = "ph" if actual["yh"] > actual["ya"] else "pd" if actual["yh"] == actual["ya"] else "pa"
                ll -= math.log(float(r[outcome])); n += 1
    independent = ll / n
    return {"harness": harness, "independent": independent, "difference": independent - harness, "matches": n, "match": abs(independent - harness) < 1e-12}


def run_naive(rows):
    # Match-by-match trailing ten means, with six-observation minimum.
    out = []
    for target in [r for r in rows if r["season"] in TARGETS]:
        hist = [r for r in rows if r["date"] < target["date"]]
        vals = {}
        league = [x for x in hist]
        mu_f = sum(x["yh"] + x["ya"] for x in league) / (2 * len(league))
        for team in {target["hi"], target["ai"]}:
            games = [x for x in hist if x["hi"] == team or x["ai"] == team][-10:]
            if len(games) < 6: vals[team] = (mu_f, mu_f)
            else:
                vals[team] = (sum(x["yh"] if x["hi"] == team else x["ya"] for x in games) / len(games), sum(x["ya"] if x["hi"] == team else x["yh"] for x in games) / len(games))
        lh = max(vals[target["hi"]][0], 1e-12); la = max(vals[target["ai"]][0], 1e-12)
        # Report only: independent Poisson without DC/home advantage.
        ph = sum(pois(x, lh) * pois(y, la) for x in range(11) for y in range(11) if x > y)
        pd = sum(pois(x, lh) * pois(x, la) for x in range(11))
        out.append({"match_id": target["match_id"], "season": target["season"], "ph": ph, "pd": pd, "pa": 1 - ph - pd,
                    "over25": sum(pois(x, lh) * pois(y, la) for x in range(11) for y in range(11) if x + y > 2)})
    return out


def synthetic_sign_checks():
    model = DC()
    model.a[1] = model.a[2] = 0.0
    model.d[1] = 0.0; model.d[2] = 1.0
    low = model.lambdas(2, 1)[0]
    high = model.lambdas(1, 2)[0]
    assert high > low, "higher defence rating did not raise conceded expectation"
    counts = {1: 0, 2: 0}
    base = adjusted_lambdas(model, 1, 2, "gate_zero", counts, {1}, 1.0, "2023")
    entrant = adjusted_lambdas(model, 1, 2, "x2", counts, {1}, 1.0, "2023")
    assert entrant[1] > base[1], "X2 defence offset did not raise entrant conceded expectation"
    return {"higher_defence_raises_conceded_lambda": high > low,
            "x2_defence_offset_raises_entrant_conceded_lambda": entrant[1] > base[1],
            "low_defence_home_lambda": low, "high_defence_home_lambda": high,
            "x2_base_away_lambda": base[1], "x2_entrant_away_lambda": entrant[1]}
