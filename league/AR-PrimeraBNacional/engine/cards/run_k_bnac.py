import argparse
from harness import run_dev, virgin
p=argparse.ArgumentParser(); p.add_argument("--dev",action="store_true"); p.add_argument("--virgin",action="store_true"); a=p.parse_args()
if a.dev == a.virgin: p.error("choose exactly one of --dev or --virgin")
if a.dev: run_dev()
else: virgin()
