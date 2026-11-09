"""Pull FULL FotMob matchDetails responses for the top leagues of
every country in FotMob's listing (catalog: fotmob_world_catalog.csv,
built by build_fotmob_world_catalog.py — top 1-3 senior tiers per
country by FotMob's own ordering, plus the user's named leagues).

Seasons: from 2021 onward, each league's own FotMob season labels
(allAvailableSeasons filtered to labels whose first year is >= 2021;
split labels like "2026 - Clausura" are pulled as their own canonical
groups, deduplicated by match id within a league). Played matches
only. The full JSON response is stored at
data_enrichment/fotmob_world/<Country>/<League>/<season>/<match_id>.json
(season "/" written as "-"), mirroring pull_fotmob_jleague.py; files
already on disk are reused, never refetched, so the run is resumable
and can be re-launched at any time (a lock prevents duplicates).

Outputs:
  data_enrichment/fotmob_world_index.csv   one row per stored match:
      match_id, country, ccode, league, league_id, season, date,
      home, away, score, has_shotmap, has_stats, has_lineup,
      has_period_splits, path
  data_enrichment/fotmob_world_checkpoint.json   resumable state
      (uncommitted), incl. per league-season played/unplayed counts
      and the failed-ids list (ids are never silently dropped)
  data_enrichment/fotmob_world_failed.csv   persistent failures
  the JSON store itself (gitignored, never committed)

Usage:
  pull_fotmob_world.py --plan-only     count fixtures, print the
                                       storage projection, pull nothing
  pull_fotmob_world.py --named-only    Stage 1: only the user's
                                       named leagues
  pull_fotmob_world.py                 the whole catalog, named
                                       leagues first, then countries
                                       A-Z (Stage 2 continues this)

Pacing: parallel workers, zero delay by default; the run aborts (with
checkpoint saved) only on a sustained run of provider stops (HTTP
401/403/429), per the standing instruction. Transient per-match
errors are retried once at the end; persistent failures are reported,
not hidden.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx  # noqa: E402

from backfill_sot_fotmob import HEADERS, atomic_json, get  # noqa: E402

STORE = BASE / "data_enrichment" / "fotmob_world"
CATALOG = BASE / "data_enrichment" / "fotmob_world_catalog.csv"
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
CHECKPOINT = BASE / "data_enrichment" / "fotmob_world_checkpoint.json"
LOCK = BASE / "data_enrichment" / "fotmob_world.lock"
FAILED = BASE / "data_enrichment" / "fotmob_world_failed.csv"
API = "https://www.fotmob.com/api/data"
INDEX_FIELDS = ["match_id", "country", "ccode", "league", "league_id",
                "season", "date", "home", "away", "score", "has_shotmap",
                "has_stats", "has_lineup", "has_period_splits", "path"]

_thread_local = threading.local()


def _thread_client() -> httpx.Client:
    client = getattr(_thread_local, "client", None)
    if client is None:
        from stealth import proxy_url
        client = httpx.Client(headers=HEADERS, timeout=60,
                              follow_redirects=True, proxy=proxy_url())
        _thread_local.client = client
    return client


def sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "-", str(name)).strip()
    return re.sub(r"\s+", " ", name) or "_"


def season_dir(season: str) -> str:
    return season.replace("/", "-")


def season_start_year(label: str) -> int | None:
    match = re.search(r"(19|20)\d{2}", label or "")
    return int(match.group(0)) if match else None


def flags_of(payload: dict) -> dict:
    content = payload.get("content") or {}
    shots = (content.get("shotmap") or {}).get("shots")
    periods = (content.get("stats") or {}).get("Periods") or {}
    return {"has_shotmap": isinstance(shots, list) and len(shots) > 0,
            "has_stats": "All" in periods,
            "has_lineup": bool(content.get("lineup")),
            "has_period_splits": "FirstHalf" in periods
            and "SecondHalf" in periods}


def score_of(fixture: dict, payload: dict | None) -> str:
    teams = (payload.get("header") or {}).get("teams") if payload else None
    if teams and len(teams) == 2 and teams[0].get("score") is not None \
            and teams[1].get("score") is not None:
        return f"{teams[0]['score']}-{teams[1]['score']}"
    raw = (fixture.get("status") or {}).get("scoreStr") or ""
    return raw.replace(" ", "")


def fetch_one(item: dict, delay: float) -> dict:
    """Store the full response for one target; never raises."""
    mid = item["match_id"]
    dest = STORE / sanitize(item["country"]) / sanitize(item["league"]) / \
        season_dir(item["season"]) / f"{mid}.json"
    try:
        if dest.exists():
            payload = json.loads(dest.read_text(encoding="utf-8"))
            origin = "store"
        else:
            payload = get(_thread_client(), "matchDetails",
                          {"matchId": mid}, delay)
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(f".tmp{threading.get_ident()}")
            tmp.write_text(json.dumps(payload, ensure_ascii=False),
                           encoding="utf-8")
            tmp.replace(dest)
            origin = "http"
        return {"item": item, "origin": origin,
                "score": score_of(item, payload), **flags_of(payload)}
    except RuntimeError as exc:
        return {"item": item, "provider_stop": str(exc)}
    except Exception as exc:
        return {"item": item, "error": repr(exc),
                "transient": isinstance(exc, (httpx.TransportError,
                                              httpx.HTTPStatusError))}


def read_checkpoint() -> dict:
    if not CHECKPOINT.exists():
        return {"done_ids": [], "errors": [], "groups": {},
                "started_utc": datetime.now(timezone.utc).isoformat()}
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def load_index() -> dict:
    rows = {}
    if INDEX.exists():
        with INDEX.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows[row["match_id"]] = row
    return rows


def write_index(rows: dict) -> None:
    """Rewrite the index ATOMICALLY and MERGE-ON-WRITE.

    Two failure modes bit the 2026-11-09 world pull: (1) the old
    open("w") truncated the file in place, so a run killed mid-write
    (a SIGTERM'd relaunch did exactly this) left a truncated index
    whose lost rows were then never re-recorded, because the
    atomically-written checkpoint's done_ids made later runs skip
    those matches; (2) a process rewrites the whole file from its
    in-memory dict, so any row it never loaded is dropped. Guard:
    re-read the on-disk index and merge (in-memory rows win per
    match_id, disk-only rows are preserved), then write to a temp
    file in the same directory and os.replace() it over the index,
    so readers only ever see a complete file."""
    import os
    merged = load_index()
    merged.update(rows)
    ordered = sorted(merged.values(),
                     key=lambda r: (r["country"], r["league"], r["season"],
                                    r["date"], r["home"]))
    tmp = INDEX.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(ordered)
    os.replace(tmp, INDEX)


def write_failed(errors: list[dict]) -> None:
    if not errors:
        if FAILED.exists():
            FAILED.unlink()
        return
    with FAILED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle,
                                fieldnames=["match_id", "country", "league",
                                            "season", "date", "home", "away",
                                            "error"])
        writer.writeheader()
        writer.writerows(errors)


def load_catalog(named_only: bool) -> list[dict]:
    with CATALOG.open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["selected"] == "yes"]
    if named_only:
        rows = [r for r in rows if r["named"] == "yes"]
    rows.sort(key=lambda r: (0 if r["named"] == "yes" else 1,
                             r["country"], int(r["tier_rank"] or 99)))
    return rows


def get_planning(path: str, params: dict, delay: float) -> dict:
    """get() with retries on transport errors: the local proxy
    occasionally refuses bursts of planning connections, and a
    silently half-fetched plan is worse than a slow one. Provider
    stops (401/403/429, raised as RuntimeError) still propagate."""
    import time
    last: Exception | None = None
    for attempt in range(3):
        try:
            return get(_thread_client(), path, params, delay)
        except RuntimeError:
            raise
        except Exception as exc:
            last = exc
            time.sleep(2.0 * (attempt + 1) ** 2)
    raise last  # type: ignore[misc]


def league_season_params(row: dict, delay: float) -> list[str]:
    """Fresh allAvailableSeasons for one league, filtered to 2021+;
    falls back to the catalog's recorded list if the probe fails."""
    try:
        payload = get_planning("leagues",
                               {"id": int(row["league_id"]),
                                "ccode3": row["ccode"]}, delay)
        seasons = [str(s) for s in (payload.get("allAvailableSeasons")
                                    or [])]
        kept = [s for s in seasons
                if (season_start_year(s) or 0) >= 2021]
        if kept:
            return kept
    except Exception as exc:
        print(f"availability probe failed for {row['country']} "
              f"{row['league']}: {exc!r}; using catalog list", flush=True)
    return [s for s in (row.get("seasons_2021plus") or "").split(";") if s]


def plan_league(row: dict, delay: float) -> tuple[list[dict], dict]:
    """Plan one league: fixtures per season param, ids deduped within
    the league, grouped under canonical selectedSeason labels."""
    plan: list[dict] = []
    planned: set[int] = set()
    groups: dict[str, dict] = {}
    for param in league_season_params(row, delay):
        try:
            payload = get_planning("leagues",
                                   {"id": int(row["league_id"]),
                                    "ccode3": row["ccode"],
                                    "season": param}, delay)
        except RuntimeError:
            raise
        except Exception as exc:
            print(f"plan fetch failed {row['country']} {row['league']} "
                  f"season {param}: {exc!r}", flush=True)
            continue
        if not isinstance(payload, dict) or not payload:
            continue
        season = str((payload.get("details") or {})
                     .get("selectedSeason") or param)
        if (season_start_year(season) or 0) < 2021:
            continue
        fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
        key = f"{row['country']} | {row['league']} | {season}"
        group = groups.setdefault(key, {"country": row["country"],
                                        "league": row["league"],
                                        "season": season, "all": 0,
                                        "played": 0, "unplayed": 0})
        if fixtures and group["all"] == 0:
            group["all"] = len(fixtures)
        n_group_plan = 0
        for fixture in fixtures:
            status = fixture.get("status") or {}
            if not status.get("finished") or status.get("cancelled"):
                continue
            mid = int(fixture["id"])
            if mid in planned:
                continue
            planned.add(mid)
            n_group_plan += 1
            plan.append({
                "match_id": mid, "country": row["country"],
                "ccode": row["ccode"], "league": row["league"],
                "league_id": int(row["league_id"]), "season": season,
                "date": str(status.get("utcTime") or "")[:10],
                "home": (fixture.get("home") or {}).get("name") or "",
                "away": (fixture.get("away") or {}).get("name") or "",
                "score": score_of(fixture, None)})
        group["played"] += n_group_plan
        group["unplayed"] = group["all"] - group["played"] \
            if group["all"] else 0
    return plan, groups


def build_plan(rows: list[dict], delay: float,
               workers: int = 4) -> tuple[list[dict], dict]:
    per_league: dict[int, tuple[list[dict], dict]] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(plan_league, row, delay): i
                   for i, row in enumerate(rows)}
        for future in as_completed(futures):
            i = futures[future]
            per_league[i] = future.result()
            row = rows[i]
            n = len(per_league[i][0])
            print(f"planned {row['country']} | {row['league']}: {n}",
                  flush=True)
    plan: list[dict] = []
    groups: dict[str, dict] = {}
    for i in range(len(rows)):
        league_plan, league_groups = per_league[i]
        plan.extend(league_plan)
        groups.update(league_groups)
    return plan, groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--plan-limit", type=int, default=0)
    parser.add_argument("--named-only", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--kb-per-match", type=float, default=110.0,
                        help="storage projection constant (J.League "
                             "measured ~110 KB/match)")
    args = parser.parse_args()

    rows = load_catalog(args.named_only)
    print(f"catalog leagues in scope: {len(rows)}", flush=True)
    plan, groups = build_plan(rows, args.delay)
    total = len(plan)
    gb = total * args.kb_per_match / 1024 / 1024
    print(json.dumps({"planned_matches": total,
                      "league_season_groups": len(groups),
                      "projection_gb_at_kb_per_match": round(gb, 2),
                      "kb_per_match": args.kb_per_match}, indent=2),
          flush=True)
    if args.plan_only:
        per_league: dict[str, int] = {}
        for item in plan:
            key = f"{item['country']} | {item['league']}"
            per_league[key] = per_league.get(key, 0) + 1
        for key in sorted(per_league):
            print(f"PLAN {key}: {per_league[key]}")
        return 0

    import fcntl
    lock_handle = LOCK.open("w")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another pull_fotmob_world instance holds the lock; exiting")
        return 2
    STORE.mkdir(parents=True, exist_ok=True)
    checkpoint = read_checkpoint()
    done_ids = set(checkpoint.get("done_ids", []))
    errors = checkpoint.get("errors", [])
    index = load_index()
    for mid in list(index):
        done_ids.add(int(mid))

    plan = [item for item in plan if item["match_id"] not in done_ids]
    print(f"plan after done-filter: {len(plan)}", flush=True)
    if args.plan_limit:
        plan = plan[:args.plan_limit]

    def save_checkpoint(finished=False):
        checkpoint.update({"done_ids": sorted(done_ids), "errors": errors,
                           "groups": groups, "finished": finished,
                           "updated_utc": datetime.now(timezone.utc)
                           .isoformat()})
        atomic_json(CHECKPOINT, checkpoint)

    def record(outcome: dict) -> None:
        item = outcome["item"]
        mid = item["match_id"]
        rel = Path("data_enrichment") / "fotmob_world" / \
            sanitize(item["country"]) / sanitize(item["league"]) / \
            season_dir(item["season"]) / f"{mid}.json"
        index[str(mid)] = {
            "match_id": mid, "country": item["country"],
            "ccode": item["ccode"], "league": item["league"],
            "league_id": item["league_id"], "season": item["season"],
            "date": item["date"], "home": item["home"],
            "away": item["away"], "score": outcome["score"],
            "has_shotmap": outcome["has_shotmap"],
            "has_stats": outcome["has_stats"],
            "has_lineup": outcome["has_lineup"],
            "has_period_splits": outcome["has_period_splits"],
            "path": str(rel)}
        done_ids.add(mid)

    fetched_http = reused = completed = stops = 0
    origins = {"store": 0, "http": 0}
    recent: list[str] = []
    retry_items: list[dict] = []
    aborted = False
    started = datetime.now(timezone.utc)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_one, item, args.delay): item
                   for item in plan}
        for future in as_completed(futures):
            outcome = future.result()
            completed += 1
            if "provider_stop" in outcome:
                stops += 1
                recent.append("stop")
            elif "error" in outcome:
                recent.append("error")
                if outcome.get("transient"):
                    retry_items.append(outcome["item"])
                    continue
                item = outcome["item"]
                errors.append({"match_id": item["match_id"],
                               "country": item["country"],
                               "league": item["league"],
                               "season": item["season"],
                               "date": item["date"], "home": item["home"],
                               "away": item["away"],
                               "error": outcome.get("error", "?")})
            else:
                recent.append("ok")
                origins[outcome["origin"]] += 1
                if outcome["origin"] == "http":
                    fetched_http += 1
                else:
                    reused += 1
                record(outcome)
            if completed % 25 == 0:
                save_checkpoint()
            if completed % 2000 == 0:
                write_index(index)
            if completed % 500 == 0:
                elapsed = (datetime.now(timezone.utc) - started) \
                    .total_seconds()
                print(f"progress {completed}/{len(plan)} http={fetched_http} "
                      f"reused={reused} errors={len(errors)} stops={stops} "
                      f"{elapsed:.0f}s", flush=True)
            if len(recent) >= 30 and recent[-30:].count("stop") >= 15:
                aborted = True
                print("ABORT: sustained provider stops; checkpoint saved.",
                      flush=True)
                break
    if retry_items and not aborted:
        print(f"retrying {len(retry_items)} transient failures once",
              flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(fetch_one, item, args.delay): item
                       for item in retry_items}
            for future in as_completed(futures):
                outcome = future.result()
                if "has_shotmap" in outcome:
                    origins[outcome["origin"]] += 1
                    if outcome["origin"] == "http":
                        fetched_http += 1
                    else:
                        reused += 1
                    record(outcome)
                else:
                    item = outcome["item"]
                    errors.append({"match_id": item["match_id"],
                                   "country": item["country"],
                                   "league": item["league"],
                                   "season": item["season"],
                                   "date": item["date"],
                                   "home": item["home"],
                                   "away": item["away"],
                                   "error": outcome.get("error",
                                                        outcome.get(
                                                            "provider_stop",
                                                            "?"))})
    save_checkpoint(finished=not aborted)
    write_index(index)
    write_failed(errors)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(json.dumps({"planned": len(plan), "completed": completed,
                      "indexed": len(index), "fetched_http": fetched_http,
                      "reused": reused, "origins": origins,
                      "errors": len(errors), "provider_stops": stops,
                      "aborted": aborted, "elapsed_s": round(elapsed, 1)},
                     indent=2), flush=True)
    return 3 if aborted else 0


if __name__ == "__main__":
    raise SystemExit(main())
