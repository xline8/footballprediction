import argparse
from harness import run_dev
parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("dev",)); args=parser.parse_args()
if args.command=="dev": run_dev()
