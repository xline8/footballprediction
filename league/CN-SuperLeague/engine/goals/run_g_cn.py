#!/usr/bin/env python3
"""G-CN runner: `dev` runs the frozen dev protocol; `virgin` reads the
2026 window ONCE and only for arms passing the dev gate (the harness
recomputes the dev gate from results_dev.json)."""
import argparse
from harness import run_dev, virgin


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["dev", "virgin"])
    args = p.parse_args()
    if args.command == "dev":
        run_dev()
    else:
        virgin()


if __name__ == "__main__":
    main()
