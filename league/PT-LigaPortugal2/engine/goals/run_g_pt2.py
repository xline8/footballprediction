import argparse, json
from pathlib import Path
from harness import run_dev, dev_passes, virgin_metrics


def main():
    p = argparse.ArgumentParser(); p.add_argument("command", choices=("dev", "virgin")); args = p.parse_args()
    dev = run_dev()
    if args.command == "dev":
        return
    passing = [arm for arm in ("gate_zero", "shrink") if dev_passes(dev, arm)]
    if not passing:
        Path(__file__).resolve().parent.joinpath("results_virgin.json").write_text(json.dumps({"virgin_read": False, "reason": "Gate Zero failed dev gate"}, indent=2) + "\n")
        return
    virgin_metrics(passing)


if __name__ == "__main__":
    main()
