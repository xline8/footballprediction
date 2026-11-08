import argparse
from harness import run_dev, virgin

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin")
    args = p.parse_args()
    if args.cmd == "dev": run_dev()
    else: virgin()

if __name__ == "__main__": main()
