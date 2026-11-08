#!/usr/bin/env python3
import argparse
from harness import run_dev, virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin"]); args=p.parse_args()
    d, rows, _ = run_dev()
    if args.command == "virgin": virgin(d, rows)
if __name__=="__main__": main()
