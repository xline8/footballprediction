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
from datetime import date, datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def _today():
    """Tanggal acuan run: UTC, sama dengan tanggal fixture di seluruh
    pipeline. date.today() lokal bisa berbeda sehari dari tanggal UTC
    fixture (audit ronde 7)."""
    return datetime.now(timezone.utc).date()


class _SkipStep(Exception):
    """Lewati satu langkah tanpa menandai run gagal (dependensi tidak
    terpenuhi — audit GPT 2026-10-31, B)."""


FIXTURE_SLUGS = ("EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1")
FIXTURE_FRESH_H = 12.0        # di bawah ini refresh fixture dilewati
FIXTURE_MAX_STALE_H = 48.0    # di atas ini prediksi tidak boleh jalan


def _fixtures_age_h():
    """Umur (jam) file fixture liga paling basi; inf bila ada yang hilang.
    Chain repo dulu tidak pernah me-refresh atau memeriksa umur fixture
    (audit GPT 2026-10-31, G) — kesegaran hanya datang dari pemanggil
    eksternal."""
    now = time.time()
    ages = []
    for slug in FIXTURE_SLUGS:
        p = os.path.join(BASE, "xg_raw", f"{slug}_2026_fixtures.json")
        if not os.path.exists(p):
            return float("inf")
        ages.append((now - os.path.getmtime(p)) / 3600.0)
    return max(ages)


class _Tee:
    """Duplikasi stdout ke file log: output shadow dulu hanya hidup di
    stdout pemanggil (cron), jadi klaim per langkah (mis. failed_dates
    di [7/9]) tidak bisa diverifikasi ulang dari disk (audit ronde 7)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            try:
                st.write(s)
            except Exception:
                pass
        # Flush semua stream selain stdout asli: tanpa ini log di
        # disk kosong sampai buffer penuh / proses selesai, padahal
        # gunanya justru dibaca saat run masih berjalan.
        for st in self.streams[1:]:
            try:
                st.flush()
            except Exception:
                pass
        return len(s)

    def flush(self):
        for st in self.streams:
            try:
                st.flush()
            except Exception:
                pass


def _run_py(script, *args):
    return subprocess.run([sys.executable, os.path.join(BASE, script), *args],
                          capture_output=True, text=True, timeout=600)


def main():
    print("#" * 70)
    print("# LIVE SHADOW DAILY RUN")
    print("#" * 70)
    failed = False

    # [0/6] Kesegaran fixture liga (audit GPT 2026-10-31, G): refresh di
    # dalam chain bila file paling basi melewati ambang, dan jangan
    # jalankan prediksi sama sekali bila fixture tetap terlalu basi —
    # jadwal/postponement basi meracuni semua produk hilir.
    fixtures_ok = True
    try:
        age = _fixtures_age_h()
        if age <= FIXTURE_FRESH_H:
            print(f"[0/6] fixtures: segar ({age:.1f} jam), refresh dilewati")
        else:
            print(f"[0/6] fixtures: umur {age:.1f} jam > "
                  f"{FIXTURE_FRESH_H:.0f} jam — refresh dari Understat")
            import refresh_fixtures
            refresh_fixtures.main()
            age = _fixtures_age_h()
            print(f"[0/6] fixtures: umur sesudah refresh {age:.1f} jam")
        if age > FIXTURE_MAX_STALE_H:
            fixtures_ok = False
            failed = True
            print(f"[0/6] FAILED fixtures: file fixture basi "
                  f"({age:.1f} jam > {FIXTURE_MAX_STALE_H:.0f} jam) dan "
                  f"refresh tidak memperbaikinya — prediksi dilewati")
    except Exception as e:
        age = _fixtures_age_h()
        if age > FIXTURE_MAX_STALE_H:
            fixtures_ok = False
            failed = True
            print(f"[0/6] FAILED fixtures: refresh gagal ({e!r}) dan "
                  f"file basi ({age:.1f} jam) — prediksi dilewati")
        else:
            print(f"[0/6] WARNING fixtures: refresh gagal ({e!r}); "
                  f"lanjut dengan file umur {age:.1f} jam")

    # pred_ok adalah gerbang konsumen prediksi (audit GPT 2026-10-31, B):
    # dulu kegagalan/partial di [1/6] hanya menandai exit code, sementara
    # best_picks, make_picks_live, market_compare, recommender tetap
    # membaca file sukses run sebelumnya dan archive menyalinnya ke
    # folder tanggal baru — arsip basi itu lalu dinilai grading run
    # berikutnya seolah rekomendasi hari ini.
    pred_ok = False
    if not fixtures_ok:
        print("[1/6] DILEWATI predictions: fixture tidak cukup segar")
    else:
        try:
            from predict_upcoming_refactored import generate_predictions
            res = generate_predictions()
            print(f"[1/6] predictions: {res.get('n_output_rows', 0)} rows "
                  f"(status {res.get('status')})")
            if res.get('t3_status') not in (None, 'ok'):
                print(f"[1/6] PERINGATAN T3: status "
                      f"{res.get('t3_status')} ({res.get('t3_error')}) — "
                      f"kolom T3 kosong; jalur meta tidak dapat dibedakan "
                      f"dari nol sah tanpa baris ini (audit GPT H)")
            if res.get('status') != 'success':
                failed = True
                print(f"[1/6] FAILED predictions: status internal "
                      f"{res.get('status')!r}; konsumen prediksi dilewati, "
                      f"file lama tidak dikonsumsi/diarsipkan")
            else:
                pred_ok = True
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
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        r = _run_py("best_picks.py", "--date", _today().isoformat())
        print(f"[4/6] best_picks: rc={r.returncode} | {r.stdout.strip()[-400:]}")
        if r.returncode != 0:
            failed = True
    except _SkipStep as e:
        print(f"[4/6] DILEWATI best_picks: {e}")
    except Exception as e:
        failed = True
        print(f"[4/6] FAILED best_picks: {e!r}")

    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import make_picks_live
        n = make_picks_live.main()
        print(f"[5/7] live picks baru: {n}")
        if n is None:
            failed = True
            print("[5/7] FAILED make_picks_live: file prediksi hilang")
    except _SkipStep as e:
        print(f"[5/7] DILEWATI make_picks_live: {e}")
    except Exception as e:
        failed = True
        print(f"[5/7] FAILED make_picks_live: {e!r}")

    # Sinkronisasi hasil tipsterarea untuk tanggal kemarin + H-2 secara eksplisit
    # (sebelum grading). --fresh memaksa fetch jaring (cache halaman tanggal
    # 20 menit dilewati) agar laga yang selesai larut ikut masuk. Kegagalan
    # jaringan tidak menggagalkan pipeline — catat warning, lanjutkan.
    try:
        y = _today() - timedelta(days=1)
        y2 = _today() - timedelta(days=2)
        r = _run_py("ta_scrape.py", y.isoformat(), y2.isoformat(), "--fresh")
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        shown = out[-300:] if out else err[-300:]
        # Kegagalan parsial (satu tanggal gagal, tanggal lain berhasil)
        # membuat CLI keluar 0 dan peringatannya hanya ada di stderr —
        # tampilkan konteks penanda gagalnya agar tanggal yang hilang
        # tidak senyap (audit ronde 5). Konteks di sekitar penanda,
        # bukan ekor: penanda yang >300 karakter dari akhir stderr
        # dulu lolos dari potongan ekor (audit ronde 7).
        if err and "gagal" not in shown and "GAGAL" not in shown:
            _i = err.find("gagal")
            if _i < 0:
                _i = err.find("GAGAL")
            if _i >= 0:
                shown += f" | stderr: ...{err[max(0, _i - 40):_i + 160]}"
        print(f"[6/7] tipsterarea hasil sync: rc={r.returncode} | {shown}")
        if r.returncode != 0:
            failed = True
            print(f"[6/7] FAILED ta sync rc={r.returncode} "
                  f"(lanjut pipeline, tapi run ditandai gagal)")
    except Exception as e:
        failed = True
        print(f"[6/7] FAILED ta sync: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [6b/7] Grading bet TA (ta/best_bets.csv) dari results.csv yang
    # baru tersinkron di [6/7]. grade() ada sejak lama tapi tidak
    # pernah dipanggil rantai mana pun, jadi bet OPEN menumpuk tak
    # dinilai berminggu-minggu (audit ronde 7). Idempoten; bet corner
    # tanpa data aktual dibiarkan OPEN oleh grade() sendiri.
    # Kegagalan = warning (pembukuan, bukan data).
    try:
        import ta_model
        ta_model.grade()
        print("[6b/7] ta bet grading: selesai")
    except Exception as e:
        print(f"[6b/7] WARNING ta bet grading gagal: {e!r}")

    # [7/9] Market odds sync: semua fixture model (liga TOP5 + piala), window
    # hari ini..+4, urut kickoff terdekat. Throttle market_needs_refresh diurus
    # sync_dates (~1.5 jam); hanya fetch yang perlu. Gagal jaringan = warning,
    # tidak menggagalkan pipeline. parse_match_page/schema tidak diubah.
    try:
        from market_orchestration import model_fixture_ids
        from ta_scrape import sync_dates
        days_mkt = [_today() + timedelta(days=k) for k in range(5)]
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
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import market_orchestration
        rc = market_orchestration.build_market_compare()
        print(f"[8/9] market_compare: {rc['fixtures']} fixture, "
              f"{rc['rows']} baris, {rc.get('unmatched', 0)} prediksi "
              f"tanpa fixture TA")
    except _SkipStep as e:
        print(f"[8/9] DILEWATI market_compare: {e}")
    except Exception as e:
        failed = True
        print(f"[8/9] FAILED market_compare: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [8b/9] Rekomendasi harian deterministik (dari market_compare.csv):
    # single bet + slip odds ±2 + slip odds ±10, semua untuk tanggal laporan.
    # Kegagalan tidak menggagalkan pipeline; file diarsipkan di langkah 9.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
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
    except _SkipStep as e:
        print(f"[8b/9] DILEWATI rekomendasi: {e}")
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

    # [9/9] Arsip snapshot harian (dengan market_compare). Arsip adalah
    # input grading hari-hari berikutnya, jadi file basi tidak boleh
    # tersalin ke folder tanggal baru (audit GPT 2026-10-31, B) —
    # langkah ini ter-gate pred_ok. Rute pick piala ke ledger terpisah:
    # prediksi piala independen dari prediksi liga, jadi tetap jalan.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        from market_orchestration import archive_snapshots
        ar = archive_snapshots()
        print(f"[9/9] archive {ar['date']}: {len(ar['archived'])} file")
    except _SkipStep as e:
        print(f"[9/9] DILEWATI archive: {e}")
    except Exception as e:
        failed = True
        print(f"[9/9] FAILED archive: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    try:
        from market_orchestration import sync_cup_picks_to_ledger
        n_cup = sync_cup_picks_to_ledger()
        print(f"[9/9] cup picks -> ledger: {n_cup} baru")
    except Exception as e:
        failed = True
        print(f"[9/9] FAILED cup-ledger: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [9b/9] Grading ledger uang (score_ledger): nilai ledger/picks.jsonl
    # (liga + piala) dari hasil yang sudah tersinkron di langkah-langkah
    # atas. Dulu grading ini hanya tercapai lewat run manual
    # pipeline_orchestrator --incremental, jadi ROI/CLV bisa basi
    # diam-diam sementara laporan harian tampil sukses (audit K4).
    # score_ledger dijalankan sebagai subprocess untuk isolasi:
    # kegagalannya terbaca dari rc dan tidak bisa menjatuhkan rantai.
    # (Impornya sendiri sudah tanpa efek samping sejak PR #26.)
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
    _real_stdout = sys.stdout
    _logf = None
    try:
        _logs = os.path.join(BASE, "logs")
        os.makedirs(_logs, exist_ok=True)
        _logf = open(os.path.join(
            _logs, f"shadow-{_today().isoformat()}.log"),
            "a", encoding="utf-8")
        sys.stdout = _Tee(_real_stdout, _logf)
    except Exception:
        pass
    try:
        main()
    finally:
        sys.stdout = _real_stdout
        if _logf is not None:
            _logf.close()
