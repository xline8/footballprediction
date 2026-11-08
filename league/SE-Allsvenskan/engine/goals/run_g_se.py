import argparse
import json
from pathlib import Path
from harness import run_dev, virgin_metrics

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero", "shrink", "x3"))
    args = p.parse_args()
    if args.cmd == "dev": run_dev()
    elif args.cmd == "virgin-metrics":
        dev = run_dev()
        gz = next(x for x in dev if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "model")
        base = next(x for x in dev if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "climatology")
        if not (gz["ll_1x2"] < base["ll_1x2"] and gz["rps"] < base["rps"] and gz["oull_2_5"] < base["oull_2_5"]):
            Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "gate zero failed dev gate"}, indent=2) + "\n"); return
        virgin_metrics()
    else: virgin_metrics((args.arm,), args.arm)

if __name__ == "__main__": main()
