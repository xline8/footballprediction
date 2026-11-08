#!/usr/bin/env python3
import argparse
from harness import run_dev, run_virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev", "virgin"]); args=p.parse_args()
    if args.command == "dev": run_dev()
    else: run_virgin()
if __name__=="__main__": main()
