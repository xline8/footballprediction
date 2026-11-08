import argparse, json
from harness import dev, virgin_metrics, predict
p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); s.add_parser("virgin-metrics"); q=s.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=("gate_zero","x8")); a=p.parse_args()
if a.cmd=="dev": dev()
elif a.cmd=="virgin-metrics":
    virgin_metrics(); predict("gate_zero")
else: predict(a.arm)
