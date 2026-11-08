import argparse
from harness import run_dev

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    args = p.parse_args()
    if args.cmd != "dev": raise SystemExit("virgin commands are forbidden in Phase 2")
    run_dev()

if __name__ == "__main__": main()
