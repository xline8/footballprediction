#!/usr/bin/env python3
import argparse
from harness import run_dev, virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin-metrics","virgin-predict"]); p.add_argument("--arm",choices=["GZ","RS","X4","X6"]); args=p.parse_args()
    if args.command=="dev": run_dev(); return
    dev,_rows,_ms=run_dev()
    if args.command=="virgin-metrics": virgin(dev,_rows); return
    virgin(dev,_rows,args.arm)
if __name__=="__main__": main()
