import argparse
from harness import run_dev,virgin
p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--arms',default=None);a=p.parse_args()
if a.mode=='dev':run_dev()
else:virgin(a.arms.split(',') if a.arms else None)
