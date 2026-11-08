"""Run G-KW: dev evaluation, then the virgin ONCE and only if
Gate Zero passed the dev gate (PREREG_G_KW.md, frozen before fitting).

Usage:
  python3 run_g_kw.py            # dev + virgin (if gated in)
  KW_DEV_ONLY=1 python3 run_g_kw.py   # dev only, virgin never read
"""
import os
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from harness import run_dev, virgin_metrics

if __name__ == "__main__":
    _, gate = run_dev()
    if os.environ.get("KW_DEV_ONLY") == "1":
        print("KW_DEV_ONLY=1: stopping after dev; virgin not read.")
    elif not gate["gate_zero"]:
        print("Gate Zero failed the dev gate: variants moot, verdict FAIL, virgin NOT read.")
    else:
        print("Gate Zero passed dev: reading virgin ONCE for dev-passing arms.")
        virgin_metrics(gate)
