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
from datetime import datetime, timedelta, timezone

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


# Status per produk untuk hasil run (audit Codex 2026-11-08, Major 3):
# dulu run bisa berakhir "OK" walau produk non-kritis (SOT, kartu,
# corner 1H, pecahan babak) gagal — monitoring tidak bisa membedakan
# run lengkap dari run parsial. Kini setiap langkah mencatat status
# produknya di sini; di akhir run ditulis ke
# logs/run_status_<tanggal>.json dan produk yang gagal disebut
# namanya di ringkasan akhir, juga saat run tetap exit 0.
PRODUCT_STATUS = {}


def _prod(name, ok, error=None):
    PRODUCT_STATUS[name] = {
        "status": "OK" if ok else "FAILED",
        "error": None if ok else (str(error) if error else "gagal"),
    }


def _write_run_status(run_failed):
    """Tulis status per produk ke logs/run_status_<tanggal>.json
    (atomik) dan kembalikan daftar nama produk yang FAILED."""
    import json
    failed_products = [n for n, s in PRODUCT_STATUS.items()
                       if s["status"] != "OK"]
    payload = {
        "date": _today().isoformat(),
        "run_ok": not run_failed,
        "products": PRODUCT_STATUS,
    }
    try:
        logs = os.path.join(BASE, "logs")
        os.makedirs(logs, exist_ok=True)
        path = os.path.join(logs,
                            f"run_status_{_today().isoformat()}.json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
    except Exception as e:
        print(f"# WARNING: status per produk gagal ditulis: {e!r}")
    return failed_products


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
    di [14/23]) tidak bisa diverifikasi ulang dari disk (audit ronde 7)."""

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
    PRODUCT_STATUS.clear()

    # [1/23] Kesegaran fixture liga (audit GPT 2026-10-31, G): refresh di
    # dalam chain bila file paling basi melewati ambang, dan jangan
    # jalankan prediksi sama sekali bila fixture tetap terlalu basi —
    # jadwal/postponement basi meracuni semua produk hilir.
    fixtures_ok = True
    try:
        age = _fixtures_age_h()
        if age <= FIXTURE_FRESH_H:
            print(f"[1/23] fixtures: segar ({age:.1f} jam), refresh dilewati")
        else:
            print(f"[1/23] fixtures: umur {age:.1f} jam > "
                  f"{FIXTURE_FRESH_H:.0f} jam — refresh jadwal "
                  f"(TipsterArea/Understat)")
            import refresh_fixtures
            srcs = refresh_fixtures.main() or {}
            age = _fixtures_age_h()
            print(f"[1/23] fixtures: umur sesudah refresh {age:.1f} jam")
            # A12-2: liga yang sumbernya fallback disk TIDAK segar —
            # kontennya dump beku yang mtime-nya baru ditulis ulang,
            # jadi cek umur di bawah tidak boleh membacanya sebagai
            # refresh berhasil. Prediksi tetap jalan di jadwal terakhir
            # yang diketahui (dump memuat semusim penuh), tapi run
            # ditandai gagal supaya sumber yang mati terlihat.
            fb = sorted(d for d, s in srcs.items()
                        if str(s).startswith("fallback"))
            if fb:
                failed = True
                print(f"[1/23] FAILED fixtures: liga {', '.join(fb)} "
                      f"disegarkan dari fallback disk (konten beku), "
                      f"bukan dari sumber segar — run ditandai gagal, "
                      f"prediksi lanjut di jadwal terakhir")
        if age > FIXTURE_MAX_STALE_H:
            fixtures_ok = False
            failed = True
            print(f"[1/23] FAILED fixtures: file fixture basi "
                  f"({age:.1f} jam > {FIXTURE_MAX_STALE_H:.0f} jam) dan "
                  f"refresh tidak memperbaikinya — prediksi dilewati")
    except Exception as e:
        # A12-6: handler ini tidak boleh ikut runtuh — _fixtures_age_h
        # yang gagal stat di sini dulu bisa membunuh shadow sebelum
        # banner kegagalan dan langkah grading. Default inf = basi.
        try:
            age = _fixtures_age_h()
        except Exception:
            age = float("inf")
        # Ronde 13: refresh bisa mati DI TENGAH loop setelah sebagian
        # liga sempat ditulis dari fallback disk — jalur sukses A12-2
        # tidak tercapai, tapi sumber liga yang sempat selesai tercatat
        # di refresh_fixtures.LAST_SOURCES; liga fallback itu tetap
        # harus menandai run gagal dan disebut namanya.
        fb = []
        try:
            import refresh_fixtures as _rf
            fb = sorted(d for d, s in (_rf.LAST_SOURCES or {}).items()
                        if str(s).startswith("fallback"))
        except Exception:
            fb = []
        if fb:
            failed = True
            print(f"[1/23] FAILED fixtures: liga {', '.join(fb)} "
                  f"disegarkan dari fallback disk (konten beku) "
                  f"sebelum refresh gagal ({e!r}) — run ditandai "
                  f"gagal, prediksi lanjut di jadwal terakhir")
        if age > FIXTURE_MAX_STALE_H:
            fixtures_ok = False
            failed = True
            print(f"[1/23] FAILED fixtures: refresh gagal ({e!r}) dan "
                  f"file basi ({age:.1f} jam) — prediksi dilewati")
        elif not fb:
            print(f"[1/23] WARNING fixtures: refresh gagal ({e!r}); "
                  f"lanjut dengan file umur {age:.1f} jam")

    if not fixtures_ok:
        _prod("fixtures", False,
              "file fixture basi dan refresh tidak memperbaikinya")
    elif failed:
        _prod("fixtures", False,
              "sebagian liga disegarkan dari fallback disk (konten beku)")
    else:
        _prod("fixtures", True)

    # pred_ok adalah gerbang konsumen prediksi (audit GPT 2026-10-31, B):
    # dulu kegagalan/partial di [2/23] hanya menandai exit code, sementara
    # best_picks, make_picks_live, market_compare, recommender tetap
    # membaca file sukses run sebelumnya dan archive menyalinnya ke
    # folder tanggal baru — arsip basi itu lalu dinilai grading run
    # berikutnya seolah rekomendasi hari ini.
    pred_ok = False
    if not fixtures_ok:
        print("[2/23] DILEWATI predictions: fixture tidak cukup segar")
    else:
        try:
            from predict_upcoming_refactored import generate_predictions
            res = generate_predictions()
            print(f"[2/23] predictions: {res.get('n_output_rows', 0)} rows "
                  f"(status {res.get('status')})")
            if res.get('t3_status') not in (None, 'ok'):
                print(f"[2/23] PERINGATAN T3: status "
                      f"{res.get('t3_status')} ({res.get('t3_error')}) — "
                      f"kolom T3 kosong; jalur meta tidak dapat dibedakan "
                      f"dari nol sah tanpa baris ini (audit GPT H)")
            if res.get('status') != 'success':
                failed = True
                print(f"[2/23] FAILED predictions: status internal "
                      f"{res.get('status')!r}; konsumen prediksi dilewati, "
                      f"file lama tidak dikonsumsi/diarsipkan")
            else:
                pred_ok = True
        except Exception as e:
            failed = True
            print(f"[2/23] FAILED predictions: {e!r}")
    _prod("predictions", pred_ok,
          None if pred_ok else "prediksi liga tidak sukses pada run ini")

    # Status produk memakai flag lokal _ok (pola langkah 4-8), BUKAN
    # delta terhadap `failed` global: dengan delta, kegagalan langkah
    # ini tercatat OK di run_status bila run sudah gagal lebih dulu.
    _ok = True
    try:
        _t_corner = time.time()
        r = _run_py("model_corners_v3.py", "--predict")
        print(f"[3/23] corner predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            failed = True
            _ok = False
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
                _ok = False
                print("[3/23] FAILED corner predictions: file corner "
                      "kosong padahal prediksi liga ada")
            else:
                # Kesegaran: script bisa keluar rc=0 TANPA menulis
                # (corner_params.json hilang / tak ada fixture) sehingga
                # file basi lolos terus. Cermin cek orchestrator.
                _cf = os.path.join(BASE, "predictions_corners_upcoming.csv")
                if os.path.exists(_cf) and \
                        os.path.getmtime(_cf) < _t_corner - 5:
                    failed = True
                    _ok = False
                    print("[3/23] FAILED corner predictions: file corner "
                          "basi (tidak ditulis ulang oleh run ini)")
    except Exception as e:
        failed = True
        _ok = False
        print(f"[3/23] FAILED corner predictions: {e!r}")
    _prod("corners", _ok,
          None if _ok else "langkah corner gagal (detail di log [3/23])")

    # [4/23] Prediksi tembakan ke gawang (SOT) untuk fixture mendatang
    # (model_sot.py, resep v5 regresi+NB+BB dari experiments/sot_model).
    # Langkah mandiri seperti corner — membaca fixture + data bersih,
    # tidak tergerbang pred_ok — tapi produknya baru dan belum punya
    # konsumen hilir, jadi kegagalannya hanya WARNING dan tidak
    # menandai run gagal (pola langkah non-kritis seperti [13/23]).
    _ok, _err = True, None
    try:
        _t_sot = time.time()
        r = _run_py("model_sot.py", "--predict")
        print(f"[4/23] sot predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _ok, _err = False, f"rc={r.returncode}"
            print(f"[4/23] WARNING sot predictions: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            # rc=0 tanpa menulis ulang = file basi lolos diam-diam
            # (cermin cek kesegaran corner di [3/23], tapi di sini
            # hanya warning).
            _sf = os.path.join(BASE, "predictions_sot_upcoming.csv")
            if not os.path.exists(_sf) or \
                    os.path.getmtime(_sf) < _t_sot - 5:
                _ok, _err = False, "file tidak ditulis ulang oleh run ini"
                print("[4/23] WARNING sot predictions: file SOT tidak "
                      "ditulis ulang oleh run ini")
    except Exception as e:
        _ok, _err = False, repr(e)
        print(f"[4/23] WARNING sot predictions gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")
    _prod("sot", _ok, _err)

    # [5/23] Pecahan babak (1H/2H) dari prediksi SOT produksi
    # (model_sot_halves_share.py): total v5 dipecah dengan porsi liga
    # konstan beku S=0,4563 — pemenang validasi v9 atas pecahan yang
    # dimodelkan per laga (RESULTS_V9_HALVES_PRODUCT.md). Langkah
    # non-kritis seperti SOT [4/23]: kegagalannya hanya WARNING,
    # tidak menandai run gagal. Belum ada sumber odds SOT per babak.
    _ok, _err = True, None
    try:
        _t_soth = time.time()
        r = _run_py("model_sot_halves_share.py")
        print(f"[5/23] sot halves split: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _ok, _err = False, f"rc={r.returncode}"
            print(f"[5/23] WARNING sot halves split: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            _shf = os.path.join(BASE, "predictions_sot_halves_upcoming.csv")
            if not os.path.exists(_shf) or \
                    os.path.getmtime(_shf) < _t_soth - 5:
                _ok, _err = False, "file tidak ditulis ulang oleh run ini"
                print("[5/23] WARNING sot halves split: file pecahan "
                      "tidak ditulis ulang oleh run ini")
    except Exception as e:
        _ok, _err = False, repr(e)
        print(f"[5/23] WARNING sot halves split gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")
    _prod("sot_halves", _ok, _err)

    # [6/23] Prediksi total kartu kuning untuk fixture mendatang
    # (model_cards.py, resep experiments/cards_model yang lolos gerbang
    # audit §3C 2026-11-07). Langkah non-kritis seperti SOT [4/23]:
    # kegagalannya hanya WARNING, tidak menandai run gagal.
    _ok, _err = True, None
    try:
        _t_cards = time.time()
        r = _run_py("model_cards.py", "--predict")
        print(f"[6/23] cards predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _ok, _err = False, f"rc={r.returncode}"
            print(f"[6/23] WARNING cards predictions: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            _kf = os.path.join(BASE, "predictions_cards_upcoming.csv")
            if not os.path.exists(_kf) or \
                    os.path.getmtime(_kf) < _t_cards - 5:
                _ok, _err = False, "file tidak ditulis ulang oleh run ini"
                print("[6/23] WARNING cards predictions: file kartu tidak "
                      "ditulis ulang oleh run ini")
    except Exception as e:
        _ok, _err = False, repr(e)
        print(f"[6/23] WARNING cards predictions gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")
    _prod("cards", _ok, _err)

    # [7/23] Prediksi corner BABAK PERTAMA untuk fixture mendatang
    # (model_corners_1h.py, resep experiments/half_corners yang lolos
    # gerbang formal audit §2C C-2 2026-11-07 — margin atas baseline
    # naif hanya 0.0001, praktis seri; lihat RESULTS.md eksperimen).
    # Langkah non-kritis seperti SOT [4/23]: kegagalannya hanya
    # WARNING, tidak menandai run gagal. Belum ada sumber odds 1H.
    _ok, _err = True, None
    try:
        _t_c1h = time.time()
        r = _run_py("model_corners_1h.py")
        print(f"[7/23] 1h-corner predictions: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _ok, _err = False, f"rc={r.returncode}"
            print(f"[7/23] WARNING 1h-corner predictions: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            _hf = os.path.join(BASE, "predictions_corners_1h_upcoming.csv")
            if not os.path.exists(_hf) or \
                    os.path.getmtime(_hf) < _t_c1h - 5:
                _ok, _err = False, "file tidak ditulis ulang oleh run ini"
                print("[7/23] WARNING 1h-corner predictions: file corner 1H "
                      "tidak ditulis ulang oleh run ini")
    except Exception as e:
        _ok, _err = False, repr(e)
        print(f"[7/23] WARNING 1h-corner predictions gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")
    _prod("corners_1h", _ok, _err)

    # [8/23] Penyajian corner per babak (model_corners_halves.py):
    # babak 1 memakai ulang output model corner 1H teradopsi di
    # langkah sebelumnya; babak 2 diturunkan dengan pengurangan dari
    # mu FT produksi (sudah termasuk pengali teritorial) — BUKAN model
    # baru dan tidak punya validasi sendiri. Langkah non-kritis
    # seperti [7/23]: kegagalannya hanya WARNING. Belum ada sumber
    # odds corner per babak.
    _ok, _err = True, None
    try:
        _t_ch = time.time()
        r = _run_py("model_corners_halves.py")
        print(f"[8/23] corner halves: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _ok, _err = False, f"rc={r.returncode}"
            print(f"[8/23] WARNING corner halves: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            _chf = os.path.join(BASE, "predictions_corners_halves_upcoming.csv")
            if not os.path.exists(_chf) or \
                    os.path.getmtime(_chf) < _t_ch - 5:
                _ok, _err = False, "file tidak ditulis ulang oleh run ini"
                print("[8/23] WARNING corner halves: file corner "
                      "halves tidak ditulis ulang oleh run ini")
    except Exception as e:
        _ok, _err = False, repr(e)
        print(f"[8/23] WARNING corner halves gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")
    _prod("corner_halves", _ok, _err)

    # [9/23] Pecahan babak (1H/2H) dari prediksi GOL produksi
    # (model_goals_halves.py): lambda FT produksi dipecah dengan
    # porsi konstan beku (babak 1: kandang 0,4419, tandang 0,4440),
    # Poisson murni, TANPA koreksi dan tanpa pemodelan babak per
    # laga — desain nol yang angkanya terverifikasi di eksperimen
    # halves 3 di bawah harness refit setia-produksi (kalibrasi
    # Over 1.5 +0,22pp babak 1 / -0,71pp babak 2, n = 5.255;
    # RESULTS_HALVES_GOALS_V3.md, keputusan tayang user
    # 2026-11-08). Konsumen murni dari prediksi liga, jadi ter-gate
    # pred_ok seperti konsumen lain; langkah non-kritis seperti
    # [8/23]: kegagalannya hanya WARNING. Belum ada sumber odds
    # gol per babak.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        _t_gh = time.time()
        r = _run_py("model_goals_halves.py")
        print(f"[9/23] goal halves: rc={r.returncode} | {r.stdout.strip()[-300:]}")
        if r.returncode != 0:
            _prod("goals_halves", False, f"rc={r.returncode}")
            print(f"[9/23] WARNING goal halves: rc={r.returncode} "
                  f"(lanjut pipeline; run tidak ditandai gagal)")
        else:
            _ghf = os.path.join(BASE, "predictions_goals_halves_upcoming.csv")
            if not os.path.exists(_ghf) or \
                    os.path.getmtime(_ghf) < _t_gh - 5:
                _prod("goals_halves", False,
                      "file tidak ditulis ulang oleh run ini")
                print("[9/23] WARNING goal halves: file pecahan "
                      "tidak ditulis ulang oleh run ini")
            else:
                _prod("goals_halves", True)
    except _SkipStep as e:
        _prod("goals_halves", False, f"dilewati: {e}")
        print(f"[9/23] DILEWATI goal halves: {e}")
    except Exception as e:
        _prod("goals_halves", False, repr(e))
        print(f"[9/23] WARNING goal halves gagal: {e!r} "
              f"(lanjut pipeline; run tidak ditandai gagal)")

    # Flag lokal _ok, bukan delta `failed` global — lihat catatan
    # di langkah corner [3/23].
    _ok = True
    try:
        import predict_cups
        rc = predict_cups.main()
        print(f"[10/23] cup predictions: {rc.get('n_gol', 0)} gol, "
              f"{rc.get('n_corner', 0)} corner")
        if rc.get('status') == 'failed':
            failed = True
            _ok = False
            print("[10/23] FAILED cup predictions: fixture piala ada "
                  "tapi nol prediksi gol terpetakan")
    except Exception as e:
        failed = True
        _ok = False
        print(f"[10/23] FAILED cup predictions: {e!r}")
    _prod("cups", _ok,
          None if _ok else "langkah piala gagal (detail di log [10/23])")

    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import make_picks_live
        n = make_picks_live.main()
        print(f"[11/23] live picks baru: {n}")
        if n is None:
            failed = True
            print("[11/23] FAILED make_picks_live: file prediksi hilang")
        _prod("live_picks", n is not None,
              None if n is not None else "file prediksi hilang")
    except _SkipStep as e:
        _prod("live_picks", False, f"dilewati: {e}")
        print(f"[11/23] DILEWATI make_picks_live: {e}")
    except Exception as e:
        failed = True
        _prod("live_picks", False, repr(e))
        print(f"[11/23] FAILED make_picks_live: {e!r}")

    # Sinkronisasi hasil tipsterarea untuk tanggal kemarin + H-2 secara eksplisit
    # (sebelum grading). --fresh memaksa fetch jaring (cache halaman tanggal
    # 20 menit dilewati) agar laga yang selesai larut ikut masuk. Kegagalan
    # jaringan tidak menggagalkan pipeline — catat warning, lanjutkan.
    # Flag lokal _ok, bukan delta `failed` global — lihat catatan
    # di langkah corner [3/23].
    _ok = True
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
        print(f"[12/23] tipsterarea hasil sync: rc={r.returncode} | {shown}")
        if r.returncode != 0:
            failed = True
            _ok = False
            print(f"[12/23] FAILED ta sync rc={r.returncode} "
                  f"(lanjut pipeline, tapi run ditandai gagal)")
    except Exception as e:
        failed = True
        _ok = False
        print(f"[12/23] FAILED ta sync: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")
    _prod("ta_sync", _ok,
          None if _ok else "sinkronisasi hasil TA gagal (detail di log [12/23])")

    # [13/23] Grading bet TA (ta/best_bets.csv) dari results.csv yang
    # baru tersinkron di [12/23]. grade() ada sejak lama tapi tidak
    # pernah dipanggil rantai mana pun, jadi bet OPEN menumpuk tak
    # dinilai berminggu-minggu (audit ronde 7). Idempoten; bet corner
    # tanpa data aktual dibiarkan OPEN oleh grade() sendiri.
    # Kegagalan = warning (pembukuan, bukan data).
    try:
        import ta_model
        ta_model.grade()
        print("[13/23] ta bet grading: selesai")
        _prod("ta_bet_grading", True)
    except Exception as e:
        _prod("ta_bet_grading", False, repr(e))
        print(f"[13/23] WARNING ta bet grading gagal: {e!r}")

    # [14/23] Market odds sync: semua fixture model (liga TOP5 + piala), window
    # hari ini..+4, urut kickoff terdekat. Throttle market_needs_refresh diurus
    # sync_dates (~1.5 jam); hanya fetch yang perlu. Gagal jaringan = warning,
    # tidak menggagalkan pipeline. parse_match_page/schema tidak diubah.
    # Tergerbang pred_ok seperti konsumen prediksi lain (A12-3): tanpa
    # gerbang, kegagalan prediksi tetap membakar fetch harga untuk id
    # dari file prediksi basi.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        from market_orchestration import model_fixture_ids
        from ta_scrape import sync_dates
        days_mkt = [_today() + timedelta(days=k) for k in range(5)]
        mkt_ids = model_fixture_ids(days_mkt)
        r = sync_dates(sorted(set(days_mkt)), with_markets=True,
                       market_ids=mkt_ids or None, verbose=False)
        print(f"[14/23] market odds sync: {len(mkt_ids)} fixture model, "
              f"+{r.get('markets', 0)} harga baru, "
              f"{r.get('unresolved_market_ids') or 0} id pasar tak "
              f"terpetakan, tanggal kosong: "
              f"{r.get('empty_dates') or []}, tanggal gagal: "
              f"{r.get('failed_dates') or []}")
        _prod("market_sync", True)
    except _SkipStep as e:
        _prod("market_sync", False, f"dilewati: {e}")
        print(f"[14/23] DILEWATI market sync: {e}")
    except Exception as e:
        failed = True
        _prod("market_sync", False, repr(e))
        print(f"[14/23] FAILED market sync: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [15/23] Join odds pasar ke prediksi -> market_compare.csv (1xbet + median +
    # prob implied ternormalisasi). Kegagalan tidak menggagalkan pipeline.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import market_orchestration
        rc = market_orchestration.build_market_compare()
        print(f"[15/23] market_compare: {rc['fixtures']} fixture, "
              f"{rc['rows']} baris, {rc.get('unmatched', 0)} prediksi "
              f"tanpa fixture TA")
        _prod("market_compare", True)
    except _SkipStep as e:
        _prod("market_compare", False, f"dilewati: {e}")
        print(f"[15/23] DILEWATI market_compare: {e}")
    except Exception as e:
        failed = True
        _prod("market_compare", False, repr(e))
        print(f"[15/23] FAILED market_compare: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [16/23] Build bet TA (ta_model): model_markets.csv + best_bets.csv
    # dari prediksi hari ini dan snapshot harga yang baru disinkronkan
    # di [14/23]. Dulu build hanya jalan di refit mingguan (--run-all)
    # dan CLI, jadi baris best_bets membeku berhari-hari sementara
    # best_picks mengonsumsinya setiap hari (audit ronde 13). Bet OPEN
    # yang bet_id-nya terbit lagi diperbarui nilainya oleh build
    # sendiri; grading bet lama sudah jalan di [13/23] sebelum baris
    # baru ditambahkan. Tergerbang pred_ok seperti konsumen prediksi
    # lain. Kegagalan ditandai gagal; best_picks lanjut dengan file
    # terakhir yang ada.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import ta_model
        if ta_model.build():
            # build() mengembalikan 1 tanpa menulis model_markets
            # bila ta/fixtures.csv kosong (A14-2): tanpa pemeriksaan
            # ini langkah tercatat selesai dan best_picks memeringkat
            # dari file build sebelumnya. Orchestrator memeriksa rc
            # yang sama; samakan di sini.
            raise RuntimeError("ta_model.build() rc != 0 "
                               "(ta/fixtures.csv kosong?)")
        print("[16/23] ta_model build: selesai")
        _prod("ta_model", True)
    except _SkipStep as e:
        _prod("ta_model", False, f"dilewati: {e}")
        print(f"[16/23] DILEWATI ta_model build: {e}")
    except Exception as e:
        failed = True
        _prod("ta_model", False, repr(e))
        print(f"[16/23] FAILED ta_model build: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [17/23] best_picks: peringkat Pick Teraman dari prediksi + bet TA.
    # Sengaja SETELAH build [16/23] supaya baris ta_model yang dibaca
    # adalah hasil build hari ini, bukan build mingguan terakhir.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        r = _run_py("best_picks.py", "--date", _today().isoformat())
        print(f"[17/23] best_picks: rc={r.returncode} | {r.stdout.strip()[-400:]}")
        if r.returncode != 0:
            failed = True
        _prod("best_picks", r.returncode == 0,
              None if r.returncode == 0 else f"rc={r.returncode}")
    except _SkipStep as e:
        _prod("best_picks", False, f"dilewati: {e}")
        print(f"[17/23] DILEWATI best_picks: {e}")
    except Exception as e:
        failed = True
        _prod("best_picks", False, repr(e))
        print(f"[17/23] FAILED best_picks: {e!r}")

    # [16/20] Rekomendasi harian deterministik (dari market_compare.csv):
    # single bet + slip odds ±2 + slip odds ±10, semua untuk tanggal laporan.
    # Kegagalan tidak menggagalkan pipeline; file diarsipkan di langkah 18.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        import slip_recommender
        rc = slip_recommender.recommend()
        print(f"[18/23] single: {rc['single']['pick']} "
              f"(EV {rc['single']['ev']}) | slip2: {rc['slip2']['n_legs']} "
              f"kaki, total {rc['slip2']['total_odds']}, "
              f"in_band={rc['slip2']['in_band']} | slip10: "
              f"{rc['slip10']['n_legs']} kaki, total "
              f"{rc['slip10']['total_odds']}, in_band={rc['slip10']['in_band']}")
        _tr = [nm for nm in ("slip2", "slip10")
               if rc[nm].get("search_truncated")]
        if _tr:
            print(f"[18/23] PERINGATAN: pencarian {'/'.join(_tr)} "
                  f"terpotong batas node — hasil kandidat terbaik "
                  f"sebagian, bukan optimum terbukti")
        _prod("recommendations", True)
    except _SkipStep as e:
        _prod("recommendations", False, f"dilewati: {e}")
        print(f"[18/23] DILEWATI rekomendasi: {e}")
    except Exception as e:
        failed = True
        _prod("recommendations", False, repr(e))
        print(f"[18/23] FAILED rekomendasi: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [17/20] Grading harian produk rekomendasi (pick teraman/single/slip2/
    # slip10) dari arsip <= kemarin -> histori kalibrasi. Bisa hasil-nya belum
    # tersedia -> pending, dinilai run berikutnya. Gagal tidak menggagalkan.
    try:
        import grade_recommendations
        rc = grade_recommendations.main()
        print(f"[19/23] grading rekomendasi: rc={rc}")
        if rc != 0:
            failed = True
            print("[19/23] FAILED grading rekomendasi: rc != 0 "
                  "(run ditandai gagal)")
        _prod("recommendation_grading", rc == 0,
              None if rc == 0 else f"rc={rc}")
    except Exception as e:
        failed = True
        _prod("recommendation_grading", False, repr(e))
        print(f"[19/23] FAILED grading rekomendasi: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [20/23] Arsip snapshot harian (dengan market_compare). Arsip adalah
    # input grading hari-hari berikutnya, jadi file basi tidak boleh
    # tersalin ke folder tanggal baru (audit GPT 2026-10-31, B) —
    # langkah ini ter-gate pred_ok. Rute pick piala ke ledger terpisah:
    # prediksi piala independen dari prediksi liga, jadi tetap jalan.
    try:
        if not pred_ok:
            raise _SkipStep("prediksi liga tidak sukses pada run ini")
        from market_orchestration import archive_snapshots
        ar = archive_snapshots()
        print(f"[20/23] archive {ar['date']}: {len(ar['archived'])} file"
              f" (+{len(ar.get('kept', []))} sudah ada, write-once)")
        if ar.get("skipped"):
            print(f"[20/23] ! file dilewati (generasi tanggal lain): "
                  f"{ar['skipped']}")
        _prod("archive", True)
    except _SkipStep as e:
        _prod("archive", False, f"dilewati: {e}")
        print(f"[20/23] DILEWATI archive: {e}")
    except Exception as e:
        failed = True
        _prod("archive", False, repr(e))
        print(f"[20/23] FAILED archive: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    try:
        from market_orchestration import sync_cup_picks_to_ledger
        n_cup = sync_cup_picks_to_ledger()
        print(f"[20/23] cup picks -> ledger: {n_cup} baru")
        _prod("cup_ledger", True)
    except Exception as e:
        failed = True
        _prod("cup_ledger", False, repr(e))
        print(f"[20/23] FAILED cup-ledger: {e!r} "
              f"(lanjut pipeline, tapi run ditandai gagal)")

    # [21/23] Grading ledger uang (score_ledger): nilai ledger/picks.jsonl
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
        print(f"[21/23] score_ledger: rc={r.returncode} | {out[-300:]}")
        if r.returncode != 0:
            failed = True
            print("[21/23] FAILED score_ledger (run ditandai gagal)")
        _prod("score_ledger", r.returncode == 0,
              None if r.returncode == 0 else f"rc={r.returncode}")
    except Exception as e:
        failed = True
        _prod("score_ledger", False, repr(e))
        print(f"[21/23] FAILED score_ledger: {e!r}")

    try:
        import resolve_and_monitor
        resolve_and_monitor.main()
        _prod("monitor", True)
    except Exception as e:
        failed = True
        _prod("monitor", False, repr(e))
        print(f"[22/23] FAILED resolve_and_monitor: {e!r}")

    # [23/23] Grading pasar baru (SOT total, kartu total, corner 1H)
    # dari snapshot arsip -> ledger/new_market_grades.jsonl +
    # new_market_summary.json (grade_new_markets.py). Aditif: tidak
    # menyentuh ledger/kalibrasi rekomendasi yang sudah ada. Langkah
    # non-kritis seperti produk yang dinilainya: kegagalan hanya
    # WARNING dan tidak menandai run gagal, tapi tercatat FAILED di
    # status per produk.
    try:
        r = _run_py("grade_new_markets.py")
        out = (r.stdout or r.stderr or "").strip()
        print(f"[23/23] grading pasar baru: rc={r.returncode} | {out[-300:]}")
        if r.returncode != 0:
            _prod("new_market_grading", False, f"rc={r.returncode}")
            print("[23/23] WARNING grading pasar baru gagal "
                  "(lanjut; run tidak ditandai gagal)")
        else:
            _prod("new_market_grading", True)
    except Exception as e:
        _prod("new_market_grading", False, repr(e))
        print(f"[23/23] WARNING grading pasar baru gagal: {e!r} "
              f"(lanjut; run tidak ditandai gagal)")

    _failed_products = _write_run_status(failed)
    if _failed_products:
        print(f"# PRODUK GAGAL: {', '.join(_failed_products)}")
    else:
        print("# SEMUA PRODUK OK")
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
