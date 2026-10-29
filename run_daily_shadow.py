#!/usr/bin/env python3
"""run_daily_shadow.py — orchestrator harian live shadow (Phase 6).

Alur: generate predictions (predict_upcoming) -> filter & ledger
(make_picks_live) -> resolve & monitor (resolve_and_monitor).

Dipakai oleh pipeline_orchestrator.py atau standalone (cron).
"""

import os
import sys
import subprocess
import time
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
        if res.get('status') != 'success':
            failed = True
            print(f"[1/6] FAILED predictions: status internal "
                  f"{res.get('status')!r}; file prediksi lama tetap di disk")
    except Exception as e:
        failed = True
        print(f"[1/6] FAILED predictions: {e!r}")

    try:
        _t_corner = time.time()
        r = _run_py("model_corners_v3.py", "--predict")
        print(f"[2/6] corner predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            failed = True
        else:
            # rc=0 dengan file corner KOSONG padahal ada prediksi liga
            # adalah kegagalan diam (lolos terus di versi lama).
            def _nrows(fn):
                p = os.path.join(BASE, fn)
                if not os.path.exists(p):
                    return 0
                with open(p, encoding="utf-8") as f:
                    return max(0, sum(1 for _ in f) - 1)
            if _nrows("predictions_upcoming.csv") > 0 and \
                    _nrows("predictions_corners_upcoming.csv") == 0:
                failed = True
                print("[2/6] FAILED corner predictions: file corner "
                      "kosong padahal prediksi liga ada")
            else:
                # Kesegaran: script bisa keluar rc=0 TANPA menulis
                # (corner_params.json hilang / tak ada fixture) sehingga
                # file basi lolos terus. Cermin cek orchestrator.
                _cf = os.path.join(BASE, "predictions_corners_upcoming.csv")
                if os.path.exists(_cf) and \
                        os.path.getmtime(_cf) < _t_corner - 5:
                    failed = True
                    print("[2/6] FAILED corner predictions: file corner "
                          "basi (tidak ditulis ulang oleh run ini)")
    except Exception as e:
        failed = True
        print(f"[2/6] FAILED corner predictions: {e!r}")

    try:
        import predict_cups
        rc = predict_cups.main()
        print(f"[3/6] cup predictions: {rc.get('n_gol', 0)} gol, "
              f"{rc.get('n_corner', 0)} corner")
        if rc.get('status') == 'failed':
            failed = True
            print("[3/6] FAILED cup predictions: fixture piala ada "
                  "tapi nol prediksi gol terpetakan")
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
        if n is None:
            failed = True
            print("[5/7] FAILED make_picks_live: file prediksi hilang")
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
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        shown = out[-300:] if out else err[-300:]
        # Kegagalan parsial (satu tanggal gagal, tanggal lain berhasil)
        # membuat CLI keluar 0 dan peringatannya hanya ada di stderr —
        # tampilkan ekornya bila memuat penanda gagal, agar tanggal yang
        # hilang tidak senyap (audit ronde 5).
        if err and ("gagal" in err or "GAGAL" in err) and err not in shown:
            shown += f" | stderr: {err[-200:]}"
        print(f"[6/7] tipsterarea hasil sync: rc={r.returncode} | {shown}")
        if r.returncode != 0:
            failed = True
            print(f"[6/7] FAILED ta sync rc={r.returncode} "
                  f"(lanjut pipeline, tapi run ditandai gagal)")
    except Exception as e:
        failed = True
        print(f"[6/7] FAILED ta sync: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

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
              f"+{r.get('markets', 0)} harga baru, "
              f"{r.get('unresolved_market_ids') or 0} id pasar tak "
              f"terpetakan, tanggal kosong: "
              f"{r.get('empty_dates') or []}, tanggal gagal: "
              f"{r.get('failed_dates') or []}")
    except Exception as e:
        failed = True
        print(f"[7/9] FAILED market sync: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [8/9] Join odds pasar ke prediksi -> market_compare.csv (1xbet + median +
    # prob implied ternormalisasi). Kegagalan tidak menggagalkan pipeline.
    try:
        import market_orchestration
        rc = market_orchestration.build_market_compare()
        print(f"[8/9] market_compare: {rc['fixtures']} fixture, "
              f"{rc['rows']} baris, {rc.get('unmatched', 0)} prediksi "
              f"tanpa fixture TA")
    except Exception as e:
        failed = True
        print(f"[8/9] FAILED market_compare: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [8b/9] Rekomendasi harian deterministik (dari market_compare.csv):
    # single bet + slip odds ±2 + slip odds ±10, semua untuk tanggal laporan.
    # Kegagalan tidak menggagalkan pipeline; file diarsipkan di langkah 9.
    try:
        import slip_recommender
        rc = slip_recommender.recommend()
        print(f"[8b/9] single: {rc['single']['pick']} "
              f"(EV {rc['single']['ev']}) | slip2: {rc['slip2']['n_legs']} "
              f"kaki, total {rc['slip2']['total_odds']}, "
              f"in_band={rc['slip2']['in_band']} | slip10: "
              f"{rc['slip10']['n_legs']} kaki, total "
              f"{rc['slip10']['total_odds']}, in_band={rc['slip10']['in_band']}")
        _tr = [nm for nm in ("slip2", "slip10")
               if rc[nm].get("search_truncated")]
        if _tr:
            print(f"[8b/9] PERINGATAN: pencarian {'/'.join(_tr)} "
                  f"terpotong batas node — hasil kandidat terbaik "
                  f"sebagian, bukan optimum terbukti")
    except Exception as e:
        failed = True
        print(f"[8b/9] FAILED rekomendasi: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [8c/9] Grading harian produk rekomendasi (pick teraman/single/slip2/
    # slip10) dari arsip <= kemarin -> histori kalibrasi. Bisa hasil-nya belum
    # tersedia -> pending, dinilai run berikutnya. Gagal tidak menggagalkan.
    try:
        import grade_recommendations
        rc = grade_recommendations.main()
        print(f"[8c/9] grading rekomendasi: rc={rc}")
        if rc != 0:
            failed = True
            print("[8c/9] FAILED grading rekomendasi: rc != 0 "
                  "(run ditandai gagal)")
    except Exception as e:
        failed = True
        print(f"[8c/9] FAILED grading rekomendasi: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [9/9] Arsip snapshot harian (dengan market_compare) + rutekan pick piala
    # ke ledger/picks.jsonl (kompetisi) sebelum grading terpisah.
    try:
        from market_orchestration import archive_snapshots, sync_cup_picks_to_ledger
        ar = archive_snapshots()
        n_cup = sync_cup_picks_to_ledger()
        print(f"[9/9] archive {ar['date']}: {len(ar['archived'])} file | "
              f"cup picks -> ledger: {n_cup} baru")
    except Exception as e:
        failed = True
        print(f"[9/9] FAILED archive/cup-ledger: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [9b/9] Grading ledger uang (score_ledger): nilai ledger/picks.jsonl
    # (liga + piala) dari hasil yang sudah tersinkron di langkah-langkah
    # atas. Dulu grading ini hanya tercapai lewat run manual
    # pipeline_orchestrator --incremental, jadi ROI/CLV bisa basi
    # diam-diam sementara laporan harian tampil sukses (audit K4).
    # score_ledger mengeksekusi saat diimpor, jadi dijalankan sebagai
    # subprocess.
    try:
        r = _run_py("score_ledger.py")
        out = (r.stdout or r.stderr or "").strip()
        print(f"[9b/9] score_ledger: rc={r.returncode} | {out[-300:]}")
        if r.returncode != 0:
            failed = True
            print("[9b/9] FAILED score_ledger (run ditandai gagal)")
    except Exception as e:
        failed = True
        print(f"[9b/9] FAILED score_ledger: {e!r}")

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
