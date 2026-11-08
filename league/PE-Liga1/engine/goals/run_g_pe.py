import argparse
from harness import run_dev, virgin_metrics

def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="cmd", required=True); sub.add_parser("dev"); sub.add_parser("virgin"); args = parser.parse_args()
    if args.cmd == "dev": run_dev()
    else: run_dev(); virgin_metrics(("gate_zero", "x2"))

if __name__ == "__main__": main()
