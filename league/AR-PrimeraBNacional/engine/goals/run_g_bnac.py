import argparse
from harness import run_dev
p=argparse.ArgumentParser(); p.add_argument("--dev",action="store_true",required=True); a=p.parse_args()
run_dev()
