#!/usr/bin/env python3
"""T-J1 dev and virgin harness."""
import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

from model import (BASE_HL, M_BAR, LevelLayer, NaiveTracker, BaseRateTracker,
                   ShotsRegressionStore, TrailingR, logloss, nb_over,
                   poisson_over)

HERE = Path(__file__).resolve().parent
J1 = HERE.parents[1] / "data" / "in_matches.csv"
PRED = HERE.parents[1] / "predictions" / "t_in_virgin_predictions.csv"
LAM_GRID = [3.0, 10.0, 30.0, 100.0, 300.0]
CELLS = [(hl, s, k) for hl in (30.0, 60.0, 120.0)
         for s in (0.5, 1.0) for k in (20.0, 50.0)]
LINES = (25.5, 26.5, 27.5)
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
VIRGIN = "2025/2026"


def load(seasons):
    wanted = set(seasons)
    rows = []
    with J1.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in wanted:
                continue
            if r["season"] in ("2025/2026", "2026/2027") and r["season"] not in wanted:
                continue
            if r["total_shots_home"] == "" or r["total_shots_away"] == "":
                continue
            d = date.fromisoformat(r["date"])
            rows.append({
                "match_id": r["match_id"], "season": r["season"], "date": r["date"],
                "day": d.toordinal(), "home_id": int(r["home_team_id"]),
                "away_id": int(r["away_team_id"]), "home": r["home_team"],
                "away": r["away_team"], "shots_h": float(r["total_shots_home"]),
                "shots_a": float(r["total_shots_away"]),
            })
    rows.sort(key=lambda x: (x["day"], int(x["match_id"])))
    assert all((a["day"], int(a["match_id"])) < (b["day"], int(b["match_id"]))
               for a, b in zip(rows, rows[1:]))
    return rows


def mom_r(s_lam2, s_res2, s_lam):
    den = s_res2 - s_lam
    return min(1e6, max(1.0, s_lam2 / den if den > 0 else 1e6))


def tune(rows):
    reg = ShotsRegressionStore(rows, LAM_GRID)
    ll = {x: [0, 0.0] for x in LAM_GRID}
    residual = {x: [0.0, 0.0, 0.0] for x in LAM_GRID}
    for m in rows:
        total = m["shots_h"] + m["shots_a"]
        for lam in LAM_GRID:
            eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            lt = eh + ea
            if m["season"] == "2022/2023":
                ll[lam][0] += 1
                ll[lam][1] += logloss(poisson_over(lt, 26.5), total > 26.5)
            if m["season"] in ("2021/2022", "2022/2023"):
                x = residual[lam]
                x[0] += lt * lt; x[1] += (total - lt) ** 2; x[2] += lt
    tune_ll = {str(lam): ll[lam][1] / ll[lam][0] for lam in LAM_GRID}
    # max lambda on exact ties.
    best_lam = min(LAM_GRID, key=lambda x: (tune_ll[str(x)], -x))
    x = residual[best_lam]
    return best_lam, mom_r(*x), tune_ll


class Acc:
    def __init__(self):
        self.n = 0; self.ll = {str(x): 0.0 for x in LINES}; self.sp = 0.0
        self.sy = 0.0; self.mae = 0.0; self.d = []

    def add(self, probs, point, actual):
        self.n += 1
        for line in LINES:
            self.ll[str(line)] += logloss(probs[line], actual > line)
        p = probs[26.5]; y = float(actual > 26.5)
        self.sp += p; self.sy += y; self.mae += abs(point - actual); self.d.append(p - y)

    def out(self):
        n = self.n
        mean_d = (self.sp - self.sy) / n
        se_pp = (sum((d - mean_d) ** 2 for d in self.d) / n) ** 0.5 / (n ** 0.5) * 100.0
        return {"n": n, "logloss": {k: v / n for k, v in self.ll.items()},
                "calibration_pp": mean_d * 100.0, "calibration_se_pp": se_pp,
                "actual_over_rate_pp": self.sy / n * 100.0,
                "mean_pred_over_pp": self.sp / n * 100.0,
                "mae": self.mae / n}


def probs(mu, r, nb=True):
    fn = nb_over if nb else poisson_over
    return {line: fn(mu, r, line) if nb else fn(mu, line) for line in LINES}


def base_prediction(reg, naive, base, m, lam):
    eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
    rh, ra = reg.league_mu(m["day"], lam)
    nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra)
    bh, ba = base.predict(m["day"])
    return eh + ea, nh + na, bh + ba


def choose_cell(rows, lam, r_a):
    reg = ShotsRegressionStore(rows, [lam]); naive = NaiveTracker(); base = BaseRateTracker()
    layer = LevelLayer(CELLS); acc = [Acc() for _ in CELLS]
    for m in rows:
        total = m["shots_h"] + m["shots_a"]
        lt, ln, _ = base_prediction(reg, naive, base, m, lam)
        ensemble = (lt + ln) / 2.0
        if m["season"] == "2022/2023":
            for i in range(len(CELLS)):
                f = layer.factor(i, m["day"])
                acc[i].add({x: 0.5 * nb_over(lt * f, r_a, x) +
                            0.5 * nb_over(ln * f, r_a, x) for x in LINES},
                           ensemble * f, total)
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"])
        for i in range(len(CELLS)):
            layer.update(i, m["day"], total, ensemble)
    scores = [a.out()["logloss"]["26.5"] for a in acc]
    best = min(range(len(CELLS)), key=lambda i: (scores[i], -CELLS[i][0], CELLS[i][1], -CELLS[i][2]))
    return CELLS[best], {"cell": list(CELLS[best]), "scores": [
        {"cell": list(c), "ll_25_5": scores[i]} for i, c in enumerate(CELLS)]}


def score_pass(rows, lam, r_a, cell, arms, collect_predictions=False):
    reg = ShotsRegressionStore(rows, [lam]); naive = NaiveTracker(); base = BaseRateTracker()
    layer = LevelLayer([cell]); trailing = TrailingR(r_a)
    methods = list(arms) + ["baseline_league", "baseline_naive"]
    by = {a: {s: Acc() for s in ("2022/2023", "2023/2024", "2024/2025", VIRGIN, "pooled")} for a in methods}
    predictions = []
    for m in rows:
        total = m["shots_h"] + m["shots_a"]
        lt, ln, lb = base_prediction(reg, naive, base, m, lam)
        ens = (lt + ln) / 2.0
        f = layer.factor(0, m["day"])
        r_c = trailing.value(m["day"])
        values = {
            "A": (ens, r_a), "B": (ens * f, r_a), "C": (ens, r_c),
            "baseline_league": (lb, None), "baseline_naive": (ln, None),
        }
        arm_probs = {
            "A": {line: 0.5 * nb_over(lt, r_a, line) +
                  0.5 * nb_over(ln, r_a, line) for line in LINES},
            "B": {line: 0.5 * nb_over(lt * f, r_a, line) +
                  0.5 * nb_over(ln * f, r_a, line) for line in LINES},
            "C": {line: 0.5 * nb_over(lt, r_c, line) +
                  0.5 * nb_over(ln, r_c, line) for line in LINES},
        }
        if m["season"] in by[methods[0]]:
            for arm in methods:
                point, rr = values[arm]
                pp = arm_probs[arm] if arm in arm_probs else probs(point, rr, nb=rr is not None)
                by[arm][m["season"]].add(pp, point, total)
                by[arm]["pooled"].add(pp, point, total) if m["season"] in ("2022/2023", "2023/2024", "2024/2025") else None
            if collect_predictions and m["season"] == VIRGIN:
                predictions.append((m, values, f, r_c, arm_probs))
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"])
        layer.update(0, m["day"], total, ens)
        trailing.update(m["day"], total)
    return {a: {s: by[a][s].out() for s in by[a] if by[a][s].n}
            for a in by}, predictions


def write_dev_csv(result):
    fields = ["method", "season", "n", "ll_25_5", "ll_26_5", "ll_27_5",
              "calibration_pp", "mae"]
    with (HERE / "results_dev.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for method, seasons in result["metrics"].items():
            for season, x in seasons.items():
                w.writerow({"method": method, "season": season, "n": x["n"],
                            "ll_25_5": x["logloss"]["25.5"],
                            "ll_26_5": x["logloss"]["26.5"],
                            "ll_27_5": x["logloss"]["27.5"],
                            "calibration_pp": x["calibration_pp"], "mae": x["mae"]})


def dev():
    start = time.time(); rows = load(SEASONS)
    counts = {s: sum(m["season"] == s for m in rows) for s in SEASONS}
    assert counts == {"2021/2022": 115, "2022/2023": 117, "2023/2024": 139, "2024/2025": 163}, counts
    assert not any(m["season"] in ("2025/2026", "2026/2027") for m in rows)
    lam, r_a, tune_lam = tune(rows)
    cell, tune_layer = choose_cell(rows, lam, r_a)
    metrics, _ = score_pass(rows, lam, r_a, cell, ("A", "B", "C"))
    metrics = {a: {s: x for s, x in seasons.items() if s != VIRGIN}
               for a, seasons in metrics.items()}
    dev_pass = {}
    for arm in ("A", "B", "C"):
        pool = metrics[arm]["pooled"]["logloss"]["26.5"]
        dev_pass[arm] = pool < metrics["baseline_league"]["pooled"]["logloss"]["26.5"] and pool < metrics["baseline_naive"]["pooled"]["logloss"]["26.5"]
    params = {"lambda": lam, "r_A": r_a, "level_cell": list(cell), "M_bar": M_BAR,
              "trailing_r_window": 200, "primary_line": 26.5,
              "ladder": list(LINES), "half_split": [0.447, 0.553],
              "base_half_life": BASE_HL, "refit_days": 7,
              "eta_clip": [-6.0, 4.0]}
    (HERE / "fitted_params.json").write_text(json.dumps(params, indent=2) + "\n")
    result = {"protocol": {"dev_seasons_loaded": list(SEASONS), "counts": counts,
                            "tuning_season": "2022/2023", "gate_pool": ["2022/2023", "2023/2024", "2024/2025"],
                            "primary_line": 26.5, "runtime_seconds": time.time() - start},
              "tuning": {"lambda_logloss_24_5": tune_lam, "lambda": lam,
                         "r_A": r_a, "level": tune_layer},
              "metrics": metrics, "dev_pass": dev_pass, "fitted_params": params}
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    write_dev_csv(result)
    print(json.dumps({"lambda": lam, "r_A": r_a, "level_cell": list(cell),
                      "dev_pass": dev_pass, "runtime_seconds": result["protocol"]["runtime_seconds"]}, indent=2))


def virgin(export_arm=None, requested_arms=None):
    start = time.time(); dev_result = json.loads((HERE / "results_dev.json").read_text())
    passing = [a for a in ("A", "B", "C") if dev_result["dev_pass"].get(a) is True and (requested_arms is None or a in requested_arms)]
    if export_arm is not None and export_arm not in passing:
        raise SystemExit("refusing virgin export: arm %s did not pass the recorded dev gate" % export_arm)
    rows = load(SEASONS + (VIRGIN,))
    assert sum(m["season"] == VIRGIN for m in rows) == 91
    p = dev_result["fitted_params"]; cell = tuple(p["level_cell"])
    metrics, preds = score_pass(rows, p["lambda"], p["r_A"], cell, tuple(passing), True)
    out = {"protocol": {"state_pass": list(SEASONS) + [VIRGIN], "virgin_season": VIRGIN,
                         "n": 91, "scored_arms": passing, "runtime_seconds": time.time() - start},
           "metrics": {a: metrics[a][VIRGIN] for a in passing + ["baseline_league", "baseline_naive"]},
           "export_arm": export_arm}
    # Accumulators above only expose named seasons, so virgin is present even though
    # it is not part of the dev-only season set in the initial accumulator.
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    eligible=[]
    best_base=min(out["metrics"][a]["logloss"]["26.5"] for a in ("baseline_league","baseline_naive"))
    reference="A" if "A" in passing else min(passing, key=lambda a: dev_result["metrics"][a]["pooled"]["logloss"]["26.5"])
    for arm in passing:
        v=out["metrics"][arm]; sign=arm==reference or sum(dev_result["metrics"][arm][s]["logloss"]["26.5"]<=dev_result["metrics"][reference][s]["logloss"]["26.5"] for s in ("2022/2023","2023/2024","2024/2025"))>=2
        if v["logloss"]["26.5"]<=out["metrics"][reference]["logloss"]["26.5"] and v["logloss"]["26.5"]<=best_base and abs(v["calibration_pp"])<=1.0+v["calibration_se_pp"] and sign: eligible.append(arm)
    chosen=min(eligible,key=lambda a:(out["metrics"][a]["logloss"]["26.5"],("A","B","C").index(a))) if eligible else None
    if chosen: write_predictions(preds, chosen, p["r_A"]); out["shipped_arm"]=chosen
    else: out["shipped_arm"]=None
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"scored_arms": passing, "virgin": out["metrics"],
                      "runtime_seconds": out["protocol"]["runtime_seconds"]}, indent=2))


def write_predictions(predictions, arm, r_a):
    PRED.parent.mkdir(parents=True, exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "arm", "pred_total_ft",
              "p_over_25_5", "p_over_26_5", "p_over_27_5", "pred_total_1h",
              "p_over_1h_10_5", "p_over_1h_11_5", "p_over_1h_12_5", "pred_total_2h",
              "p_over_2h_12_5", "p_over_2h_13_5", "p_over_2h_14_5", "actual_total"]
    p = json.loads((HERE / "fitted_params.json").read_text()); cell = tuple(p["level_cell"])
    with PRED.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for m, values, factor, r_c, arm_probs in predictions:
            mu, rr = values[arm]; r = r_c if arm == "C" else r_a
            ft = arm_probs[arm]; mu1, mu2 = mu * 0.447, mu * 0.553
            q = {"match_id": m["match_id"], "date": m["date"], "home_team": m["home"],
                 "away_team": m["away"], "arm": arm, "pred_total_ft": mu,
                 "actual_total": m["shots_h"] + m["shots_a"], "pred_total_1h": mu1,
                 "pred_total_2h": mu2}
            for line in LINES: q["p_over_" + str(line).replace(".", "_")] = ft[line]
            for line in (10.5, 11.5, 12.5): q["p_over_1h_" + str(line).replace(".", "_")] = nb_over(mu1, r, line)
            for line in (12.5, 13.5, 14.5): q["p_over_2h_" + str(line).replace(".", "_")] = nb_over(mu2, r, line)
            w.writerow(q)
    (HERE / "fitted_params_virgin.json").write_text(json.dumps({"arm": arm, "r_A": r_a, "level_cell": list(cell), "half_split": [0.447, 0.553]}, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="step", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin"); v.add_argument("--arms", nargs="+", choices=("A", "B", "C")); v.add_argument("--export-arm", choices=("A", "B", "C"))
    args = ap.parse_args()
    if args.step == "dev": dev()
    else: virgin(args.export_arm, tuple(args.arms) if args.arms else None)


if __name__ == "__main__":
    main()
