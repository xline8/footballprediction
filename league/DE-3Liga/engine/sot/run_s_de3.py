from harness import run_dev, virgin
import argparse

p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); s.add_parser("virgin"); a=p.parse_args()
if a.cmd=="dev": run_dev()
else:
    d,_r,m=run_dev(); virgin(d, m)
