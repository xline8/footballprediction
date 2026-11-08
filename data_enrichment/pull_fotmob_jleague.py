"""Pull FULL FotMob matchDetails responses for J.League (J1/J2/J3).

Targets: every PLAYED match of Japan's J1 League (FotMob id 223),
J2 League (8974) and J3 League (9136) from season 2021 onward — calendar
seasons 2021..2025, the transitional 2026 season where it exists as its
own label (J1), and the in-progress 2026/2027 season (matches played so
far). There is no local spine for these leagues, so fixtures come
straight from the FotMob leagues endpoint; the canonical season label
of each group is the payload's details.selectedSeason (the season param
"2026" resolves to "2026/2027" for J2/J3). Match ids are deduplicated
across season params, so a group reachable under two params is pulled
once, under its canonical label.

The full JSON response is stored at
data_enrichment/fotmob_jleague/<LEAGUE>/<season>/<match_id>.json
(season written with a dash, e.g. 2026-2027), mirroring the top-5 store
in pull_fotmob_full.py. Responses already on disk are reused, never
refetched.

Outputs:
  data_enrichment/fotmob_jleague_index.csv   one row per stored match:
      match_id, league, season, date, home, away, score, has_shotmap,
      has_stats, has_lineup, has_period_splits, path
  data_enrichment/fotmob_jleague_checkpoint.json   resumable state
      (uncommitted), incl. per league-season played/unplayed counts and
      the failed-ids list (ids are never silently dropped)
  the JSON store itself (gitignored, never committed)

Coverage found by the pre-pull probe (2026-11-08): J1 carries shotmap
from 2022 on, match stats from 2021 (All-period; 1H/2H splits common
from 2023 on) and lineups throughout; J2 has lineups throughout and
All-period stats in part of 2021-2024, but no shotmap and (playoffs
aside) no period splits; J3 is thinnest — lineups only from 2025 on and
stats only in isolated (playoff) matches. The index flags record the
exact per-match truth.

Pacing: parallel workers, zero delay by default; the run aborts (with
checkpoint saved) only on a sustained run of provider stops (HTTP
401/403/429), per the standing instruction. Transient per-match errors
are retried once at the end; persistent failures are reported, not
hidden.
"""
from __future__ import annotations

import argparse
import csv
import json
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

STORE = BASE / "data_enrichment" / "fotmob_jleague"
INDEX = BASE / "data_enrichment" / "fotmob_jleague_index.csv"
CHECKPOINT = BASE / "data_enrichment" / "fotmob_jleague_checkpoint.json"
LOCK = BASE / "data_enrichment" / "fotmob_jleague.lock"
FAILED = BASE / "data_enrichment" / "fotmob_jleague_failed.csv"

LEAGUES = {"J1": 223, "J2": 8974, "J3": 9136}
CCODE = "JPN"
SEASON_PARAMS = ["2021", "2022", "2023", "2024", "2025", "2026", "2026/2027"]
INDEX_FIELDS = ["match_id", "league", "season", "date", "home", "away",
                "score", "has_shotmap", "has_stats", "has_lineup",
                "has_period_splits", "path"]

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
    dest = STORE / item["league"] / season_dir(item["season"]) / f"{mid}.json"
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
        return {"item": item, "origin": origin, "score": score_of(item, payload),
                **flags_of(payload)}
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
    ordered = sorted(rows.values(),
                     key=lambda r: (r["league"], r["season"], r["date"],
                                    r["home"]))
    with INDEX.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(ordered)


def write_failed(errors: list[dict]) -> None:
    if not errors:
        if FAILED.exists():
            FAILED.unlink()
        return
    with FAILED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle,
                                fieldnames=["match_id", "league", "season",
                                            "date", "home", "away", "error"])
        writer.writeheader()
        writer.writerows(errors)


def build_plan(delay: float) -> tuple[list[dict], dict]:
    """Fixtures per league/season-param; dedupe ids across params."""
    plan: list[dict] = []
    planned: set[int] = set()
    groups: dict[str, dict] = {}
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=60, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for league, lid in LEAGUES.items():
            for param in SEASON_PARAMS:
                payload = get(client, "leagues",
                              {"id": lid, "ccode3": CCODE, "season": param},
                              delay)
                season = str((payload.get("details") or {})
                             .get("selectedSeason") or param)
                fixtures = (payload.get("fixtures") or {}) \
                    .get("allMatches") or []
                key = f"{league} {season}"
                group = groups.setdefault(key, {"league": league,
                                                "season": season,
                                                "all": 0, "played": 0,
                                                "unplayed": 0})
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
                        "match_id": mid, "league": league, "season": season,
                        "date": str(status.get("utcTime") or "")[:10],
                        "home": (fixture.get("home") or {}).get("name") or "",
                        "away": (fixture.get("away") or {}).get("name") or "",
                        "score": score_of(fixture, None)})
                group["played"] += n_group_plan
                group["unplayed"] = group["all"] - group["played"] \
                    if group["all"] else 0
                print(f"group {key}: all={group['all']} "
                      f"played_total={group['played']} plan_total={len(plan)}",
                      flush=True)
    return plan, groups


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
        print("another pull_fotmob_jleague instance holds the lock; exiting")
        return 2
    STORE.mkdir(parents=True, exist_ok=True)
    checkpoint = read_checkpoint()
    done_ids = set(checkpoint.get("done_ids", []))
    errors = checkpoint.get("errors", [])
    index = load_index()
    for mid in list(index):
        done_ids.add(int(mid))

    plan, groups = build_plan(args.delay)
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
        rel = Path("data_enrichment") / "fotmob_jleague" / item["league"] / \
            season_dir(item["season"]) / f"{mid}.json"
        index[str(mid)] = {"match_id": mid, "league": item["league"],
                           "season": item["season"], "date": item["date"],
                           "home": item["home"], "away": item["away"],
                           "score": outcome["score"],
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
                               "league": item["league"],
                               "season": item["season"], "date": item["date"],
                               "home": item["home"], "away": item["away"],
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
                                   "league": item["league"],
                                   "season": item["season"],
                                   "date": item["date"],
                                   "home": item["home"], "away": item["away"],
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
