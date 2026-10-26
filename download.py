"""Download CSV pertandingan + odds historis dari football-data.co.uk (divisi utama)."""
import os
import ssl
import time
import urllib.request
import urllib.error
import concurrent.futures

# Verifikasi TLS aktif secara default. Set FOOTBALL_DATA_NO_VERIFY=1 hanya untuk
# proxy lokal self-signed (bukan praktik yang disarankan).
CTX = ssl.create_default_context()
if os.environ.get("FOOTBALL_DATA_NO_VERIFY") == "1":
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

BASE = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
SITE = "https://www.football-data.co.uk/"
OUT = os.path.join(os.path.expanduser("~"), "football-data", "raw")
LEAGUES = ["E0", "E1", "E2", "E3", "SC0", "SC1", "SC2", "SC3", "D1", "D2",
           "I1", "I2", "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526", "2627"]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

os.makedirs(OUT, exist_ok=True)


def get(url, tries=4):
    """GET dengan retry utk gangguan jaringan reset; HTTPError (404) tidak di-retry."""
    last = None
    for i in range(tries):
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
                return r.read()
        except urllib.error.HTTPError:
            raise
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


# --- sanity check dulu: satu file yang pasti ada ---
probe = get(BASE.format(season="2526", league="E0"))
print(f"Probe E0_2526: {len(probe)} bytes, awal: {probe[:80]!r}")
if probe[:120].lstrip().lower().startswith(b"<"):
    raise SystemExit("Format balloon! Situs mengembalikan HTML, bukan CSV. Dibatalkan.")

# --- kamus data (non-www, sesuai link asli di situs) ---
notes = os.path.join(os.path.dirname(OUT), "notes.txt")
try:
    if not (os.path.exists(notes) and os.path.getsize(notes) > 5000):
        with open(notes, "wb") as f:
            f.write(get("https://football-data.co.uk/notes.txt"))
    print("notes.txt: OK")
except Exception as e:
    print(f"notes.txt gagal: {e}")


def fetch(lg, se):
    path = os.path.join(OUT, f"{lg}_{se}.csv")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
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


jobs = [(lg, se) for lg in LEAGUES for se in SEASONS]
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    res = list(ex.map(lambda t: fetch(*t), jobs))

ok = sum(1 for _, _, s in res if s in ("ok", "cached"))
print(f"OK: {ok}/{len(jobs)} file")
by = {}
for lg, se, st in res:
    if st not in ("ok", "cached"):
        by.setdefault(st, []).append(f"{lg}_{se}")
for st in sorted(by):
    print(f"  {st}: {len(by[st])} -> {' '.join(by[st][:20])}"
          f"{' ...' if len(by[st]) > 20 else ''}")

total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print(f"Total ukuran raw: {total / 1e6:.1f} MB | folder: {OUT}")
