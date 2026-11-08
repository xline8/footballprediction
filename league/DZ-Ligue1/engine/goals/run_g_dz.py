import argparse
from harness import run_dev

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True); sub.add_parser("dev")
    if p.parse_args().cmd == "dev": run_dev()

if __name__ == "__main__": main()
