#!/usr/bin/env python3
"""run_daily_shadow.py — orchestrator harian live shadow (Phase 6).

Alur: generate predictions (predict_upcoming) -> filter & ledger
(make_picks_live) -> resolve & monitor (resolve_and_monitor).

Dipakai oleh pipeline_orchestrator.py atau standalone (cron).
"""

import os
import sys
import subprocess
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def _run_py(script, *args):
    return subprocess.run([sys.executable, os.path.join(BASE, script), *args],
                          capture_output=True, text=True, timeout=600)


def main():
    print("#" * 70)
    print("# LIVE SHADOW DAILY RUN")
    print("#" * 70)
    failed = False

    try:
        from predict_upcoming_refactored import generate_predictions
        res = generate_predictions()
        print(f"[1/6] predictions: {res.get('n_output_rows', 0)} rows "
              f"(status {res.get('status')})")
    except Exception as e:
        failed = True
        print(f"[1/6] FAILED predictions: {e!r}")

    try:
        r = _run_py("model_corners_v3.py", "--predict")
        print(f"[2/6] corner predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            failed = True
    except Exception as e:
        failed = True
        print(f"[2/6] FAILED corner predictions: {e!r}")

    try:
        import predict_cups
        rc = predict_cups.main()
        print(f"[3/6] cup predictions: {rc.get('n_gol', 0)} gol, "
              f"{rc.get('n_corner', 0)} corner")
    except Exception as e:
        failed = True
        print(f"[3/6] FAILED cup predictions: {e!r}")

    try:
        r = _run_py("best_picks.py", "--date", date.today().isoformat())
        print(f"[4/6] best_picks: rc={r.returncode} | {r.stdout.strip()[-400:]}")
        if r.returncode != 0:
            failed = True
    except Exception as e:
        failed = True
        print(f"[4/6] FAILED best_picks: {e!r}")

    try:
        import make_picks_live
        n = make_picks_live.main()
        print(f"[5/7] live picks baru: {n}")
    except Exception as e:
        failed = True
        print(f"[5/7] FAILED make_picks_live: {e!r}")

    # Sinkronisasi hasil tipsterarea untuk tanggal kemarin + H-2 secara eksplisit
    # (sebelum grading). --fresh memaksa fetch jaring (cache halaman tanggal
    # 20 menit dilewati) agar laga yang selesai larut ikut masuk. Kegagalan
    # jaringan tidak menggagalkan pipeline — catat warning, lanjutkan.
    try:
        y = date.today() - timedelta(days=1)
        y2 = date.today() - timedelta(days=2)
        r = _run_py("ta_scrape.py", y.isoformat(), y2.isoformat(), "--fresh")
        out = (r.stdout or r.stderr or "").strip()
        print(f"[6/7] tipsterarea hasil sync: rc={r.returncode} | {out[-300:]}")
        if r.returncode != 0:
            print(f"[6/7] WARNING ta sync rc={r.returncode} (lanjut pipeline)")
    except Exception as e:
        print(f"[6/7] WARNING ta sync gagal: {e!r} (lanjut pipeline)")

    # [7/9] Market odds sync: semua fixture model (liga TOP5 + piala), window
    # hari ini..+4, urut kickoff terdekat. Throttle market_needs_refresh diurus
    # sync_dates (~1.5 jam); hanya fetch yang perlu. Gagal jaringan = warning,
    # tidak menggagalkan pipeline. parse_match_page/schema tidak diubah.
    try:
        from market_orchestration import model_fixture_ids
        from ta_scrape import sync_dates
        days_mkt = [date.today() + timedelta(days=k) for k in range(5)]
        mkt_ids = model_fixture_ids(days_mkt)
        r = sync_dates(sorted(set(days_mkt)), with_markets=True,
                       market_ids=mkt_ids or None, verbose=False)
        print(f"[7/9] market odds sync: {len(mkt_ids)} fixture model, "
              f"+{r.get('markets', 0)} harga baru")
    except Exception as e:
        print(f"[7/9] WARNING market sync gagal: {e!r} (lanjut pipeline)")

    # [8/9] Join odds pasar ke prediksi -> market_compare.csv (1xbet + median +
    # prob implied ternormalisasi). Kegagalan tidak menggagalkan pipeline.
    try:
        import market_orchestration
        rc = market_orchestration.build_market_compare()
        print(f"[8/9] market_compare: {rc['fixtures']} fixture, {rc['rows']} baris")
    except Exception as e:
        print(f"[8/9] WARNING market_compare gagal: {e!r} (lanjut pipeline)")

    # [8b/9] Rekomendasi slip odds deterministik (dari market_compare.csv).
    # Kegagalan tidak menggagalkan pipeline; slip diarsipkan di langkah 9.
    try:
        import slip_recommender
        rc = slip_recommender.recommend()
        print(f"[8b/9] slip: {rc['n_legs']} kaki, total {rc['total_odds']}, "
              f"in_band={rc['in_band']}")
    except Exception as e:
        print(f"[8b/9] WARNING slip gagal: {e!r} (lanjut pipeline)")

    # [9/9] Arsip snapshot harian (dengan market_compare) + rutekan pick piala
    # ke ledger/picks.jsonl (kompetisi) sebelum grading terpisah.
    try:
        from market_orchestration import archive_snapshots, sync_cup_picks_to_ledger
        ar = archive_snapshots()
        n_cup = sync_cup_picks_to_ledger()
        print(f"[9/9] archive {ar['date']}: {len(ar['archived'])} file | "
              f"cup picks -> ledger: {n_cup} baru")
    except Exception as e:
        print(f"[9/9] WARNING archive/cup-ledger gagal: {e!r} (lanjut pipeline)")

    try:
        import resolve_and_monitor
        resolve_and_monitor.main()
    except Exception as e:
        failed = True
        print(f"[10/9] FAILED resolve_and_monitor: {e!r}")

    if failed:
        print("# LIVE SHADOW: ADA LANGKAH GAGAL")
        sys.exit(1)
    print("# LIVE SHADOW OK")


if __name__ == "__main__":
    main()
