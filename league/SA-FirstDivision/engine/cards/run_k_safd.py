#!/usr/bin/env python3
import argparse
from harness import dev,virgin
p=argparse.ArgumentParser(); p.add_argument('command',choices=['dev','virgin-metrics','virgin-predict']); a=p.parse_args()
if a.command=='dev':
    d=dev()
    if not d['arms']['gate_zero']['dev_gate_pass']: virgin(False)
else:
    d=dev()
    virgin(a.command=='virgin-predict') if d['arms']['gate_zero']['dev_gate_pass'] else virgin(False)
