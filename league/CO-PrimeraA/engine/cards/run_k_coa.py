import argparse
from harness import dev, virgin_metrics
p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); s.add_parser("virgin")
a=p.parse_args()
if a.cmd=="dev": dev()
else: dev(); virgin_metrics()
