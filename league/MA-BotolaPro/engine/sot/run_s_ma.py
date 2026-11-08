import argparse
from harness import run_dev
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev"]); p.parse_args(); run_dev()
