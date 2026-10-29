#!/usr/bin/env python3
"""
ta_scrape.py -- pengambil harga pasar (odds) + hasil pertandingan dari tipsterarea.com.

Sumber:
  * /matches/date-DD-MM-YYYY  -> semua laga 1 hari: jam, tim, skor, status, odds 1X2
  * /match/<slug>-<id>        -> pasar lengkap per bandar: 1X2, Double Chance,
                                 Draw No Bet, Over/Under (banyak garis), BTS

Keluaran (append-only, di folder ta/):
  fixtures.csv             satu baris per laga yang pernah terlihat
  odds_1x2_snapshots.csv   riwayat harga 1X2 (dari halaman tanggal)
  odds_markets_snapshots.csv riwayat harga pasar lain (dari halaman laga)
  results.csv              skor akhir per laga
  raw/                     cache HTML mentah (audit)

File ini TIDAK menyentuh model, CSV model, atau struktur data situs.
"""
import asyncio
import csv
import gzip
import html
import json
import os
import random
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

from stealth import (BACKOFF_BASE, BACKOFF_MAX, RETRYABLE, _retry_delay,
                     proxy_url, ua as stealth_ua)

from data_enrichment.utils import norm_team, to_float

BASE = "https://tipsterarea.com"
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ta")
RAW = os.path.join(DIR, "raw")
COOKIE_FILE = os.path.join(DIR, "session_cookies.json")

DELAY = 1.2          # detik antar-request (sopan ke server)
TIMEOUT = 30
RETRIES = 3
MAX_CONCURRENCY = 5  # async batch size
CACHE_TTL_DATE = 60 * 20    # 20 menit cache HTML untuk halaman tanggal
CACHE_TTL_MATCH = 60 * 30   # 30 menit cache HTML untuk halaman laga

FIX_COLS = ["game_id", "date", "time", "league", "country", "home", "away",
            "status", "score_h", "score_a", "url", "first_seen", "last_seen"]
SNAP_COLS = ["captured_at", "game_id", "date", "home", "away", "o1", "ox", "o2",
             "status", "score_h", "score_a"]
MKT_COLS = ["captured_at", "game_id", "market", "line", "selection", "bookmaker",
            "odds", "url"]
RES_COLS = ["game_id", "date", "league", "home", "away", "score_h", "score_a",
            "status", "source_url", "updated_at"]
CORNER_OUT_COLS = ("date", "home_team", "away_team", "corner_line",
                   "odds_over", "odds_under")


# ---------------------------------------------------------------- util
def now_iso():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def ensure_dirs():
    os.makedirs(DIR, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path, cols, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def append_rows(path, cols, rows):
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- http
def _cache_path(cache_name):
    ensure_dirs()
    return os.path.join(RAW, cache_name)


def _from_cache(cache_name, ttl):
    if not cache_name:
        return None
    cp = _cache_path(cache_name)
    if os.path.exists(cp):
        if time.time() - os.path.getmtime(cp) < ttl:
            with open(cp, "r", encoding="utf-8") as f:
                return f.read()
    return None


def _to_cache(cache_name, text):
    if not cache_name:
        return
    cp = _cache_path(cache_name)
    with open(cp, "w", encoding="utf-8") as f:
        f.write(text)


def _sync_fetch(url, cache_name=None, ttl=CACHE_TTL_DATE):
    """Sync fetch (fallback jika httpx tidak tersedia)."""
    cached = _from_cache(cache_name, ttl)
    if cached is not None:
        return cached, True
    text = _http_get(url)
    if cache_name:
        _to_cache(cache_name, text)
    return text, False


def _load_cookie_jar():
    """Muat cookie tersimpan -> httpx.Cookies (kosong bila file tak ada/rusak)."""
    jar = httpx.Cookies()
    try:
        with open(COOKIE_FILE, encoding="utf-8") as f:
            for c in json.load(f):
                jar.set(c["name"], c["value"], domain=c.get("domain"),
                        path=c.get("path", "/"))
    except Exception:  # noqa: BLE001
        pass
    return jar


def _save_cookie_jar(client):
    """Simpan cookie dari sesi terakhir ke disk (lintas-run)."""
    try:
        entries = [{
            "name": c.name, "value": c.value, "domain": c.domain,
            "path": c.path, "secure": c.secure, "expires": c.expires,
        } for c in client.cookies.jar]
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f)
    except Exception as e:  # noqa: BLE001
        print(f"  ! cookie save gagal: {e!r}", file=sys.stderr)


async def _async_fetch(client, url, cache_name=None, ttl=CACHE_TTL_DATE):
    """Async fetch: cek cache, retry sadar-status, jangan cache error page."""
    cached = _from_cache(cache_name, ttl)
    if cached is not None:
        return cached, True
    last = None
    for attempt in range(RETRIES):
        try:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True,
                                    headers={"User-Agent": stealth_ua()})
            code = resp.status_code
            if code == 200:
                text = resp.text
                if cache_name:
                    _to_cache(cache_name, text)
                return text, False
            if code in RETRYABLE:
                last = resp
                delay = _retry_delay(resp.headers, attempt)
                if delay > 0:
                    await asyncio.sleep(delay)
                continue
            resp.raise_for_status()  # 403/404/dll -> hard-stop
        except asyncio.CancelledError:
            raise
        except Exception as e:
            last = e
            cached = _from_cache(cache_name, ttl)
            if cached is not None:
                return cached, True
            if attempt < RETRIES - 1:
                await asyncio.sleep(min(BACKOFF_BASE * (2 ** attempt),
                                        BACKOFF_MAX))
    if isinstance(last, httpx.Response):
        last.raise_for_status()
    raise RuntimeError(f"gagal ambil {url}: {last}")


def _http_get(url):
    """urllib fallback."""
    import urllib.error
    import urllib.request
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": stealth_ua(),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-GB,en;q=0.9",
                "Accept-Encoding": "gzip",
            })
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return data.decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last = e
            if attempt < RETRIES - 1:
                time.sleep(2.0 * (attempt + 1) + random.random())
    raise RuntimeError(f"gagal ambil {url}: {last}")


# ---------------------------------------------------------------- market completeness
def market_last_snapshot_time(game_id):
    """Waktu snapshot pasar terakhir per game_id (atau None)."""
    path = os.path.join(DIR, "odds_markets_snapshots.csv")
    if not os.path.exists(path):
        return None
    latest = {}
    for r in _read(path):
        if r["game_id"] == game_id:
            ts = r.get("captured_at", "")
            if ts and (latest.get(game_id) is None or ts > latest[game_id]):
                latest[game_id] = ts
    return latest.get(game_id)


def market_needs_refresh(game_id, refresh_hours=1.5):
    """True bila perlu fetch market page: belum ada snapshot atau >refresh_hours."""
    ts = market_last_snapshot_time(game_id)
    if ts is None:
        return True
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+0000", "+00:00"))
    except (ValueError, AttributeError):
        return True
    return (datetime.now(timezone.utc) - dt).total_seconds() > refresh_hours * 3600


# ---------------------------------------------------------------- async batch
async def async_fetch_pages(urls_with_cache, ttl_map=None):
    """Fetch multiple pages concurrently.
    urls_with_cache: list of (url, cache_name, ttl) tuples.
    Returns list of (text, from_cache) aligned to input order.
    """
    if not _HAS_HTTPX:
        # Fallback: sync sequential
        return [(_sync_fetch(u, c, ttl_map.get(i, CACHE_TTL_DATE) if ttl_map else CACHE_TTL_DATE)[0],
                 _sync_cache_check(c, ttl_map.get(i, CACHE_TTL_DATE) if ttl_map else CACHE_TTL_DATE))
                for i, (u, c, _) in enumerate(urls_with_cache)]

    results = [None] * len(urls_with_cache)
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    ttl_map = ttl_map or {}

    async def fetch_one(idx, url, cache_name, ttl):
        async with semaphore:
            try:
                text, cached = await _async_fetch(client, url, cache_name, ttl)
            except Exception as e:  # noqa: BLE001
                # satu URL gagal tidak boleh membatalkan seluruh batch
                print(f"  ! fetch gagal {url}: {e!r}", file=sys.stderr)
                results[idx] = (None, True)
                return
            # Delay sopan setelah request asli (bukan cache)
            if not cached:
                await asyncio.sleep(DELAY)
            results[idx] = (text, cached)

    jar = _load_cookie_jar()
    async with httpx.AsyncClient(
        headers={
            "User-Agent": stealth_ua(),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip",
        },
        proxy=proxy_url(),
        cookies=jar,
    ) as client:
        tasks = []
        for i, (url, cache_name, ttl) in enumerate(urls_with_cache):
            ttl_val = ttl if ttl else ttl_map.get(i, CACHE_TTL_DATE)
            tasks.append(fetch_one(i, url, cache_name, ttl_val))
        await asyncio.gather(*tasks)
        _save_cookie_jar(client)

    return results


def _sync_cache_check(cache_name, ttl):
    """For fallback: cek apakah dari cache."""
    if not cache_name:
        return False
    cp = _cache_path(cache_name)
    return os.path.exists(cp) and (time.time() - os.path.getmtime(cp) < ttl)


def fetch(url, cache_name=None, ttl=CACHE_TTL_DATE):
    """Wrapper: sync atau async fetch. Default sync (untuk backward compat)."""
    return _sync_fetch(url, cache_name, ttl)


def _txt(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).replace("&nbsp;", " ").strip()


def parse_date_page(html, iso_date):
    """Halaman tanggal -> list dict per laga (1X2 + skor + status).

    Markup (terverifikasi 17 Okt 2026):
      <a class="game" href="/match/slug-949892" id="g_949892">
        <span class="time notime started">12:30</span>
        <span class="status play">HT</span>            (opsional)
        <span class="teams">
          <span class="home"><span>Everton</span></span>
          <span class="score scsm play">0 - 0</span>   (opsional)
          <span class="away"><span>Chelsea</span></span>
        </span>
        <span class="odds">
          <span class="o1">3.14</span><span class="oX">3.72</span><span class="o2">2.21</span>
        </span>
      </a>
    """
    games = []
    league = country = ""
    for m in re.finditer(
            r'<span class="league-name"><span>([^<]+)</span>'
            r'|(<a class="game" href="(/match/[^"]+)"[^>]*>.*?</a>)', html, re.S):
        if m.group(1):
            league = m.group(1).strip()
            country = league.split(" - ")[0].strip() if " - " in league else league
            continue
        block, href = m.group(2), m.group(3)
        gid = re.search(r"-(\d+)$", href)
        gid = gid.group(1) if gid else href.rsplit("/", 1)[-1]

        def pick(pat, s=block):
            mm = re.search(pat, s, re.S)
            return _txt(mm.group(1)) if mm else ""

        ttime = pick(r'<span class="time[^"]*">([^<]*)</span>')
        status_txt = pick(r'<span class="status[^"]*">(.*?)</span>')
        home = pick(r'<span class="home"><span[^>]*>([^<]+)</span></span>')
        away = pick(r'<span class="away"><span[^>]*>([^<]+)</span></span>')
        if not home or not away:
            continue
        home = norm_team(home)
        away = norm_team(away)

        sh = sa = ""
        sc = pick(r'<span class="score[^"]*">(.*?)</span>')
        mm = re.match(r"(\d+)\s*-\s*(\d+)", sc)
        if mm:
            sh, sa = mm.group(1), mm.group(2)

        o = {}
        for k in ("o1", "oX", "o2"):
            o[k] = pick(r'<span class="%s[^"]*">([\d.]+)</span>' % k)
        if not o["o1"]:
            o["o1"] = pick(r'<td class="odd">([\d.]+)</td>')
            o["oX"] = pick(r'<td class="odd">([\d.]+)</td>')
            o["o2"] = pick(r'<td class="odd">([\d.]+)</td>')

        # status: halaman lampau tidak punya <span class="status">, tapi ada skor
        st = status_txt.strip().upper()
        if sh == "":
            status = "NS"
        elif st.startswith("FT") or st.startswith("AET") or st.startswith("PEN"):
            status = "FT"
        elif st in ("", "-"):
            status = "FT"          # arsip: skor ada, penanda status tidak ada
        else:
            status = "LIVE"        # HT, 67', 1H, 2H, ...

        games.append({
            "game_id": gid, "date": iso_date, "time": ttime,
            "league": league, "country": country,
            "home": home, "away": away, "status": status,
            "score_h": sh, "score_a": sa,
            "o1": o["o1"], "ox": o["oX"], "o2": o["o2"],
            "url": BASE + href,
        })
    return games


RE_TABLE = re.compile(r'<table class="odds">(.*?)</table>', re.S)


def parse_match_page(html, game_id, url):
    """Halaman laga -> list baris pasar: market, line, selection, bookmaker, odds."""
    out = []
    for tbl in RE_TABLE.findall(html):
        head = re.search(r"<thead>(.*?)</thead>", tbl, re.S)
        if not head:
            continue
        ths = re.findall(r"<th([^>]*)>(.*?)</th>", head.group(1), re.S)
        if not ths:
            continue
        market = ""
        labels = []
        for attrs, label in ths:
            txt = _txt(label)
            if "odds-type" in attrs:
                market = txt
            elif txt:
                labels.append(txt)
        if not market:
            continue
        body = re.search(r"<tbody>(.*?)</tbody>", tbl, re.S)
        if not body:
            continue
        for tr in re.findall(r"<tr>(.*?)</tr>", body.group(1), re.S):
            bm = re.search(r'<img class="bookie"[^>]*alt="([^"]+)"', tr)
            if not bm:
                continue
            book = bm.group(1).strip()
            line = ""
            lc = re.search(r'<td class="center">([^<]*)</td>', tr)
            if lc:
                line = _txt(lc.group(1))
                if not re.match(r"^[\d.]+$", line):
                    line = ""
            odds = [_txt(x) for x in
                    re.findall(r'<td class="odd">([^<]*)</td>', tr)]
            odds = [o for o in odds if re.match(r"^\d+(\.\d+)?$", o)]
            # Over/Under: header [Goals][Under][Over] tapi kolom harga hanya 2,
            # karena "Goals" menunjuk ke kolom garis (td.center).
            labs = list(labels)
            if len(odds) == len(labs) - 1 and labs and \
                    labs[0].lower() in ("goals", "line", "total", "handicap"):
                labs = labs[1:]
            for i, lab in enumerate(labs):
                if i >= len(odds):
                    break
                out.append({
                    "game_id": game_id, "market": market, "line": line,
                    "selection": lab, "bookmaker": book,
                    "odds": odds[i], "url": url,
                })
    return out


# ---------------------------------------------------------------- simpan
def save_date_page(games, captured):
    ensure_dirs()
    fpath = os.path.join(DIR, "fixtures.csv")
    frows = {r["game_id"]: r for r in _read(fpath)}
    srows = []
    for g in games:
        old = frows.get(g["game_id"])
        if old:
            old.update({k: g[k] for k in ("date", "time", "league", "country",
                                          "home", "away", "status",
                                          "score_h", "score_a", "url")})
            old["last_seen"] = captured
        else:
            g2 = dict(g)
            g2["first_seen"] = g2["last_seen"] = captured
            frows[g["game_id"]] = g2
        srows.append({"captured_at": captured, "game_id": g["game_id"],
                      "date": g["date"], "home": g["home"], "away": g["away"],
                      "o1": g["o1"], "ox": g["ox"], "o2": g["o2"],
                      "status": g["status"], "score_h": g["score_h"],
                      "score_a": g["score_a"]})
    _write(fpath, FIX_COLS, list(frows.values()))

    # snapshot: tulis hanya kalau harga/status berubah dari snapshot terakhir
    spath = os.path.join(DIR, "odds_1x2_snapshots.csv")
    prev = {}
    for r in _read(spath):
        prev[r["game_id"]] = (r["o1"], r["ox"], r["o2"], r["status"],
                              r["score_h"], r["score_a"])
    fresh = []
    for r in srows:
        key = (r["o1"], r["ox"], r["o2"], r["status"], r["score_h"], r["score_a"])
        if prev.get(r["game_id"]) != key:
            fresh.append(r)
            prev[r["game_id"]] = key
    if fresh:
        append_rows(spath, SNAP_COLS, fresh)

    # results
    rpath = os.path.join(DIR, "results.csv")
    res = {r["game_id"]: r for r in _read(rpath)}
    changed = 0
    for g in games:
        if g["status"] == "FT" and g["score_h"] != "":
            cur = res.get(g["game_id"])
            if (not cur or cur["score_h"] != g["score_h"]
                    or cur["score_a"] != g["score_a"] or cur["status"] != "FT"):
                res[g["game_id"]] = {
                    "game_id": g["game_id"], "date": g["date"],
                    "league": g["league"], "home": g["home"], "away": g["away"],
                    "score_h": g["score_h"], "score_a": g["score_a"],
                    "status": "FT", "source_url": g["url"],
                    "updated_at": captured,
                }
                changed += 1
    if changed:
        _write(rpath, RES_COLS, list(res.values()))
    return len(fresh), changed


def save_markets(rows, captured):
    if not rows:
        return 0
    ensure_dirs()
    path = os.path.join(DIR, "odds_markets_snapshots.csv")
    prev = {}
    for r in _read(path):
        prev[(r["game_id"], r["market"], r["line"], r["selection"],
              r["bookmaker"])] = r["odds"]
    fresh = []
    for r in rows:
        k = (r["game_id"], r["market"], r["line"], r["selection"], r["bookmaker"])
        if prev.get(k) != r["odds"]:
            row = dict(r)
            row["captured_at"] = captured
            fresh.append(row)
            prev[k] = r["odds"]
    if fresh:
        append_rows(path, MKT_COLS, fresh)
    return len(fresh)


# ---------------------------------------------------------------- main
def iso(d):
    return d.strftime("%Y-%m-%d")


def ta_date(d):
    return d.strftime("date-%d-%m-%Y")


def await_wrap(coro):
    """Run async coro in sync context (for nested asyncio.run)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Already in async context (seharang ini tidak dipakai, tapi future-proof)
        return asyncio.ensure_future(coro)
    return asyncio.run(coro)


def sync_dates(days, with_markets=False, market_ids=None, verbose=True, fresh=False):
    """days: list objek date. Return ringkasan.

    fresh=True: paksa fetch jaring untuk halaman tanggal (ttl=0) — dipakai
    sinkronisasi tanggal lampau yang status FT-nya belum lengkap.
    """
    captured = now_iso()
    tot_snap = tot_res = 0
    nrows = 0
    all_games = []

    # --- Phase 1: date pages (async if httpx available) ---
    date_ttl = 0 if fresh else CACHE_TTL_DATE
    date_urls = [(f"{BASE}/matches/{ta_date(d)}", f"date-{iso(d)}.html", date_ttl)
                 for d in days]

    if _HAS_HTTPX:
        results = asyncio.run(async_fetch_pages(date_urls))
    else:
        results = [((_sync_fetch(u, c, ttl), ))[0]
                   for u, c, ttl in date_urls]
        results = [(r[0], r[1]) for r in results]

    date_htmls = {}  # iso_date -> (html, cached)
    for d, (html, cached) in zip(days, results):
        iso_d = iso(d)
        try:
            date_htmls[iso_d] = (html, cached)
            games = parse_date_page(html, iso_d)
            snap, res = save_date_page(games, captured)
            tot_snap += snap
            tot_res += res
            all_games.extend(games)
            if verbose:
                tag = "cache" if cached else "net"
                print(f"  {iso_d}  {len(games):3d} laga  "
                      f"snapshot+{snap:3d}  hasil+{res:2d}  ({tag})")
        except Exception as e:
            print(f"  ! {iso_d}: {e}", file=sys.stderr)
            date_htmls[iso_d] = (None, True)

    # --- Phase 2: market pages (hanya yang perlu, async) ---
    if with_markets:
        # Filter: hanya laga yang belum lengkap / perlu refresh
        candidate_ids = market_ids if market_ids is not None else [g["game_id"] for g in all_games]
        byid = {g["game_id"]: g for g in all_games}

        if _HAS_HTTPX and verbose:
            print(f"  memfilter {len(candidate_ids)} laga, mengambil yang perlu refresh...", end=" ")

        pending = []
        skipped = 0
        for gid in candidate_ids:
            g = byid.get(gid)
            if not g:
                continue
            if not market_needs_refresh(gid, refresh_hours=1.5):
                skipped += 1
                continue
            pending.append((gid, g))

        if verbose:
            print(f"{len(pending)} perlu fetch, {skipped} fresh/lewat")

        if pending:
            match_urls = [(g["url"], f"match-{gid}.html", CACHE_TTL_MATCH)
                          for gid, g in pending]

            if _HAS_HTTPX:
                results = await_wrap(async_fetch_pages(match_urls))
            else:
                results = []
                for gid, g in pending:
                    html, cached = _sync_fetch(g["url"], f"match-{gid}.html", CACHE_TTL_MATCH)
                    results.append((html, cached))

            for (gid, g), (html, cached) in zip(pending, results):
                try:
                    if not isinstance(html, str):
                        print(f"  ! laga {gid}: html type={type(html).__name__}", file=sys.stderr)
                        continue
                    rows = parse_match_page(html, gid, g["url"])
                    n = save_markets(rows, captured)
                    nrows += n
                    if verbose:
                        tag = "cache" if cached else "net"
                        print(f"  [{nrows}/{len(pending)}] {g['home']} v {g['away']}: "
                              f"{len(rows)} harga, +{n} baru ({tag})")
                except Exception as e:
                    import traceback
                    print(f"  ! laga {gid}: {e}", file=sys.stderr)
                    print(f"    {traceback.format_exc().splitlines()[-1]}", file=sys.stderr)

        if verbose:
            print(f"  pasar lain: +{nrows} baris baru")

    return {"snapshots": tot_snap, "results": tot_res, "games": len(all_games),
            "markets": nrows}


RUN_LOG = os.path.join(DIR, "scrape_runs.csv")
_RUN_LOG_COLS = ("ts", "games", "snapshots", "results", "markets", "corner_rows")


def log_run_summary(r, corner_rows=0):
    """Append satu baris ringkasan run ke scrape_runs.csv (audit cron)."""
    try:
        ensure_dirs()
        new = not os.path.exists(RUN_LOG)
        with open(RUN_LOG, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=_RUN_LOG_COLS, extrasaction="ignore")
            if new:
                w.writeheader()
            w.writerow({
                "ts": now_iso(), "games": r.get("games", 0),
                "snapshots": r.get("snapshots", 0),
                "results": r.get("results", 0),
                "markets": r.get("markets", 0), "corner_rows": corner_rows,
            })
    except Exception as e:  # noqa: BLE001
        print(f"  ! log run gagal: {e!r}", file=sys.stderr)


def matched_ids():
    """game_id yang sudah dipasangkan dengan prediksi model (ta/model_markets.csv)."""
    path = os.path.join(DIR, "model_markets.csv")
    if not os.path.exists(path):
        return []
    seen = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gid = row.get("game_id")
            if gid and gid not in seen:
                seen.append(gid)
    return seen


def main(argv):
    today = date.today()
    days = []
    with_markets = "--markets" in argv
    only_matched = "--markets-matched" in argv
    fresh = "--fresh" in argv
    market_ids = None
    for a in argv[1:]:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", a):
            days.append(datetime.strptime(a, "%Y-%m-%d").date())
    for a in argv[1:]:
        m = re.match(r"^--window=(-?\d+):(-?\d+)$", a)
        if m:
            days = [today + timedelta(days=k)
                    for k in range(int(m.group(1)), int(m.group(2)) + 1)]
    if not days:
        days = [today - timedelta(days=1), today, today + timedelta(days=1)]
    if only_matched:
        with_markets = True
        market_ids = matched_ids()
        if not market_ids:
            print("ta/model_markets.csv kosong — jalankan dulu: "
                  "python ta_model.py --build", file=sys.stderr)
            return 2

    print(f"tipsterarea sync: {len(days)} tanggal "
          f"({iso(min(days))} .. {iso(max(days))})"
          + (" [FRESH]" if fresh else "")
          + (f", pasar lain untuk {len(market_ids)} laga model" if market_ids else ""))
    r = sync_dates(sorted(set(days)), with_markets=with_markets,
                   market_ids=market_ids, fresh=fresh)
    print(f"selesai: {r['games']} laga, snapshot +{r['snapshots']}, "
          f"hasil +{r['results']}")
    log_run_summary(r, corner_rows=0)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
