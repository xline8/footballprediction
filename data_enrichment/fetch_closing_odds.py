"""fetch_closing_odds.py — ekstraksi closing odds (Pinnacle/Max/Avg).

Catatan data: `all_matches_clean.csv` (sumber football-data.co.uk) sudah memuat
satu snapshot odds per match untuk berbagai bandar, termasuk **Pinnacle**
(PSH/PSD/PSA), Max, dan Avg. Tidak ada snapshot kedua (opening), jadi "odds
movement" murni tidak tersedia; modul ini mengekstrak kolom Pinnacle/Max/Avg
secara eksplisit utk dipakai sebagai proxy CLV lintas-bandar di fase lanjut.
"""

from __future__ import annotations

import csv
import os
from typing import Any

from .utils import setup_logging, to_float, norm_team

_log = setup_logging()

COL_PS_H, COL_PS_D, COL_PS_A = "PSH", "PSD", "PSA"
COL_MX_H, COL_AV_H = "MaxH", "AvgH"
COL_PSH = ("PSH", "PSD", "PSA")
COL_MX = ("MaxH", "MaxD", "MaxA")
COL_AV = ("AvgH", "AvgD", "AvgA")


def extract_closing_odds(csv_path: str) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Key (div, date_iso, home_norm, away_norm) -> dict odds Pinnacle/Max/Avg."""
    out: dict[tuple[str, str, str], dict[str, Any]] = {}
    if not os.path.exists(csv_path):
        _log.warning("csv tidak ada: %s", csv_path)
        return out
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            div = r.get("Div")
            date_iso = str(r.get("Date") or "")[:10]
            home, away = r.get("HomeTeam"), r.get("AwayTeam")
            if not (div and date_iso and home and away):
                continue
            key = (div, date_iso, norm_team(home), norm_team(away))
            out[key] = {
                "ps": tuple(to_float(r.get(c)) for c in COL_PSH),
                "mx": tuple(to_float(r.get(c)) for c in COL_MX),
                "av": tuple(to_float(r.get(c)) for c in COL_AV),
            }
    return out
