"""Run K-ITB in the preregistered order: dev, then conditional virgin (Gate Zero only)."""
import argparse, json
from pathlib import Path
from harness import dev, virgin_metrics, predict

HERE = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser(); s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("dev"); s.add_parser("virgin")
    a = p.parse_args()
    if a.cmd == "dev":
        dev(); return
    devj = json.loads((HERE / "results_dev.json").read_text())
    if not devj["arms"]["gate_zero"]["dev_gate_pass"]:
        (HERE / "results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "gate zero failed dev gate"}, indent=2) + "\n")
        print("virgin not read: gate zero failed dev gate"); return
    virgin_metrics(("gate_zero",))
    result = json.loads((HERE / "results_virgin.json").read_text())
    v = result["arms"]["gate_zero"]
    best_base = min(v["metrics"]["base"]["4.5"]["ll"], v["metrics"]["naive"]["4.5"]["ll"])
    leg_i = v["metrics"]["model"]["4.5"]["ll"] <= best_base
    leg_ii = abs(v["calibration"]["diff_4_5"]) <= 0.01 + v["calibration"]["se_4_5"]
    print("virgin legs", {"leg_i": leg_i, "leg_ii": leg_ii, "best_baseline_ll": best_base})
    if leg_i and leg_ii:
        result["shipped_arm"] = "gate_zero"; predict("gate_zero"); print("shipped gate_zero")
    else:
        result["shipped_arm"] = None; print("shipped FAIL (no arm passed)")
    (HERE / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")

if __name__ == "__main__":
    main()
