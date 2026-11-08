import argparse
import json
from pathlib import Path

from harness import OUT, run_dev, virgin_metrics


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict")
    q.add_argument("--arm", required=True, choices=("gate_zero", "shrink"))
    args = parser.parse_args()
    if args.cmd == "dev":
        run_dev()
        return
    if args.cmd == "virgin-metrics":
        virgin_metrics()
    else:
        virgin_metrics((args.arm,), args.arm)


if __name__ == "__main__":
    main()
