import argparse
from harness import run_dev, virgin
parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("dev","virgin")); args=parser.parse_args()
if args.command=="dev": run_dev()
if args.command=="virgin": virgin()
