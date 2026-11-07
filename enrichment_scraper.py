"""Ambil snapshot enrichment FotMob/SofaScore secara hemat dan point-in-time.

Penggunaan:
    python enrichment_scraper.py --date 2026-11-05
    python enrichment_scraper.py --date 2026-11-05 --source ta/fixtures.csv

Output mentah immutable disimpan di data_enrichment/raw/provider/date/match_id/.
Endpoint yang dipakai adalah endpoint web internal, bukan API publik berlisensi.
Collector ini sengaja berurutan, memakai jeda, menghormati Retry-After, dan berhenti
pada 403/429. Proxy rotasi/free-proxy tidak didukung; proxy milik sendiri dapat
dipasang lewat HTTPS_PROXY/HTTP_PROXY yang otomatis dibaca httpx.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import httpx

from data_enrichment.utils import norm_team
from stealth import BACKOFF_MAX, RETRYABLE, _retry_delay

BASE = Path(__file__).resolve().parent
DEFAULT_SOURCE = BASE / "predictions_upcoming.csv"
DEFAULT_OUT = BASE / "data_enrichment" / "raw" / "match_enrichment"
USER_AGENT = os.environ.get(
    "FOOTBALL_ENRICHMENT_USER_AGENT",
    "football-data-personal-research/1.0",
)


class RateLimited(RuntimeError):
    pass


class Fetcher:
    def __init__(self, delay: float = 3.0, timeout: float = 30.0,
                 tries: int = 3, max_retry_after: float = 120.0):
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.tries = max(1, tries)
        self.max_retry_after = max(0.0, max_retry_after)
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            trust_env=True,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        self._last_request = 0.0

    def close(self) -> None:
        self.client.close()

    def _pace(self) -> None:
        wait = self.delay - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)

    def get_json(self, url: str, params: dict | None = None,
                 optional: bool = False) -> Any:
        last: Exception | None = None
        for attempt in range(self.tries):
            self._pace()
            try:
                response = self.client.get(url, params=params)
                self._last_request = time.monotonic()
                if response.status_code == 404 and optional:
                    return None
                if response.status_code in (401, 403):
                    raise PermissionError(f"HTTP {response.status_code}: {url}")
                if response.status_code == 429:
                    delay = _retry_delay(response.headers, attempt)
                    if attempt + 1 >= self.tries or delay > self.max_retry_after:
                        raise RateLimited(
                            f"HTTP 429: hentikan provider; Retry-After={delay:g}s")
                    time.sleep(delay)
                    continue
                if response.status_code in RETRYABLE:
                    last = httpx.HTTPStatusError(
                        f"HTTP {response.status_code}", request=response.request,
                        response=response)
                    if attempt + 1 < self.tries:
                        time.sleep(min(_retry_delay(response.headers, attempt),
                                       BACKOFF_MAX))
                        continue
                response.raise_for_status()
                return response.json()
            except (PermissionError, RateLimited):
                raise
            except (httpx.HTTPError, ValueError) as exc:
                last = exc
                if attempt + 1 < self.tries:
                    time.sleep(min(2 ** attempt, BACKOFF_MAX))
        raise last or RuntimeError(f"GET gagal: {url}")


def _iso_utc(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _fotmob_candidates(payload: dict) -> list[dict]:
    out = []
    for league in payload.get("leagues") or []:
        for match in league.get("matches") or []:
            home, away = match.get("home") or {}, match.get("away") or {}
            status = match.get("status") or {}
            out.append({
                "id": str(match.get("id") or ""),
                "home": home.get("longName") or home.get("name") or "",
                "away": away.get("longName") or away.get("name") or "",
                "kickoff": _iso_utc(status.get("utcTime")),
                "summary": match,
            })
    return [row for row in out if row["id"] and row["home"] and row["away"]]


def _sofascore_candidates(payload: dict) -> list[dict]:
    out = []
    for event in payload.get("events") or []:
        home, away = event.get("homeTeam") or {}, event.get("awayTeam") or {}
        out.append({
            "id": str(event.get("id") or ""),
            "home": home.get("name") or "",
            "away": away.get("name") or "",
            "kickoff": _iso_utc(event.get("startTimestamp")),
            "summary": event,
        })
    return [row for row in out if row["id"] and row["home"] and row["away"]]


def _similar(a: str, b: str) -> float:
    na, nb = norm_team(a), norm_team(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ta, tb = set(na.split()), set(nb.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return 0.96
    return SequenceMatcher(None, na, nb).ratio()


def match_candidate(fixture: dict, candidates: list[dict],
                    threshold: float = 0.82) -> tuple[dict | None, float]:
    best, score = None, 0.0
    for candidate in candidates:
        current = (_similar(fixture["home"], candidate["home"]) +
                   _similar(fixture["away"], candidate["away"])) / 2
        if current > score:
            best, score = candidate, current
    return (best, score) if score >= threshold else (None, score)


def load_fixtures(path: Path, start: date, days: int) -> list[dict]:
    wanted = {(start + timedelta(days=i)).isoformat() for i in range(days)}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle)
                if row.get("date") in wanted and row.get("home") and row.get("away")]
    seen, out = set(), []
    for row in rows:
        key = (row["date"], norm_team(row["home"]), norm_team(row["away"]))
        if key not in seen:
            seen.add(key)
            out.append({"date": row["date"], "time": row.get("time", ""),
                        "home": row["home"], "away": row["away"],
                        "div": row.get("div", ""), "source_row": row})
    return out


def _atomic_snapshot(out_dir: Path, provider: str, fixture: dict,
                     candidate: dict, data: dict) -> Path:
    captured = datetime.now(timezone.utc)
    folder = out_dir / provider / fixture["date"] / candidate["id"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{captured.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    envelope = {
        "provider": provider,
        "provider_match_id": candidate["id"],
        "captured_at": captured.isoformat(),
        "kickoff_at": candidate.get("kickoff"),
        "fixture": {k: fixture.get(k) for k in ("div", "date", "time", "home", "away")},
        "provider_teams": {"home": candidate["home"], "away": candidate["away"]},
        "data": data,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(envelope, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    os.replace(tmp, path)
    return path


def _schedule(fetcher: Fetcher, provider: str, day: str) -> list[dict]:
    if provider == "fotmob":
        payload = fetcher.get_json(
            "https://www.fotmob.com/api/data/matches",
            {"date": day.replace("-", "")})
        return _fotmob_candidates(payload)
    payload = fetcher.get_json(
        f"https://www.sofascore.com/api/v1/sport/football/scheduled-events/{day}")
    return _sofascore_candidates(payload)


def _details(fetcher: Fetcher, provider: str, match_id: str) -> dict:
    if provider == "fotmob":
        return {"matchDetails": fetcher.get_json(
            "https://www.fotmob.com/api/data/matchDetails", {"matchId": match_id})}
    base = f"https://www.sofascore.com/api/v1/event/{match_id}"
    out = {}
    for name in ("lineups", "missing-players", "statistics", "shotmap", "incidents"):
        value = fetcher.get_json(f"{base}/{name}", optional=True)
        if value is not None:
            out[name] = value
    return out


def collect(fixtures: list[dict], providers: list[str], out_dir: Path,
            fetcher: Fetcher, threshold: float = 0.82) -> dict:
    result = {"saved": 0, "unmatched": [], "errors": [], "stopped": []}
    by_day = {}
    for fixture in fixtures:
        by_day.setdefault(fixture["date"], []).append(fixture)
    for provider in providers:
        stopped = False
        for day, day_fixtures in sorted(by_day.items()):
            try:
                candidates = _schedule(fetcher, provider, day)
            except (RateLimited, PermissionError) as exc:
                result["stopped"].append(f"{provider}: {exc}")
                stopped = True
                break
            except Exception as exc:  # satu provider/date gagal, lanjut provider lain
                result["errors"].append(f"{provider} {day}: {exc!r}")
                continue
            for fixture in day_fixtures:
                candidate, score = match_candidate(fixture, candidates, threshold)
                if candidate is None:
                    result["unmatched"].append(
                        f"{provider} {day} {fixture['home']} v {fixture['away']} ({score:.2f})")
                    continue
                try:
                    data = {"schedule": candidate["summary"],
                            **_details(fetcher, provider, candidate["id"])}
                    path = _atomic_snapshot(out_dir, provider, fixture, candidate, data)
                    print(f"OK {provider}: {fixture['home']} v {fixture['away']} -> {path}")
                    result["saved"] += 1
                except (RateLimited, PermissionError) as exc:
                    result["stopped"].append(f"{provider}: {exc}")
                    stopped = True
                    break
                except Exception as exc:
                    result["errors"].append(
                        f"{provider} {fixture['home']} v {fixture['away']}: {exc!r}")
            if stopped:
                break
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--providers", nargs="+", choices=("fotmob", "sofascore"),
                        default=("fotmob", "sofascore"))
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--threshold", type=float, default=0.82)
    args = parser.parse_args(argv)
    if args.days < 1 or args.delay < 0 or not 0 <= args.threshold <= 1:
        parser.error("days>=1, delay>=0, dan threshold 0..1 wajib")
    start = date.fromisoformat(args.date)
    if not args.source.exists():
        parser.error(f"source tidak ada: {args.source}")
    fixtures = load_fixtures(args.source, start, args.days)
    if not fixtures:
        print("Tidak ada fixture dalam rentang tanggal.")
        return 0
    fetcher = Fetcher(delay=args.delay)
    try:
        result = collect(fixtures, list(args.providers), args.out, fetcher,
                         args.threshold)
    finally:
        fetcher.close()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] or result["stopped"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
