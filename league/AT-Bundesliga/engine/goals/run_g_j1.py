import argparse
from harness import run_dev, virgin_metrics

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero", "shr", "x3"))
    args = p.parse_args()
    if args.cmd == "dev": run_dev()
    elif args.cmd == "virgin-metrics": virgin_metrics()
    else: virgin_metrics((args.arm,), args.arm)

if __name__ == "__main__": main()
