#!/usr/bin/env python3
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
