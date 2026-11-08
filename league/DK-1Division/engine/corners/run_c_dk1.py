"""C-DK1 corners engine: Gate Zero = model_corners_v3 pattern (core.py,
ported from DK-Superligaen: shot-rate factors + possession/big-chance
multiplier, beta fitted per season-block on prior data). X7 = box-touch
multiplier arm (core multiplier non-GZ branch). X5 = trailing-rate blend:
mu = 0.5*mu_GZ + 0.5*naive trailing-10 total (attach_naive), GZ's r.
Seed 2022/2023 (params for the first scored season fit on the seed),
scored dev 2023/2024-2024/2025, virgin 2025/2026.
Usage: run_c_dk1.py dev|virgin"""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import core
from common_dk1 import VIRGIN, agg, count_gate, write_json, DATA

SEED = "2022/2023"; SCORED = ("2023/2024", "2024/2025"); LINE = 9.5
ARMS = ("gate_zero", "x5", "x7")

def build(seasons):
    rows = core.load(str(DATA), set(seasons))
    rows = core.FeatureBuilder(rows).build()
    rows = core.attach_naive(rows)
    return rows

def score(rows, scored):
    res = {a: {} for a in ARMS + ("__base", "__naive")}; preds = []
    for S in scored:
        train = [r for r in rows if r["season"] < S]
        params = {a: core.fit_params(train, a) for a in ("gate_zero", "x7")}
        for r in [x for x in rows if x["season"] == S]:
            y = 1 if r["y"] > LINE else 0
            mu_gz, rr = core.model_prediction(r, params["gate_zero"], "gate_zero")
            mu_x7, _ = core.model_prediction(r, params["x7"], "x7")
            naive_mu = (r["naive_home"] + r["naive_away"]) / 2.0
            vals = {"gate_zero": core.over_prob(mu_gz, rr, LINE),
                    "x7": core.over_prob(mu_x7, rr, LINE),
                    "x5": core.over_prob(0.5 * mu_gz + 0.5 * naive_mu, rr, LINE),
                    "__base": core.over_prob(r["season_base_mu"], r["season_r_base"], LINE),
                    "__naive": core.over_prob(naive_mu, r["season_r_base"], LINE)}
            mus = {"gate_zero": mu_gz, "x7": mu_x7, "x5": 0.5 * mu_gz + 0.5 * naive_mu}
            for a, p in vals.items(): res[a].setdefault(S, []).append((p, y))
            if S == VIRGIN:
                for a in ARMS: preds.append((r, a, vals[a], mus[a], params))
    out = {}
    for a, bys in res.items():
        out[a] = {s: agg(v) for s, v in bys.items()}; out[a]["pooled"] = agg([x for v in bys.values() for x in v])
    return out, preds

def main(cmd):
    if cmd == "dev":
        rows = build((SEED,) + SCORED)
        res, _ = score(rows, SCORED)
        out = {"protocol": {"seed": SEED, "scored": list(SCORED), "line": LINE, "virgin_read": False},
               "arms": {a: res[a] for a in ARMS}, "baselines": {b: res[b] for b in ("__base", "__naive")}}
        out["gate_zero_pass"] = res["gate_zero"]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res["gate_zero"]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        for a in ARMS: out["arms"][a]["dev_pass"] = res[a]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res[a]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        write_json(HERE / "results_dev.json", out)
        print("dev", {a: res[a]["pooled"] for a in ARMS + ("__base", "__naive")}, "gz_pass", out["gate_zero_pass"]); return
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        write_json(HERE / "results_virgin.json", {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}); print("virgin unread"); return
    rows = build((SEED,) + SCORED + (VIRGIN,))
    res, preds = score(rows, (VIRGIN,))
    devmap = {a: dev["arms"][a] for a in ARMS}; devmap["__base"] = dev["baselines"]["__base"]; devmap["__naive"] = dev["baselines"]["__naive"]
    shipped, legs, _ = count_gate(devmap, res, ARMS, LINE)
    out = {"virgin_read": True, "arms": {a: res[a]["pooled"] for a in ARMS},
           "baselines": {b: res[b]["pooled"] for b in ("__base", "__naive")}, "legs": legs, "shipped_arm": shipped,
           "verdict": "FAIL" if not shipped else ("PASS" if legs[shipped]["calibration"] == "PASS" else "PROVISIONAL")}
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        pdir = HERE.parents[1] / "predictions"; pdir.mkdir(exist_ok=True)
        with (pdir / "c_dk1_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["match_id", "date", "home", "away", "arm", "pred_total_ft", "p_over_9.5", "pred_total_1h", "pred_total_2h", "actual_total"])
            for r, a, p, mu, params in preds:
                if a != shipped: continue
                w.writerow([r["match_id"], r["date"].isoformat(), r["home"], r["away"], shipped, round(mu, 3), round(p, 4),
                            round(mu * 0.469, 3), round(mu * 0.531, 3), int(r["y"])])
        pr = preds[0][4]
        write_json(HERE / "fitted_params_virgin.json", {"market": "corners", "arm": shipped, "params": pr[shipped] if shipped in pr else pr["gate_zero"], "halves_share_1h": 0.469})
    print("virgin", out["verdict"], shipped, {a: res[a]["pooled"] for a in ARMS})

if __name__ == "__main__":
    main(sys.argv[1])
