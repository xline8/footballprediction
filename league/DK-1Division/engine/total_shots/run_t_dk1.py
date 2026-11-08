"""T-DK1 total-shots engine: Gate Zero = shots-family pattern (model.py
ShotsRegressionStore joint Poisson ridge; lambda tuned on the tuning
window by Poisson LL at 25.5, NB r by method of moments — the
DK-Superligaen run_t pattern). X5 = trailing-rate blend (0.5*GZ total +
0.5*NaiveTracker total). X7 = box-touch territorial multiplier with beta
fitted on prior data over the BBT-style grid by binary LL at 26.5.
Seed/tuning 2022/2023, scored dev 2023/2024-2024/2025, virgin 2025/2026.
Usage: run_t_dk1.py dev|virgin"""
import csv, json, math, sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from model import ShotsRegressionStore, NaiveTracker, BaseRateTracker, nb_over, poisson_over, logloss
from common_dk1 import load, VIRGIN, agg, count_gate, write_json

SEED = "2022/2023"; SCORED = ("2023/2024", "2024/2025"); LINE = 26.5
ARMS = ("gate_zero", "x5", "x7")
LAM_GRID = [3.0, 10.0, 30.0, 100.0, 300.0]
BBT = (-0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04)

def to_rows(rows):
    return [{"home_id": m["home_id"], "away_id": m["away_id"], "day": m["day"], "season": m["season"],
             "shots_h": m["shots_h"], "shots_a": m["shots_a"], "match_id": m["match_id"], "date": m["date"],
             "bt_h": m["bt_h"], "bt_a": m["bt_a"]} for m in rows if m["shots_h"] is not None]

def tune(rows):
    reg = ShotsRegressionStore(rows, LAM_GRID)
    ll = {x: [0, 0.0] for x in LAM_GRID}; resid = {x: [0.0, 0.0, 0.0] for x in LAM_GRID}
    for m in rows:
        for lam in LAM_GRID:
            eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            tot = m["shots_h"] + m["shots_a"]; lt = eh + ea
            ll[lam][0] += 1; ll[lam][1] += logloss(poisson_over(lt, 25.5), tot > 25.5)
            x = resid[lam]; x[0] += lt * lt; x[1] += (tot - lt) ** 2; x[2] += lt
    best = min(LAM_GRID, key=lambda x: ll[x][1] / ll[x][0])
    s2, sr2, sl = resid[best]
    den = sr2 - sl
    r = 500.0 if den <= 0 else min(max(s2 / den, 2.0), 500.0)
    return best, r

class Terr:
    """Trailing-10 box-touch differential state (date-causal updates in caller)."""
    def __init__(self): self.h = defaultdict(lambda: deque(maxlen=10))
    def z(self, home, away):
        def rel(t):
            v = self.h[t]
            if len(v) < 6: return None
            f = sum(x[0] for x in v) / len(v); a = sum(x[1] for x in v) / len(v)
            return f - a
        rh, ra = rel(home), rel(away)
        return None if rh is None or ra is None else rh - ra
    def update(self, m):
        if m["bt_h"] is not None and m["bt_a"] is not None:
            self.h[m["home_id"]].append((m["bt_h"], m["bt_a"])); self.h[m["away_id"]].append((m["bt_a"], m["bt_h"]))

def run(rows, scored, tune_rows):
    lam, r = tune(tune_rows)
    reg = ShotsRegressionStore(rows, [lam]); nav = NaiveTracker(); base = BaseRateTracker(); terr = Terr()
    # fit x7 beta on tune_rows: replay causally
    reg_t = ShotsRegressionStore(tune_rows, [lam]); terr_t = Terr(); cand = {b: [0.0, 0] for b in BBT}
    for m in tune_rows:
        eh, ea = reg_t.predict(m["home_id"], m["away_id"], m["day"], lam)
        z = terr_t.z(m["home_id"], m["away_id"]); tot = m["shots_h"] + m["shots_a"]
        if z is not None:
            for b in BBT:
                mu = (eh + ea) * min(1.25, max(0.8, math.exp(b * z)))
                p = nb_over(mu, r, LINE)
                cand[b][0] += -(1 if tot > LINE else 0) * math.log(max(p, 1e-12)) - (0 if tot > LINE else 1) * math.log(max(1 - p, 1e-12)); cand[b][1] += 1
        terr_t.update(m)
    beta = min(BBT, key=lambda b: (cand[b][0] / max(cand[b][1], 1), abs(b))) if any(cand[b][1] for b in BBT) else 0.0
    res = {a: {} for a in ARMS + ("__base", "__naive")}; preds = []
    for m in rows:
        eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
        gz = eh + ea
        mh, ma = reg.league_mu(m["day"], lam)
        nh, na = nav.predict(m["home_id"], m["away_id"], mh, ma)
        bm = sum(base.predict(m["day"])); z = terr.z(m["home_id"], m["away_id"])
        x7 = gz * (min(1.25, max(0.8, math.exp(beta * z))) if z is not None else 1.0)
        if m["season"] in scored:
            tot = m["shots_h"] + m["shots_a"]; y = 1 if tot > LINE else 0
            vals = {"gate_zero": nb_over(gz, r, LINE), "x5": nb_over(0.5 * gz + 0.5 * (nh + na), r, LINE),
                    "x7": nb_over(x7, r, LINE), "__base": nb_over(bm, r, LINE), "__naive": nb_over(nh + na, r, LINE)}
            mus = {"gate_zero": gz, "x5": 0.5 * gz + 0.5 * (nh + na), "x7": x7}
            for a, p in vals.items(): res[a].setdefault(m["season"], []).append((p, y))
            if m["season"] == VIRGIN:
                for a in ARMS: preds.append((m, a, vals[a], mus[a]))
        nav.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"]); terr.update(m)
    out = {}
    for a, bys in res.items():
        out[a] = {s: agg(v) for s, v in bys.items()}; out[a]["pooled"] = agg([x for v in bys.values() for x in v])
    return out, preds, {"lambda": lam, "r": r, "beta_x7": beta}

def main(cmd):
    if cmd == "dev":
        rows = to_rows(load((SEED,) + SCORED)); tune_rows = [m for m in rows if m["season"] == SEED]
        res, _, prm = run(rows, set(SCORED), tune_rows)
        out = {"protocol": {"seed": SEED, "scored": list(SCORED), "line": LINE, "params": prm, "virgin_read": False},
               "arms": {a: res[a] for a in ARMS}, "baselines": {b: res[b] for b in ("__base", "__naive")}}
        out["gate_zero_pass"] = res["gate_zero"]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res["gate_zero"]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        for a in ARMS: out["arms"][a]["dev_pass"] = res[a]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res[a]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        write_json(HERE / "results_dev.json", out)
        print("dev", {a: res[a]["pooled"] for a in ARMS + ("__base", "__naive")}, prm, "gz_pass", out["gate_zero_pass"]); return
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        write_json(HERE / "results_virgin.json", {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}); print("virgin unread"); return
    rows = to_rows(load((SEED,) + SCORED + (VIRGIN,)))
    tune_rows = [m for m in rows if m["season"] != VIRGIN]
    res, preds, prm = run(rows, {VIRGIN}, tune_rows)
    devmap = {a: dev["arms"][a] for a in ARMS}; devmap["__base"] = dev["baselines"]["__base"]; devmap["__naive"] = dev["baselines"]["__naive"]
    shipped, legs, _ = count_gate(devmap, res, ARMS, LINE)
    out = {"virgin_read": True, "params": prm, "arms": {a: res[a]["pooled"] for a in ARMS},
           "baselines": {b: res[b]["pooled"] for b in ("__base", "__naive")}, "legs": legs, "shipped_arm": shipped,
           "verdict": "FAIL" if not shipped else ("PASS" if legs[shipped]["calibration"] == "PASS" else "PROVISIONAL")}
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        pdir = HERE.parents[1] / "predictions"; pdir.mkdir(exist_ok=True)
        with (pdir / "t_dk1_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["match_id", "date", "home_id", "away_id", "arm", "pred_total_ft", "p_over_26.5", "pred_total_1h", "pred_total_2h", "actual_total"])
            for m, a, p, mu in preds:
                if a != shipped: continue
                w.writerow([m["match_id"], m["date"].isoformat(), m["home_id"], m["away_id"], shipped, round(mu, 3), round(p, 4),
                            round(mu * 0.461, 3), round(mu * 0.539, 3), int(m["shots_h"] + m["shots_a"])])
        write_json(HERE / "fitted_params_virgin.json", {"market": "total_shots", "arm": shipped, **prm, "halves_share_1h": 0.461})
    print("virgin", out["verdict"], shipped, {a: res[a]["pooled"] for a in ARMS})

if __name__ == "__main__":
    main(sys.argv[1])
