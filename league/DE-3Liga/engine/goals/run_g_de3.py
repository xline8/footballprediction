import argparse
import json
from pathlib import Path
from harness import run_dev, virgin_metrics

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    v = sub.add_parser("virgin-metrics"); v.add_argument("--arms", nargs="+", required=True, choices=("gate_zero", "shrink"))
    a = p.parse_args()
    if a.cmd == "dev": run_dev(); return
    dev = run_dev()
    gz = next(x for x in dev if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "model")
    base = next(x for x in dev if x["arm"] == "gate_zero" and x["season"] == "pooled" and x["kind"] == "climatology")
    if not (gz["ll_1x2"] < base["ll_1x2"] and gz["rps"] < base["rps"] and gz["oull_2_5"] < base["oull_2_5"]):
        Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "gate zero failed dev gate"}, indent=2) + "\n"); return
    passing = []
    for arm in a.arms:
        row = next(x for x in dev if x["arm"] == arm and x["season"] == "pooled" and x["kind"] == "model")
        if row["ll_1x2"] < base["ll_1x2"] and row["rps"] < base["rps"] and row["oull_2_5"] < base["oull_2_5"]:
            passing.append(arm)
    if passing: virgin_metrics(tuple(passing), passing[0])
    else: Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "no dev-passing arms"}, indent=2) + "\n")

if __name__ == "__main__": main()
