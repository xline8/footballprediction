#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from harness import run_dev, virgin

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev","virgin-metrics","virgin-predict"]); p.add_argument("--arm",choices=["GZ","RS"]); args=p.parse_args()
    if args.command=="dev": run_dev(); return
    # Virgin consumes the committed dev result; it must not rerun dev.
    dev = json.loads(Path(__file__).resolve().parent.joinpath("results_dev.json").read_text())
    gz=dev["arms"]["GZ"]["pooled"]["ll_7.5"]; base=min(dev["baselines"][x]["pooled"]["ll_7.5"] for x in ("league_base_rate","naive"))
    if gz >= base:
        Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read":False,"reason":"gate zero failed dev gate"},indent=2)+"\n"); return
    if args.command=="virgin-metrics": virgin(dev, []); return
    virgin(dev, [], args.arm)
if __name__=="__main__": main()
