"""fetch_corner_odds.py — ingestion scaffolding untuk odds Corners (Phase 16).

Proyek sementara terblokir oleh tidak adanya odds historis Corners (blocker
T10). Modul ini menyiapkan pipa pemasukan data agar begitu sumber odds
(API-Football / Sportmonks / dump CSV eksternal) tersedia, backtest Phase 15
dapat langsung dieksekusi.

Dua jalur:
  1. parse_corner_odds_csv — baca file eksternal `external_corner_odds.csv`
     (kolom: date, home_team, away_team, corner_line, odds_over, odds_under;
     optional `div`). Tangani baris kosong/NaN dgn to_float.
  2. merge_to_records — left-join ke records (records_cache.jsonl) memakai
     key (div, date, home_norm, away_norm), fallback (date, home_norm,
     away_norm) bila tidak ada div.
+ MockCornerOddsClient — placeholder klien API (belum diimplementasikan
hingga kunci API tersedia).
"""

from __future__ import annotations

import csv
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from .utils import norm_team, to_float

CSV_COLS = ("date", "home_team", "away_team", "corner_line",
            "odds_over", "odds_under")


@dataclass
class CornerOddsRow:
    """Satu baris odds corner O/U pada satu line.

    `line` = total corners line (mis. 9.5); over/under = odds desimal (None
    bila tidak tersedia pada sumber).
    """
    date: str
    home: str
    away: str
    line: float
    odds_over: Optional[float]
    odds_under: Optional[float]
    div: Optional[str] = None


def parse_corner_odds_csv(path: str | Path) -> tuple[list[CornerOddsRow], int]:
    """Baca external_corner_odds.csv -> (rows, skipped).

    Baris tanpa date/teams/line valid dibuang dan dihitung sbg `skipped`.
    """
    rows: list[CornerOddsRow] = []
    skipped = 0
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            d = (r.get("date") or "")[:10]
            h = norm_team(r.get("home_team") or "")
            a = norm_team(r.get("away_team") or "")
            line = to_float(r.get("corner_line"))
            if not (d and h and a and line is not None):
                skipped += 1
                continue
            rows.append(CornerOddsRow(
                date=d, home=h, away=a, line=line,
                odds_over=to_float(r.get("odds_over")),
                odds_under=to_float(r.get("odds_under")),
                div=(r.get("div") or "").strip() or None,
            ))
    return rows, skipped


class MockCornerOddsClient:
    """Placeholder klien API odds (API-Football / Sportmonks).

    Ganti dengan implementasi nyata saat kunci API tersedia; pertahankan
    signature supaya pemanggil tidak berubah.
    """

    def __init__(self, lines: Sequence[float] = (9.5, 10.5, 11.5)):
        self.lines = list(lines)

    def fetch_odds(self, league: Optional[str] = None) -> list[CornerOddsRow]:
        """Mock: kembalikan sampel kecil; jangan dipakai untuk produksi."""
        return [
            CornerOddsRow(date="2026-04-15", home="manchester city",
                          away="liverpool", line=9.5,
                          odds_over=1.90, odds_under=1.90, div=league),
        ]


def _key(row: CornerOddsRow) -> tuple:
    return (row.div, row.date, row.home, row.away) if row.div \
        else (row.date, row.home, row.away)


def build_index(rows: Sequence[CornerOddsRow]) -> dict[tuple, list[CornerOddsRow]]:
    idx: dict[tuple, list[CornerOddsRow]] = {}
    for row in rows:
        idx.setdefault(_key(row), []).append(row)
    return idx


def merge_to_records(records: list[dict], rows: Sequence[CornerOddsRow]) -> int:
    """Left-join odds corner ke records; tambah kunci `corner_odds`.

    Return: jumlah record yang berhasil di-join. Records tanpa data dibiarkan
    apa adanya (graceful). `corner_odds` = list {line, over, under} terurut.
    """
    idx = build_index(rows)
    joined = 0
    for rec in records:
        d, h, a = rec.get("date"), norm_team(rec.get("home")), norm_team(rec.get("away"))
        if not (d and h and a):
            continue
        matches = idx.get((rec.get("div"), d, h, a)) or idx.get((d, h, a))
        if not matches:
            continue
        rec["corner_odds"] = [
            {"line": m.line, "over": m.odds_over, "under": m.odds_under}
            for m in sorted(matches, key=lambda m: m.line)
        ]
        joined += 1
    return joined


def _selfcheck() -> None:
    """Self-check: parse + merge pada CSV sementara."""
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        f.write("date,home_team,away_team,corner_line,odds_over,odds_under\n")
        f.write("2026-04-15,Man City,Liverpool,9.5,1.90,1.90\n")
        f.write("2026-04-15,Man City,Liverpool,10.5,2.05,1.80\n")
        f.write("2026-04-15,,,9.5,1.90,1.90\n")  # invalid -> skipped
        path = f.name
    rows, skipped = parse_corner_odds_csv(path)
    assert skipped == 1, skipped
    assert len(rows) == 2 and rows[0].line == 9.5
    records = [{"div": "E0", "date": "2026-04-15", "home": "Man City",
                "away": "Liverpool", "yi": 0}]
    joined = merge_to_records(records, rows)
    assert joined == 1 and len(records[0]["corner_odds"]) == 2
    assert records[0]["corner_odds"][0]["line"] == 9.5
    print("fetch_corner_odds self-check OK:", joined, "joined,", skipped, "skipped")


if __name__ == "__main__":
    _selfcheck()
