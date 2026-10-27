"""api_football_client.py — klien nyata API-Football v3 (menutup Gap 1 & 2).

Menggantikan MockCornerOddsClient di fetch_corner_odds.py. Tujuan:
- Ambil odds historis `Corners Over/Under` + `Both Teams To Score`.
- Proteksi kuota: cache raw JSON ke `raw/api_football_cache/` — tidak pernah
  re-fetch bila item sudah di-cache; pace <= 10 req/menit (free tier);
  hard-stop saat HTTP 429 atau `x-ratelimit-remaining == 0`.

Auth: kunci dibaca dari env `API_FOOTBALL_KEY`. Host default
`v3.football.api-sports.io` -> header `x-apisports-key`. Bila lewat RapidAPI,
set `API_FOOTBALL_HOST=v3.football.api-sports.io` -> header
`x-rapidapi-key` + `x-rapidapi-host`.

Market id TIDAK dikeraskan: di-resolve saat runtime lewat `GET /odds/markets`
cocokkan nama ("Corners Over/Under", "Both Teams To Score"). Ini lebih tahan
thd perubahan skema daripada menebak angka.

Penggunaan (dry-run satu tanggal, satu halaman):
  python -m data_enrichment.api_football_client --dry-run 2026-10-20
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .utils import norm_team

BASE = "https://v3.football.api-sports.io/"
DEFAULT_HOST = "v3.football.api-sports.io"
CACHE_DIR = Path(__file__).parent / "raw" / "api_football_cache"

MIN_INTERVAL = 6.0  # free tier <=10 req/menit -> minimal 6 dtk antar-request
DEFAULT_LEAGUE = 39  # Premier League
BOOKMAKER_PINNACLE = 8
CORNER_MARKET = "Corners Over Under"
BTTS_MARKET = "Both Teams Score"


def season_for_date(date_iso: str) -> int:
    """Musim API-Football utk tanggal: tahun mulai (>=Agustus) atau tahun-1."""
    y = int(date_iso[:4])
    return y if int(date_iso[5:7]) >= 8 else y - 1


class ApiError(RuntimeError):
    pass


class NoApiKey(ApiError):
    pass


class QuotaExceeded(ApiError):
    pass


def get_key() -> str:
    k = os.environ.get("API_FOOTBALL_KEY")
    if not k:
        raise NoApiKey(
            "API_FOOTBALL_KEY belum diset. Export dulu, mis.:\n"
            "  set API_FOOTBALL_KEY=xxx       (Windows PowerShell)\n"
            "  export API_FOOTBALL_KEY=xxx   (bash)")
    return k.strip()


class ApiFootballClient:
    def __init__(self, key: Optional[str] = None,
                 host: Optional[str] = None):
        self.key = key or get_key()
        self.host = host or os.environ.get("API_FOOTBALL_HOST", DEFAULT_HOST)
        self.base = BASE
        self.last_call = 0.0
        self._bets_cache: dict[str, Optional[list[dict]]] = {}

    # ---- transport --------------------------------------------------
    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if "rapidapi.com" in self.host:
            h["x-rapidapi-key"] = self.key
            h["x-rapidapi-host"] = self.host
        else:
            h["x-apisports-key"] = self.key
        return h

    def _pace(self) -> None:
        wait = MIN_INTERVAL - (time.monotonic() - self.last_call)
        if wait > 0:
            time.sleep(wait)

    def _http_once(self, url: str) -> tuple[bytes, dict[str, str]]:
        self._pace()
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=45) as r:
            self.last_call = time.monotonic()
            body = r.read()
            rh = {k.lower(): v for k, v in r.headers.items()}
            return body, rh

    # ---- cache ------------------------------------------------------
    def _cache_path(self, endpoint: str, params: dict) -> Path:
        q = urllib.parse.urlencode(
            sorted((k, str(v)) for k, v in params.items()))
        h = hashlib.sha1(f"{endpoint}?{q}".encode()).hexdigest()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return CACHE_DIR / f"{h}.json"

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        params = params or {}
        path = self._cache_path(endpoint, params)
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:  # cache rusak -> ambil ulang
                pass
        q = urllib.parse.urlencode(params)
        url = f"{self.base}{endpoint}?{q}" if q else f"{self.base}{endpoint}"
        body, rh = self._http_once(url)
        if rh.get("x-ratelimit-remaining") == "0":
            raise QuotaExceeded("x-ratelimit-remaining = 0 — kuota harian habis.")
        # 429 dicek setelah header, sebelum parse body
        status = rh.get("status") or "200"
        if status == "429":
            raise QuotaExceeded("HTTP 429 diterima — hard stop.")
        if status != "200":
            raise ApiError(f"HTTP {status} untuk {url}: {body[:300]!r}")
        data = json.loads(body.decode("utf-8"))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return data

    # ---- endpoints --------------------------------------------------
    def fetch_bets(self, search: Optional[str] = None,
                   force_refresh: bool = False) -> list[dict]:
        """GET /odds/bets[?search=...] -> [{id, name}, ...].

        Endpoint yang benar per dokumentasi v3 (`/odds/markets` TIDAK ada).
        Dicache per kata kunci; `force_refresh` memaksa tarik ulang.
        """
        key = f"bets:{search or '*'}"
        if not force_refresh and self._bets_cache.get(key) is not None:
            return self._bets_cache[key]
        params = {"search": search} if search else None
        data = self.get("odds/bets", params)
        bets = list(data.get("response") or [])
        self._bets_cache[key] = bets
        return bets

    def resolve_market_ids(self, force_refresh: bool = False
                           ) -> tuple[Optional[int], Optional[int]]:
        """Resolve bet id lewat /odds/bets?search= (cocokkan nama normalisasi).

        Corner: search "corner" -> bet "Corners Over Under".
        BTTS : search "both teams" -> bet "Both Teams Score".
        """
        corner = btts = None
        tgt_c = _norm_market(CORNER_MARKET)
        tgt_b = _norm_market(BTTS_MARKET)
        for b in self.fetch_bets(search="corner",
                                  force_refresh=force_refresh):
            if _norm_market(b.get("name", "")) == tgt_c:
                corner = b.get("id")
                break
        for b in self.fetch_bets(search="both teams",
                                  force_refresh=force_refresh):
            if _norm_market(b.get("name", "")) == tgt_b:
                btts = b.get("id")
                break
        return corner, btts

    def fetch_fixtures(self, *, league: Optional[int] = None,
                       season: Optional[int] = None,
                       date: Optional[str] = None,
                       page: int = 1) -> dict:
        params = {"page": page}
        if league is not None:
            params["league"] = league
        if season is not None:
            params["season"] = season
        if date is not None:
            params["date"] = date
        return self.get("fixtures", params)

    def fetch_odds_page(self, *, league: Optional[int] = None,
                        season: Optional[int] = None,
                        date: Optional[str] = None,
                        fixture: Optional[int] = None,
                        bookmaker: Optional[int] = None,
                        bet: Optional[int] = None,
                        page: int = 1) -> dict:
        params = {"page": page}
        if league is not None:
            params["league"] = league
        if season is not None:
            params["season"] = season
        if date is not None:
            params["date"] = date
        if fixture is not None:
            params["fixture"] = fixture
        if bookmaker is not None:
            params["bookmaker"] = bookmaker
        if bet is not None:
            params["bet"] = bet
        return self.get("odds", params)


# ---- parsing ---------------------------------------------------------
_RE_LINE = re.compile(r"(over|under)\s*([0-9]+(?:\.[0-9]+)?)", re.I)
_RE_NUM = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


def _norm_market(name: str) -> str:
    """'Corners Over/Under' & 'Corners Over Under' -> 'cornersoverunder'."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _group_ou(values: dict[str, str]) -> dict[float, dict[str, str]]:
    """'Over 9.5'/'Under 9.5' -> {9.5: {'over': odd, 'under': odd}}."""
    out: dict[float, dict[str, str]] = {}
    for label, odd in values.items():
        m = _RE_LINE.search(label)
        if m:
            line = float(m.group(2))
            out.setdefault(line, {})[m.group(1).lower()] = odd
    return out


def parse_odds(data: dict, corner_market: str = CORNER_MARKET,
               btts_market: str = BTTS_MARKET,
               teams: Optional[dict[int, tuple[str, str]]] = None,
               ) -> tuple[list[dict], list[dict]]:
    """Terjemah respons `GET /odds` -> (corner_rows, btts_rows).

    corner_rows: {date, home_team, away_team, corner_line, odds_over,
                  odds_under}
    btts_rows : {date, home_team, away_team, btts_yes, btts_no}
    `teams` = {fixture_id: (home_norm, away_norm)} dari /fixtures (opsional;
    bila kosong, baris tetap dibuat dgn team kosong — pemicu join lanjut).
    """
    corner_rows: list[dict] = []
    btts_rows: list[dict] = []
    for item in data.get("response", []):
        fx = item.get("fixture", {})
        fid = fx.get("id")
        date = str(fx.get("date", ""))[:10]
        home, away = teams.get(fid, ("", "")) if teams else ("", "")
        for bm in item.get("bookmakers", []):
            for bet in bm.get("bets", []):
                name = bet.get("name", "")
                values = {v.get("value", ""): v.get("odd", "")
                          for v in bet.get("values", [])}
                if corner_market and _norm_market(name) == _norm_market(corner_market):
                    for line, sides in _group_ou(values).items():
                        corner_rows.append({
                            "date": date, "home_team": home,
                            "away_team": away, "corner_line": line,
                            "odds_over": sides.get("over"),
                            "odds_under": sides.get("under"),
                        })
                if btts_market and _norm_market(name) == _norm_market(btts_market):
                    btts_rows.append({
                        "date": date, "home_team": home,
                        "away_team": away,
                        "btts_yes": values.get("Yes"),
                        "btts_no": values.get("No"),
                    })
    return corner_rows, btts_rows


def fixtures_teams_map(fix_data: dict) -> dict[int, tuple[str, str]]:
    """{fixture_id: (norm_team(home), norm_team(away))} dari /fixtures."""
    out: dict[int, tuple[str, str]] = {}
    for it in fix_data.get("response", []):
        fid = it.get("fixture", {}).get("id")
        t = it.get("teams", {})
        h = t.get("home", {}).get("name")
        a = t.get("away", {}).get("name")
        if fid and h and a:
            out[fid] = (norm_team(h), norm_team(a))
    return out


# ---- dry-run ---------------------------------------------------------
CSV_COLS = ("date", "home_team", "away_team", "corner_line", "odds_over",
            "odds_under", "btts_yes", "btts_no")


def dry_run(date: str, league: Optional[int] = None,
            season: Optional[int] = None,
            out_path: Optional[str] = None) -> int:
    """Ambil SATU halaman odds untuk satu tanggal; tulis sampel CSV.

    Quota aman: ~2-3 request (markets + fixtures + 1 halaman odds), semua
    di-cache. Tanpa kunci -> exit 2 tanpa sentuh API. League/season opsional:
    bila diisi, filter query; bila dikosongkan, ambil semua liga.
    """
    try:
        client = ApiFootballClient()
    except NoApiKey as e:
        print(f"! {e}")
        return 2

    if season is None and league is not None:
        season = season_for_date(date)

    print(f"resolve market ids ...")
    corner_mid, btts_mid = client.resolve_market_ids()
    print(f"  Corners Over/Under bet id : {corner_mid}")
    print(f"  Both Teams Score bet id    : {btts_mid}")

    print(f"fetch fixtures {date} (liga {league}, season {season}) ...")
    fix = client.fetch_fixtures(league=league, season=season, date=date)
    teams = fixtures_teams_map(fix)
    print(f"  {len(teams)} fixture dipetakan")

    print(f"fetch odds page 1 (bet={corner_mid or btts_mid}) ...")
    odds = client.fetch_odds_page(league=league, season=season, date=date,
                                  bet=corner_mid or btts_mid)
    corner_rows, btts_rows = parse_odds(odds, teams=teams)
    print(f"  parsed: {len(corner_rows)} rows corner, "
          f"{len(btts_rows)} rows BTTS")

    all_rows = corner_rows + btts_rows
    if not all_rows:
        print("! tidak ada baris odds untuk tanggal ini (cek tanggal/liga).")
        return 1
    out_path = out_path or str(Path(__file__).parent /
                               "sample_api_odds.csv")
    import csv
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)
    print(f"sample tersimpan -> {out_path}")
    for r in all_rows[:8]:
        print(" ", r)
    return 0


def _selfcheck() -> None:
    """Offline: validasi parser thd shape respons API (tanpa jaringan)."""
    sample = {
        "get": "odds",
        "results": 1,
        "response": [{
            "fixture": {"id": 1234, "date": "2026-10-20T20:00:00+00:00"},
            "league": {"id": 39, "name": "Premier League", "season": 2025},
            "bookmakers": [{
                "id": 8,
                "name": "Pinnacle",
                "bets": [
                    {"id": 99, "name": "Corners Over/Under", "values": [
                        {"value": "Over 9.5", "odd": "1.95"},
                        {"value": "Under 9.5", "odd": "1.85"},
                    ]},
                    {"id": 8, "name": "Both Teams Score", "values": [
                        {"value": "Yes", "odd": "1.90"},
                        {"value": "No", "odd": "1.90"},
                    ]},
                ],
            }],
        }],
    }
    teams = {1234: ("tottenham", "coventry city")}
    cr, br = parse_odds(sample, teams=teams)
    assert len(cr) == 1 and len(br) == 1, (len(cr), len(br))
    c = cr[0]
    assert c["home_team"] == "tottenham" and c["away_team"] == "coventry city"
    assert c["corner_line"] == 9.5
    assert c["odds_over"] == "1.95" and c["odds_under"] == "1.85"
    b = br[0]
    assert b["btts_yes"] == "1.90" and b["btts_no"] == "1.90"
    assert c["date"] == "2026-10-20"
    print("api_football_client self-check OK (parser + norm team)")


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--selfcheck" in argv:
        _selfcheck()
        return 0
    if "--dry-run" in argv:
        i = argv.index("--dry-run")
        date = argv[i + 1] if i + 1 < len(argv) else None
        if not date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            print("usage: python -m data_enrichment.api_football_client "
                  "--dry-run YYYY-MM-DD")
            return 2
        return dry_run(date)
    print("usage: python -m data_enrichment.api_football_client "
          "[--dry-run YYYY-MM-DD | --selfcheck]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
