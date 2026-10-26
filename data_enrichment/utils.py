"""utils.py — shared helpers utk data_enrichment (normalisasi, fuzzy, logging)."""

from __future__ import annotations

import logging
import re
import unicodedata

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


def to_float(v: str | float | None) -> float | None:
    try:
        if v is None or v == "":
            return None
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None
