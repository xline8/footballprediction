#!/usr/bin/env python3
"""C-UA runner: `dev` runs the frozen dev protocol; `virgin` reads the
2026 window ONCE and only for arms recorded dev-passing."""
import argparse
from harness import dev, virgin


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["dev", "virgin"])
    args = p.parse_args()
    if args.command == "dev":
        dev()
    else:
        virgin()


if __name__ == "__main__":
    main()
