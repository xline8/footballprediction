"""S-DK1 SOT engine: Gate Zero = model_sot.py v5 pattern (model.py Engine,
ported from DK-Superligaen). X5 = trailing-rate blend: predicted total =
0.5 * GZ expected total + 0.5 * trailing-10 naive total (NaiveTracker),
probability via the same NB r=79.94. Seed 2022/2023, scored dev
2023/2024-2024/2025, virgin 2025/2026. Usage: run_s_dk1.py dev|virgin"""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from model import Engine, NaiveTracker, nb_over, NB_R
from common_dk1 import load, VIRGIN, agg, count_gate, write_json

SEED = "2022/2023"; SCORED = ("2023/2024", "2024/2025"); LINE = 9.5
ARMS = ("gate_zero", "x5")

def to_engine(rows):
    out = []
    for m in rows:
        if m["sot_h"] is None or m["shots_h"] is None: continue
        e = {"match_id": m["match_id"], "date": m["date"], "day": m["day"], "season": m["season"],
             "div": "DK1", "home": m["home_id"], "away": m["away_id"],
             "shots_h": m["shots_h"], "shots_a": m["shots_a"], "sot_h": m["sot_h"], "sot_a": m["sot_a"]}
        for side in ("home", "away"):
            e["smshots_" + side] = None; e["xg_" + side] = None
            e["xgot_" + side] = None; e["xgotn_" + side] = None
        out.append(e)
    return out

def run(rows_e, scored_seasons):
    eng = Engine(rows_e, "GZ"); nav = NaiveTracker()
    res = {a: {} for a in ARMS + ("__base", "__naive")}
    preds = []
    prior_totals = []
    for m in rows_e:
        pred = eng.predict(m); mh, ma = eng.reg.means(m["div"], m["day"])
        nh, na = nav.predict(m["div"], m["home"], m["away"], mh, ma)
        naive_total = nh + na; gz_total = pred["exp_h"] + pred["exp_a"]
        y = 1 if m["sot_h"] + m["sot_a"] > LINE else 0
        base_p = (sum(1 for t in prior_totals if t > LINE) / len(prior_totals)) if prior_totals else 0.5
        if m["season"] in scored_seasons:
            vals = {"gate_zero": pred["probs"][LINE], "x5": nb_over(0.5 * gz_total + 0.5 * naive_total, NB_R, LINE),
                    "__base": base_p, "__naive": pred["naive_probs"][LINE]}
            for a, p in vals.items(): res[a].setdefault(m["season"], []).append((p, y))
            if m["season"] == VIRGIN:
                for a in ARMS: preds.append((m, a, vals[a], gz_total if a == "gate_zero" else 0.5 * gz_total + 0.5 * naive_total))
        eng.update(m); nav.update(m); prior_totals.append(m["sot_h"] + m["sot_a"])
    out = {}
    for a, bys in res.items():
        out[a] = {s: agg(v) for s, v in bys.items()}
        pool = [x for v in bys.values() for x in v]
        out[a]["pooled"] = agg(pool)
    return out, preds

def main(cmd):
    if cmd == "dev":
        rows = to_engine(load((SEED,) + SCORED))
        res, _ = run(rows, set(SCORED))
        out = {"protocol": {"seed": SEED, "scored": list(SCORED), "line": LINE, "virgin_read": False},
               "arms": {a: res[a] for a in ARMS}, "baselines": {b: res[b] for b in ("__base", "__naive")}}
        out["gate_zero_pass"] = res["gate_zero"]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res["gate_zero"]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        for a in ARMS: out["arms"][a]["dev_pass"] = res[a]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res[a]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        write_json(HERE / "results_dev.json", out)
        print("dev", {a: res[a]["pooled"] for a in ARMS + ("__base", "__naive")}, "gz_pass", out["gate_zero_pass"])
        return
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        write_json(HERE / "results_virgin.json", {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}); print("virgin unread"); return
    rows = to_engine(load((SEED,) + SCORED + (VIRGIN,)))
    res, preds = run(rows, {VIRGIN})
    devmap = {a: dev["arms"][a] for a in ARMS}; devmap["__base"] = dev["baselines"]["__base"]; devmap["__naive"] = dev["baselines"]["__naive"]
    shipped, legs, _ = count_gate(devmap, res, ARMS, LINE)
    out = {"virgin_read": True, "arms": {a: res[a]["pooled"] for a in ARMS},
           "baselines": {b: res[b]["pooled"] for b in ("__base", "__naive")}, "legs": legs, "shipped_arm": shipped,
           "verdict": "FAIL" if not shipped else ("PASS" if legs[shipped]["calibration"] == "PASS" else "PROVISIONAL")}
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        pdir = HERE.parents[1] / "predictions"; pdir.mkdir(exist_ok=True)
        with (pdir / "s_dk1_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["match_id", "date", "home_id", "away_id", "arm", "pred_total_ft", "p_over_9.5", "pred_total_1h", "pred_total_2h", "actual_total"])
            raw = {m["match_id"]: m for m in load((VIRGIN,))}
            for m, a, p, tot in preds:
                if a != shipped: continue
                w.writerow([m["match_id"], m["date"].isoformat(), m["home"], m["away"], shipped, round(tot, 3), round(p, 4),
                            round(tot * 0.455, 3), round(tot * 0.545, 3), int(raw[m["match_id"]]["sot_h"] + raw[m["match_id"]]["sot_a"])])
        write_json(HERE / "fitted_params_virgin.json", {"market": "sot", "arm": shipped, "nb_r": NB_R, "halves_share_1h": 0.455})
    print("virgin", out["verdict"], shipped, {a: res[a]["pooled"] for a in ARMS})

if __name__ == "__main__":
    main(sys.argv[1])
