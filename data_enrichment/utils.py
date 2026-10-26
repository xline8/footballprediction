"""utils.py — shared helpers utk data_enrichment (normalisasi, fuzzy, logging)."""

from __future__ import annotations

import logging
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Iterable, Sequence

LOGGER_NAME = "data_enrichment"
_log = logging.getLogger(LOGGER_NAME)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    if not _log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(name)s [%(levelname)s] %(message)s"))
        _log.addHandler(h)
    _log.setLevel(level)
    return _log


# Alias nomor tim terkenal -> bentuk kanonik (dipakai setelah lower/clean)
ALIASES = {
    "man utd": "manchester united", "man united": "manchester united",
    "man u": "manchester united", "manchester utd": "manchester united",
    "man city": "manchester city", "man c": "manchester city",
    "spurs": "tottenham", "tottenham hotspur": "tottenham",
    "newcastle utd": "newcastle", "milan": "ac milan",
    "inter": "inter milan", "atalanta": "atalanta",
    "napoli": "napoli", "juventus": "juventus",
    "real madrid": "real madrid", "atletico": "atletico madrid",
    "atletico madrid": "atletico madrid", "athletic": "athletic bilbao",
    "barcelona": "barcelona", "sevilla": "sevilla",
    "bayern": "bayern munich", "bayern munchen": "bayern munich",
    "borussia dortmund": "dortmund", "leipzig": "rb leipzig",
    "leverkusen": "bayer leverkusen", "wolfsburg": "wolfsburg",
    "psg": "paris saint germain", "paris sg": "paris saint germain",
    "france": "france", "england": "england",
}


def clean_team(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore")\
        .decode("ascii").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm_team(name: str) -> str:
    """Normalisasi nama tim: bersihkan + alias kanonik."""
    c = clean_team(name)
    return ALIASES.get(c, c)


def lev_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def fuzzy_match(name: str, choices: Sequence[str], threshold: float = 0.86) -> str | None:
    """Cari kandidat terdekat dgn Levenshtein ratio; None jika di bawah ambang."""
    norm = norm_team(name)
    best, best_r = None, 0.0
    for ch in choices:
        r = lev_ratio(norm, norm_team(ch))
        if r > best_r:
            best_r, best = r, ch
    return best if best_r >= threshold else None


def to_float(v: str | float | None) -> float | None:
    try:
        if v is None or v == "":
            return None
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def safe_key(date_iso: str, home: str, away: str) -> tuple[str, str, str]:
    return (str(date_iso)[:10], norm_team(home), norm_team(away))


def ensure_iter(x: Iterable) -> list:
    return list(x)
