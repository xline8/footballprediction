import argparse
import json
from pathlib import Path

from harness import dev_passes, run_dev, virgin_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("dev", "virgin"))
    args = parser.parse_args()
    dev = run_dev()
    if args.command == "dev":
        for arm in ("gate_zero", "shrink"):
            print(f"dev gate {arm}: {'PASS' if dev_passes(dev, arm) else 'FAIL'}")
        return
    passing = [arm for arm in ("gate_zero", "shrink") if dev_passes(dev, arm)]
    if not passing:
        Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(
            json.dumps({"virgin_read": False, "reason": "No arm passed pooled dev gate"}, sort_keys=True) + "\n"
        )
        print("No arm passed dev gate; virgin deliberately not read")
        return
    virgin_metrics(passing, dev)


if __name__ == "__main__":
    main()
