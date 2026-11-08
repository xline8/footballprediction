"""Run the G-RS goals engine — DEV ONLY.

Mirrors ``run_g_fi.py`` but with a single ``dev`` subcommand. There is
deliberately NO virgin subcommand here: the virgin run is a separate
later step, only if the dev gate passes (PREREG_G_RS.md).

Usage (from this directory):
    python3 run_g_rs.py dev
"""
import argparse
from harness import run_dev

def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    args = p.parse_args()
    if args.cmd == "dev": run_dev()

if __name__ == "__main__": main()
