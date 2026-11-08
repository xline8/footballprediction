import argparse, json
from pathlib import Path
from harness import run_dev, virgin_metrics, write_predictions, ARMS

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True); sub.add_parser("dev"); sub.add_parser("virgin-metrics")
    q=sub.add_parser("virgin-predict"); q.add_argument("--arm",required=True,choices=ARMS); args=p.parse_args()
    if args.cmd == "dev": run_dev()
    elif args.cmd == "virgin-metrics":
        dev=run_dev(); passing=[]
        for arm in ARMS:
            m=next(x for x in dev if x["arm"]==arm and x["season"]=="pooled" and x["kind"]=="model")
            b=next(x for x in dev if x["arm"]==arm and x["season"]=="pooled" and x["kind"]=="climatology")
            if m["ll_1x2"] < b["ll_1x2"] and m["rps"] < b["rps"] and m["oull_2_5"] < b["oull_2_5"]: passing.append(arm)
        if not passing: Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read":False,"reason":"no arm passed the dev gate"})+"\n")
        else: virgin_metrics(passing)
    else: write_predictions(args.arm)
if __name__ == "__main__": main()
