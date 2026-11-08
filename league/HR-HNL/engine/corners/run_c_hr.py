import argparse
import json
from pathlib import Path
from harness import dev, gate_passes, virgin, write_predictions

HERE = Path(__file__).resolve().parent
ARMS = ("gate_zero", "x7")

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev"); sub.add_parser("virgin")
    args = p.parse_args()
    dev_result = dev()
    if args.cmd == "dev": return
    gates = gate_passes(dev_result)
    # Frozen rule (PREREG_C_HR): Gate Zero dev failure => candidate FAILS,
    # variants moot, virgin NOT read.
    if not gates.get("gate_zero"):
        (HERE / "results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "gate zero failed dev gate"}, indent=2) + "\n")
        print("virgin NOT read: gate zero failed dev gate"); return
    arms = tuple(a for a in ARMS if gates.get(a))
    result, target = virgin(arms, dev_result)
    best_base = min(result[k]["ll_8.5"] for k in ("league_base_rate", "naive_trailing_10"))
    eligible = []
    for arm in arms:
        r = result[arm]
        leg_i = r["ll_8.5"] <= result["gate_zero"]["ll_8.5"] and r["ll_8.5"] <= best_base
        leg_ii = abs(r["calibration_diff"]) <= 0.01 + r["calibration_se"]
        if arm == "gate_zero": sign = True
        else:
            sign = sum(next(x for x in dev_result if x["arm"] == arm and x["season"] == s and x["kind"] == "model")["ll_8.5"]
                       <= next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == s and x["kind"] == "model")["ll_8.5"]
                       for s in ("2022/2023", "2023/2024", "2024/2025")) >= 2
        print("virgin gate", arm, {"leg_i": leg_i, "leg_ii_provisional_counts": leg_ii, "leg_iii_sign": sign})
        if leg_i and leg_ii and sign: eligible.append(arm)
    if eligible:
        shipped = min(eligible, key=lambda a: (result[a]["ll_8.5"], ARMS.index(a)))
        write_predictions(shipped, target, result[shipped]["params"])
    else:
        shipped = None
    result["shipped_arm"] = shipped
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    print("shipped", shipped)

if __name__ == "__main__": main()
