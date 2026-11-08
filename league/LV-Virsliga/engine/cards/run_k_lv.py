from harness import run_dev, run_virgin
import argparse
p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="command", required=True)
sub.add_parser("dev")
sub.add_parser("virgin")
q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero",))
a = p.parse_args()
if a.command == "dev": run_dev()
elif a.command == "virgin": run_virgin()
else: run_virgin(predict_arm=a.arm)
