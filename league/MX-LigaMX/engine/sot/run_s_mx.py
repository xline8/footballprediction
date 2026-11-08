#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from harness import run_dev, virgin, OUT

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin-metrics","virgin-predict"]); p.add_argument("--arm",choices=["GZ","RS","X4"]); args=p.parse_args()
    if args.command=="dev": run_dev(); return
    dev=json.loads((Path(OUT)/"results_dev.json").read_text())
    if args.command=="virgin-metrics": virgin(dev,None); return
    virgin(dev,None,args.arm)
if __name__=="__main__": main()
