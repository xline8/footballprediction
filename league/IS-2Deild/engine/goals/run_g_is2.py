import argparse
from harness import run_dev


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    args = parser.parse_args()
    if args.cmd == "dev":
        run_dev()


if __name__ == "__main__":
    main()
