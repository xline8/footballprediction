"""stealth.py — lapisan anti-bot bersama: rotasi User-Agent, jitter acak,
dan dukungan proxy dari lingkungan. Dipakai oleh download.py,
refresh_fixtures.py, fetch_xg.py, dan ta_scrape.py.

Prinsip: satu sumber kebenaran untuk header HTTP dan tidur antar-request,
supaya semua scraper punya jejak yang sopan dan tidak seragam.
"""

from __future__ import annotations

import os
import random
import time
from typing import Optional

UA_POOL = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 "
    "Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 "
    "Firefox/127.0",
)

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,"
              "*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip",
}


def ua() -> str:
    """Satu User-Agent acak dari kolam."""
    return random.choice(UA_POOL)


def headers(extra: Optional[dict] = None, referer: Optional[str] = None) -> dict:
    """Header dasar + UA rotasi + tambahan opsional."""
    h = dict(BASE_HEADERS)
    h["User-Agent"] = ua()
    if referer:
        h["Referer"] = referer
    if extra:
        h.update(extra)
    return h


def jitter(lo: float = 1.2, hi: float = 3.0) -> None:
    """Tidur acak antar-request (sopan, pola tidak seragam). lo<=0 => no-op."""
    if lo > 0:
        time.sleep(random.uniform(lo, hi))


def proxy_url() -> Optional[dict]:
    """Dict {scheme: url} untuk httpx, dari STEALTH_PROXY/HTTPS_PROXY/
    HTTP_PROXY. None bila tak ada."""
    for key in ("STEALTH_PROXY", "HTTPS_PROXY", "HTTP_PROXY"):
        v = os.environ.get(key)
        if v:
            scheme = "https" if "https" in key.lower() else "http"
            return {"https": v, "http": v}
    return None


def urlopen_with_retry(url: str, tries: int = 4, timeout: int = 40,
                       extra_headers: Optional[dict] = None,
                       referer: Optional[str] = None) -> tuple[bytes, object]:
    """GET urllib dgn rotasi UA, jitter antar-percobaan, dan backoff acak.

    Semantik sama seperti download.get lama: HTTPError (404 dst) langsung
    dilempar tanpa retry; gangguan jaringan/reset di-retry hingga `tries`.
    Return (bytes, headers-respon). Proxy env dipakai otomatis oleh
    urllib.request.urlopen.
    """
    import ssl
    import urllib.error
    import urllib.request

    ctx = ssl.create_default_context()
    if os.environ.get("FOOTBALL_DATA_NO_VERIFY") == "1":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    last: Optional[Exception] = None
    for i in range(tries):
        if i:
            jitter(lo=1.0, hi=2.0 * i + 1.0)
        req = urllib.request.Request(url, headers=headers(extra_headers, referer))
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read(), r.headers
        except urllib.error.HTTPError:
            raise
        except Exception as e:  # noqa: BLE001
            last = e
    assert last is not None
    raise last


def _selfcheck() -> None:
    """Self-check: rotasi, header, jitter singkat, proxy env."""
    seen = {ua() for _ in range(200)}
    assert len(seen) >= 2, f"UA tidak berotasi: {seen}"
    h = headers(referer="https://example.com/")
    assert h["User-Agent"] in UA_POOL
    assert h["Referer"] == "https://example.com/"
    t0 = time.time()
    jitter(lo=0.001, hi=0.002)
    assert time.time() - t0 < 1.0
    p = proxy_url()
    assert p is None or isinstance(p, dict)
    print(f"stealth self-check OK ({len(seen)} UA berbeda)")


if __name__ == "__main__":
    _selfcheck()
