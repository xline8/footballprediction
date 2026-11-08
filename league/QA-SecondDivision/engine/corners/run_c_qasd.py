#!/usr/bin/env python3
import argparse
import os
from harness import dev, virgin_metrics, virgin_predict

ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="step",required=True)
sub.add_parser("dev"); sub.add_parser("virgin-metrics"); sub.add_parser("virgin-predict")
a=ap.parse_args()
if a.step != 'dev' and os.environ.get('QASD_RUN_VIRGIN') != '1': raise SystemExit('virgin run requires QASD_RUN_VIRGIN=1')
{"dev":dev,"virgin-metrics":virgin_metrics,"virgin-predict":virgin_predict}[a.step]()
