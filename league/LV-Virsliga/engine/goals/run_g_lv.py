import argparse

from harness import run_dev, virgin


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    m = sub.add_parser("virgin-metrics")
    m.add_argument("--arm", required=True, nargs="+", choices=("gate_zero", "shrink"))
    q = sub.add_parser("virgin-predict")
    q.add_argument("--arm", required=True, choices=("gate_zero", "shrink"))
    args = p.parse_args()
    if args.cmd == "dev":
        run_dev()
    elif args.cmd == "virgin-metrics":
        virgin(args.arm)
    else:
        virgin([args.arm], predict_arm=args.arm)


if __name__ == "__main__":
    main()
