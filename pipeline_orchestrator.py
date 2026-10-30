#!/usr/bin/env python3
"""pipeline_orchestrator.py - Orchestrator untuk pipeline prediksi sepakbola."""

import csv
import glob
import os
import shutil
import sys
import json
import time
import traceback
from datetime import datetime, date, timedelta, timezone
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import paths
from football_etl import (
    get_config, load_fd_odds, TOP5
)
from data_loader import get_loader
from model_state import ModelState, save_model_state

CUP_LEAGUES = ("England - EFL Cup", "Germany - Cup Germany")

RECORDS = os.path.join(BASE_DIR, "records_cache.jsonl")
XG_SLUGS = ("EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1")
# Refresh data latih hanya musim berjalan (2627). Override via env bila perlu.
REFRESH_SEASON = os.environ.get("FOOTBALL_REFRESH_SEASON", "2627")

# Langkah yang status 'partial'-nya LUNAK: tidak memblokir langkah
# hilir dan tidak menggagalkan run, tapi tetap dicatat di
# partial_steps + last_full_pipeline.json (audit ronde 8). Alasannya:
# degradasi sebagian di kedua langkah ini meninggalkan artefak lama
# yang masih sah — model: state divisi yang gagal fit tetap versi
# sebelumnya (divisi lain segar); odds: sumber football-data memang
# kosong di produksi, jadi exception di satu divisi tidak mengubah
# output apa pun. Partial dari langkah LAIN (xg, scoring) tetap keras.
SOFT_PARTIAL_STEPS = {"model", "odds"}


def _cup_fixture_ids(days):
    """game_id fixture piala (EFL Cup / DFB Pokal) dalam jendela tanggal.

    Bila tidak ada fixture piala, return kosong (perilaku tanggal tanpa piala
    tidak berubah). Dipakai untuk memastikan odds pasar piala tersedia.
    """
    try:
        import csv
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "ta", "fixtures.csv")
        lo, hi = min(days), max(days)
        ids = []
        with open(fpath, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("league") not in CUP_LEAGUES:
                    continue
                d = r.get("date", "")
                if lo.isoformat() <= d <= hi.isoformat():
                    ids.append(r["game_id"])
        return ids
    except Exception:
        return []


def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


class PipelineOrchestrator:
    """Orchestrator utama untuk pipeline prediksi sepakbola."""

    def __init__(self, config: dict = None, verbose: bool = True):
        self.loader = get_loader()
        self.config = config or get_config()
        self.verbose = verbose
        self.half_life = self.config.get('hl', 270.0)
        self.w_1x2 = self.config.get('w_1x2', 0.05)
        self.w_ou = self.config.get('w_ou', 0.05)
        self.max_train = self.config.get('max_train', 4000)
        self.start_time = None
        self.stats = defaultdict(int)

    def run_full_pipeline(self) -> dict:
        """Jalankan pipeline lengkap dari awal ke akhir."""
        self.start_time = time.time()
        results = {}
        log("=" * 60, "INFO")
        log("Starting Full Pipeline", "INFO")
        log("=" * 60, "INFO")

        # Urutan + gerbang dependensi (audit ronde 7, MEDIUM): dulu
        # kegagalan satu langkah TIDAK mengisolasi langkah berikutnya —
        # refresh yang gagal (dan dirollback) tetap diikuti fit/scoring
        # yang menimpa state & prediksi, jadi artefak di disk tampak
        # segar dan satu-satunya jejak kegagalan adalah status akhir.
        # Kini langkah yang hulunya 'failed'/'partial' dilewati dan
        # dicatat 'skipped'. Corner berjalan SETELAH scoring agar guard
        # file kosong/basinya membaca predictions_upcoming.csv run ini,
        # bukan run sebelumnya. Langkah TA (scrape/model) independen
        # dari data latih dan selalu jalan; validation selalu jalan
        # (murni pelaporan).
        steps = [
            ("refresh", self.step_refresh_training_data, ()),
            ("data", self.step_check_data, ()),
            ("xg", self.step_build_xg, ("refresh",)),
            ("model", self.step_fit_models, ("refresh",)),
            ("scoring", self.step_score_upcoming, ("refresh", "xg", "model")),
            ("corner_model", self.step_score_corners, ("refresh",)),
            ("odds", self.step_integrate_odds, ("scoring",)),
            ("ta_scrape", self.scrape_live_odds, ()),
            ("ta_model", self.step_ta_model, ()),
            ("cups", self.step_predict_cups, ("refresh",)),
            ("picks", self.step_generate_picks, ("scoring", "cups")),
            ("validation", self.step_validation, ()),
        ]
        current = None
        try:
            for name, fn, blocked_by in steps:
                # 'skipped' karena upstream gagal ikut memblokir:
                # tanpa ini rantai skip berhenti di langkah pertama
                # dan langkah hilir tetap mengonsumsi artefak basi.
                # 'partial' hanya memblokir dari langkah non-lunak
                # (SOFT_PARTIAL_STEPS).
                def _blocks(step_name, v):
                    if not isinstance(v, dict):
                        return False
                    if v.get('status') == 'failed':
                        return True
                    if v.get('status') == 'partial':
                        return step_name not in SOFT_PARTIAL_STEPS
                    return (v.get('status') == 'skipped'
                            and str(v.get('reason', '')).startswith(
                                'upstream_failed'))
                bad = [b for b in blocked_by
                       if _blocks(b, results.get(b))]
                if bad:
                    log(f"  ! {name} dilewati: langkah hulu gagal: {bad}",
                        "WARN")
                    results[name] = {
                        'status': 'skipped',
                        'reason': f"upstream_failed:{','.join(bad)}"}
                    continue
                current = name
                results[name] = fn()
                current = None
            results['status'] = 'completed'
        except Exception as e:
            log(f"Pipeline failed: {str(e)}", "ERROR")
            traceback.print_exc()
            results['status'] = 'failed'
            results['error'] = str(e)
            if current:
                # Langkah yang melempar tidak pernah tercatat di
                # results, jadi agregasi di bawah tidak melihatnya dan
                # last_full_pipeline.json menunjukkan failed_steps
                # kosong untuk run yang jelas gagal (audit ronde 8).
                results['error_step'] = current

        # Kejujuran status (audit K4): langkah yang melaporkan 'failed'
        # tidak boleh tertutup status 'completed'. Pemanggil (cron refit
        # mingguan) membaca field ini dan exit code proses.
        # 'partial' (mis. fallback legacy step_score_upcoming) juga
        # kegagalan untuk agregasi — rantai harian menolak status
        # selain 'success' dengan cara yang sama (audit ronde 3).
        failed_steps = [k for k, v in results.items()
                        if isinstance(v, dict)
                        and (v.get('status') == 'failed'
                             or (v.get('status') == 'partial'
                                 and k not in SOFT_PARTIAL_STEPS))]
        # 'skipped' karena modul hilang (ImportError) adalah kegagalan
        # nyata, bukan skip sukarela — ikut gagalkan run. Skip karena
        # upstream gagal tidak dobel-hitung: hulunya sudah tercatat.
        failed_steps += [k for k, v in results.items()
                         if isinstance(v, dict)
                         and v.get('status') == 'skip'
                         and v.get('reason') == 'module_not_found']
        # Langkah yang melempar exception (error_step) juga gagal,
        # walau dict hasilnya tidak pernah terbentuk.
        if (results.get('error_step')
                and results['error_step'] not in failed_steps):
            failed_steps.append(results['error_step'])
        # Partial lunak: tercatat dan terlihat, tidak menggagalkan.
        partial_steps = [k for k, v in results.items()
                         if isinstance(v, dict)
                         and v.get('status') == 'partial'
                         and k in SOFT_PARTIAL_STEPS]
        if partial_steps:
            results['partial_steps'] = partial_steps
            log(f"Pipeline finished with PARTIAL steps: "
                f"{partial_steps}", "WARN")
        if failed_steps:
            results['failed_steps'] = failed_steps
            if results.get('status') == 'completed':
                results['status'] = 'failed'
            log(f"Pipeline finished with FAILED steps: {failed_steps}",
                "ERROR")

        # Jejak run lengkap terakhir untuk /api/status: is_stale model
        # tidak bisa membedakan refit mingguan yang gagal dari fit
        # harian yang sehat (fit harian menulis ulang updated_at), jadi
        # keberhasilan --run-all dicatat eksplisit di file ini
        # (audit ronde 7).
        try:
            rec = {"finished_at": datetime.now(timezone.utc).isoformat(),
                   "status": results.get('status'),
                   "failed_steps": results.get('failed_steps', [])}
            if results.get('partial_steps'):
                rec["partial_steps"] = results['partial_steps']
            if results.get('error'):
                rec["error"] = results['error']
                rec["error_step"] = results.get('error_step')
            tmp = os.path.join(BASE_DIR, "last_full_pipeline.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(rec, f)
            os.replace(tmp, os.path.join(BASE_DIR, "last_full_pipeline.json"))
        except Exception:
            pass

        runtime = time.time() - self.start_time
        log(f"\nPipeline completed in {runtime:.1f}s", "INFO")
        log(f"Stats: {dict(self.stats)}", "INFO")
        return results

    # ---- refresh data latih (football-data.co.uk + xG Understat) ----
    @staticmethod
    def _cur_season_label(on=None) -> str:
        """Label musim berjalan ("2026/27"): musim mulai Juli.

        Versi lama memakai tahun kalender mentah, jadi mulai 1 Januari
        labelnya melompat ke musim berikutnya (vakum: 0 baris) dan cek
        susut musim-berjalan berhenti bekerja di tengah musim
        (audit ronde 7).
        """
        d = on or datetime.now().date()
        y = d.year if d.month >= 7 else d.year - 1
        return f"{y}/{str(y + 1)[-2:]}"

    @staticmethod
    def _clean_stats(path):
        """{total, max_date, cur_season, div_counts} dari all_matches_clean.csv."""
        total = max_date = cur = 0
        div_counts = {}
        if not os.path.exists(path):
            return {"total": 0, "max_date": None, "cur_season": 0,
                    "div_counts": {}}
        seas = PipelineOrchestrator._cur_season_label()
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                total += 1
                d = (r.get("Date") or "")[:10]
                if d and d > (max_date or ""):
                    max_date = d
                if r.get("Season") == seas:
                    cur += 1
                dv = r.get("Div") or "?"
                div_counts[dv] = div_counts.get(dv, 0) + 1
        return {"total": total, "max_date": max_date, "cur_season": cur,
                "div_counts": div_counts}

    def _xg_year(self) -> str:
        return f"20{REFRESH_SEASON[:2]}"

    def _xg_dump_counts(self) -> dict:
        out = {}
        yr = self._xg_year()
        for slug in XG_SLUGS:
            p = os.path.join(paths.XGRAW, f"{slug}_{yr}.json")
            if not os.path.exists(p):
                out[slug] = -1
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    out[slug] = len(json.load(f))
            except Exception:
                out[slug] = -1
        return out

    def _refresh_understat_seasons(self, ts) -> bool:
        """Segarkan dump musim Understat ({League}_{yr}.json) via getLeagueData
        (pola sama dgn refresh_fixtures.fetch). Return False bila ada yang gagal."""
        from refresh_fixtures import fetch
        ok = True
        yr = self._xg_year()
        for slug in XG_SLUGS:
            p = os.path.join(paths.XGRAW, f"{slug}_{yr}.json")
            try:
                fresh = fetch(slug)
            except Exception as e:
                log(f"  ! understat {slug} fetch gagal: {e!r}", "WARN")
                ok = False
                continue
            if not fresh:
                log(f"  ! understat {slug} kosong", "WARN")
                ok = False
                continue
            if os.path.exists(p):
                shutil.copy2(p, f"{p}.bak-{ts}")
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(fresh, f, ensure_ascii=False)
            os.replace(tmp, p)
            log(f"  OK understat {slug}: {len(fresh)} matches -> "
                f"{os.path.basename(p)}", "INFO")
        return ok

    def _records_fingerprint(self) -> str:
        st = self._clean_stats(paths.DATA_CLEAN)
        try:
            size = os.path.getsize(paths.DATA_CLEAN)
        except OSError:
            size = -1
        # Ukuran file ikut: perubahan isi yang tidak mengubah jumlah
        # baris / tanggal maks / hitungan musim (mis. skor terkoreksi)
        # sebelumnya tidak terlihat fingerprint sama sekali
        # (audit ronde 7).
        return f"{st['total']}|{st['max_date']}|{st['cur_season']}|{size}"

    def _rebuild_records_if_changed(self) -> bool:
        """Rebuild records_cache bila data latih berubah (stamp data)."""
        meta_path = os.path.splitext(RECORDS)[0] + ".meta.json"
        fp = self._records_fingerprint()
        stored = None
        if os.path.exists(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    stored = json.load(f).get("data_fingerprint")
            except Exception:
                stored = None
        if stored == fp:
            log("  records_cache segar (data tak berubah)", "INFO")
            return False
        log("  data latih berubah -> rebuild records_cache ...", "INFO")
        from backtest_picks import cache_records
        from model_v2 import DC_FIT_MODE
        cache_records(RECORDS)
        # Skema meta SATU: cache_records menulis {dc_fit_mode, data_stamp}
        # (dibaca make_picks_live._records_stale); fingerprint langkah ini
        # DITAMBAHKAN ke dict yang sama, bukan menimpanya. Menimpa seperti
        # sebelumnya menghapus data_stamp, sehingga [5/7] harian selalu
        # menganggap records basi dan membangunnya ulang sekali lagi
        # setiap minggu aktif (audit ronde 6, M2).
        meta = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}
        meta["dc_fit_mode"] = DC_FIT_MODE
        meta["data_fingerprint"] = fp
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f)
        log("  records_cache direbuild (stamp data baru)", "INFO")
        return True

    def _rotate_clean_backups(self, clean_path):
        """Simpan 3 backup file bersih terbaru. Tanpa ini setiap refit
        menambah ~33 MB .bak tanpa batas (~1,7 GB/tahun)."""
        try:
            _baks = sorted(glob.glob(clean_path + ".bak-*"))
            for _old in _baks[:-3]:
                os.remove(_old)
        except Exception:
            pass

    def _discard_run_backups(self, transient_baks, ts):
        """Buang backup transien milik run ini (raw, all_matches.csv,
        dump xG): asuransi rollback-nya sudah terpakai — entah
        ter-restore (jalur gagal) atau tak lagi dibutuhkan (sukses).
        Backup file bersih generasional tidak ikut dibuang; ia diatur
        _rotate_clean_backups."""
        for bak in transient_baks:
            try:
                os.remove(bak)
            except OSError:
                pass
        yr = self._xg_year()
        for slug in XG_SLUGS:
            bak = os.path.join(paths.XGRAW, f"{slug}_{yr}.json") + f".bak-{ts}"
            try:
                os.remove(bak)
            except OSError:
                pass
        # Sapu sisa .bak dump xG dari run LAMA: discard di atas hanya
        # tahu nama milik run ini, jadi backup peninggalan kode lama
        # (yang membuat .bak tapi tidak pernah membuangnya) tertinggal
        # selamanya. Discard berjalan setelah restore run ini selesai,
        # jadi .bak yang tersisa hanya milik run yang sudah tuntas —
        # tidak ada konsumennya (audit ronde 8).
        for stale in glob.glob(os.path.join(paths.XGRAW, "*.json.bak-*")):
            try:
                os.remove(stale)
            except OSError:
                pass

    def step_refresh_training_data(self) -> dict:
        """Segarkan data latih sebelum fit (musim berjalan saja).

        Uri: unduh CSV football-data.co.uk musim 2627 (21 divisi) ->
        agregasi (prepare) -> bersihkan (clean) -> segarkan dump xG Understat.
        Backup bertimestamp sebelum menimpa; validasi baris tidak menurun; bila
        gagal -> rollback ke file lama dan laporkan. Tanpa API-Football.
        """
        log("\n[Step refresh] Refresh data latih (football-data + xG)...")
        clean_path = paths.DATA_CLEAN
        # Resolusi mikrodetik: stempel 1 detik membuat dua refresh
        # dalam detik yang sama berbagi nama backup, menggabungkan dua
        # generasi backup jadi satu nama (audit ronde 8).
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        # Backup SEMUA file yang akan ditimpa langkah ini, bukan hanya
        # file bersih: rollback lama hanya memulihkan
        # all_matches_clean.csv, sementara unduhan raw, all_matches.csv
        # (output prepare) dan dump xG tertinggal dalam keadaan
        # baru/campuran sambil log mengklaim "dirollback"
        # (audit ronde 7, MEDIUM). Backup file bersih bersifat
        # generasional (dirotasi, simpan 3); sisanya transien — dipakai
        # untuk rollback run ini lalu dibuang.
        baks = []
        transient_baks = []
        existed = {}  # path -> ada sebelum run ini (untuk rollback)

        def _note(path):
            if path not in existed:
                existed[path] = os.path.exists(path)

        def _backup(path, transient=False):
            _note(path)
            if existed[path]:
                bak = f"{path}.bak-{ts}"
                shutil.copy2(path, bak)
                baks.append(bak)
                if transient:
                    transient_baks.append(bak)

        # Catat keberadaan SEMUA file yang bisa disentuh run ini
        # SEBELUM try: loop hapus rollback memakai `existed` untuk
        # mengenali file buatan run, jadi catatannya harus lengkap
        # sejak awal. Dulu catatan diisi bertahap di dalam try —
        # sesudah _clean_stats dan backup yang berurutan — sehingga
        # kegagalan sebelum/selama fase backup membuat file raw yang
        # sudah ada tampak seperti buatan run dan ikut terhapus oleh
        # rollback, dalam run yang tidak menimpa apa pun (audit
        # ronde 9, MEDIUM). _note hanya memanggil os.path.exists,
        # yang tidak bisa raise.
        _note(clean_path)
        _note(paths.DATA_RAW)
        for rp in sorted(glob.glob(os.path.join(
                paths.RAW_DIR, f"*_{REFRESH_SEASON}.csv"))):
            _note(rp)
        _yr0 = self._xg_year()
        for slug in XG_SLUGS:
            _note(os.path.join(paths.XGRAW, f"{slug}_{_yr0}.json"))

        issues = []
        shrink_issues = []
        dl = p = c = None
        before = {"total": 0, "max_date": 0, "cur_season": 0,
                  "div_counts": {}}
        after = dict(before)
        # Koreksi sah football-data (fixture duplikat dihapus, hasil
        # dianulir) menyusutkan satu divisi dan akan menggagalkan
        # SETIAP refresh berikutnya — rollback memulihkan file lama
        # dan susut yang sama terdeteksi lagi minggu depan. Penerimaan
        # manual satu kali: REFRESH_ACCEPT_SHRINK=1 memperlakukan isu
        # susut sebagai peringatan untuk run itu saja (audit ronde 8).
        accept_shrink = os.environ.get("REFRESH_ACCEPT_SHRINK") == "1"
        try:
            # Statistik awal + semua backup DI DALAM try: dulu di luar,
            # jadi error filesystem saat backup lolos dari langkah ini
            # dan membatalkan seluruh run_full_pipeline — termasuk
            # langkah TA yang independen — tanpa rollback (ronde 8).
            before = self._clean_stats(clean_path)
            after = dict(before)
            _backup(clean_path)
            _backup(paths.DATA_RAW, transient=True)
            for rp in sorted(glob.glob(os.path.join(
                    paths.RAW_DIR, f"*_{REFRESH_SEASON}.csv"))):
                _backup(rp, transient=True)

            from download import download
            dl = download(seasons=[REFRESH_SEASON], force=True)
            log(f"  football-data {REFRESH_SEASON}: "
                f"{dl['ok']}/{dl['total']} file", "INFO")
            if dl["ok"] < dl["total"]:
                # download() tidak pernah raise per-file: file yang gagal
                # tetap versi lama di disk, jadi tanpa cek ini refit bisa
                # "sukses" di atas data basi seminggu — validasi susut di
                # bawah tidak menangkapnya karena jumlah baris data basi
                # sama (audit ronde 6, M1).
                issues.append(f"unduhan football-data tidak lengkap: "
                              f"{dl['ok']}/{dl['total']} file")

            # Unduhan tidak lengkap = berhenti di sini: menjalankan
            # prepare/clean di atas raw campuran hanya membuang kerja
            # dan menimpa artefak sebelum rollback (audit ronde 7).
            if not issues:
                from prepare import prepare
                from clean import clean
                p = prepare()
                c = clean()
                after = self._clean_stats(clean_path)

                if after["total"] < before["total"]:
                    shrink_issues.append(
                        f"total baris menurun {before['total']}->{after['total']}")
                if after["cur_season"] < before["cur_season"]:
                    shrink_issues.append(
                        f"baris musim berjalan menurun "
                        f"{before['cur_season']}->{after['cur_season']}")
                # Cek susut PER DIVISI: cek agregat di atas menutupi
                # satu divisi yang menyusut/basi bila divisi lain
                # tumbuh (audit ronde 7).
                for dv, n0 in sorted(before["div_counts"].items()):
                    n1 = after["div_counts"].get(dv, 0)
                    if n1 < n0:
                        shrink_issues.append(
                            f"baris divisi {dv} menurun {n0}->{n1}")

            if not issues:
                xg_before = self._xg_dump_counts()
                ok_xg = self._refresh_understat_seasons(ts)
                xg_after = self._xg_dump_counts()
                if not ok_xg:
                    issues.append("refresh understat gagal (sebagian/total)")
                else:
                    for slug in XG_SLUGS:
                        if xg_after.get(slug, 0) < xg_before.get(slug, 0):
                            shrink_issues.append(
                                f"dump {slug} menurun "
                                f"{xg_before.get(slug)}->{xg_after.get(slug)}")
        except Exception as e:
            issues.append(f"exception: {e!r}")
            traceback.print_exc()

        if shrink_issues and accept_shrink:
            log(f"  ! susut data DITERIMA manual "
                f"(REFRESH_ACCEPT_SHRINK=1): {shrink_issues}", "WARN")
            shrink_issues = []
        issues += shrink_issues

        if issues:
            for bak in reversed(baks):
                orig = bak.rsplit(".bak-", 1)[0]
                try:
                    shutil.copy2(bak, orig)
                except Exception as e:
                    log(f"  ! rollback {orig} gagal: {e!r}", "ERROR")
            # Dump xG: _refresh_understat_seasons membuat
            # {dump}.bak-{ts} sebelum menimpa tiap slug — pulihkan
            # dari sana (dulu backup ini tidak pernah dipakai sama
            # sekali, jadi dump tertinggal campuran baru/lama).
            yr = self._xg_year()
            for slug in XG_SLUGS:
                dump = os.path.join(paths.XGRAW, f"{slug}_{yr}.json")
                bak = f"{dump}.bak-{ts}"
                if os.path.exists(bak):
                    try:
                        shutil.copy2(bak, dump)
                    except Exception as e:
                        log(f"  ! rollback {dump} gagal: {e!r}", "ERROR")
            # File yang TIDAK ada sebelum run tidak punya backup untuk
            # dipulihkan — hapus versi buatan run ini (file bersih /
            # all_matches.csv / dump xG baru), jangan tinggalkan sambil
            # log mengklaim rollback (audit ronde 8).
            for path, was in existed.items():
                if not was and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
            # File raw musim berjalan yang baru dibuat unduhan run ini
            # (tidak ada di glob awal) juga buatan run ini.
            for rp in glob.glob(os.path.join(
                    paths.RAW_DIR, f"*_{REFRESH_SEASON}.csv")):
                if rp not in existed and os.path.exists(rp):
                    try:
                        os.remove(rp)
                    except OSError:
                        pass
            self._discard_run_backups(transient_baks, ts)
            # Rotasi juga di jalur gagal: dulu hanya jalur sukses yang
            # merotasi, jadi refit yang gagal beruntun menumpuk backup
            # file bersih tanpa batas (audit ronde 7).
            self._rotate_clean_backups(clean_path)
            log(f"  X refresh data GAGAL & dirollback: {issues}", "ERROR")
            return {"status": "failed", "issues": issues,
                    "before": before, "after": after}

        self._discard_run_backups(transient_baks, ts)
        self._rotate_clean_backups(clean_path)
        # Kerja pasca-commit (reload loader + rebuild records) dulu
        # tanpa guard: exception di sana lolos dari langkah ini
        # SETELAH data baru ter-commit dan backup transien dibuang,
        # jadi run tercatat gagal lewat jalur error_step dengan data
        # yang sebenarnya sudah segar, dan langkah independen ikut
        # terbatalkan. Kini kegagalan pasca menjadi hasil langkah
        # yang jujur — failed dengan committed=True — sehingga hilir
        # tergerbang rapi dan langkah independen tetap jalan
        # (audit ronde 9).
        post_issues = []
        try:
            self.loader.reload_data()
        except Exception as e:
            post_issues.append(f"reload loader gagal: {e!r}")
            traceback.print_exc()
        rebuilt = False
        if not post_issues:
            log(f"  OK all_matches_clean.csv: {before['total']}->{after['total']} baris "
                f"(musim {REFRESH_SEASON}: {before['cur_season']}->{after['cur_season']})",
                "INFO")
            log(f"      max date: {before['max_date']} -> {after['max_date']}", "INFO")

            # _rebuild_records_if_changed no-op sendiri bila fingerprint
            # sama, jadi panggil selalu: gerbang lama (musim naik / tanggal
            # berubah) melewatkan perubahan isi yang kini ditangkap
            # fingerprint (audit ronde 7).
            try:
                rebuilt = self._rebuild_records_if_changed()
            except Exception as e:
                post_issues.append(f"rebuild records gagal: {e!r}")
                traceback.print_exc()
        if post_issues:
            log(f"  X refresh ter-commit tapi pasca-langkah gagal: "
                f"{post_issues}", "ERROR")
            return {"status": "failed", "issues": post_issues,
                    "before": before, "after": after, "committed": True}

        return {"status": "success", "download": dl, "prepare": p, "clean": c,
                "before": before, "after": after, "records_rebuilt": rebuilt}

    def step_check_data(self) -> dict:
        """Validasi semua data input tersedia."""
        log("\n[Step 1/6] Checking data availability...")

        # Check essential files directly
        data_files = {}
        required_files = ['all_matches_clean.csv', 'all_matches.csv']
        for f in required_files:
            path = os.path.join(BASE_DIR, f)
            data_files[f] = {
                'exists': os.path.exists(path),
                'size_mb': round(os.path.getsize(path) / (1024*1024), 2) if os.path.exists(path) else 0
            }

        missing_files = [name for name, info in data_files.items()
                        if not info.get('exists')]
        if missing_files:
            raise FileNotFoundError(f"Missing required data files: {missing_files}")

        cache_matches = self.loader.cache.matches
        total_matches = len(cache_matches)
        divisions = list(self.loader.cache.by_div.keys())

        log(f"  OK Data OK: {total_matches:,} matches loaded", "INFO")
        self.stats['matches_loaded'] = total_matches

        # Freshness guard (non-fatal): data/snapshot terlalu tua -> peringatan.
        warnings = []
        now_ts = time.time()
        age_days = lambda p: (now_ts - os.path.getmtime(p)) / 86400.0 if os.path.exists(p) else None
        match_age = age_days(os.path.join(BASE_DIR, "all_matches_clean.csv"))
        if match_age is not None and match_age > 7:
            warnings.append(f"all_matches_clean.csv berumur {match_age:.1f} hari (>7)")
        if match_age is None:
            warnings.append("all_matches_clean.csv tidak ditemukan")
        for w in warnings:
            log(f"  ! FRESHNESS: {w}", "WARN")

        return {
            'all_matches_clean': True,
            'total_matches': total_matches,
            'data_files': data_files,
            'divisions': divisions,
            'freshness_warnings': warnings
        }

    @staticmethod
    def _restore_xg_snap(xg_out, snap):
        """Pulihkan xg_matches.csv dari snapshot pra-build (bila ada)."""
        if not snap:
            return
        try:
            if os.path.exists(snap):
                shutil.copy2(snap, xg_out)
                os.remove(snap)
                log("  ! xg_matches.csv dipulihkan dari snapshot "
                    "(hasil build terdegradasi ditolak)", "WARN")
        except OSError:
            pass

    def step_build_xg(self) -> dict:
        """Bangun xg_raw/xg_matches.csv dari dump Understat terversi (lokal)."""
        log("\n[Step xg] Membangun xg_matches.csv dari dump Understat...")
        xg_out = os.path.join(paths.XGRAW, "xg_matches.csv")
        snap = None
        try:
            from data_enrichment.build_xg_matches import build as build_xg
            # build() menulis ulang xg_matches.csv SEBELUM langkah ini
            # sempat menilai hasilnya, jadi status partial/failed saja
            # tidak melindungi artefaknya: rantai harian tetap akan
            # mengonsumsi file terdegradasi itu. Snapshot dulu;
            # pulihkan bila hasil build terdegradasi (audit ronde 8).
            if os.path.exists(xg_out):
                snap = xg_out + ".bak-snap"
                shutil.copy2(xg_out, snap)
            r = build_xg()
            # build() melewati dump yang hilang/rusak dengan senyap
            # (daftar 'missing' di return dict-nya tidak pernah dibaca
            # siapa pun) — satu liga hilang total dari xg_matches dulu
            # tetap "success" dan blend jatuh ke goals-only diam-diam
            # (audit ronde 7). Dump musim berjalan yang rusak atau
            # divisi TOP5 yang kosong = partial (gagal untuk agregasi);
            # dump historis yang rusak hanya dicatat.
            missing = r.get("missing") or []
            zero_divs = [d for d, n in (r.get("per_league") or {}).items()
                         if not n]
            yr = self._xg_year()
            cur_missing = [nm for nm, _ in missing
                           if nm.endswith(f"_{yr}.json")]
            if zero_divs or cur_missing:
                log(f"  X build_xg_matches: divisi kosong {zero_divs}, "
                    f"dump musim berjalan rusak {cur_missing}", "ERROR")
                self._restore_xg_snap(xg_out, snap)
                return {"status": "failed" if not r.get("n_rows") else "partial",
                        **r, "zero_divs": zero_divs}
            if missing:
                log(f"  ! build_xg_matches: {len(missing)} dump historis "
                    f"dilewati: {[nm for nm, _ in missing]}", "WARN")
            log(f"  OK xG matches: {r['n_rows']} rows", "INFO")
            if snap:
                try:
                    os.remove(snap)
                except OSError:
                    pass
            return {"status": "success", **r}
        except Exception as e:
            log(f"  X build_xg_matches gagal: {str(e)}", "ERROR")
            traceback.print_exc()
            self._restore_xg_snap(xg_out, snap)
            return {"status": "failed", "error": str(e)}

    def step_fit_models(self) -> dict:
        """Fit atau update model untuk semua divisi TOP5."""
        log("\n[Step 2/6] Fitting/updating models...")
        results = {}
        today = datetime.now().date()
        xg_map = None  # dimuat sekali, hanya bila ada divisi yang fit

        for div in TOP5:
            try:
                state = ModelState(div)
                was_loaded = state.load()
                matches = self.loader.get_matches_by_div(div)
                matches_with_scores = [
                    m for m in matches if m.get('yh') is not None
                    and m.get('ya') is not None
                    and m.get('ftr') in ('H', 'D', 'A')
                ]

                if len(matches_with_scores) < 100:
                    log(f"  ! {div}: Insufficient data ({len(matches_with_scores)} matches)", "WARN")
                    continue

                dates = [m['date'] for m in matches_with_scores if m.get('date')]
                cutoff = max(dates) if dates else today

                needs_fit = True
                if was_loaded and state.last_fit_date:
                    days_since_fit = (cutoff - state.last_fit_date).days
                    needs_fit = days_since_fit > 7 or state.mode_mismatch() or state.needs_fit(
                        [(m['home'], m['away'], m['yh'], m['ya'], m['date'])
                         for m in matches_with_scores[-100:]], cutoff
                    )

                if needs_fit:
                    log(f"  Fitting {div} (cutoff: {cutoff})...", "INFO")
                    from model_v2 import DC, xg_key
                    if xg_map is None:
                        # Dulu _load_xg_map() dipanggil di dalam loop
                        # per divisi (parse CSV 18k baris sampai 5x);
                        # pola yang sama yang di-hoist dari
                        # predict_upcoming di ronde 6 (audit ronde 7).
                        from features import _load_xg_map
                        xg_map = _load_xg_map()
                    model = DC()
                    history = [(m['home'], m['away'], m['yh'], m['ya'],
                                xg_map.get(xg_key(div, m['date'], m['home'], m['away']), (None, None))[0],
                                xg_map.get(xg_key(div, m['date'], m['home'], m['away']), (None, None))[1],
                                m['date'])
                              for m in matches_with_scores]
                    model.fit(history[-self.max_train:], cutoff, self.half_life)
                    state.update_from_model(model, cutoff, self.half_life)
                    save_model_state(state)
                    self.stats['models_fit'] += 1
                    log(f"  OK {div}: Model fitted (teams: {len(state.get_known_teams())}, "
                        f"rho: {model.rho})", "INFO")
                else:
                    log(f"  OK {div}: Model up-to-date (fit: {state.last_fit_date})", "INFO")

                results[div] = {
                    'status': 'fit' if needs_fit else 'cached',
                    'last_fit': state.last_fit_date.isoformat() if state.last_fit_date else None,
                    'n_teams': len(state.get_known_teams()),
                    'n_matches_trained': state.n_matches_trained,
                    'rho': state.rho
                }
            except Exception as e:
                log(f"  X {div}: Failed to fit - {str(e)}", "ERROR")
                results[div] = {'status': 'failed', 'error': str(e)}

        # Rollup top-level: agregasi run_full_pipeline (audit K4) hanya
        # membaca status di level atas dict langkah; tanpa ini kegagalan
        # fit satu divisi tidak terlihat dan run tetap 'completed'
        # (lubang yang ditemukan audit ulang 2026-10-29).
        # Sebagian divisi gagal = 'partial', bukan 'failed': state
        # divisi yang gagal tidak pernah ditimpa (save hanya terjadi
        # setelah fit sukses), jadi versi lamanya tetap sah untuk
        # scoring, dan gerbang memperlakukan partial model sebagai
        # lunak (audit ronde 8). Semua divisi gagal tetap 'failed'.
        _div_statuses = [v.get('status') for v in results.values()
                         if isinstance(v, dict)]
        _n_failed = _div_statuses.count('failed')
        if not _div_statuses:
            # Tak ada divisi yang masuk hitungan (semua <100 laga
            # ber-skor, jadi di-skip sebelum tercatat): langkah ini
            # tidak memfit dan tidak membaca cache apa pun — label
            # 'success' di sini tidak jujur (audit ronde 9).
            results['status'] = 'failed'
        elif _n_failed and _n_failed == len(_div_statuses):
            results['status'] = 'failed'
        elif _n_failed:
            results['status'] = 'partial'
        else:
            results['status'] = 'success'
        return results

    def step_score_upcoming(self) -> dict:
        """Generate predictions for upcoming fixtures."""
        log("\n[Step 3/6] Scoring upcoming fixtures...")

        try:
            from predict_upcoming_refactored import generate_predictions
            results = generate_predictions()
            inner = results.get('status')
            if inner is not None and inner != 'success':
                log(f"  X generate_predictions status {inner!r}", "ERROR")
                return {'status': 'failed',
                        'error': f'generate_predictions status {inner!r}',
                        'results': results}
            n_preds = results.get('n_output_rows',
                                  len(results.get('predictions', [])))
            log(f"  OK Generated {n_preds} predictions", "INFO")
            self.stats['predictions_generated'] = n_preds
            return {'status': 'success', 'n_predictions': n_preds, 'results': results}
        except ImportError:
            log("  ! predict_upcoming not refactored, using legacy method", "WARN")
            fixtures = self.loader.load_fixtures("2026")
            log(f"  Found {len(fixtures)} upcoming fixtures", "INFO")
            return {
                'status': 'partial',
                'n_fixtures': len(fixtures),
                'message': 'Using legacy predict_upcoming'
            }

    def step_score_corners(self) -> dict:
        """Generate corner match predictions."""
        log("\n[Step 3/6] Scoring corner predictions...")

        try:
            import subprocess
            started = time.time()
            result = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "model_corners_v3.py"), "--predict"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                log(f"  X Corner model rc={result.returncode}", "ERROR")
                return {'status': 'failed', 'error': f'rc={result.returncode}',
                        'stderr': (result.stderr or '')[-300:]}

            corner_file = os.path.join(BASE_DIR, "predictions_corners_upcoming.csv")
            if os.path.exists(corner_file):
                if os.path.getmtime(corner_file) < started - 5:
                    log("  X Corner predictions file is stale "
                        "(not rewritten by this run)", "ERROR")
                    return {'status': 'failed', 'error': 'stale_output'}
                import csv
                with open(corner_file, 'r') as f:
                    rows = list(csv.DictReader(f))
                if not rows:
                    # File segar tapi KOSONG padahal prediksi liga ada =
                    # kegagalan diam (lolos sebagai sukses di versi lama).
                    pred_file = os.path.join(
                        BASE_DIR, "predictions_upcoming.csv")
                    n_pred = 0
                    if os.path.exists(pred_file):
                        with open(pred_file, 'r') as f:
                            n_pred = len(list(csv.DictReader(f)))
                    if n_pred > 0:
                        log("  X Corner predictions empty while league "
                            "predictions exist", "ERROR")
                        return {'status': 'failed', 'error': 'empty_output'}
                log(f"  OK Corner predictions: {len(rows)} rows", "INFO")
                self.stats['corner_predictions'] = len(rows)
                return {
                    'status': 'success',
                    'n_predictions': len(rows),
                    'file': corner_file
                }
            else:
                # File tidak dibuat sama sekali (mis. corner_params.json
                # hilang sehingga script keluar rc=0 tanpa menulis).
                # Bila prediksi liga ada, ini kegagalan diam yang bisa
                # menghijaukan --run-all tanpa prediksi corner sama
                # sekali — gagalkan, jangan skip.
                pred_file = os.path.join(
                    BASE_DIR, "predictions_upcoming.csv")
                n_pred = 0
                if os.path.exists(pred_file):
                    import csv
                    with open(pred_file, 'r') as f:
                        n_pred = len(list(csv.DictReader(f)))
                if n_pred > 0:
                    log("  X No corner predictions file while league "
                        "predictions exist", "ERROR")
                    return {'status': 'failed', 'error': 'no_output'}
                log("  ! No corner predictions file created", "WARN")
                return {'status': 'skip', 'reason': 'no_output'}
        except ImportError:
            log("  ! model_corners_v3 not available", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except subprocess.TimeoutExpired:
            log("  X Corner model timeout (>120s)", "ERROR")
            return {'status': 'failed', 'error': 'timeout'}
        except Exception as e:
            log(f"  X Corner scoring failed: {str(e)}", "ERROR")
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}

    def step_integrate_odds(self) -> dict:
        """Integrate live odds from multiple sources."""
        log("\n[Step 4/6] Integrating odds...")
        results = {'sources': {}, 'games_updated': 0, 'errors': {}}

        pred_file = os.path.join(BASE_DIR, "predictions_upcoming.csv")
        if not os.path.exists(pred_file):
            log("  ! No predictions file found", "WARN")
            return {'status': 'skip', 'reason': 'no_predictions',
                    'sources': {}, 'games_updated': 0, 'errors': {}}

        fd_odds_updated = 0
        for div in TOP5:
            try:
                odds_map = load_fd_odds(div, "2627")
                if odds_map:
                    results['sources'][f'fd_{div}'] = len(odds_map)
                    fd_odds_updated += len(odds_map)
                    log(f"  OK {div}: Loaded {len(odds_map)} FD odds entries", "INFO")
            except Exception as e:
                # Dulu kegagalan per divisi hanya log ERROR dan dict
                # hasil tidak punya kunci 'status' sama sekali, jadi
                # agregasi run tidak pernah melihatnya (audit ronde 7).
                # Map kosong BUKAN error (gap file fixtures FD yang
                # sudah dikenal) — hanya exception yang dihitung.
                results['errors'][div] = str(e)
                log(f"  X {div}: FD odds load failed - {str(e)}", "ERROR")

        results['games_updated'] = fd_odds_updated
        self.stats['odds_loaded'] = fd_odds_updated
        if len(results['errors']) == len(TOP5):
            results['status'] = 'failed'
        elif results['errors']:
            results['status'] = 'partial'
        else:
            results['status'] = 'success'
        log(f"  OK Odds integrated from {len(results['sources'])} sources", "INFO")
        return results

    def step_generate_picks(self) -> dict:
        """Generate betting picks from predictions and odds.

        Uses existing make_picks.py script for pick generation.
        Appends new picks to ledger/picks.jsonl.
        """
        log("\n[Step 5/6] Generating picks...")

        try:
            import make_picks
            make_picks.main()

            # Generate unified best_picks.csv (corner probs + DC + ta_model)
            import best_picks
            best_picks.main()

            # Rutekan pick piala (best_picks ber-label kompetisi) ke ledger
            # dgn competition=EFL Cup/DFB Pokal — biar grading per-kompetisi.
            try:
                import market_orchestration
                n_cup = market_orchestration.sync_cup_picks_to_ledger()
                if n_cup:
                    log(f"  OK cup picks -> ledger: {n_cup} baru", "INFO")
            except Exception as e:
                log(f"  ! cup-ledger sync failed: {e!r}", "WARN")
            bp_file = os.path.join(BASE_DIR, "best_picks.csv")
            import csv as _csv
            n_bp = 0
            if os.path.exists(bp_file):
                with open(bp_file, 'r') as f:
                    n_bp = sum(1 for _ in _csv.DictReader(f))
            # Count market distribution
            market_counts = {}
            with open(bp_file, 'r') as f:
                for row in _csv.DictReader(f):
                    m = row.get('market', '')
                    market_counts[m] = market_counts.get(m, 0) + 1
            log(f"  OK best_picks.csv: {n_bp} top picks ({market_counts})", "INFO")
            self.stats['best_picks'] = n_bp

            # Count picks from ledger
            picks_file = os.path.join(BASE_DIR, "ledger", "picks.jsonl")
            if os.path.exists(picks_file):
                with open(picks_file, 'r') as f:
                    picks = [json.loads(line) for line in f if line.strip()]
                pending = sum(1 for p in picks if p.get('status') == 'pending')
                log(f"  OK Ledger: {len(picks)} total picks ({pending} pending)", "INFO")
                self.stats['picks_generated'] = pending
                return {
                    'status': 'success',
                    'n_total_picks': len(picks),
                    'n_pending': pending
                }
            else:
                log("  ! No picks file found", "WARN")
                return {'status': 'no_picks', 'n_picks': 0}
        except ImportError as e:
            log(f"  ! make_picks not available: {e}", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except Exception as e:
            log(f"  X Pick generation failed: {str(e)}", "ERROR")
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}

    def step_validation(self) -> dict:
        """Validate pipeline outputs."""
        log("\n[Step 6/6] Running validation...")
        results = {'validations': {}, 'issues': []}

        pred_file = os.path.join(BASE_DIR, "predictions_upcoming.csv")
        if os.path.exists(pred_file):
            try:
                import csv
                with open(pred_file, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                n_valid = sum(1 for r in rows if r.get('ph_dc') and r.get('pd_dc') and r.get('pa_dc'))
                n_blended = sum(1 for r in rows if r.get('ph_bl'))
                results['validations']['predictions'] = {
                    'total': len(rows),
                    'with_dc_probs': n_valid,
                    'with_blended_probs': n_blended,
                    'missing_probs': len(rows) - n_valid
                }
                log(f"  OK Predictions: {len(rows)} total, {n_valid} valid DC probs", "INFO")
                if n_valid < len(rows):
                    results['issues'].append(f"{len(rows) - n_valid} predictions missing DC probs")
            except Exception as e:
                log(f"  X Prediction validation failed: {str(e)}", "ERROR")
                results['issues'].append(f"Prediction validation error: {str(e)}")

        # Validate best_picks.csv
        bp_file = os.path.join(BASE_DIR, "best_picks.csv")
        if os.path.exists(bp_file):
            try:
                with open(bp_file, 'r') as f:
                    bp_rows = list(csv.DictReader(f))
                corner = sum(1 for r in bp_rows if r.get('market') == 'Corners')
                dc = sum(1 for r in bp_rows if r.get('market') in ('1X2', 'DC'))
                ta = sum(1 for r in bp_rows if r.get('source') == 'ta_model')
                results['validations']['best_picks'] = {
                    'total': len(bp_rows),
                    'corner': corner,
                    'dixon_coles': dc,
                    'ta_model': ta
                }
                log(f"  OK best_picks.csv: {len(bp_rows)} total ({corner} corner, {dc} DC, {ta} ta_model)", "INFO")
            except Exception as e:
                log(f"  X best_picks validation failed: {str(e)}", "ERROR")
                results['issues'].append(f"best_picks validation error: {str(e)}")

        picks_file = os.path.join(BASE_DIR, "ledger", "picks.jsonl")
        if os.path.exists(picks_file):
            try:
                with open(picks_file, 'r') as f:
                    picks = [json.loads(line) for line in f if line.strip()]
                pending = sum(1 for p in picks if p.get('status') == 'pending')
                graded = sum(1 for p in picks if p.get('status') in ('win', 'loss', 'push'))
                results['validations']['ledger'] = {'total': len(picks), 'pending': pending, 'graded': graded}
                log(f"  OK Ledger: {len(picks)} total picks ({pending} pending, {graded} graded)", "INFO")
            except Exception as e:
                log(f"  X Ledger validation failed: {str(e)}", "ERROR")
                results['issues'].append(f"Ledger validation error: {str(e)}")

        model_info = {div: ModelState(div) for div in TOP5}
        loaded_models = [div for div in TOP5 if state_load(model_info[div])]
        results['validations']['model_cache'] = {
            'cached': len(loaded_models),
            'total': len(TOP5),
            'teams_total': sum(len(model_info[div].get_known_teams()) for div in loaded_models)
        }
        log(f"  OK Model cache: {len(loaded_models)}/{len(TOP5)} models cached", "INFO")
        results['status'] = 'passed' if not results['issues'] else 'warnings'
        return results

    def step_ta_model(self) -> dict:
        """Build TA model markets & bets (uses scraped tipsterarea odds)."""
        log("\n[Step 12/6] Building TA model markets...")
        try:
            import ta_model
            rc = ta_model.build()
            if rc == 0:
                # Nilai bet OPEN yang laganya sudah selesai. grade()
                # ada sejak lama tapi tidak dipanggil rantai mana pun,
                # jadi bet menumpuk tak dinilai (audit ronde 7).
                # Idempoten; kegagalannya warning saja (pembukuan,
                # bukan pembangunan pasar).
                try:
                    ta_model.grade()
                except Exception as e:
                    log(f"  ! TA bet grading gagal: {e!r}", "WARN")
                log("  OK TA model markets built", "INFO")
                return {'status': 'success'}
            log(f"  ! TA model build rc={rc}", "WARN")
            return {'status': 'failed', 'rc': rc}
        except ImportError:
            log("  ! ta_model not available", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except Exception as e:
            log(f"  X TA model build failed: {e}", "ERROR")
            return {'status': 'failed', 'error': str(e)}

    def step_predict_cups(self) -> dict:
        """Predict EFL Cup / DFB Pokal fixtures (predict_cups.main in-process).

        Membaca ta/fixtures.csv + ta/odds_1x2_snapshots.csv (mengambil hasil
        scrape pasar piala) dan menulis predictions_cups_upcoming.csv /
        predictions_corners_cups.csv. Tanpa fixture piala di window -> file
        header-only (bukan gagal), jadi best_picks tidak pernah membaca baris
        sisa dari babak piala lalu.
        """
        log("\n[Step cups] Predicting cup fixtures...")
        try:
            import predict_cups
            rc = predict_cups.main()
            if not isinstance(rc, dict):
                return {'status': 'success', 'n_gol': 0, 'n_corner': 0}
            n_gol = rc.get('n_gol', 0)
            n_corner = rc.get('n_corner', 0)
            if rc.get('status') == 'failed':
                # predict_cups melaporkan gagal (fixture piala ada
                # tapi nol yang terpetakan ke model liga) — status itu
                # dulu dibuang di sini dan langkah selalu 'success',
                # jadi gerbang cups->picks di jalur --run-all tak
                # pernah bisa trip untuk mode kegagalan ini; rantai
                # harian sudah memeriksanya dengan benar (ronde 8).
                log(f"  X Cup predictions GAGAL: fixture ada, "
                    f"0 terpetakan (n_fixtures={rc.get('n_fixtures')})",
                    "ERROR")
                return {'status': 'failed', 'n_gol': n_gol,
                        'n_corner': n_corner,
                        'n_fixtures': rc.get('n_fixtures', 0)}
            log(f"  OK Cup predictions: {n_gol} gol, {n_corner} corner", "INFO")
            return {'status': 'success', 'n_gol': n_gol, 'n_corner': n_corner}
        except ImportError:
            log("  ! predict_cups not available", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except Exception as e:
            log(f"  X Cup prediction failed: {str(e)}", "ERROR")
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}

    def run_incremental(self, hours_back: int = 24) -> dict:
        """Jalankan update inkremental."""
        log(f"\n{'=' * 60}", "INFO")
        log(f"Incremental run (last {hours_back}h)", "INFO")
        log(f"{'=' * 60}", "INFO")
        self.start_time = time.time()
        results = {}

        try:
            results['odds_scrape'] = self.scrape_live_odds()
            results['scoring'] = self.step_score_upcoming()
            results['ta_model'] = self.step_ta_model()
            results['picks'] = self.step_generate_picks()
            results['grading'] = self.grade_completed_picks()
            results['status'] = 'completed'
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)

        # Agregasi kejujuran yang sama seperti run_full_pipeline,
        # termasuk aturan partial lunaknya (SOFT_PARTIAL_STEPS):
        # kedua agregasi tadinya bisa berbeda diam-diam untuk status
        # yang sama (audit ronde 9). Set langkah jalur incremental
        # saat ini tidak memuat langkah lunak mana pun, jadi
        # penyelarasan ini tidak mengubah perilaku hari ini — hanya
        # mencegah divergensi bila langkah lunak ditambahkan ke sini.
        failed_steps = [k for k, v in results.items()
                        if isinstance(v, dict)
                        and (v.get('status') == 'failed'
                             or (v.get('status') == 'partial'
                                 and k not in SOFT_PARTIAL_STEPS))]
        partial_steps = [k for k, v in results.items()
                         if isinstance(v, dict)
                         and v.get('status') == 'partial'
                         and k in SOFT_PARTIAL_STEPS]
        if partial_steps:
            results['partial_steps'] = partial_steps
        if failed_steps:
            results['failed_steps'] = failed_steps
            if results.get('status') == 'completed':
                results['status'] = 'failed'
            log(f"Incremental run finished with FAILED steps: "
                f"{failed_steps}", "ERROR")

        runtime = time.time() - self.start_time
        log(f"\nIncremental run completed in {runtime:.1f}s", "INFO")
        return results

    def scrape_live_odds(self) -> dict:
        """Scrape live odds dari tipsterarea (freshness-aware).

        Date pages fetch sekali untuk semua tanggal. Market pages hanya
        untuk laga yang ada di predictions_upcoming.csv (match via div+date+home+away),
        dengan freshness check otomatis (1.5 jam) — hanya fetch yang perlu.
        """
        try:
            from ta_scrape import sync_dates, matched_ids
            today = date.today()
            days = [today + timedelta(days=k) for k in range(-1, 8)]

            # Phase 1: fetch date pages (snapshots + results)
            result = sync_dates(days, with_markets=False, verbose=False)

            # Phase 2: market pages — laga yang sudah dipasangkan model duluan
            # (fresness check di sync_dates membuat fetch ulang hanya bila >1.5 jam).
            # Run pertama (model_markets kosong) -> fetch semua laga di window.
            market_ids = matched_ids()
            # Sertakan fixture piala (EFL Cup / DFB Pokal) supaya odds pasar
            # (DC/O-U/BTTS/corner)- tersedia untuk laga piala.
            market_ids = list(market_ids) + _cup_fixture_ids(days)
            result_m = sync_dates(days, with_markets=True,
                                  market_ids=market_ids or None, verbose=False)
            result["markets_snapshots"] = result_m.get("snapshots", 0)

            log(f"  OK Scraped {result.get('games', 0)} games "
                f"({days[0]}..{days[-1]}), {result.get('snapshots', 0)} snapshots, "
                f"{result.get('results', 0)} results"
                + (f", markets utk {len(market_ids)} laga model" if market_ids else ""), "INFO")
            return {'status': 'success', 'scraped': result}
        except ImportError:
            log("  ! ta_scrape not available", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except Exception as e:
            log(f"  X Scrape failed: {str(e)}", "ERROR")
            return {'status': 'failed', 'error': str(e)}

    def grade_completed_picks(self) -> dict:
        """Grade picks from ledger/picks.jsonl via score_ledger.py.

        score_ledger.py membaca ledger/picks.jsonl (format ledger nyata) dan
        menulis grades.jsonl + ledger_summary.json — pengganti grade_picks.py
        yang membaca picks.csv/odds_timeseries.csv yang tidak pernah dibuat.
        """
        try:
            picks_file = os.path.join(BASE_DIR, "ledger", "picks.jsonl")
            if not os.path.exists(picks_file):
                log("  ! ledger/picks.jsonl belum ada — skip grading", "WARN")
                return {'status': 'skip', 'reason': 'no_picks'}
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "score_ledger.py")],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                msg = (result.stderr or result.stdout or "").strip()
                log(f"  X Grading failed: {msg}", "ERROR")
                return {'status': 'failed', 'error': msg or 'rc!=0'}
            grades_file = os.path.join(BASE_DIR, "ledger", "grades.jsonl")
            graded = 0
            if os.path.exists(grades_file):
                with open(grades_file, encoding="utf-8") as f:
                    graded = sum(1 for l in f if l.strip())
            log(f"  OK Graded picks: {graded} total", "INFO")
            return {'status': 'success', 'graded_count': graded}
        except ImportError:
            log("  ! score_ledger not available", "WARN")
            return {'status': 'skip', 'reason': 'module_not_found'}
        except Exception as e:
            log(f"  X Grading failed: {str(e)}", "ERROR")
            return {'status': 'failed', 'error': str(e)}

    def get_pipeline_status(self) -> dict:
        """Get current status of all pipeline components."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'data': {},
            'models': {},
            'predictions': {},
            'picks': {},
            'cache': {}
        }

        total_matches = len(self.loader.cache.matches)
        divisions = list(self.loader.cache.by_div.keys())
        dates = [m['date'] for m in self.loader.cache.matches if m.get('date')]

        status['data'] = {
            'total_matches': total_matches,
            'divisions': divisions,
            'date_range': {
                'start': min(dates).isoformat() if dates else None,
                'end': max(dates).isoformat() if dates else None
            } if dates else {},
            'cache_exists': True
        }

        for div in TOP5:
            state = ModelState(div)
            if state.load():
                status['models'][div] = {
                    'initialized': True,
                    'last_fit': state.last_fit_date.isoformat() if state.last_fit_date else None,
                    'n_teams': len(state.get_known_teams()),
                    'n_matches_trained': state.n_matches_trained,
                    'is_stale': state.is_stale(datetime.now().date())
                }
            else:
                status['models'][div] = {'initialized': False}

        pred_file = os.path.join(BASE_DIR, "predictions_upcoming.csv")
        status['predictions'] = {
            'exists': os.path.exists(pred_file),
            'size_kb': round(os.path.getsize(pred_file) / 1024, 2) if os.path.exists(pred_file) else 0
        }

        picks_file = os.path.join(BASE_DIR, "ledger", "picks.jsonl")
        picks_graded_file = os.path.join(BASE_DIR, "ledger", "graded.csv")
        status['picks'] = {
            'picks_file': os.path.exists(picks_file),
            'graded_file': os.path.exists(picks_graded_file),
            'picks_count': sum(1 for _ in open(picks_file)) if os.path.exists(picks_file) else 0,
            'graded_count': sum(1 for _ in open(picks_graded_file)) - 1 if os.path.exists(picks_graded_file) else 0
        }

        status['cache'] = self._get_cache_info()
        return status

    def _get_cache_info(self) -> dict:
        """Get cache directory info."""
        cache_dirs = ['.cache', '.cache/models', '.cache/predictions', '.cache/tmp']
        info = {}
        for d in cache_dirs:
            path = os.path.join(BASE_DIR, d)
            if os.path.exists(path):
                size = sum(os.path.getsize(os.path.join(dirpath, f))
                          for dirpath, _, filenames in os.walk(path) for f in filenames)
                info[d] = {'exists': True, 'size_mb': round(size / (1024*1024), 2)}
            else:
                info[d] = {'exists': False}
        return info


def state_load(state: ModelState) -> bool:
    """Helper to load state."""
    return state.load()


def main():
    """Main CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Football prediction pipeline orchestrator')
    parser.add_argument('--run-all', action='store_true', help='Run full pipeline')
    parser.add_argument('--predict-only', action='store_true', help='Run only scoring step')
    parser.add_argument('--update-data', action='store_true', help='Update data and cache')
    parser.add_argument('--incremental', action='store_true', help='Run incremental update')
    parser.add_argument('--status', action='store_true', help='Check pipeline status')
    parser.add_argument('--dry-run', action='store_true', help='Validate without executing')
    parser.add_argument('--verbose', '-v', action='store_true', default=True)
    args = parser.parse_args()

    orchestrator = PipelineOrchestrator(verbose=args.verbose)

    if args.status:
        status = orchestrator.get_pipeline_status()
        print(json.dumps(status, indent=2, default=str))
        return

    if args.dry_run:
        log("Dry run mode - validating configuration", "INFO")
        status = orchestrator.get_pipeline_status()
        print(json.dumps({
            'data_available': status['data']['total_matches'] > 0,
            'models_cached': len([m for m in status['models'].values()
                                 if m.get('initialized', False)]) > 0,
            'cache_ok': status['cache'].get('.cache', {}).get('exists', False)
        }, indent=2))
        return

    if args.predict_only:
        results = orchestrator.step_score_upcoming()
        print(json.dumps(results, indent=2, default=str))
        if results.get('status') in ('failed', 'partial'):
            sys.exit(1)
        return

    if args.update_data:
        check = orchestrator.step_check_data()
        results = dict(check)
        fit = orchestrator.step_fit_models()
        results.update(fit)
        print(json.dumps(results, indent=2, default=str))
        if check.get('status') == 'failed' or \
                fit.get('status') == 'failed':
            sys.exit(1)
        return

    if args.incremental:
        results = orchestrator.run_incremental()
        print(json.dumps(results, indent=2, default=str))
        sys.exit(1 if results.get('status') == 'failed' else 0)

    if args.run_all:
        results = orchestrator.run_full_pipeline()
        print(json.dumps(results, indent=2, default=str))
        sys.exit(1 if results.get('status') == 'failed' else 0)

    # Default: run all
    results = orchestrator.run_full_pipeline()
    print(json.dumps(results, indent=2, default=str))
    sys.exit(1 if results.get('status') == 'failed' else 0)


if __name__ == "__main__":
    main()
