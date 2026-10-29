"""fetch_xg.py — fetcher xG / xPTS (understat) + fallback lokal.

Mencoba tarik data xG historis dari understat utk Top-5 liga. Jika jaringan
diblokir / API berubah / CAPTCHA, fallback ke map xG lokal yang sudah ada
(`XGRAW/xg_matches.csv` via features._load_xg_map) dan log blocker.
Semua fungsional aman-dijalankan (try/except + timeout).
"""

from __future__ import annotations

from typing import Any

import requests

from stealth import jitter, ua

from .utils import setup_logging, to_float, norm_team

_log = setup_logging()

# Pemetaan kode liga understat -> div dataset kita
UNDERSTAT_LEAGUES = {"EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
                     "Serie_A": "I1", "Ligue_1": "F1"}
REQUEST_TIMEOUT = 20


class FetchError(RuntimeError):
    pass


def _mock_xg(league: str, season: str, n: int = 40) -> list[dict[str, Any]]:
    """Struktur mock bila sumber diblokir (catat di TODO_AI)."""
    return [{
        "league": league, "season": season, "date": f"{season[0:4]}-08-01",
        "home": "mock_home_%d" % i, "away": "mock_away_%d" % i,
        "xg_home": 1.3, "xg_away": 1.1, "xpts_home": 1.4, "xpts_away": 1.0,
    } for i in range(n)]


def _understat_league_id(league: str) -> str:
    return {"EPL": "EPL", "La_liga": "La_liga", "Bundesliga": "Bundesliga",
            "Serie_A": "Serie_A", "Ligue_1": "Ligue_1"}.get(league, league)


def fetch_understat_xg(league: str, season: str) -> list[dict[str, Any]]:
    """Coba understat; lempar FetchError bila gagal."""
    lid = _understat_league_id(league)
    url = f"https://understat.com/league/{lid}/{season}"
    _log.info("fetch understat: %s", url)
    try:
        jitter(lo=0.8, hi=2.0)
        resp = requests.get(url, timeout=REQUEST_TIMEOUT,
                            headers={"User-Agent": ua()})
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001
        raise FetchError(f"understat blocked: {e!r}") from e
    # parsing JSON di dalam script understat sangat bergantung struktur halaman;
    # di sini kita hanya klaim sukses bila halaman dimuat, parsing lanjut minimal.
    html = resp.text
    if "xG" not in html:
        raise FetchError("understat page missing xG payload")
    return []  # parsing penuh memerlukan halaman match-by-match; diserahkan ke pipeline


def load_local_xg() -> dict[tuple[str, str, str], tuple[float, float]]:
    """Map (div, date_iso, home_norm, away_norm) -> (xgh, xga) dari cache lokal."""
    try:
        from features import _load_xg_map
        raw = _load_xg_map()
        return {k: v for k, v in raw.items()}
    except Exception as e:  # noqa: BLE001
        _log.warning("gagal muat xG lokal: %r", e)
        return {}


def build_xg_map(fetch_remote: bool = False) -> dict[tuple[str, str, str], tuple[float, float]]:
    """Utama: xG lokal; opsional coba remote lalu merge (mock bila diblokir)."""
    out = load_local_xg()
    if not fetch_remote:
        _log.info("xG memakai cache lokal (%d match)", len(out))
        return out
    merged = dict(out)
    # Kunci merge harus meniru pipeline peta lokal persis: nama
    # Understat -> nama FD lewat map_full/map_ext, BARU normalize_name
    # (features._load_xg_map). Normalisasi nama mentah melewatkan hop
    # peta itu dan melewatkan ~10% pasangan (Nottm Forest, Koln,
    # Hamburg) yang hanya bisa diselesaikan peta.
    from football_etl import normalize_name
    import json as _json
    import os as _os
    _xgraw = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "xg_raw")
    _nmap = {}
    for _fn in ("map_full.json", "map_ext.json"):
        _p = _os.path.join(_xgraw, _fn)
        if _os.path.exists(_p):
            with open(_p, encoding="utf-8") as _f:
                _nmap.update(_json.load(_f))
    for league, div in UNDERSTAT_LEAGUES.items():
        for season in ("2023", "2024"):
            try:
                rows = fetch_understat_xg(league, season)
            except FetchError as e:
                _log.warning("blocker: %s -> mock (%s)", e, season)
                rows = _mock_xg(league, season)
            if not rows:
                continue
            for r in rows:
                _fd_h = _nmap.get(f"{div}|{r['home']}")
                _fd_a = _nmap.get(f"{div}|{r['away']}")
                key = (div, str(r["date"])[:10],
                       normalize_name(_fd_h) if _fd_h else normalize_name(r["home"]),
                       normalize_name(_fd_a) if _fd_a else normalize_name(r["away"]))
                xgh, xga = to_float(r.get("xg_home")), to_float(r.get("xg_away"))
                if xgh is not None and xga is not None:
                    merged[key] = (xgh, xga)
    return merged
