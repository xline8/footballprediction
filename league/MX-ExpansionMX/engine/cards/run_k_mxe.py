"""K-MXE cards engine: production online cards pattern, Gate Zero only.

Prereg: league/MX-ExpansionMX/prereg/PREREG_K_MXE.md (frozen before fitting).
Corpus: clean era only (2023/2024 - Apertura on). Warm-up unscored;
dev scored online walk-forward; virgin read once iff the dev gate passes.
Usage: python3 run_k_mxe.py dev | virgin
"""
import csv, json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from model import Online, estimate_r, nb_over
from common_mxe import load, BLOCKS, agg, write_json

WARMUP = "2023/2024 - Apertura"
DEV_BLOCKS = ["2023/2024 - Clausura", "2024/2025 - Apertura", "2024/2025 - Clausura", "2025/2026 - Apertura"]
VIRGIN = "2025/2026 - Clausura"
PRIMARY = 5.5
LADDER = (4.5, 5.5, 6.5)
HALVES_YELLOW_1H = 0.402
ERA_BLOCKS = [WARMUP] + DEV_BLOCKS + [VIRGIN]


def rows_for(blocks):
    rows = load(blocks)
    for r in rows:
        r["day"] = r["date"].toordinal()
        r["y"] = r["yh"] + r["ya"]
    return rows


def scored(records, rmap):
    out = {}
    for method in ("model", "base", "naive"):
        vals = {}
        for line in LADDER:
            pairs = [(nb_over(x[method], rmap[method], line), int(x["y"] > line)) for x in records]
            a = agg(pairs)
            vals[str(line)] = {"n": a["n"], "ll": a["ll"], "mean_p": a["mean_pred"],
                               "actual_rate": a["actual_rate"],
                               "calibration_pp": a["calibration_pp"], "calibration_se_pp": a["calibration_se_pp"]}
        out[method] = vals
    return out


def run_dev():
    rows = rows_for([WARMUP] + DEV_BLOCKS)
    online = Online(); warm = []; per_block = {b: [] for b in DEV_BLOCKS}; pooled = []
    for row in rows:
        p = online.prediction(row)
        rec = {"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]}
        if row["block"] == WARMUP:
            warm.append(rec)
        else:
            per_block[row["block"]].append(rec); pooled.append(rec)
        online.update(row)
    rmap = {m: estimate_r(warm, m) for m in ("model", "base", "naive")}
    out = {"protocol": {"warmup": WARMUP, "scored": DEV_BLOCKS, "primary_line": PRIMARY,
                        "corpus": "clean era only (2023/2024 - Apertura on); 2022/2023 - Clausura excluded for partial capture"},
           "r": rmap, "blocks": {b: scored(per_block[b], rmap) for b in DEV_BLOCKS},
           "pooled": scored(pooled, rmap)}
    mp = out["pooled"]["model"][str(PRIMARY)]["ll"]
    bp = out["pooled"]["base"][str(PRIMARY)]["ll"]
    np_ = out["pooled"]["naive"][str(PRIMARY)]["ll"]
    out["dev_gate_pass"] = mp < bp and mp < np_
    out["dev_gate"] = {"model_ll": mp, "base_ll": bp, "naive_ll": np_}
    write_json(HERE / "results_dev.json", out)
    return out, rmap


def virgin(dev_out, rmap):
    if not dev_out["dev_gate_pass"]:
        out = {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}
        write_json(HERE / "results_virgin.json", out); return out
    rows = rows_for(ERA_BLOCKS)
    online = Online(); vrecs = []; vrows = []
    cutoff_state = None
    for row in rows:
        p = online.prediction(row)
        if row["block"] == VIRGIN:
            if cutoff_state is None:
                cutoff_state = online.state.snapshot(row["day"])
            vrecs.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
            vrows.append((row, p))
        online.update(row)
    met = scored(vrecs, rmap)
    cal = met["model"][str(PRIMARY)]
    from common_mxe import calib_verdict
    cv = calib_verdict(cal)
    ll_leg = met["model"][str(PRIMARY)]["ll"] <= met["base"][str(PRIMARY)]["ll"] and \
        met["model"][str(PRIMARY)]["ll"] <= met["naive"][str(PRIMARY)]["ll"]
    verdict = "FAIL" if (not ll_leg or cv == "FAIL") else ("PROVISIONAL" if cv == "PROVISIONAL" else "PASS")
    out = {"virgin_read": True, "metrics": met, "r": rmap,
           "legs": {"ll_leg": ll_leg, "calibration": cv,
                    "calibration_pp": cal["calibration_pp"], "calibration_se_pp": cal["calibration_se_pp"]},
           "verdict": verdict, "shipped_arm": "gate_zero" if verdict in ("PASS", "PROVISIONAL") else None}
    write_json(HERE / "results_virgin.json", out)
    if verdict in ("PASS", "PROVISIONAL"):
        write_json(HERE / "fitted_params_virgin.json",
                   {"arm": "gate_zero", "HL": 270, "K_PRIOR": 8, "r": rmap,
                    "cutoff_state": cutoff_state, "halves_yellow_1h_share": HALVES_YELLOW_1H})
        pred_dir = HERE.parents[1] / "predictions"; pred_dir.mkdir(exist_ok=True)
        try:
            with (pred_dir / "k_mxe_virgin_predictions.csv").open("w", newline="") as f:
                fields = ["match_id", "date", "home", "away", "expected_home", "expected_away", "expected_total",
                          "p_over_4_5", "p_over_5_5", "p_over_6_5", "mean_1h", "mean_2h", "arm"]
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                for row, p in vrows:
                    w.writerow({"match_id": row["match_id"], "date": row["date"].isoformat(),
                                "home": row["home"], "away": row["away"], "expected_home": p["eh"],
                                "expected_away": p["ea"], "expected_total": p["model"],
                                "p_over_4_5": nb_over(p["model"], rmap["model"], 4.5),
                                "p_over_5_5": nb_over(p["model"], rmap["model"], 5.5),
                                "p_over_6_5": nb_over(p["model"], rmap["model"], 6.5),
                                "mean_1h": p["model"] * HALVES_YELLOW_1H,
                                "mean_2h": p["model"] * (1 - HALVES_YELLOW_1H), "arm": "gate_zero"})
        except OSError as e:
            print(f"WRITE_FAILED predictions: {e}", file=sys.stderr)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "dev":
        o, _ = run_dev()
        print(json.dumps({"r": o["r"], "pooled": o["pooled"], "dev_gate": o["dev_gate"],
                          "dev_gate_pass": o["dev_gate_pass"]}, indent=1))
        for b in DEV_BLOCKS:
            print(b, {m: o["blocks"][b][m][str(PRIMARY)]["ll"] for m in ("model", "base", "naive")})
    else:
        dpath = HERE / "results_dev.json"
        if dpath.exists() and dpath.stat().st_size > 0:
            dev_out = json.loads(dpath.read_text()); rmap = dev_out["r"]
        else:
            dev_out, rmap = run_dev()
        print(json.dumps(virgin(dev_out, rmap), indent=1, default=str))
