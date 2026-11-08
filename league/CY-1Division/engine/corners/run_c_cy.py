#!/usr/bin/env python3
import argparse
import json
from harness import dev, virgin

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=("dev", "virgin"))
args=parser.parse_args()
dev() if args.command == "dev" else virgin(("gate_zero",), json.load(open("results_dev.json"))["rows"])
