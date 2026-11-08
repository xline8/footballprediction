import argparse
from harness import run_dev, virgin


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin")
    args = parser.parse_args()
    (run_dev if args.cmd == "dev" else virgin)()


if __name__ == "__main__":
    main()
