"""CLI for the preregistered LT-Toplyga development walk-forward."""
import argparse
from harness import run_dev


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("dev", help="run the 2022-2025 development walk-forward")
    args = parser.parse_args()
    if args.command == "dev":
        run_dev()


if __name__ == "__main__":
    main()
