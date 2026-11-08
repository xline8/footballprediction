import argparse
from harness import run_dev, virgin


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin")
    v.add_argument("--arms", required=True, help="comma-separated registered arms")
    v.add_argument("--out", required=True, help="predictions CSV output path")
    args = parser.parse_args()
    if args.command == "dev":
        run_dev()
    else:
        virgin(tuple(a.strip() for a in args.arms.split(",") if a.strip()), args.out)


if __name__ == "__main__":
    main()
