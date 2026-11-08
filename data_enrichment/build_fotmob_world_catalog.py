"""Build the FotMob world catalog: top senior leagues of every country.

Source of truth is FotMob's own league listing (api/data/allLeagues:
94 countries, ~430 competitions, each country list ordered the way
FotMob presents them — top division first). The selection rule:

  * walk each country's list in FotMob's order;
  * skip competitions that are not standing league tiers by name
    (cups and super cups in any of the listing's languages,
    Qualification / playoff mini-tables, youth and novelty leagues);
  * confirm the candidate's details payload: gender must not be
    female for the general rule;
  * take the first three survivors as the country's tiers 1-3.

User-named leagues are always selected on top of that rule:
Argentina 112 / 8965 / 9213 (id 9213 is FotMob's combined
"Primera B Metropolitana & Torneo Federal A" entry, so the four named
Argentinian competitions live in three ids), Armenia 118,
Australia 113 + 9495 (A-League Women, named), Austria 38 + 119,
Azerbaijan 262, Bangladesh 10443. Japan's J1/J2/J3 (223/8974/9136)
are marked already_pulled — they live in fotmob_jleague/ and are
never re-pulled.

For every selected league the seasons from 2021 onward are recorded
from the payload's allAvailableSeasons (the season's own FotMob
label; kept when the label's first year is >= 2021).

Output: data_enrichment/fotmob_world_catalog.csv — one row per
LISTED competition (selected or not, with the reason), so the
selection is auditable.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx  # noqa: E402

from backfill_sot_fotmob import HEADERS  # noqa: E402

API = "https://www.fotmob.com/api/data"
OUT = BASE / "data_enrichment" / "fotmob_world_catalog.csv"

NAMED = {("ARG", 112), ("ARG", 8965), ("ARG", 9213), ("ARM", 118),
         ("AUS", 113), ("AUS", 9495), ("AUT", 38), ("AUT", 119),
         ("AZE", 262), ("BAN", 10443)}
ALREADY_PULLED = {("JPN", 223), ("JPN", 8974), ("JPN", 9136)}

# Patterns are matched against the ASCII-folded league name.
EXCLUDE_PATTERNS = [
    (re.compile(r"\bcup\b|copa|coppa|cupa|pokal|coupe|trofeo|trophy|"
                r"shield|kupa|kubok|taca|beker|\bkup\b|pohar|puchar|"
                r"karikas|kauss|kypello|bikar|campeon de campeones", re.I),
     "cup-like name"),
    (re.compile(r"super\s?(cup|kupa|copa|taca)|supercopa|superkupa",
                re.I), "super cup"),
    (re.compile(r"recopa", re.I), "recopa"),
    (re.compile(r"qualification|play[\s-]?off", re.I), "qualification/playoff"),
    (re.compile(r"\bu\s?1[6-9]\b|\bu\s?2[0-3]\b|premier league 2", re.I),
     "youth league"),
    (re.compile(r"baller", re.I), "novelty league"),
]
# Competitions that are cups despite a league-sounding name.
HARDCODED_CUPS = {("CAN", 9837)}  # Canadian Championship = Voyageurs Cup
FEMALE_NAME = re.compile(
    r"women|\(women\)|femenina|feminina|femminile|frauen|damer|kvinner|"
    r"női|ženy|femenino", re.I)

_thread_local = threading.local()


def _client() -> httpx.Client:
    client = getattr(_thread_local, "client", None)
    if client is None:
        from stealth import proxy_url
        client = httpx.Client(headers=HEADERS, timeout=60,
                              follow_redirects=True, proxy=proxy_url())
        _thread_local.client = client
    return client


def fetch_details(league_id: int, ccode: str) -> dict | None:
    """League payload (no season) or None after retries; {} if the
    provider answers with an empty/null payload (dead entry)."""
    for attempt in range(3):
        try:
            resp = _client().get(f"{API}/leagues",
                                 params={"id": league_id, "ccode3": ccode})
            if resp.status_code in (401, 403, 429):
                raise RuntimeError(f"provider stopped: HTTP "
                                   f"{resp.status_code}")
            resp.raise_for_status()
            payload = resp.json()
            return payload if isinstance(payload, dict) else {}
        except RuntimeError:
            raise
        except Exception:
            if attempt == 2:
                return None
            time.sleep(1.0 * (attempt + 1))
    return None


def season_start_year(label: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", label or "")
    return int(match.group(0)) if match else None


def exclusion_reason(name: str) -> str | None:
    folded = unicodedata.normalize("NFKD", name or "") \
        .encode("ascii", "ignore").decode()
    for pattern, reason in EXCLUDE_PATTERNS:
        if pattern.search(folded):
            return reason
    return None


def main() -> int:
    resp = _client().get(f"{API}/allLeagues")
    resp.raise_for_status()
    listing = resp.json()
    countries = listing["countries"]

    rows: list[dict] = []
    detail_cache: dict[tuple[str, int], dict | None] = {}

    def details(ccode: str, lid: int) -> dict | None:
        key = (ccode, lid)
        if key not in detail_cache:
            detail_cache[key] = fetch_details(lid, ccode)
        return detail_cache[key]

    for country in countries:
        ccode = country["ccode"]
        cname = country["name"]
        leagues = country.get("leagues") or []
        selected_count = 0
        pending: list[dict] = []
        for entry in leagues:
            lid = int(entry["id"])
            name = entry["name"]
            row = {"country": cname, "ccode": ccode, "league": name,
                   "league_id": lid, "gender": "", "named": "",
                   "tier_rank": "", "selected": "no", "reason": "",
                   "seasons_2021plus": "", "n_seasons": 0}
            if (ccode, lid) in NAMED:
                row["named"] = "yes"
            if (ccode, lid) in ALREADY_PULLED:
                row["selected"] = "already_pulled"
                row["reason"] = "pulled earlier into fotmob_jleague/"
                rows.append(row)
                selected_count += 1
                continue
            if (ccode, lid) in HARDCODED_CUPS:
                row["reason"] = "cup-like name (hardcoded)"
                rows.append(row)
                continue
            reason = exclusion_reason(name)
            if reason and (ccode, lid) not in NAMED:
                row["reason"] = reason
                rows.append(row)
                continue
            pending.append(row)
        # Walk candidates in FotMob order; confirm via details payload.
        for row in pending:
            lid = row["league_id"]
            if row["named"] != "yes" and selected_count >= 3:
                row["reason"] = "beyond top-3"
                rows.append(row)
                continue
            payload = details(ccode, lid)
            if payload is None:
                row["reason"] = "details fetch failed (3 retries)"
                rows.append(row)
                continue
            if not payload:
                row["reason"] = "fotmob payload empty (dead entry)"
                rows.append(row)
                continue
            det = payload.get("details") or {}
            gender = str(det.get("gender") or "")
            row["gender"] = gender
            if gender == "female" and row["named"] != "yes":
                row["reason"] = "women's league (general rule: men's tiers)"
                rows.append(row)
                continue
            if FEMALE_NAME.search(row["league"]) and gender == "female" \
                    and row["named"] != "yes":
                row["reason"] = "women's league"
                rows.append(row)
                continue
            seasons = [s for s in (payload.get("allAvailableSeasons")
                                   or [])
                       if (season_start_year(str(s)) or 0) >= 2021]
            row["seasons_2021plus"] = ";".join(str(s) for s in seasons)
            row["n_seasons"] = len(seasons)
            selected_count += 1
            row["tier_rank"] = selected_count
            row["selected"] = "yes"
            row["reason"] = "named by user" if row["named"] == "yes" \
                else f"tier {selected_count} by FotMob order"
            rows.append(row)
        print(f"{ccode} {cname}: selected {selected_count}", flush=True)

    fields = ["country", "ccode", "league", "league_id", "gender",
              "named", "tier_rank", "selected", "reason",
              "seasons_2021plus", "n_seasons"]
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    sel = [r for r in rows if r["selected"] == "yes"]
    named = [r for r in sel if r["named"] == "yes"]
    print(json.dumps({
        "countries": len(countries), "listed": len(rows),
        "selected": len(sel), "named_selected": len(named),
        "season_groups": sum(int(r["n_seasons"]) for r in sel),
        "named": [(r["ccode"], r["league"], r["league_id"]) for r in named],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
