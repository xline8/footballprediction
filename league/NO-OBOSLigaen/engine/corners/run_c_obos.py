#!/usr/bin/env python3
"""Run C-NO-OBOS in the preregistered order: dev, then conditional virgin."""
import argparse
from harness import dev, gate_passes, virgin, write_predictions


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin")
    v.add_argument("--arms", nargs="+", choices=("gate_zero", "plain"), required=True)
    args = ap.parse_args()
    if args.command == "dev":
        dev()
        return
    result_path = __import__("pathlib").Path(__file__).resolve().parent / "results_dev.json"
    dev_result = __import__("json").loads(result_path.read_text())
    gates = gate_passes(dev_result)
    print("dev gate:", gates)
    result, target = virgin(args.arms, dev_result)
    # Selection is mechanical; caller may request only evaluated passing arms.
    baselines = [result["league_base_rate"]["ll_10.5"], result["naive_trailing_10"]["ll_10.5"]]
    best_baseline = min(baselines)
    eligible = []
    for arm in args.arms:
        r = result[arm]
        leg1 = r["ll_10.5"] <= best_baseline
        leg2 = abs(r["calibration_diff"]) <= 0.01 + r["calibration_se"]
        sign = True
        if arm == "plain":
            signs = []
            for season in ("2022", "2023", "2024", "2025"):
                # This is recomputed from persisted dev values, no virgin read.
                a = next(x for x in dev_result if x["arm"] == "plain" and x["season"] == season and x["kind"] == "model")
                z = next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == season and x["kind"] == "model")
                signs.append(a["ll_10.5"] <= z["ll_10.5"])
            sign = sum(signs) >= 2
        if leg1 and leg2 and sign:
            eligible.append(arm)
        print("virgin gate", arm, {"leg_i": leg1, "leg_ii": leg2, "leg_iii": sign})
    shipped = min(eligible, key=lambda a: (result[a]["ll_10.5"], 0 if a == "gate_zero" else 1)) if eligible else "gate_zero"
    write_predictions(shipped, target, result[shipped]["params"])
    print("shipped", shipped if eligible else "gate_zero (fallback; no arm passed)")


if __name__ == "__main__":
    main()
