#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from harness import run_dev, virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin"]); args=p.parse_args()
    dev=run_dev(); print(json.dumps(dev,indent=2,default=str))
    if args.command=="virgin": print(json.dumps(virgin(dev),indent=2,default=str))
if __name__=="__main__": main()


