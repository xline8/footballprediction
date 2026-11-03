# -*- coding: utf-8 -*-
"""refresh_fixtures.py — segarkan jadwal (INPUT DATA SAJA).

Sekarang: sumber utama FotMob (fotmob_fixtures.fetch — pengganti
Understat yang sejak 31 Okt 2026 balasan 403 challenge); Understat
masuk sebagai fallback bila kelak pulih. Hubungannya dengan disk:
- Tulis xg_raw/{slug}_2026_fixtures.json, {slug}_2026.json,
  {slug}_2026_all.json dgn dump musim utuh (pipeline sendiri memfilter
  tanggal >= TODAY). MODEL, config, hasil (xG) TIDAK disentuh.
- Backup lampau ditaruh di xg_raw/backup_fixtures/.
- Bila fetch gagal: fallback ke {slug}_2026_all.json yang ada di disk
  (tercatat di laporan), supaya pipeline tetap berjalan deterministik.
Output: laporan diff per liga (baris baru/hilang di >= hari ini).
"""
import gzip
import json
import os
import shutil
from datetime import datetime

from stealth import urlopen_with_retry

PROJ = os.path.dirname(os.path.abspath(__file__))
XG = os.path.join(PROJ, "xg_raw")
LEAGUES = {
    "EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
    "Serie_A": "I1", "Ligue_1": "F1",
}
TODAY = datetime.now().date().isoformat()


def fetch(slug, out_src=None):
    """Ambil dump musim utuh utk slug (list laga schema Understat).

    Urutan sumber: FotMob (fotmob_fixtures.fetch) -> Understat
    getLeagueData (ditemukan 17 Okt; sejak 31 Okt balasan 403 —
    dicoba lagi bila fotmob juga gagal, tergantung laporan main()).
    Bila out_src (list 1 elemen) diberikan, diisi nama sumber yang
    sukses ('fotmob.com'/'understat.com') supaya main() tidak salah
    label kesegaran."""
    import fotmob_fixtures

    first = None
    for name, fn in (("fotmob.com", fotmob_fixtures.fetch),
                     ("understat.com", _understat_fetch)):
        try:
            data = fn(slug)
            if out_src is not None:
                out_src[0] = name
            return data
        except Exception as e:  # noqa: BLE001
            first = first or e
    raise first


def _understat_fetch(slug):
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


def main():
    """Segarkan semua liga; kembalikan {div: sumber} per liga.

    Sumber "fotmob.com"/"understat.com" berarti konten segar; "fallback
    disk (...)" berarti fetch gagal dan file ditulis ulang dari dump
    {slug}_2026_all.json di disk — kontennya bisa berumur beberapa
    hari walau mtime file fixture baru. Pemanggil yang menilai
    kesegaran dari mtime saja akan tertipu (audit ronde 12, A12-2),
    jadi status sumber dikembalikan secara eksplisit.
    """
    bdir = os.path.join(XG, "backup_fixtures")
    os.makedirs(bdir, exist_ok=True)
    total_add, total_del = [], []
    sources = {}
    LAST_SOURCES.clear()
    for slug, div in LEAGUES.items():
        path = os.path.join(XG, f"{slug}_2026_fixtures.json")
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        src = None
        tag = [None]
        try:
            fresh = fetch(slug, out_src=tag)
            src = tag[0]
        except Exception as e:  # noqa: BLE001
            allp = os.path.join(XG, f"{slug}_2026_all.json")
            with open(allp, encoding="utf-8") as f:
                fresh = json.load(f)
            src = f"fallback disk ({e})"
        if not src:  # jaga-jaga: fetch lama tak mengisi tag
            src = "understat.com"
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
        total_add += [(div,) + d for d in add_fut]
        total_del += [(div,) + d for d in drop_fut]
        sources[div] = src
        LAST_SOURCES[div] = src
        print(f"[{div:>3}] {src}: {len(old)}->" f"{len(fresh)} rows | baru>=H: {len(add_fut)} "
              f"| hilang>=H: {len(drop_fut)} | backup: {os.path.basename(bpath)}")
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
              "disk (konten beku), bukan dari Understat")
        raise SystemExit(1)
