from harness import run_dev, run_virgin, ARMS
import argparse
p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="command", required=True)
sub.add_parser("dev")
v = sub.add_parser("virgin"); v.add_argument("--arm", required=True, nargs="+", choices=ARMS)
q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=ARMS)
a = p.parse_args()
if a.command == "dev": run_dev()
elif a.command == "virgin": run_virgin(tuple(a.arm))
else: run_virgin((a.arm,), predict_arm=a.arm)
