#!/usr/bin/env python3
import argparse
from harness import dev, virgin

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=("dev", "virgin"))
args=parser.parse_args()
if args.command == "dev": dev()
else: virgin()
