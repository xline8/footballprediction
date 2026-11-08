import argparse
import json
from pathlib import Path
from harness import run_dev, virgin_metrics, dev_gate_table

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero", "shrink", "x2"))
    args = p.parse_args()
    if args.cmd == "dev":
        result = run_dev()
        gates = dev_gate_table(result)
        print("dev gate:")
        for arm, g in gates.items():
            print(f'{arm} passed={g["passed"]} sign_check={g["sign_check"]} sign_pass={g["sign_pass"]}')
    elif args.cmd == "virgin-metrics":
        dev = run_dev()
        gates = dev_gate_table(dev)
        passing = [a for a, g in gates.items() if g["passed"]]
        if not passing:
            Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "no arm passed the dev gate", "gates": gates}, indent=2) + "\n")
            print("virgin NOT read: no arm passed the dev gate")
            return
        print(f"virgin read for dev-passing arms: {passing}")
        virgin_metrics(tuple(passing))
    else:
        dev = run_dev()
        gates = dev_gate_table(dev)
        if not gates[args.arm]["passed"]:
            raise SystemExit(f"arm {args.arm} did not pass the dev gate; virgin predictions refused")
        virgin_metrics((args.arm,), args.arm)

if __name__ == "__main__": main()
