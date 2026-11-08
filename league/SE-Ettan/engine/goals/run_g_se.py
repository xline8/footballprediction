"""Run G-SE dev evaluation (Phase 4, dev only — no virgin read).

Usage: python3 run_g_se.py   (from this directory)
Outputs: results_dev.json, results_dev.csv, fitted_params_dev.json
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from dc import run_goals

if __name__ == "__main__":
    res = run_goals(Path(__file__).parent)
    print(json.dumps(res["dev"], indent=1))
    print("VIRGIN:", res["virgin"])
