import argparse
from harness import run_dev, virgin


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("dev")
    subparsers.add_parser("virgin")
    args = parser.parse_args()
    if args.command == "dev":
        run_dev()
    else:
        virgin()


if __name__ == "__main__":
    main()
