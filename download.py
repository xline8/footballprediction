"""Download CSV pertandingan + odds historis dari football-data.co.uk (divisi utama)."""
import os
import concurrent.futures
import sys
import urllib.error

from stealth import urlopen_with_retry

BASE = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
OUT = os.path.join(os.path.expanduser("~"), "football-data", "raw")
LEAGUES = ["E0", "E1", "E2", "E3", "SC0", "SC1", "SC2", "SC3", "D1", "D2",
           "I1", "I2", "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526", "2627"]
os.makedirs(OUT, exist_ok=True)


def get(url, tries=4):
    """GET dengan retry utk gangguan jaringan reset; HTTPError (404) tidak di-retry."""
    data, _ = urlopen_with_retry(url, tries=tries, timeout=40)
    return data


def fetch(lg, se, force=False):
    path = os.path.join(OUT, f"{lg}_{se}.csv")
    if not force and os.path.exists(path) and os.path.getsize(path) > 1000:
        return lg, se, "cached"
    try:
        data = get(BASE.format(season=se, league=lg), tries=3)
    except urllib.error.HTTPError as e:
        return lg, se, f"http-{e.code}"
    except Exception as e:
        return lg, se, f"error-{type(e).__name__}"
    if data[:120].lstrip().lower().startswith(b"<"):
        return lg, se, "html-error"
    with open(path, "wb") as f:
        f.write(data)
    return lg, se, "ok"


def download(seasons=SEASONS, leagues=LEAGUES, force=False):
    """Unduh CSV untuk daftar musim (default semua). Return dict ringkasan.

    Dipakai pipeline untuk refresh hanya musim berjalan (mis. ["2627"]).
    force=True: re-unduh walau file sudah ada (refresh mingguan; tanpa force,
    file yang ada dianggap segar dan dilewati).
    """
    # sanity check dulu: satu file yang pasti ada
    probe = get(BASE.format(season="2526", league="E0"), tries=2)
    if probe[:120].lstrip().lower().startswith(b"<"):
        raise RuntimeError("Format balloon! Situs mengembalikan HTML, bukan CSV. Dibatalkan.")

    jobs = [(lg, se) for lg in leagues for se in seasons]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(lambda t: fetch(*t, force=force), jobs))

    ok = sum(1 for _, _, s in res if s in ("ok", "cached"))
    by = {s: [f"{lg}_{se}" for lg, se, st in res if st == s]
          for s in {st for _, _, st in res}}
    return {"ok": ok, "total": len(jobs), "by_status": by}


if __name__ == "__main__":
    seasons = sys.argv[1:] or SEASONS
    r = download(seasons=seasons)
    print(f"OK: {r['ok']}/{r['total']} file")
    for st in sorted(r["by_status"]):
        if st in ("ok", "cached"):
            continue
        files = r["by_status"][st]
        print(f"  {st}: {len(files)} -> {' '.join(files[:20])}"
              f"{' ...' if len(files) > 20 else ''}")
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"Total ukuran raw: {total / 1e6:.1f} MB | folder: {OUT}")
