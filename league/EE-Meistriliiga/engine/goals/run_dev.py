#!/usr/bin/env python3
import json
from pathlib import Path
from harness import run_dev

if __name__ == "__main__":
    result = run_dev()
    print(json.dumps(result["dev_gate"], sort_keys=True))
