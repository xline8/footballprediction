"""K-ID cards engine: event-unified yellows with Gate Zero and X5.
Usage: run_k_id.py dev|virgin."""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from model import Online, estimate_r, nb_over
from common_id import load, VIRGIN, agg, count_gate, write_json

SEED = "2021/2022"; SCORED = ("2022/2023", "2023/2024", "2024/2025"); LINE = 4.5
ARMS = ("gate_zero", "x5")

def to_rows(rows):
    return [{"home_id": m["home_id"], "away_id": m["away_id"], "day": m["day"],
             "kickoff_utc": m["date"].isoformat() + "T00:00:00Z", "yh": m["cards_h"], "ya": m["cards_a"],
             "y": m["cards_h"] + m["cards_a"], "referee": m["referee"], "season": m["season"],
             "match_id": m["match_id"], "date": m["date"]} for m in rows
            if m["cards_h"] is not None and m["cards_a"] is not None]

def run(rows, scored_seasons, seed_season):
    on = Online(); seed_recs = []; rs_set = [False]
    res = {a: {} for a in ARMS + ("__base", "__naive")}; preds = []
    rs = {"model": 500.0, "base": 500.0, "naive": 500.0}
    for r in rows:
        p = on.prediction(r, "gate_zero")
        if r["season"] == seed_season:
            seed_recs.append({"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        if r["season"] in scored_seasons and seed_recs and not rs_set[0]:
            rs = {k: estimate_r(seed_recs, k) for k in rs}; rs_set[0] = True
        if r["season"] in scored_seasons:
            y = 1 if r["y"] > LINE else 0
            vals = {"gate_zero": nb_over(p["model"], rs["model"], LINE),
                    "x5": nb_over(0.5 * p["model"] + 0.5 * p["naive"], rs["model"], LINE),
                    "__base": nb_over(p["base"], rs["base"], LINE),
                    "__naive": nb_over(p["naive"], rs["naive"], LINE)}
            for a, pv in vals.items(): res[a].setdefault(r["season"], []).append((pv, y))
            if r["season"] == VIRGIN:
                for a in ARMS: preds.append((r, a, vals[a], p["model"] if a == "gate_zero" else 0.5 * p["model"] + 0.5 * p["naive"]))
        on.update(r)
    out = {}
    for a, bys in res.items():
        out[a] = {s: agg(v) for s, v in bys.items()}; out[a]["pooled"] = agg([x for v in bys.values() for x in v])
    return out, preds, rs

def main(cmd):
    if cmd == "dev":
        rows = to_rows(load((SEED,) + SCORED))
        res, _, rs = run(rows, set(SCORED), SEED)
        out = {"protocol": {"seed": SEED, "scored": list(SCORED), "line": LINE, "r": rs, "virgin_read": False},
               "arms": {a: res[a] for a in ARMS}, "baselines": {b: res[b] for b in ("__base", "__naive")}}
        out["gate_zero_pass"] = res["gate_zero"]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res["gate_zero"]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        for a in ARMS: out["arms"][a]["dev_pass"] = res[a]["pooled"]["ll"] < res["__base"]["pooled"]["ll"] and res[a]["pooled"]["ll"] < res["__naive"]["pooled"]["ll"]
        write_json(HERE / "results_dev.json", out)
        print("dev", {a: res[a]["pooled"] for a in ARMS + ("__base", "__naive")}, "r", rs, "gz_pass", out["gate_zero_pass"]); return
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        write_json(HERE / "results_virgin.json", {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}); print("virgin unread"); return
    rows = to_rows(load((SEED,) + SCORED + (VIRGIN,)))
    # virgin phase: r re-estimated on all pre-virgin records via a warmup pass
    res, preds, rs = run(rows, {VIRGIN}, "__none__")
    # re-run with seed = all pre-virgin seasons for r estimation
    on = Online(); warm = []
    for r in rows:
        if r["season"] == VIRGIN: break
        p = on.prediction(r, "gate_zero"); warm.append({"y": r["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}); on.update(r)
    rs_v = {k: estimate_r(warm, k) for k in ("model", "base", "naive")}
    # score virgin with rs_v
    res2 = {a: {} for a in ARMS + ("__base", "__naive")}; preds = []
    for r in [x for x in rows if x["season"] == VIRGIN]:
        p = on.prediction(r, "gate_zero"); y = 1 if r["y"] > LINE else 0
        vals = {"gate_zero": nb_over(p["model"], rs_v["model"], LINE),
                "x5": nb_over(0.5 * p["model"] + 0.5 * p["naive"], rs_v["model"], LINE),
                "__base": nb_over(p["base"], rs_v["base"], LINE), "__naive": nb_over(p["naive"], rs_v["naive"], LINE)}
        for a, pv in vals.items(): res2[a].setdefault(VIRGIN, []).append((pv, y))
        for a in ARMS: preds.append((r, a, vals[a], p["model"] if a == "gate_zero" else 0.5 * p["model"] + 0.5 * p["naive"]))
        on.update(r)
    res = {}
    for a, bys in res2.items():
        res[a] = {s: agg(v) for s, v in bys.items()}; res[a]["pooled"] = agg([x for v in bys.values() for x in v])
    devmap = {a: dev["arms"][a] for a in ARMS}; devmap["__base"] = dev["baselines"]["__base"]; devmap["__naive"] = dev["baselines"]["__naive"]
    shipped, legs, _ = count_gate(devmap, res, ARMS, LINE)
    out = {"virgin_read": True, "r_virgin": rs_v, "arms": {a: res[a]["pooled"] for a in ARMS},
           "baselines": {b: res[b]["pooled"] for b in ("__base", "__naive")}, "legs": legs, "shipped_arm": shipped,
           "verdict": "FAIL" if not shipped else ("PASS" if legs[shipped]["calibration"] == "PASS" else "PROVISIONAL")}
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        pdir = HERE.parents[1] / "predictions"; pdir.mkdir(exist_ok=True)
        with (pdir / "k_id_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["match_id", "date", "home_id", "away_id", "arm", "pred_total_ft", "p_over_4.5", "pred_total_1h", "pred_total_2h", "actual_total"])
            for r, a, p, tot in preds:
                if a != shipped: continue
                w.writerow([r["match_id"], r["date"].isoformat(), r["home_id"], r["away_id"], shipped, round(tot, 3), round(p, 4),
                            round(tot * 0.385, 3), round(tot * 0.615, 3), int(r["y"])])
        write_json(HERE / "fitted_params_virgin.json", {"market": "cards", "arm": shipped, "r": rs_v, "halves_share_1h": 0.385})
    print("virgin", out["verdict"], shipped, {a: res[a]["pooled"] for a in ARMS})

if __name__ == "__main__":
    main(sys.argv[1])
