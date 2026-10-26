#!/usr/bin/env python3
"""run_daily_shadow.py — orchestrator harian live shadow (Phase 6).

Alur: generate predictions (predict_upcoming) -> filter & ledger
(make_picks_live) -> resolve & monitor (resolve_and_monitor).

Dipakai oleh pipeline_orchestrator.py atau standalone (cron).
"""

import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def main():
    print("#" * 70)
    print("# LIVE SHADOW DAILY RUN")
    print("#" * 70)

    try:
        from predict_upcoming_refactored import generate_predictions
        res = generate_predictions()
        print(f"[1/3] predictions: {res.get('n_output_rows', 0)} rows "
              f"(status {res.get('status')})")
    except Exception as e:
        print(f"[1/3] ! predictions gagal (dilewati): {e}")

    try:
        import make_picks_live
        n = make_picks_live.main()
        print(f"[2/3] live picks baru: {n}")
    except Exception as e:
        print(f"[2/3] ! make_picks_live gagal (dilewati): {e}")

    try:
        import resolve_and_monitor
        resolve_and_monitor.main()
    except Exception as e:
        print(f"[3/3] ! resolve_and_monitor gagal (dilewati): {e}")


if __name__ == "__main__":
    main()
