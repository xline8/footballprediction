import argparse

from harness import ARMS, run_dev, run_virgin, write_predictions


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("dev")
    virgin = subparsers.add_parser("virgin")
    virgin.add_argument("--arms", required=True)
    predict = subparsers.add_parser("predict")
    predict.add_argument("--arm", required=True, choices=ARMS)
    args = parser.parse_args()
    if args.command == "dev":
        run_dev()
    elif args.command == "virgin":
        arms = tuple(args.arms.split(","))
        if not arms or any(arm not in ARMS for arm in arms):
            parser.error("--arms must contain only gate_zero and/or shrink")
        run_virgin(arms)
    else:
        write_predictions(args.arm)


if __name__ == "__main__":
    main()
