#!/usr/bin/env python3
"""T-VE total-shots harness (VE adaptation of the T-BO harness).

Frozen in league/VE-PrimeraDivision/prereg/PREREG_T_VE.md: seed 2025
Clausura regular, dev scored 2026 Apertura regular in two expanding
blocks (R1-7, R8-13), virgin 2026 Clausura regular (transitional).
Primary line 24.5. Arms A (v1), B (v2 level layer), C (E9 trailing-r).
The lambda is tuned on the seed+dev rows and the level cell on the
first dev block (R1-7), mirroring the BO tuning protocol; calibration
is reported in percentage points (predicted - actual in the JSON; the
verdict flips the sign to actual - predicted, the gate uses |.|).
"""
import argparse, csv, json, math, os
from datetime import date
import numpy as np
from model import BASE_HL, M_BAR, LevelLayer, NaiveTracker, BaseRateTracker, ShotsRegressionStore, TrailingR, logloss, nb_over, poisson_over

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data", "ve_matches.csv")
PRED = os.path.join(HERE, "..", "..", "predictions", "t_ve_virgin_predictions.csv")
DEV = ("R1-7", "R8-13")
VIRGIN = "2026 Clausura"
ARMS = ("A", "B", "C")
LINES = (24.5, 23.5, 25.5)
CELLS = [(h, s, k) for h in (30., 60., 120.) for s in (.5, 1.) for k in (20., 50.)]
HALF = .4662  # VE frozen total-shots 1H share (BO used .4633)
PRIMARY = 24.5


def block_of(season, stage, rnd):
    if season == "2025": return "seed"
    if stage == "Clausura": return VIRGIN  # 2026 Clausura rounds are 1-13 too; stage (not round) separates them from Apertura dev blocks
    return "R1-7" if rnd <= 7 else "R8-13"


def load(seasons, virgin=False):
    out = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in set(seasons) or r.get("phase") != "regular" or (r["season"] == "2025" and r.get("stage") != "Clausura") or (r["season"] == "2026" and r.get("stage") not in (("Apertura", "Clausura") if virgin else ("Apertura",))) or r["total_shots_home"] == "" or r["total_shots_away"] == "":
                continue
            d = date.fromisoformat(r["date"])
            rnd = int(float(r["round"])) if r["round"].replace('.', '', 1).isdigit() else int(r["round"].rsplit(' ', 1)[-1])
            out.append({"match_id": r["match_id"], "season": r["season"], "block": block_of(r["season"], r.get("stage"), rnd), "date": r["date"], "day": d.toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"], "shots_h": float(r["total_shots_home"]), "shots_a": float(r["total_shots_away"])})
    out.sort(key=lambda x: (x["day"], int(x["match_id"])))
    return out


def mom_r(a, b, c):
    d = b - c
    return min(1e6, max(1., a / d if d > 0 else 1e6))


def tune(rows):
    reg = ShotsRegressionStore(rows, [3., 10., 30., 100., 300.])
    scores = {x: [0., 0] for x in (3., 10., 30., 100., 300.)}
    res = {x: [0., 0., 0.] for x in scores}
    for m in rows:
        y = m["shots_h"] + m["shots_a"]
        for lam in scores:
            h, a = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            mu = h + a
            scores[lam][1] += logloss(poisson_over(mu, PRIMARY), y > PRIMARY)
            scores[lam][0] += 1
            x = res[lam]
            x[0] += mu * mu
            x[1] += (y - mu) ** 2
            x[2] += mu
    best = min(scores, key=lambda x: (scores[x][1] / scores[x][0], -x))
    return best, mom_r(*res[best]), {str(x): scores[x][1] / scores[x][0] for x in scores}


class Acc:
    def __init__(self):
        self.n = 0
        self.ll = {str(x): 0. for x in LINES}
        self.d = []
        self.sy = 0.
        self.sp = 0.

    def add(self, pp, actual):
        self.n += 1
        for x in LINES:
            self.ll[str(x)] += logloss(pp[x], actual > x)
        self.sp += pp[PRIMARY]
        self.sy += actual > PRIMARY
        self.d.append(pp[PRIMARY] - (actual > PRIMARY))

    def out(self):
        d = np.array(self.d)
        return {"n": self.n, "logloss": {k: v / self.n for k, v in self.ll.items()}, "calibration_pp": float(d.mean() * 100), "calibration_se_pp": float(d.std(ddof=1) / math.sqrt(self.n) * 100), "actual_over_rate_pp": float(self.sy / self.n * 100), "mean_pred_over_pp": float(self.sp / self.n * 100)}


def score(rows, lam, ra, cell, arms, want_preds=False):
    reg = ShotsRegressionStore(rows, [lam])
    naive = NaiveTracker()
    base = BaseRateTracker()
    layer = LevelLayer([cell])
    trail = TrailingR(ra)
    block_rates = {}
    for b in DEV:
        br = [x for x in rows if x["block"] == b]
        cut = min(x["day"] for x in br)
        prior = [x for x in rows if x["day"] < cut]
        block_rates[b] = (sum(x["shots_h"] for x in prior) / len(prior), sum(x["shots_a"] for x in prior) / len(prior))
    methods = list(arms) + ["baseline_league", "baseline_naive"]
    by = {a: {s: Acc() for s in (*DEV, VIRGIN, "pooled")} for a in methods}
    preds = []
    for m in rows:
        total = m["shots_h"] + m["shots_a"]
        eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
        rh, ra0 = reg.league_mu(m["day"], lam)
        nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra0)
        bh, ba = block_rates.get(m["block"], base.predict(m["day"]))
        lt = eh + ea
        ln = nh + na
        lb = bh + ba
        ens = (lt + ln) / 2
        f = layer.factor(0, m["day"])
        rc = trail.value(m["day"])
        probs = {"A": {x: .5 * nb_over(lt, ra, x) + .5 * nb_over(ln, ra, x) for x in LINES}, "B": {x: .5 * nb_over(lt * f, ra, x) + .5 * nb_over(ln * f, ra, x) for x in LINES}, "C": {x: .5 * nb_over(lt, rc, x) + .5 * nb_over(ln, rc, x) for x in LINES}, "baseline_league": {x: poisson_over(lb, x) for x in LINES}, "baseline_naive": {x: .5 * nb_over(ln, ra, x) + .5 * nb_over(ln, ra, x) for x in LINES}}
        if m["block"] in by[methods[0]]:
            for a in methods:
                by[a][m["block"]].add(probs[a], total)
                if m["block"] in DEV:
                    by[a]["pooled"].add(probs[a], total)
            if want_preds and m["block"] == VIRGIN:
                preds.append((m, lt, probs, f, rc))
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"])
        layer.update(0, m["day"], total, ens)
        trail.update(m["day"], total)
    return {a: {s: x.out() for s, x in z.items() if x.n} for a, z in by.items()}, preds


def dev():
    rows = load(("2025", "2026"))
    assert not any(m["block"] not in ("seed", *DEV) for m in rows)
    lam, ra, tune_ll = tune(rows)
    cell = CELLS[0]
    best = None
    bestll = 1e9
    for c in CELLS:
        z, _ = score(rows, lam, ra, c, ("A",))
        x = z["A"]["R1-7"]["logloss"][str(PRIMARY)]
        if x < bestll:
            bestll = x
            best = c
    cell = best
    metrics, _ = score(rows, lam, ra, cell, ARMS)
    passes = {a: metrics[a]["pooled"]["logloss"][str(PRIMARY)] < metrics["baseline_league"]["pooled"]["logloss"][str(PRIMARY)] and metrics[a]["pooled"]["logloss"][str(PRIMARY)] < metrics["baseline_naive"]["pooled"]["logloss"][str(PRIMARY)] for a in ARMS}
    p = {"lambda": lam, "r_A": ra, "level_cell": list(cell), "primary_line": PRIMARY, "ladder": list(LINES), "half_split": [HALF, 1 - HALF], "base_half_life": BASE_HL}
    out = {"protocol": {"seed": "2025 Clausura regular", "dev_blocks": list(DEV), "virgin_not_loaded": True, "primary_line": PRIMARY}, "tuning": {"lambda_logloss_24_5": tune_ll, "lambda": lam, "r_A": ra}, "metrics": metrics, "dev_pass": passes, "fitted_params": p}
    json.dump(out, open(os.path.join(HERE, "results_dev.json"), "w"), indent=2)
    json.dump(p, open(os.path.join(HERE, "fitted_params.json"), "w"), indent=2)
    print(json.dumps(out, indent=2))
    return out


def virgin(dev):
    if not dev["dev_pass"].get("A"):
        out = {"verdict": "FAIL", "virgin_read": False, "reason": "arm A failed dev gate; virgin NOT read", "read_arms": [], "dev_pass": dev["dev_pass"]}
        json.dump(out, open(os.path.join(HERE, "results_virgin.json"), "w"), indent=2)
        json.dump({"virgin_read": False, "reason": out["reason"]}, open(os.path.join(HERE, "fitted_params_virgin.json"), "w"), indent=2)
        print(json.dumps(out, indent=2))
        return out
    passing = [a for a in ARMS if dev["dev_pass"].get(a)]
    rows = load(("2025", "2026"), virgin=True)  # seasons, not the VIRGIN block label; Clausura rows included only in virgin mode
    p = dev["fitted_params"]
    metrics, preds = score(rows, p["lambda"], p["r_A"], tuple(p["level_cell"]), tuple(passing), True)
    out = {"protocol": {"virgin_season": VIRGIN, "transitional": True, "scored_n": metrics[passing[0]][VIRGIN]["n"]}, "virgin_read": True, "read_arms": passing, "metrics": {a: metrics[a][VIRGIN] for a in passing + ["baseline_league", "baseline_naive"]}, "dev_pass": dev["dev_pass"]}
    eligible = []
    ref = "A"
    base = min(out["metrics"][x]["logloss"][str(PRIMARY)] for x in ("baseline_league", "baseline_naive"))
    for a in passing:
        v = out["metrics"][a]
        sign = a == "A" or sum(dev["metrics"][a][s]["logloss"][str(PRIMARY)] <= dev["metrics"]["A"][s]["logloss"][str(PRIMARY)] for s in DEV) >= len(DEV) / 2  # prereg: at least half the dev blocks (VE has 2; BO's literal 2 was its half of 4)
        v["leg_i"] = v["logloss"][str(PRIMARY)] <= out["metrics"][ref]["logloss"][str(PRIMARY)] and v["logloss"][str(PRIMARY)] <= base
        v["leg_ii"] = abs(v["calibration_pp"]) <= 1.0 or abs(v["calibration_pp"]) <= 1.0 + v["calibration_se_pp"]
        v["leg_iii"] = sign
        v["virgin_(i)"] = v["leg_i"]
        v["virgin_(ii)"] = v["leg_ii"]
        v["virgin_(iii)"] = v["leg_iii"]
        if v["leg_i"] and v["leg_ii"] and v["leg_iii"]:
            eligible.append(a)
    chosen = min(eligible, key=lambda a: (out["metrics"][a]["logloss"][str(PRIMARY)], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = chosen
    out["verdict"] = "PASS" if chosen else "FAIL"
    out["calibration_breach_plus_se_pp"] = {a: abs(v["calibration_pp"]) - 1. - v["calibration_se_pp"] for a, v in out["metrics"].items() if a in passing}
    json.dump(out, open(os.path.join(HERE, "results_virgin.json"), "w"), indent=2)
    if chosen:
        write_predictions(preds, chosen, p["r_A"])
        json.dump({"arm": chosen, "r_A": p["r_A"], "level_cell": p["level_cell"], "half_split": [HALF, 1 - HALF]}, open(os.path.join(HERE, "fitted_params_virgin.json"), "w"), indent=2)
    print(json.dumps(out, indent=2))
    return out


def write_predictions(preds, arm, ra):
    with open(PRED, "w", newline="") as f:
        fields = ["match_id", "date", "home_team", "away_team", "arm", "pred_total_ft", "p_over_24_5", "p_over_23_5", "p_over_25_5", "pred_total_1h", "pred_total_2h", "actual_total"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m, mu, probs, f, rc in preds:
            q = {"match_id": m["match_id"], "date": m["date"], "home_team": m["home"], "away_team": m["away"], "arm": arm, "pred_total_ft": mu, "pred_total_1h": mu * HALF, "pred_total_2h": mu * (1 - HALF), "actual_total": m["shots_h"] + m["shots_a"]}
            q.update({f"p_over_{x}".replace(".", "_"): probs[arm][x] for x in LINES})
            w.writerow(q)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=("dev", "virgin"))
    a = ap.parse_args()
    d = dev()
    if a.step == "virgin":
        virgin(d)


if __name__ == "__main__":
    main()
