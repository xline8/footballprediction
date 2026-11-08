#!/usr/bin/env python3
"""Run C-NL in the preregistered order: dev, then conditional virgin."""
import argparse
import json
from pathlib import Path
from harness import dev, gate_passes, virgin, write_predictions


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("dev")
    sub.add_parser("virgin")
    args = ap.parse_args()
    if args.command == "dev":
        dev()
        return
    result_path = Path(__file__).resolve().parent / "results_dev.json"
    dev_result = json.loads(result_path.read_text())
    arms = ["gate_zero"] if gate_passes(dev_result).get("gate_zero") else []
    if not arms: raise SystemExit("virgin refused: no persisted passing corners arm")
    virgin(arms, dev_result)


if __name__ == "__main__":
    main()
