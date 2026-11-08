#!/usr/bin/env python3
import argparse
from harness import dev, virgin_metrics, virgin_predict

ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="step",required=True)
sub.add_parser("dev"); sub.add_parser("virgin-metrics"); sub.add_parser("virgin-predict")
a=ap.parse_args()
{"dev":dev,"virgin-metrics":virgin_metrics,"virgin-predict":virgin_predict}[a.step]()
