import argparse
import json
from pathlib import Path
from harness import dev, virgin


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("dev", "virgin"))
    args = parser.parse_args()
    if args.command == "dev": dev()
    else: virgin(json.loads((Path(__file__).resolve().parent / "results_dev.json").read_text()))
