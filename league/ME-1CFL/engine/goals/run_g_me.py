"""CLI for the preregistered Montenegro 1. CFL development walk-forward."""
import argparse
from harness import run_dev, run_virgin


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("dev", help="run the 2022/2023-2024/2025 development walk-forward")
    sub.add_parser("virgin", help="run the one-shot 2025/2026 virgin evaluation")
    args = parser.parse_args()
    if args.command == "dev":
        run_dev()
    elif args.command == "virgin":
        run_virgin()


if __name__ == "__main__":
    main()
