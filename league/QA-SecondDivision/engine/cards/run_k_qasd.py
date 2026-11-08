#!/usr/bin/env python3
import argparse
import os
from harness import dev,virgin
p=argparse.ArgumentParser(); p.add_argument('command',choices=['dev','virgin-metrics','virgin-predict']); a=p.parse_args()
if a.command=='dev':
    dev()
else:
    if os.environ.get('QASD_RUN_VIRGIN') != '1': raise SystemExit('virgin run requires QASD_RUN_VIRGIN=1')
    d=dev()
    virgin(a.command=='virgin-predict') if d['arms']['gate_zero']['dev_gate_pass'] else virgin(False)
