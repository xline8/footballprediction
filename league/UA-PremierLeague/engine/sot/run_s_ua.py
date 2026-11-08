#!/usr/bin/env python3
"""S-UA runner: `dev` runs the frozen dev protocol; `virgin` reads the
2026 window ONCE and only for arms recorded dev-passing."""
import argparse
from harness import run_dev, run_virgin


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["dev", "virgin"])
    args = p.parse_args()
    if args.command == "dev":
        run_dev()
    else:
        run_virgin()


if __name__ == "__main__":
    main()
