#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from harness import run_dev, virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin-metrics","virgin-predict"]); p.add_argument("--arm",choices=["GZ","RS"]); args=p.parse_args()
    if args.command=="dev": run_dev(); return
    dev,_rows,_ms=run_dev()
    gz=dev["arms"]["GZ"]["pooled"]["ll_8.5"]; base=dev["baselines"]["league_base_rate"]["pooled"]["ll_8.5"]
    if gz >= base:
        Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read":False,"reason":"gate zero failed dev gate"},indent=2)+"\n"); return
    if args.command=="virgin-metrics": virgin(dev,_rows); return
    virgin(dev,_rows,args.arm)
if __name__=="__main__": main()
