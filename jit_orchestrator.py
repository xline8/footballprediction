"""jit_orchestrator.py — JIT Hybrid Fallback & CLV capture.

Menjalankan tiap 30 menit (cron `*/30 * * * *`):

  1. Muat jadwal dari cache Understat (`xg_raw/{slug}_2026_fixtures.json`,
     di-refresh oleh refresh_fixtures.py).
  2. Filter laga yang mulai dalam 45 menit ke depan (JIT window).
  3. Tanpa laga -> log "No upcoming matches in the JIT window", exit 0.
  4. Punya laga -> gratis dulu: panggil ta_scrape (TipsterArea) utk 1X2,
     Over/Under, dst utk tanggal tsb.
  5. Fallback premium: ApiFootballClient hanya utk market yg scrape tak punya
     (Corners bet=45, BTTS bet=8), per liga dgn laga di window. Append dedup
     ke ta/external_corner_odds.csv & ta/external_btts_odds.csv.

Quota: API hanya dipanggil utk liga yang punya laga dalam window (bukan semua
liga). Semua raw JSON di-cache oleh klien. Jalankan:
  python jit_orchestrator.py              # live
  python jit_orchestrator.py --selfcheck  # offline window-logic
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from daily_api_capture import (
    BTTS_COLS, BTTS_KEY, BTTS_OUT, CORNER_COLS, CORNER_KEY, CORNER_OUT,
    LEAGUES, append_rows, load_env, load_keys,
)
from data_enrichment.api_football_client import (
    ApiFootballClient, fixtures_teams_map, parse_odds, season_for_date,
)
from data_enrichment.utils import norm_team

ROOT = Path(__file__).resolve().parent
JIT_MINUTES = 45

# slug file Understat -> div dataset
SLUG_DIV = {"EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
            "Serie_A": "I1", "Ligue_1": "F1"}


def _parse_dt(s: str) -> datetime:
    s = s.strip()
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"datetime tak dikenal: {s!r}")


def _local_naive(d: datetime) -> datetime:
    return d.astimezone().replace(tzinfo=None) if d.tzinfo is not None else d


def load_understat_fixtures() -> list[dict]:
    """Semua laga dari cache fixtures Understat -> {dt, home, away, div}."""
    out = []
    for slug, div in SLUG_DIV.items():
        p = ROOT / "xg_raw" / f"{slug}_2026_fixtures.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for m in data:
            h = norm_team(m.get("h", {}).get("title", ""))
            a = norm_team(m.get("a", {}).get("title", ""))
            dt = m.get("datetime")
            if dt and h and a:
                out.append({"dt": dt, "home": h, "away": a, "div": div})
    return out


def in_window(fixtures: list[dict], now: datetime | None = None,
              minutes: int = JIT_MINUTES) -> list[dict]:
    """Laga dgn kickoff di [now, now+minutes]. now default lokal, naive."""
    now = now or datetime.now().replace(microsecond=0)
    cutoff = now + timedelta(minutes=minutes)
    out = []
    for f in fixtures:
        try:
            k = _local_naive(_parse_dt(f["dt"]))
        except ValueError:
            continue
        if now <= k <= cutoff:
            g = dict(f)
            g["kickoff"] = k
            out.append(g)
    return out


def api_capture(matches: list[dict], client: ApiFootballClient | None = None,
                dry: bool = False) -> tuple[int, int]:
    """Fallback API premium utk laga dalam window. Return (corner, btts)."""
    if not matches:
        return 0, 0
    client = client or ApiFootballClient()
    corner_id, btts_id = client.resolve_market_ids()
    keys_c = load_keys(CORNER_OUT, CORNER_KEY)
    keys_b = load_keys(BTTS_OUT, BTTS_KEY)

    # kelompokkan per (liga, season, date)
    groups: dict[tuple, list[tuple[str, str]]] = defaultdict(list)
    for m in matches:
        lid = LEAGUES.get(m["div"])
        if not lid:
            continue
        date = m["kickoff"].date().isoformat()
        groups[(lid, season_for_date(date), date)].append((m["home"], m["away"]))

    total_c = total_b = 0
    for (lid, season, date), pairs in groups.items():
        if dry:
            print(f"  [dry] API league={lid} season={season} date={date} "
                  f"({len(pairs)} match)")
            continue
        fix = client.fetch_fixtures(league=lid, season=season, date=date)
        teams = fixtures_teams_map(fix)
        if not teams:
            print(f"  ! liga {lid}: /fixtures kosong — API premium dilewati "
                  f"(tak bisa atribusi team)")
            continue
        want = set(pairs)
        for bet, kind, cols, keycols, out, keys in (
                (corner_id, "corner", CORNER_COLS, CORNER_KEY, CORNER_OUT, keys_c),
                (btts_id, "btts", BTTS_COLS, BTTS_KEY, BTTS_OUT, keys_b)):
            if not bet:
                continue
            page = 1
            while True:
                od = client.fetch_odds_page(league=lid, season=season,
                                            date=date, bet=bet, page=page)
                cr, br = parse_odds(od, teams=teams)
                rows = cr if kind == "corner" else br
                rows = [r for r in rows
                        if (r["home_team"], r["away_team"]) in want]
                n = append_rows(out, cols, rows, keys, keycols)
                if kind == "corner":
                    total_c += n
                else:
                    total_b += n
                pg = od.get("paging") or {}
                if page >= int(pg.get("total") or 1):
                    break
                page += 1
    return total_c, total_b


def run(matches: list[dict], dry: bool = False) -> tuple[int, int]:
    """Scrape gratis (TipsterArea) lalu API fallback. Return (corner, btts)."""
    if not matches:
        print("No upcoming matches in the JIT window")
        return 0, 0
    print(f"JIT: {len(matches)} laga dlm window — scrape gratis dulu")
    dates = sorted({m["kickoff"].date() for m in matches})
    if not dry:
        try:
            import ta_scrape
            for d in dates:
                r = ta_scrape.sync_dates([d], with_markets=True, verbose=False)
                print(f"  scrape {d.isoformat()}: {r['games']} laga, "
                      f"+{r['markets']} pasar")
        except Exception as e:  # noqa: BLE001
            print(f"  ! scrape gagal (lanjut API fallback): {e!r}")
    return api_capture(matches, dry=dry)


def selfcheck() -> int:
    """Offline: validasi logika window (tanpa jaringan/API)."""
    now = datetime.now().replace(microsecond=0)
    fx = [
        {"dt": now.isoformat(), "home": "arsenal", "away": "chelsea",
         "div": "E0"},                                            # in window
        {"dt": (now + timedelta(minutes=10)).isoformat(),
         "home": "barcelona", "away": "real madrid", "div": "SP1"},  # in window
        {"dt": (now + timedelta(hours=3)).isoformat(),
         "home": "a", "away": "b", "div": "D1"},                  # outside
        {"dt": (now - timedelta(minutes=5)).isoformat(),
         "home": "c", "away": "d", "div": "I1"},                  # past
        {"dt": "bukan-datetime", "home": "e", "away": "f",
         "div": "F1"},                                            # invalid
    ]
    win = in_window(fx, now=now)
    assert len(win) == 2, win
    assert (win[0]["home"], win[0]["away"]) == ("arsenal", "chelsea")
    assert (win[1]["home"], win[1]["away"]) == ("barcelona", "real madrid")
    print("jit_orchestrator self-check OK (window logic)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--selfcheck" in argv:
        return selfcheck()
    dry = "--dry-run" in argv
    load_env()
    fixtures = load_understat_fixtures()
    matches = in_window(fixtures)
    tc, tb = run(matches, dry=dry)
    print(f"TOTAL: +{tc} corner, +{tb} btts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
