import argparse
import json
from pathlib import Path
from harness import run_dev, virgin_metrics


def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin")
    args = p.parse_args()
    if args.cmd == "dev":
        run_dev()
    else:
        run_dev(); virgin_metrics(("gate_zero", "shrink"))


if __name__ == "__main__":
    main()
