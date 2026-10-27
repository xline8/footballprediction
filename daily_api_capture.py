"""daily_api_capture.py — Organic Data Collection Mode (Gap 1 & 2).

Setiap hari, ambil fixture + odds *hari ini* untuk Top-5 liga dari
API-Football v3 (klien `data_enrichment.api_football_client`), ekstrak
Corners Over/Under & Both Teams Score, lalu append ke:
  - ta/external_corner_odds.csv  (date, home_team, away_team, corner_line,
                                    odds_over, odds_under)
  - ta/external_btts_odds.csv    (date, home_team, away_team, btts_yes,
                                    btts_no)
Deduplikasi berdasarkan (date, home, away[, corner_line]) — aman dijalankan
berulang. Dengan berjalannya waktu, ini mengakumulasi data historis organik.

Kuota: ~3 request per liga (fixtures + odds corners + odds BTTS) = ~15/hari;
semua di-cache oleh klien. Jangan ubah ini menjadi loop historis di tier
gratis (odds historis tidak disediakan).

Jalankan:
  python daily_api_capture.py            # untuk tanggal hari ini
  python daily_api_capture.py 2026-10-24
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import date as _date
from pathlib import Path
from typing import Optional

from data_enrichment.api_football_client import (
    ApiFootballClient, BTTS_MARKET, CORNER_MARKET,
    fixtures_teams_map, parse_odds, season_for_date,
)

ROOT = Path(__file__).resolve().parent
CORNER_OUT = ROOT / "ta" / "external_corner_odds.csv"
BTTS_OUT = ROOT / "ta" / "external_btts_odds.csv"
CORNER_COLS = ("date", "home_team", "away_team", "corner_line",
               "odds_over", "odds_under")
BTTS_COLS = ("date", "home_team", "away_team", "btts_yes", "btts_no")
CORNER_KEY = ("date", "home_team", "away_team", "corner_line")
BTTS_KEY = ("date", "home_team", "away_team")

# div dataset -> league id API-Football (Top-5 Eropa)
LEAGUES = {"E0": 39, "D1": 78, "I1": 135, "SP1": 140, "F1": 61}


def load_env() -> None:
    """Muat .env (gaya `export KEY=val`) ke os.environ bila belum diset."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export "):]
        if "=" in s:
            k, v = s.split("=", 1)
            k = k.strip()
            if k and k not in os.environ:
                os.environ[k] = v.strip().strip("\"").strip("'")


def load_keys(path: Path, cols: tuple) -> set[tuple]:
    """Baca kunci dedup yang sudah ada -> set tuple (dari kolom dedup)."""
    if not path.exists():
        return set()
    keys = set()
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            keys.add(tuple((r.get(c) or "").strip() for c in cols))
    return keys


def append_rows(path: Path, cols: tuple, rows: list[dict],
               keys: set[tuple], keycols: tuple) -> int:
    """Append baris baru yg belum ada; update set keys. Return jumlah ditulis."""
    if not rows:
        return 0
    def k(row: dict) -> tuple:
        # nilai baca CSV = str; nilai in-memory bisa float (corner_line)
        return tuple(str(row.get(c) or "").strip() for c in keycols)
    new = [r for r in rows if k(r) not in keys]
    if not new:
        return 0
    write_header = not path.exists() or path.stat().st_size == 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if write_header:
            w.writeheader()
        for r in new:
            w.writerow(r)
            keys.add(k(r))
    return len(new)


def run_daily_capture(date: Optional[str] = None) -> dict:
    date = date or _date.today().isoformat()
    season = season_for_date(date)
    client = ApiFootballClient()
    corner_id, btts_id = client.resolve_market_ids()
    print(f"bet ids: corners={corner_id} btts={btts_id}")

    keys_c = load_keys(CORNER_OUT, CORNER_KEY)
    keys_b = load_keys(BTTS_OUT, BTTS_KEY)
    total_c = total_b = 0
    per_league = {}

    for div, lid in LEAGUES.items():
        fix = client.fetch_fixtures(league=lid, season=season, date=date)
        teams = fixtures_teams_map(fix)
        if not teams:
            print(f"[{div}] tanpa fixture {date} — dilewati")
            per_league[div] = (0, 0)
            continue

        n_c = n_b = 0
        for bet, kind in ((corner_id, "corner"), (btts_id, "btts")):
            if not bet:
                continue
            page = 1
            while True:
                od = client.fetch_odds_page(league=lid, season=season,
                                            date=date, bet=bet, page=page)
                cr, br = parse_odds(od, teams=teams)
                if kind == "corner" and cr:
                    n_c += append_rows(CORNER_OUT, CORNER_COLS, cr,
                                       keys_c, CORNER_KEY)
                if kind == "btts" and br:
                    n_b += append_rows(BTTS_OUT, BTTS_COLS, br,
                                       keys_b, BTTS_KEY)
                pg = od.get("paging") or {}
                if page >= int(pg.get("total") or 1):
                    break
                page += 1
        print(f"[{div}] +{n_c} corner, +{n_b} btts")
        total_c += n_c
        total_b += n_b
        per_league[div] = (n_c, n_b)

    print(f"TOTAL: +{total_c} corner rows, +{total_b} btts rows")
    return {"date": date, "season": season, "corner": total_c,
            "btts": total_b, "per_league": per_league}


def _selfcheck() -> None:
    """Offline: validasi dedup + append (tanpa jaringan)."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     encoding="utf-8") as f:
        path = Path(f.name)
    keys = load_keys(path, CORNER_KEY)
    rows = [
        {"date": "2026-10-24", "home_team": "arsenal", "away_team": "chelsea",
         "corner_line": 9.5, "odds_over": "1.95", "odds_under": "1.85"},
        {"date": "2026-10-24", "home_team": "arsenal", "away_team": "chelsea",
         "corner_line": 10.5, "odds_over": "2.05", "odds_under": "1.80"},
    ]
    assert append_rows(path, CORNER_COLS, rows, keys, CORNER_KEY) == 2
    assert append_rows(path, CORNER_COLS, rows, keys, CORNER_KEY) == 0
    keys2 = load_keys(path, CORNER_KEY)
    assert len(keys2) == 2
    path.unlink(missing_ok=True)
    print("daily_api_capture self-check OK (dedup + append)")


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--selfcheck" in argv:
        _selfcheck()
        return 0
    load_env()
    date = argv[0] if argv and not argv[0].startswith("-") else None
    if date and not _date.fromisoformat(date):
        print("usage: python daily_api_capture.py [YYYY-MM-DD]")
        return 2
    run_daily_capture(date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
