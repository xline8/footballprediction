import argparse
import json
from pathlib import Path

from harness import OUT, run_dev


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    args = parser.parse_args()
    if args.cmd == "dev":
        run_dev()
        return
    dev = run_dev()
    print("dev_gate", json.dumps(dev["dev_gate"], sort_keys=True))


if __name__ == "__main__":
    main()
