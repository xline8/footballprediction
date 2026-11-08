#!/usr/bin/env python3
"""Run C-AE in the preregistered order: dev, then conditional virgin.

Selection is mechanical per PREREG_C_AE: an arm ships iff it passed the
dev gate AND virgin legs (i) LL <= Gate Zero's (for x7) and <= best
baseline, (ii) calibration within 1pp + 1 SE, (iii) dev sign check for
x7 (>=2 of 3 dev seasons). Both pass -> lower virgin LL ships; ties ->
gate_zero. NOTHING is written when no arm passes (no fallback ship).
"""
import argparse
import json
from pathlib import Path
from harness import dev, gate_passes, virgin, write_predictions

DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin")
    v.add_argument("--arms", nargs="+", choices=("gate_zero", "x7"), required=True)
    args = ap.parse_args()
    if args.command == "dev":
        dev()
        return
    result_path = Path(__file__).resolve().parent / "results_dev.json"
    dev_result = json.loads(result_path.read_text())
    gates = gate_passes(dev_result)
    print("dev gate:", gates)
    result, target = virgin(args.arms, dev_result)
    best_baseline = min(result["league_base_rate"]["ll_10.5"], result["naive_trailing_10"]["ll_10.5"])
    eligible = []
    for arm in args.arms:
        r = result[arm]
        leg1 = r["ll_10.5"] <= best_baseline and (arm == "gate_zero" or "gate_zero" not in result or r["ll_10.5"] <= result["gate_zero"]["ll_10.5"])
        leg2 = abs(r["calibration_diff"]) <= 0.01 + r["calibration_se"]
        sign = True
        if arm == "x7":
            signs = []
            for season in DEV_SEASONS:
                a = next(x for x in dev_result if x["arm"] == "x7" and x["season"] == season and x["kind"] == "model")
                z = next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == season and x["kind"] == "model")
                signs.append(a["ll_10.5"] <= z["ll_10.5"])
            sign = sum(signs) >= 2
        if leg1 and leg2 and sign:
            eligible.append(arm)
        print("virgin gate", arm, {"leg_i": leg1, "leg_ii": leg2, "leg_iii": sign})
    if not eligible:
        print("shipped: NONE (no arm passed all virgin legs)")
        return
    shipped = min(eligible, key=lambda a: (result[a]["ll_10.5"], 0 if a == "gate_zero" else 1))
    write_predictions(shipped, target, result[shipped]["params"])
    print("shipped", shipped)

if __name__ == "__main__":
    main()
