import argparse
import json
from pathlib import Path

from harness import OUT, run_dev, virgin_metrics


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin-metrics")
    predict = sub.add_parser("virgin-predict")
    predict.add_argument("--arm", required=True, choices=("gate_zero", "shrink", "x2"))
    args = parser.parse_args()
    if args.cmd == "dev":
        run_dev()
        return
    if args.cmd == "virgin-predict":
        # Operator/verdict logic decides that this arm ships; this command does not enforce it.
        virgin_metrics((args.arm,), args.arm)
        return

    dev = run_dev()
    gates = dev["dev_gate"]
    print("dev_gate", json.dumps(gates, sort_keys=True))
    if not dev["dev_pass"]["gate_zero"]:
        reason = "gate zero failed dev gate; virgin not read (variants moot)"
        (OUT / "results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": reason}, indent=2) + "\n")
        print("virgin_read", False, "arms", [])
        return
    passing = [arm for arm in ("gate_zero", "shrink", "x2") if dev["dev_pass"][arm]]
    if not passing:
        reason = "no arm passed dev gate; virgin not read"
        (OUT / "results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": reason}, indent=2) + "\n")
        print("virgin_read", False, "arms", [])
        return
    virgin_metrics(tuple(passing))
    print("virgin_read", True, "arms", passing)


if __name__ == "__main__":
    main()
