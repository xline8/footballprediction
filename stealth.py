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


def proxy_url() -> Optional[str]:
    """String URL proxy untuk httpx (http://user:pass@host:port), dari
    STEALTH_PROXY/HTTPS_PROXY/HTTP_PROXY. None bila tak ada.

    httpx >= 0.27 menerima string tunggal untuk param `proxy`; dict
    {scheme: url} memicu `'dict' object has no attribute 'url'`.
    """
    for key in ("STEALTH_PROXY", "HTTPS_PROXY", "HTTP_PROXY"):
        v = os.environ.get(key)
        if v:
            return v
    return None


BACKOFF_BASE = 2.0
BACKOFF_MAX = 30.0
RETRYABLE = {408, 425, 429, 500, 502, 503, 504}


def _retry_delay(headers: Optional[object], attempt: int) -> float:
    """Delay retry: hormati `Retry-After`, else exponential backoff."""
    ra = headers.get("Retry-After") if headers is not None else None
    if ra is not None:
        try:
            return float(ra)
        except ValueError:
            pass
    return min(BACKOFF_BASE * (2 ** attempt), BACKOFF_MAX)


def urlopen_with_retry(url: str, tries: int = 4, timeout: int = 40,
                       extra_headers: Optional[dict] = None,
                       referer: Optional[str] = None) -> tuple[bytes, object]:
    """GET urllib dgn rotasi UA, jitter, dan retry sadar-status.

    - 429 / 5xx -> retry + exponential backoff; hormati `Retry-After`.
    - 403 / 404 / 4xx lain -> hard-stop (tidak di-retry).
    - Gangguan jaringan/reset -> retry hingga `tries`.
    Return (bytes, headers-respon). Proxy env dipakai otomatis urllib.
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
        except urllib.error.HTTPError as e:
            code = e.code
            if code not in RETRYABLE:
                raise  # 403/404/dll permanen
            delay = _retry_delay(getattr(e, "headers", None), i)
            if delay > 0:
                time.sleep(delay)
            last = e
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(min(BACKOFF_BASE * (2 ** i), BACKOFF_MAX))
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
    assert p is None or isinstance(p, str)
    assert 429 in RETRYABLE and 403 not in RETRYABLE
    assert _retry_delay({"Retry-After": "5"}, 0) == 5.0
    assert 0 < _retry_delay(None, 0) <= BACKOFF_BASE
    print(f"stealth self-check OK ({len(seen)} UA berbeda)")


if __name__ == "__main__":
    _selfcheck()
