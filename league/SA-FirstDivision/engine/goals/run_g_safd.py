#!/usr/bin/env python3
import argparse
from harness import run_dev, virgin, virgin_predict


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["dev", "virgin-metrics", "virgin-predict"])
    args = p.parse_args()
    if args.command == "dev":
        run_dev()
    elif args.command == "virgin-metrics":
        virgin()
    else:
        virgin_predict()


if __name__ == "__main__":
    main()
