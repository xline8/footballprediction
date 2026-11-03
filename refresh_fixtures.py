# -*- coding: utf-8 -*-
"""refresh_fixtures.py — segarkan jadwal liga (INPUT DATA SAJA).

Rantai sumber per liga (sejak 2026-11-03; TA masuk 2026-11-02,
sebelumnya Understat saja):
0. FotMob (fotmob_fixtures.fetch) — dump musim UTUH (hasil + jadwal
   semusim + xG per laga dari shotmap), skema identik dump Understat
   sehingga semua konsumen bekerja tanpa perubahan. Bila sukses,
   ketiga file dump ditulis ({slug}_2026_fixtures.json,
   {slug}_2026.json, {slug}_2026_all.json) — satu-satunya sumber yang
   juga menyegarkan stok hasil/xG untuk refit sejak Understat mati.
1. TipsterArea — halaman tanggal /matches/date-DD-MM-YYYY untuk jendela
   hari ini s/d +5 hari (UTC; jam TA terbukti UTC). TA hanya menerbitkan
   jadwal beberapa hari ke depan (halaman di luar horizon terbit berupa
   stub tanpa blok laga — jendela efektif berhenti di hari terakhir
   yang benar-benar terbit), jadi TA otoritatif DI DALAM jendela
   efektif:
   pasangan laga yang sama diambil dari TA (termasuk koreksi tanggal/jam
   laga yang digeser), entri lama di dalam jendela yang tidak
   dikonfirmasi TA dibuang, dan entri di luar jendela + masa lalu
   dipertahankan dari file lama apa adanya. Nama tim TA dipetakan ke
   title yang dipakai file fixture lewat peta berlapis yang dibangun
   dari entri file fixture + {slug}_2026_all.json liga itu sendiri;
   tim/pasangan yang tidak terpetakan dengan pasti LEWATI + dilaporkan
   (LAST_UNMAPPED), tidak pernah ditebak.
2. Understat getLeagueData (jalur lama, fungsi fetch) bila TA gagal
   total untuk liga itu — termasuk bila satu halaman jendela saja
   gagal/kosong, karena jendela TA yang bolong tidak boleh dipercaya
   sebagai otoritas (entri hari yang hilang akan ikut terbuang).
3. Fallback disk: dump {slug}_2026_all.json di disk (konten beku) bila
   keduanya gagal — tercatat eksplisit sebagai "fallback disk (...)".

Kontrak yang dipertahankan:
- Hasil akhir selalu ditulis ulang ke xg_raw/{slug}_2026_fixtures.json
  dengan bentuk entri yang sama (list dict Understat-shaped).
- Backup lampau di xg_raw/backup_fixtures/ (rotasi 4), tulis atomik
  via tmp + os.replace.
- main() mengembalikan {div: sumber}; LAST_SOURCES terisi per liga
  SELAMA loop berjalan (jalur pengecualian shadow membacanya).
- Run mandiri exit 1 bila ada liga yang hanya tersegar dari fallback.
MODEL, config, hasil (xG) TIDAK disentuh.
Output: laporan diff per liga (baris baru/hilang di >= hari ini).
"""
import copy
import gzip
import json
import os
import re
import shutil
import time
from datetime import datetime, timedelta, timezone

from stealth import urlopen_with_retry

PROJ = os.path.dirname(os.path.abspath(__file__))
XG = os.path.join(PROJ, "xg_raw")
LEAGUES = {
    "EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
    "Serie_A": "I1", "Ligue_1": "F1",
}
TODAY = datetime.now().date().isoformat()

# Nama liga di TipsterArea per divisi (string persis seperti di
# ta/results.csv dan score_ledger.TA_LEAGUE).
TA_LEAGUES = {
    "E0": "England - Premier League",
    "SP1": "Spain - Primera Division",
    "D1": "Germany - Bundesliga",
    "I1": "Italy - Serie A",
    "F1": "France - Ligue 1",
}
WINDOW_DAYS = 5  # jendela otoritas TA: hari ini s/d +5 (UTC)


def fetch_fotmob(slug):
    """Dump musim utuh dari FotMob (fotmob_fixtures.fetch).

    Mengembalikan list laga skema Understat musim berjalan yang sudah
    digabung ke dump lama (baris lama dipertahankan identik bila tak
    ada informasi baru; laga selesai diperbarui dgn hasil + xG FotMob).
    """
    import fotmob_fixtures

    return fotmob_fixtures.fetch(slug)


def fetch_season(slug, out_src=None):
    """Rantai dump musim utuh untuk pipeline_orchestrator (refit):
    FotMob -> Understat. TA bukan sumber musim (jadwal saja, tanpa
    hasil/xG) jadi tidak masuk rantai ini. out_src (list 1 elemen)
    diisi nama sumber yang sukses bila diberikan."""
    first = None
    for name, fn in (("fotmob.com", fetch_fotmob),
                     ("understat.com", fetch)):
        try:
            data = fn(slug)
            if out_src is not None:
                out_src[0] = name
            return data
        except Exception as e:  # noqa: BLE001
            first = first or e
    raise first


def fetch(slug):
    """Ambil datesData langsung dari API internal Understat (ditemukan 17 Okt:
    halaman HTML jadi shell tanpa data, tapi endpoint getLeagueData terbuka)."""
    url = f"https://understat.com/getLeagueData/{slug}/2026"
    raw, _ = urlopen_with_retry(
        url, tries=3, timeout=45,
        extra_headers={"X-Requested-With": "XMLHttpRequest",
                       "Accept": "application/json"},
        referer=f"https://understat.com/league/{slug}/2026")
    if raw[:2] == b"\x1f\x8b":  # server balas gzip walau Accept-Encoding tak diminta
        raw = gzip.decompress(raw)
    data = json.loads(raw.decode("utf-8"))
    matches = data.get("dates") or []  # endpoint memuat list fixture, bukan var datesData halaman
    if not matches:
        raise ValueError(f"dates kosong dari {url}")
    return matches


def dkey(d):
    return (d["datetime"], d["h"]["title"], d["a"]["title"])


# Sumber per liga dari run main() terakhir, diperbarui liga demi liga
# SELAMA loop berjalan. Bila main() mati di tengah loop (pengecualian
# sesudah sebagian liga ditulis), nilai kembali tidak pernah sampai ke
# pemanggil — tapi liga yang sempat selesai, termasuk yang ditulis
# dari fallback disk, tetap terbaca di sini (audit ronde 13: jalur
# pengecualian shadow [1/16]).
LAST_SOURCES = {}
# Laga TA yang dilewati per liga pada run main() terakhir (nama tim /
# pasangan tak terpetakan). String siap cetak.
LAST_UNMAPPED = {}

# Cache halaman tanggal TA per run main(): {iso_date: [games]},
# {iso_date: exception}, atau {iso_date: None} (halaman stub = di
# luar horizon terbit TA). Dibersihkan di awal main() — proses
# berumur panjang (shadow) tidak boleh menyajikan halaman basi.
_PAGE_CACHE = {}


# ---------------------------------------------------------------- TA
def _numbers_for(dt_str):
    """Blok `numbers` gaya Understat untuk satu datetime UTC.

    Diverifikasi dari entri nyata file fixture: dateTime = UTC (Z),
    sedangkan year/month/week/day/hours/minutes adalah komponen jam
    dinding WIB (UTC+7) — mis. kickoff 2026-11-02 20:00 UTC tercatat
    day=3, hours="03", week=45 (tanggal WIB 3 Nov).
    """
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    wib = dt + timedelta(hours=7)
    return {
        "dateTime": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "year": wib.year, "month": wib.month,
        "week": wib.isocalendar()[1], "day": wib.day,
        "hours": f"{wib.hour:02d}", "minutes": f"{wib.minute:02d}",
    }


def _build_name_map(entries):
    """Peta berlapis nama TA -> title file fixture, dari title yang ada.

    Tiga lapis fungsi kunci, diterapkan simetris ke title dan ke nama
    TA: (1) norm_team, (2) lipatan kanonis TA score_ledger
    (_ta_key_name — memang dibangun untuk mempertemukan ejaan
    Understat dengan TipsterArea), (3) ta_model.norm. Kunci yang
    dihasilkan dua title berbeda dalam satu lapis dibuang dari lapis
    itu (ambigu = tidak pasti = jangan ditebak).
    """
    from data_enrichment.utils import norm_team
    from score_ledger import _ta_key_name
    import ta_model

    titles = sorted({e["h"]["title"] for e in entries}
                    | {e["a"]["title"] for e in entries})
    layers = []
    for fn in (norm_team, _ta_key_name, ta_model.norm):
        d, poison = {}, set()
        for t in titles:
            k = fn(t)
            if k in d and d[k] != t:
                poison.add(k)
            else:
                d[k] = t
        for k in poison:
            d.pop(k, None)
        layers.append((fn, d))
    return layers


def _map_title(layers, ta_name):
    for fn, d in layers:
        t = d.get(fn(ta_name))
        if t:
            return t
    return None


def _ta_window_games(today):
    """({iso_date: [games]}, tanggal_horizon) halaman TA hari ini..+WINDOW_DAYS.

    TA hanya menerbitkan jadwal beberapa hari ke depan; tanggal di
    luar horizon terbit dijawab halaman stub (HTTP 200 tanpa satu pun
    blok laga — penanda yang sama yang dipakai validasi
    ta_scrape._date_page_ok). Halaman stub BUKAN kegagalan: jendela
    efektif berakhir di hari sebelumnya dan entri lama di luar
    jendela efektif tidak disentuh merge. Sebaliknya kegagalan
    jaringan pada halaman mana pun menggagalkan sumber TA
    keseluruhan — jendela yang bolong di tengah tidak boleh dipercaya
    sebagai otoritas. Raise juga bila halaman HARI INI saja stub
    (TA sedang blokir/mati, bukan horizon).
    """
    import ta_scrape

    out = {}
    horizon = None
    for off in range(WINDOW_DAYS + 1):
        d = today + timedelta(days=off)
        iso = d.isoformat()
        if iso in _PAGE_CACHE:
            cached = _PAGE_CACHE[iso]
            if isinstance(cached, Exception):
                raise cached
            if cached is None:
                break  # stub: horizon sudah berakhir sebelum hari ini
            out[iso] = cached
            horizon = d
            continue
        try:
            url = f"{ta_scrape.BASE}/matches/date-{d.strftime('%d-%m-%Y')}"
            text, _ = ta_scrape.fetch(url, cache_name=None)
            if '<a class="game"' not in text:
                _PAGE_CACHE[iso] = None  # stub: di luar horizon terbit
                break
            games = ta_scrape.parse_date_page(text, iso)
        except Exception as e:  # noqa: BLE001
            _PAGE_CACHE[iso] = e
            raise
        _PAGE_CACHE[iso] = games
        out[iso] = games
        horizon = d
        time.sleep(ta_scrape.DELAY)  # sopan ke server, hanya saat fetch nyata
    if horizon is None:
        raise RuntimeError(
            f"halaman TA {today.isoformat()} pun stub (di luar horizon "
            "terbit / diblokir?) — TA dianggap gagal")
    return out, horizon


def _ta_entries(slug, old, all_entries, today):
    """Entri fixture berbentuk Understat dari halaman TA liga ini.

    Mengembalikan (entries, unmapped, horizon): entries = list dict
    siap merge; unmapped = list string laga yang dilewati
    (nama/pasangan tak terpetakan, jam tak terbaca); horizon =
    tanggal terakhir yang benar-benar diterbitkan TA. Template entri
    diambil dari file lama (fixtures menang atas _all) supaya id
    tim/judul persis sama; hanya datetime + numbers yang diganti
    dari TA.
    """
    div = LEAGUES[slug]
    games_by_date, horizon = _ta_window_games(today)
    layers = _build_name_map(list(old) + list(all_entries))
    templates = {}
    for e in all_entries:
        templates[(e["h"]["title"], e["a"]["title"])] = e
    for e in old:
        templates[(e["h"]["title"], e["a"]["title"])] = e
    ta_league = TA_LEAGUES[div]
    by_pair, unmapped = {}, []
    for iso in sorted(games_by_date):
        for g in games_by_date[iso]:
            if g["league"] != ta_league or g["status"] != "NS":
                continue
            raw = (g.get("status_raw") or "").upper()
            if "POSTP" in raw or "CANC" in raw or "ABD" in raw:
                continue  # ditunda/batal versi TA: jangan jadikan fixture
            ht = _map_title(layers, g["home"])
            at = _map_title(layers, g["away"])
            if not ht or not at:
                unmapped.append(
                    f"{iso} {g['home']} v {g['away']} (nama tak terpetakan)")
                continue
            tpl = templates.get((ht, at))
            if tpl is None:
                unmapped.append(
                    f"{iso} {ht} v {at} (pasangan tak ada di file lama)")
                continue
            tm = re.match(r"^(\d{1,2}):(\d{2})$", (g["time"] or "").strip())
            if not tm:
                unmapped.append(
                    f"{iso} {ht} v {at} (jam TA tak terbaca: {g['time']!r})")
                continue
            dt_str = f"{iso} {int(tm.group(1)):02d}:{tm.group(2)}:00"
            ent = copy.deepcopy(tpl)
            ent["datetime"] = dt_str
            ent["numbers"] = _numbers_for(dt_str)
            if ent.get("isResult"):
                # Template laga yang sudah ber-result tidak boleh
                # menyeret skor/xG lama ke jadwal baru.
                ent["isResult"] = False
                ent["goals"] = {"h": None, "a": None}
                ent["xG"] = {"h": None, "a": None}
                ent.pop("forecast", None)
            by_pair[(ht, at)] = ent  # tanggal terbaru menang bila ganda
    return list(by_pair.values()), unmapped, horizon


def merge_fixtures(old, ta_entries, today, window_days=WINDOW_DAYS):
    """Gabung entri lama dengan entri TA menurut aturan jendela.

    - Pasangan yang ada di TA: versi TA yang dipakai (koreksi geser
      berlaku juga bila entri lama bertanggal SEBELUM jendela — laga
      yang ternyata belum dimainkan tidak boleh jadi duplikat hantu).
    - Entri lama di dalam jendela tanpa konfirmasi TA: dibuang.
    - Sisanya (masa lalu + luar jendela): dipertahankan apa adanya.
    Mengembalikan (merged terurut datetime, jumlah dibuang).
    """
    win_lo = today.isoformat()
    win_hi = (today + timedelta(days=window_days)).isoformat()
    ta_pairs = {(e["h"]["title"], e["a"]["title"]) for e in ta_entries}
    kept, dropped = [], 0
    for e in old:
        pair = (e["h"]["title"], e["a"]["title"])
        if pair in ta_pairs:
            continue  # digantikan versi TA di bawah
        if win_lo <= e["datetime"][:10] <= win_hi:
            dropped += 1
            continue  # di dalam jendela, TA tidak menjadwalkannya
        kept.append(e)
    merged = kept + list(ta_entries)
    merged.sort(key=lambda e: (e["datetime"], e["h"]["title"], e["a"]["title"]))
    return merged, dropped


def fetch_tipsterarea(slug, old, all_entries, today=None):
    """Sumber utama: jadwal TA ter-merge. Mengembalikan (entries, unmapped).

    Raise bila jendela TA tidak utuh, atau TA tidak memberi satu pun
    fixture untuk liga ini padahal file lama punya entri di jendela
    (halaman kosong parsial tidak boleh menghapus jadwal satu liga).
    """
    today = today or datetime.now(timezone.utc).date()
    ta_entries, unmapped, horizon = _ta_entries(
        slug, old, all_entries, today)
    win_days = (horizon - today).days  # jendela efektif s/d horizon TA
    if not ta_entries:
        win_lo = today.isoformat()
        win_hi = horizon.isoformat()
        n_old_win = sum(1 for e in old
                        if win_lo <= e["datetime"][:10] <= win_hi)
        if n_old_win:
            raise RuntimeError(
                f"TA memberi 0 fixture untuk {slug} di jendela "
                f"{win_lo}..{win_hi}, file lama punya {n_old_win} — "
                "TA dianggap gagal untuk liga ini")
    merged, _dropped = merge_fixtures(old, ta_entries, today,
                                       window_days=win_days)
    return merged, unmapped


# ---------------------------------------------------------------- main
def main():
    """Segarkan semua liga; kembalikan {div: sumber} per liga.

    Sumber "fotmob.com"/"tipsterarea.com"/"understat.com" berarti
    konten segar; "fallback disk (...)" berarti semua sumber gagal dan file ditulis
    ulang dari dump {slug}_2026_all.json di disk — kontennya bisa
    berumur beberapa hari walau mtime file fixture baru. Pemanggil
    yang menilai kesegaran dari mtime saja akan tertipu (audit ronde
    12, A12-2), jadi status sumber dikembalikan secara eksplisit.
    """
    bdir = os.path.join(XG, "backup_fixtures")
    os.makedirs(bdir, exist_ok=True)
    _PAGE_CACHE.clear()
    total_add, total_del = [], []
    sources = {}
    LAST_SOURCES.clear()
    LAST_UNMAPPED.clear()
    for slug, div in LEAGUES.items():
        path = os.path.join(XG, f"{slug}_2026_fixtures.json")
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        allp = os.path.join(XG, f"{slug}_2026_all.json")
        all_entries = []
        if os.path.exists(allp):
            with open(allp, encoding="utf-8") as f:
                all_entries = json.load(f)
        unmapped = []
        season_fresh = None
        try:
            fresh = fetch_fotmob(slug)
            season_fresh = fresh
            src = "fotmob.com"
            import fotmob_fixtures
            fails = (fotmob_fixtures.LAST_SOURCES.get("_fails")
                     or {}).get(div)
            if fails:
                unmapped = [f"nama FotMob tak terpetakan: {f}"
                            for f in fails]
        except Exception as fm_e:  # noqa: BLE001
            try:
                fresh, unmapped = fetch_tipsterarea(slug, old, all_entries)
                src = "tipsterarea.com"
            except Exception as ta_e:  # noqa: BLE001
                try:
                    fresh = fetch(slug)
                    src = "understat.com"
                except Exception as us_e:  # noqa: BLE001
                    fresh = all_entries if all_entries else old
                    src = (f"fallback disk (FotMob: {fm_e}; TA: {ta_e}; "
                           f"Understat: {us_e})")
        LAST_UNMAPPED[div] = unmapped
        old_ids = {dkey(d) for d in old}
        new_ids = {dkey(d) for d in fresh}
        add = sorted(new_ids - old_ids)
        drop = sorted(old_ids - new_ids)
        add_fut = [d for d in add if d[0] >= TODAY]
        drop_fut = [d for d in drop if d[0] >= TODAY]
        # backup lama lalu tulis baru (immutable backup, satu salinan per run)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        bpath = os.path.join(bdir, f"{slug}_2026_fixtures_{ts}.json")
        shutil.copy2(path, bpath)
        # rotasi: simpan 4 backup terbaru per liga
        _old = sorted(f for f in os.listdir(bdir)
                      if f.startswith(f"{slug}_2026_fixtures_"))
        for _f in _old[:-4]:
            try:
                os.remove(os.path.join(bdir, _f))
            except OSError:
                pass
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(fresh, f, ensure_ascii=False)
        os.replace(tmp, path)
        if season_fresh is not None:
            # Sumber musim utuh (FotMob): segarkan juga dump musim yang
            # dibaca jalur refit ({slug}_2026.json + {slug}_2026_all.json)
            # dari baris yang sama, supaya stok hasil/xG ikut maju.
            for sname in (f"{slug}_2026.json", f"{slug}_2026_all.json"):
                spath = os.path.join(XG, sname)
                stmp = spath + ".tmp"
                with open(stmp, "w", encoding="utf-8") as f:
                    json.dump(season_fresh, f, ensure_ascii=False)
                os.replace(stmp, spath)
        total_add += [(div,) + d for d in add_fut]
        total_del += [(div,) + d for d in drop_fut]
        sources[div] = src
        LAST_SOURCES[div] = src
        print(f"[{div:>3}] {src}: {len(old)}->" f"{len(fresh)} rows | baru>=H: {len(add_fut)} "
              f"| hilang>=H: {len(drop_fut)} | backup: {os.path.basename(bpath)}")
        for u in unmapped[:10]:
            print(f"      dilewati: {u}")
        if len(unmapped) > 10:
            print(f"      ... dan {len(unmapped) - 10} laga TA lain dilewati")
    print(f"TOTAL fixture >= {TODAY}: +{len(total_add)} / -{len(total_del)}")
    for d in total_add[:10]:
        print("  +", d[0], d[1][:10], d[2], "v", d[3])
    for d in total_del[:10]:
        print("  -", d[0], d[1][:10], d[2], "v", d[3])
    return sources


if __name__ == "__main__":
    _srcs = main()
    if any(str(s).startswith("fallback") for s in _srcs.values()):
        # Run mandiri harus terlihat gagal bila ada liga yang hanya
        # tersegar dari konten beku (audit ronde 13) — pemanggil
        # in-process membaca peta sumbernya langsung.
        print("PERINGATAN: sebagian liga disegarkan dari fallback "
              "disk (konten beku), bukan dari sumber segar "
              "(FotMob/TipsterArea/Understat)")
        raise SystemExit(1)
