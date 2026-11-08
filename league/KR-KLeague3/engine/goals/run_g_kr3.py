import argparse
from harness import run_dev, virgin

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['dev', 'virgin'])
parser.add_argument('--arms', default=None)
args = parser.parse_args()
if args.mode == 'dev':
    run_dev()
else:
    virgin(args.arms.split(',') if args.arms else None)
