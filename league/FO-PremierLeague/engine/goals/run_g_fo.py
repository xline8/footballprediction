import argparse
from harness import run_dev
p=argparse.ArgumentParser(); p.add_argument("cmd",choices=("dev",)); a=p.parse_args()
if a.cmd == "dev": run_dev()
