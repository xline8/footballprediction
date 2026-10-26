# -*- coding: utf-8 -*-
"""refresh_fixtures.py — segarkan jadwal dari Understat (INPUT DATA SAJA).

Kontrak:
- Ambil halaman liga Understat (5 liga model), ekstrak `datesData` (JSON di <script>).
- Tulis ulang xg_raw/{slug}_2026_fixtures.json dgn dump utuh (pipeline sendiri
  memfilter tanggal >= TODAY). MODEL, config, hasil (xG) TIDAK disentuh.
- Backup lampau ditaruh di xg_raw/backup_fixtures/.
- Bila fetch gagal: fallback ke {slug}_2026_all.json yang ada di disk (tercatat di laporan),
  supaya pipeline tetap berjalan deterministik.
Output: laporan diff per liga (baris baru/hilang di >= hari ini).
"""
import gzip
import json
import os
import shutil
import urllib.request
from datetime import datetime

PROJ = os.path.dirname(os.path.abspath(__file__))
XG = os.path.join(PROJ, "xg_raw")
LEAGUES = {
    "EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
    "Serie_A": "I1", "Ligue_1": "F1",
}
TODAY = datetime.now().date().isoformat()
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def fetch(slug):
    """Ambil datesData langsung dari API internal Understat (ditemukan 17 Okt:
    halaman HTML jadi shell tanpa data, tapi endpoint getLeagueData terbuka)."""
    url = f"https://understat.com/getLeagueData/{slug}/2026"
    headers = {
        "User-Agent": UA,
        "Referer": f"https://understat.com/league/{slug}/2026",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    raw = urllib.request.urlopen(req, timeout=45).read()
    if raw[:2] == b"\x1f\x8b":  # server balas gzip walau Accept-Encoding tak diminta
        raw = gzip.decompress(raw)
    data = json.loads(raw.decode("utf-8"))
    matches = data.get("dates") or []  # endpoint memuat list fixture, bukan var datesData halaman
    if not matches:
        raise ValueError(f"dates kosong dari {url}")
    return matches


def dkey(d):
    return (d["datetime"], d["h"]["title"], d["a"]["title"])


def main():
    bdir = os.path.join(XG, "backup_fixtures")
    os.makedirs(bdir, exist_ok=True)
    total_add, total_del = [], []
    for slug, div in LEAGUES.items():
        path = os.path.join(XG, f"{slug}_2026_fixtures.json")
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        src = "understat.com"
        try:
            fresh = fetch(slug)
        except Exception as e:  # noqa: BLE001
            allp = os.path.join(XG, f"{slug}_2026_all.json")
            with open(allp, encoding="utf-8") as f:
                fresh = json.load(f)
            src = f"fallback disk ({e.__class__.__name__})"
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
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(fresh, f, ensure_ascii=False)
        os.replace(tmp, path)
        total_add += [(div,) + d for d in add_fut]
        total_del += [(div,) + d for d in drop_fut]
        print(f"[{div:>3}] {src}: {len(old)}->" f"{len(fresh)} rows | baru>=H: {len(add_fut)} "
              f"| hilang>=H: {len(drop_fut)} | backup: {os.path.basename(bpath)}")
    print(f"TOTAL fixture >= {TODAY}: +{len(total_add)} / -{len(total_del)}")
    for d in total_add[:10]:
        print("  +", d[0], d[1][:10], d[2], "v", d[3])
    for d in total_del[:10]:
        print("  -", d[0], d[1][:10], d[2], "v", d[3])


if __name__ == "__main__":
    main()
