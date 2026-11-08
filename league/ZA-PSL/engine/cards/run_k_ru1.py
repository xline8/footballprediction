#!/usr/bin/env python3
import argparse
from harness import dev

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=("dev",))
args=parser.parse_args()
dev()
