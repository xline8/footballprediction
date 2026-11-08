import argparse
from harness import run_dev, virgin


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--virgin", action="store_true")
    args = parser.parse_args()
    if args.dev == args.virgin:
        parser.error("choose exactly one of --dev or --virgin")
    (run_dev if args.dev else virgin)()


if __name__ == "__main__":
    main()
