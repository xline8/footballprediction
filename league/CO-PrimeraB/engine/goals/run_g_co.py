import argparse
from harness import ARMS, run_dev, run_virgin, write_predictions

parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True); sub.add_parser("dev")
virgin = sub.add_parser("virgin"); virgin.add_argument("--arms", required=True)
predict = sub.add_parser("predict"); predict.add_argument("--arm", required=True, choices=ARMS)
args = parser.parse_args()
if args.command == "dev": run_dev()
elif args.command == "virgin":
    arms = tuple(args.arms.split(","))
    if not arms or any(arm not in ARMS for arm in arms): parser.error("--arms must contain only gate_zero, shrink, and/or x2")
    run_virgin(arms)
else: write_predictions(args.arm)
