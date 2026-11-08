import argparse
from harness import run_dev, virgin_metrics

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero", "x2", "x3"))
    args = p.parse_args()
    if args.cmd == "dev": run_dev()
    elif args.cmd == "virgin-metrics":
        dev = run_dev(); passed=[]
        for arm in ("gate_zero","x2","x3"):
            m=next(x for x in dev if x["arm"]==arm and x["season"]=="pooled" and x["kind"]=="model")
            b=next(x for x in dev if x["arm"]==arm and x["season"]=="pooled" and x["kind"]=="climatology")
            if m["ll_1x2"] < b["ll_1x2"] and m["rps"] < b["rps"] and m["oull_2_5"] < b["oull_2_5"]: passed.append(arm)
        virgin_metrics(tuple(passed or ["gate_zero"]), passed[0] if len(passed)==1 else None)
    else: virgin_metrics((args.arm,), args.arm)

if __name__ == "__main__": main()
