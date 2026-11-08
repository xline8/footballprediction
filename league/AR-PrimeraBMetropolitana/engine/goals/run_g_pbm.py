"""CLI for the DEV-only G-PBM engine."""
import argparse
from harness import run_dev


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", required=True, help="run the frozen development harness")
    args = parser.parse_args()
    if args.dev:
        run_dev()


if __name__ == "__main__":
    main()
