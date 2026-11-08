import argparse
import json
from pathlib import Path
from harness import run_dev, virgin_metrics

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics")
    q = sub.add_parser("virgin-predict"); q.add_argument("--arm", required=True, choices=("gate_zero", "shrink", "x2"))
    args = p.parse_args()
    if args.cmd == "dev": run_dev()
    elif args.cmd == "virgin-metrics":
        dev = run_dev()
        passing = []
        for arm in ("gate_zero", "shrink", "x2"):
            model = next(x for x in dev if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
            clim = next(x for x in dev if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "climatology")
            base_ou = clim["oull_2_5"]
            if model["ll_1x2"] < clim["ll_1x2"] and model["rps"] < clim["rps"] and model["oull_2_5"] < base_ou:
                passing.append(arm)
        if not passing:
            Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "no arm passed dev gate"}, indent=2) + "\n")
            return
        virgin_metrics(tuple(passing))
    else:
        dev = json.loads(Path(__file__).resolve().parent.joinpath("results_dev.json").read_text())
        model = next(x for x in dev if x["arm"] == args.arm and x["season"] == "pooled" and x["kind"] == "model")
        clim = next(x for x in dev if x["arm"] == args.arm and x["season"] == "pooled" and x["kind"] == "climatology")
        assert model["ll_1x2"] < clim["ll_1x2"] and model["rps"] < clim["rps"] and model["oull_2_5"] < clim["oull_2_5"], f"{args.arm} failed dev gate"
        virgin_metrics((args.arm,), args.arm)

if __name__ == "__main__": main()
