"""Pull FULL FotMob matchDetails responses for recent top-5 matches.

Targets: every top-5 match in all_matches_clean.csv with season >= 2022/23
(including played 2026/27 matches), resolved to a FotMob match id with the
same fixture-matching machinery as the SOT halves fill (fixture_map_fixed
and the alias patch from fill_halves_gaps). The full JSON response is stored
at data_enrichment/fotmob_full/<div>/<season>/<fotmob_match_id>.json
(season written with a dash, e.g. 2022-23). Responses already on disk —
either in the store or in the phase-1 raw cache
(data_enrichment/sot_backfill/gap_raw/) — are reused, never refetched.

Outputs:
  data_enrichment/fotmob_full_index.csv   one row per stored match with
                                          has_shotmap / has_lineup /
                                          has_stats flags
  data_enrichment/fotmob_full_checkpoint.json   resumable state (uncommitted)
  the JSON store itself (gitignored, never committed)

Pacing: parallel workers, zero delay by default; the run aborts (with
checkpoint saved) only on a sustained run of provider stops (HTTP
401/403/429), per the standing instruction. Transient per-match errors
are retried once at the end; persistent failures are reported, not hidden.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx  # noqa: E402

import backfill_sot_fotmob as _bf  # noqa: E402
from backfill_sot_fotmob import (  # noqa: E402
    HEADERS, LEAGUES, atomic_json, get, load_master, season_api,
)
from fill_halves_gaps import fixture_map_fixed, spine_key  # noqa: E402

STORE = BASE / "data_enrichment" / "fotmob_full"
INDEX = BASE / "data_enrichment" / "fotmob_full_index.csv"
CHECKPOINT = BASE / "data_enrichment" / "fotmob_full_checkpoint.json"
LOCK = BASE / "data_enrichment" / "fotmob_full.lock"
GAP_RAW = BASE / "data_enrichment" / "sot_backfill" / "gap_raw"
MIN_SEASON = "2022/23"
INDEX_FIELDS = ["div", "season", "date", "home", "away", "fotmob_match_id",
                "path", "has_shotmap", "has_lineup", "has_stats"]

_thread_local = threading.local()


def _thread_client() -> httpx.Client:
    client = getattr(_thread_local, "client", None)
    if client is None:
        from stealth import proxy_url
        client = httpx.Client(headers=HEADERS, timeout=60,
                              follow_redirects=True, proxy=proxy_url())
        _thread_local.client = client
    return client


def season_dir(season: str) -> str:
    return season.replace("/", "-")


def flags_of(payload: dict) -> dict:
    content = payload.get("content") or {}
    shots = (content.get("shotmap") or {}).get("shots")
    stats = (content.get("stats") or {}).get("Periods") or {}
    return {"has_shotmap": isinstance(shots, list) and len(shots) > 0,
            "has_lineup": bool(content.get("lineup")),
            "has_stats": "All" in stats}


def fetch_one(item: dict, delay: float) -> dict:
    """Store the full response for one target; never raises."""
    mid = item["fotmob_match_id"]
    dest = STORE / item["div"] / season_dir(item["season"]) / f"{mid}.json"
    try:
        if dest.exists():
            payload = json.loads(dest.read_text(encoding="utf-8"))
            origin = "store"
        else:
            cached = GAP_RAW / f"{item['div']}_{season_dir(item['season'])}_{mid}.json"
            if cached.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(cached, dest)
                payload = json.loads(dest.read_text(encoding="utf-8"))
                origin = "phase1_cache"
            else:
                payload = get(_thread_client(), "matchDetails",
                              {"matchId": mid}, delay)
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(f".tmp{threading.get_ident()}")
                tmp.write_text(json.dumps(payload, ensure_ascii=False),
                               encoding="utf-8")
                tmp.replace(dest)
                origin = "http"
        return {"item": item, "origin": origin, **flags_of(payload)}
    except RuntimeError as exc:
        return {"item": item, "provider_stop": str(exc)}
    except Exception as exc:
        return {"item": item, "error": repr(exc),
                "transient": isinstance(exc, (httpx.TransportError,
                                              httpx.HTTPStatusError))}


def read_checkpoint() -> dict:
    if not CHECKPOINT.exists():
        return {"done_ids": [], "errors": [], "unfetchable": [],
                "started_utc": datetime.now(timezone.utc).isoformat()}
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def load_index() -> dict:
    rows = {}
    if INDEX.exists():
        with INDEX.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows[row["fotmob_match_id"]] = row
    return rows


def write_index(rows: dict) -> None:
    ordered = sorted(rows.values(),
                     key=lambda r: (r["div"], r["season"], r["date"], r["home"]))
    with INDEX.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(ordered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--plan-limit", type=int, default=0)
    args = parser.parse_args()
    import fcntl
    lock_handle = LOCK.open("w")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another pull_fotmob_full instance holds the lock; exiting")
        return 2
    STORE.mkdir(parents=True, exist_ok=True)
    spine = [r for r in load_master() if r["Season"] >= MIN_SEASON]
    print(f"targets (spine, season >= {MIN_SEASON}): {len(spine)}", flush=True)
    checkpoint = read_checkpoint()
    done_ids = set(checkpoint.get("done_ids", []))
    errors = checkpoint.get("errors", [])
    unfetchable = checkpoint.get("unfetchable", [])
    index = load_index()
    for mid in list(index):
        done_ids.add(mid)

    # Plan: resolve FotMob ids per div/season group.
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in spine:
        groups.setdefault((row["Div"], row["Season"]), []).append(row)
    plan: list[dict] = []
    planned_keys = set()
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for (div, season), group_rows in sorted(groups.items()):
            payload = get(client, "leagues",
                          {"id": LEAGUES[div][0], "ccode3": LEAGUES[div][1],
                           "season": season_api(season)}, args.delay)
            fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
            matched, rejected = fixture_map_fixed(group_rows, fixtures)
            if len(group_rows) >= 20 and len(matched) < 0.5 * len(group_rows):
                raise RuntimeError(
                    f"implausible match rate for {div} {season}: "
                    f"{len(matched)}/{len(group_rows)} — aborting")
            matched_keys = set()
            for item in matched:
                row = item["csv"]
                skey = spine_key(row)
                matched_keys.add(skey)
                mid = item["mapping"]["fotmob_match_id"]
                if mid in done_ids or skey in planned_keys:
                    continue
                planned_keys.add(skey)
                plan.append({"div": div, "season": season, "date": row["Date"],
                             "home": row["HomeTeam"], "away": row["AwayTeam"],
                             "fotmob_match_id": mid})
            have_unfetch = {u["spine_key"] for u in unfetchable}
            for row in group_rows:
                skey = spine_key(row)
                if skey not in matched_keys and skey not in have_unfetch:
                    unfetchable.append({"spine_key": skey, "div": div,
                                        "season": season, "date": row["Date"],
                                        "home": row["HomeTeam"],
                                        "away": row["AwayTeam"],
                                        "reason": "no matching FotMob fixture"})
            print(f"group {div} {season}: matched={len(matched)}/"
                  f"{len(group_rows)} plan_total={len(plan)}", flush=True)
    if args.plan_limit:
        plan = plan[:args.plan_limit]

    def save_checkpoint(finished=False):
        checkpoint.update({"done_ids": sorted(done_ids), "errors": errors,
                           "unfetchable": unfetchable, "finished": finished,
                           "updated_utc": datetime.now(timezone.utc).isoformat()})
        atomic_json(CHECKPOINT, checkpoint)

    def record(outcome: dict) -> None:
        item = outcome["item"]
        mid = item["fotmob_match_id"]
        rel = Path("data_enrichment") / "fotmob_full" / item["div"] / \
            season_dir(item["season"]) / f"{mid}.json"
        index[mid] = {"div": item["div"], "season": item["season"],
                      "date": item["date"], "home": item["home"],
                      "away": item["away"], "fotmob_match_id": mid,
                      "path": str(rel),
                      "has_shotmap": outcome["has_shotmap"],
                      "has_lineup": outcome["has_lineup"],
                      "has_stats": outcome["has_stats"]}
        done_ids.add(mid)

    fetched_http = reused = completed = stops = 0
    origins = {"store": 0, "phase1_cache": 0, "http": 0}
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
                errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
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
            if completed % 500 == 0:
                elapsed = (datetime.now(timezone.utc) - started).total_seconds()
                print(f"progress {completed}/{len(plan)} http={fetched_http} "
                      f"reused={reused} errors={len(errors)} stops={stops} "
                      f"{elapsed:.0f}s", flush=True)
            if len(recent) >= 30 and recent[-30:].count("stop") >= 15:
                aborted = True
                print("ABORT: sustained provider stops; checkpoint saved.",
                      flush=True)
                break
    if retry_items and not aborted:
        print(f"retrying {len(retry_items)} transient failures once", flush=True)
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
                    errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
                                   "error": outcome.get("error",
                                                        outcome.get("provider_stop", "?"))})
    save_checkpoint(finished=not aborted)
    write_index(index)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(json.dumps({"targets": len(spine), "planned": len(plan),
                      "completed": completed, "indexed": len(index),
                      "fetched_http": fetched_http, "reused": reused,
                      "origins": origins, "errors": len(errors),
                      "provider_stops": stops, "unfetchable": len(unfetchable),
                      "aborted": aborted, "elapsed_s": round(elapsed, 1)},
                     indent=2), flush=True)
    return 3 if aborted else 0


if __name__ == "__main__":
    raise SystemExit(main())
