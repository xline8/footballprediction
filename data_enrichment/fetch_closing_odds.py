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

# Kolom CLOSING football-data.co.uk (akhiran C), sesuai konvensi repo
# (model_v2 / football_etl: PSC*/AvgC*/B365C* = closing). Versi lama
# membaca kolom OPENING (PSH/MaxH/AvgH) dan melabelinya closing,
# sehingga setiap pembacaan CLV dari file enriched terbalik.
COL_PS_H, COL_PS_D, COL_PS_A = "PPCH", "PPCD", "PPCA"
COL_MX_H, COL_AV_H = "MaxCH", "AvgCH"
# football-data mengganti nama kolom Pinnacle PSC* -> PPC* di file
# 2627; baris musim lama hanya punya PSC*. Ambil per baris: PPC dulu.
COL_PSH = ("PSCH", "PSCD", "PSCA")
COL_PP = ("PPCH", "PPCD", "PPCA")
COL_MX = ("MaxCH", "MaxCD", "MaxCA")
COL_AV = ("AvgCH", "AvgCD", "AvgCA")


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
                "ps": tuple(to_float(r.get(pp) or r.get(ps))
                            for pp, ps in zip(COL_PP, COL_PSH)),
                "mx": tuple(to_float(r.get(c)) for c in COL_MX),
                "av": tuple(to_float(r.get(c)) for c in COL_AV),
            }
    return out
