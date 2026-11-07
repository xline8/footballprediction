"""Fill SOT half-split gaps in the SofaScore dataset from FotMob shotmaps.

Spine: all_matches_clean.csv (top-5 divisions, via backfill_sot_fotmob.load_master).
Source A: data_enrichment/sot_sofascore/sofascore_sot_dataset.csv (already in repo).
This driver fetches FotMob matchDetails ONLY for spine matches that lack a
SofaScore half split, plus a seeded random sample of SofaScore-covered matches
(for cross-validation of the two sources). Per-team half splits are extracted
from the shotmap with exactly the counting rules of
backfill_sot_fotmob.extract (on-target, not blocked, not own goal), split by
the header team ids; the stats-periods table is the fallback, mirroring
backfill_sot_fotmob._stats_sot but keeping the [home, away] pairs.

Outputs (data_enrichment/sot_backfill/):
  gap_labels.csv       one row per gap match FotMob could label
  crossval_labels.csv  one row per sampled SofaScore-covered match
  remaining_gaps.csv   spine matches FotMob could not label, with reason
  gap_checkpoint.json  resumable state (done ids, processed keys, errors)
  gap_raw/             cached matchDetails JSON (not committed)

Resumable: rerun the same command; finished work is skipped. --batch N caps
the number of NEW matchDetails fetches per invocation.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

import httpx  # noqa: E402

import backfill_sot_fotmob as _bf  # noqa: E402
from backfill_sot_fotmob import (  # noqa: E402
    HEADERS, LEAGUES, atomic_json, get, load_master, norm, season_api,
)

# Team-name aliases the base module lacks, found empirically by comparing
# every spine team name against every FotMob league payload (2017/18-2026/27,
# all top-5 divisions): these seven were the only ones whose best name score
# fell below 0.80. 'Ath Bilbao' alone accounted for ~38 unmatched matches per
# La Liga season. The dict is patched in place (backfill_sot_fotmob.norm reads
# it at call time); the file itself is not modified. Keys are norm(spine
# name), values are norm(FotMob name), same convention as the base ALIASES.
_bf.ALIASES.update({
    "ath bilbao": "athletic club",
    "ath madrid": "atletico madrid",
    "la coruna": "deportivo a coruna",
    "m gladbach": "borussia monchengladbach",
    "hamburg": "hamburger sv",
    "west brom": "west bromwich albion",
    "paris sg": "paris saint germain",
})

OUT = BASE / "data_enrichment" / "sot_backfill"
RAW = OUT / "gap_raw"
GAP_LABELS = OUT / "gap_labels.csv"
XVAL_LABELS = OUT / "crossval_labels.csv"
GAPS_FILE = OUT / "remaining_gaps.csv"
CHECKPOINT = OUT / "gap_checkpoint.json"
SOFA = BASE / "data_enrichment" / "sot_sofascore" / "sofascore_sot_dataset.csv"

LABEL_FIELDS = ["div", "season", "date", "home", "away", "fotmob_match_id",
                "csv_sot_ft", "delta_sot_ft", "shot_count", "sot_1h", "sot_2h",
                "sot_1h_h", "sot_1h_a", "sot_2h_h", "sot_2h_a", "sot_ft",
                "blocked_on_target", "shotmap_complete", "label_source",
                "quality"]
GAP_FIELDS = ["div", "season", "date", "home", "away", "reason"]
SAMPLE_SEED = 20261107
SAMPLE_N = 200
DIV_PRIORITY = {"F1": 0, "SP1": 1, "E0": 2, "I1": 3, "D1": 4}


def fixture_map_fixed(rows: list[dict], fixtures: list[dict]):
    """Same matching semantics as backfill_sot_fotmob.fixture_map (same
    score(), same 1.60 threshold, same 0.10 ambiguity margin, same exact
    rule), but with correct bookkeeping: the original tracks used rows by
    their index WITHIN one date's list, and those indices repeat on every
    other date — once index 0 is used anywhere, it is blocked everywhere,
    so matching collapses after the first few fixtures (measured: 8/380
    on SP1 2017/18). Here rows are tracked by identity in the full list.
    backfill_sot_fotmob.py itself is not modified."""
    from backfill_sot_fotmob import score
    by_date: dict[str, list[int]] = {}
    for idx, row in enumerate(rows):
        by_date.setdefault(row["Date"], []).append(idx)
    matched, rejected = [], []
    used: set[int] = set()
    for fixture in fixtures:
        status = fixture.get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        date = str(status.get("utcTime") or "")[:10]
        home = (fixture.get("home") or {}).get("name") or ""
        away = (fixture.get("away") or {}).get("name") or ""
        candidates = [i for i in by_date.get(date, []) if i not in used]
        ranked = sorted((score(rows[i]["HomeTeam"], home) +
                         score(rows[i]["AwayTeam"], away), i)
                        for i in candidates)
        if not ranked:
            rejected.append({"fotmob_id": str(fixture.get("id")), "reason": "date"})
            continue
        best_score, index = ranked[-1]
        row = rows[index]
        second = ranked[-2][0] if len(ranked) > 1 else 0.0
        status_name = "exact" if best_score == 2 else "fuzzy"
        if best_score < 1.60:
            status_name = "unmatched"
        elif best_score - second < 0.10:
            status_name = "ambiguous"
        record = {"fotmob_match_id": str(fixture.get("id")), "date": date,
                  "fotmob_home": home, "fotmob_away": away,
                  "csv_home": row["HomeTeam"], "csv_away": row["AwayTeam"],
                  "score": round(best_score, 4), "status": status_name}
        if status_name in {"unmatched", "ambiguous"}:
            rejected.append(record)
            continue
        used.add(index)
        matched.append({"fixture": fixture, "csv": row, "mapping": record})
    return matched, rejected


def key_of(div: str, date: str, home: str, away: str) -> str:
    return "|".join([div, date, norm(home), norm(away)])


def spine_key(row: dict) -> str:
    return key_of(row["Div"], row["Date"], row["HomeTeam"], row["AwayTeam"])


def sofa_keys() -> set[str]:
    keys = set()
    with SOFA.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["div"] in LEAGUES:
                keys.add(key_of(row["div"], row["date"], row["home"], row["away"]))
    return keys


def extract_halves(payload: dict) -> dict:
    """Per-team half splits from a FotMob matchDetails payload.

    Counting rules identical to backfill_sot_fotmob.extract: a shot counts
    when isOnTarget is True, it is not an own goal, and it is not blocked
    (blocked on-target shots are tallied separately)."""
    content = payload.get("content") or {}
    teams = (payload.get("header") or {}).get("teams") or []
    shots = (content.get("shotmap") or {}).get("shots")
    if isinstance(shots, list) and shots and len(teams) == 2:
        home_id, away_id = teams[0].get("id"), teams[1].get("id")
        counts = {("FirstHalf", "h"): 0, ("FirstHalf", "a"): 0,
                  ("SecondHalf", "h"): 0, ("SecondHalf", "a"): 0}
        blocked = 0
        invalid = 0
        for shot in shots:
            if shot.get("isOwnGoal") or shot.get("isOnTarget") is not True:
                continue
            if shot.get("isBlocked") is True:
                blocked += 1
                continue
            period = shot.get("period")
            side = ("h" if shot.get("teamId") == home_id else
                    "a" if shot.get("teamId") == away_id else None)
            if period in ("FirstHalf", "SecondHalf") and side:
                counts[(period, side)] += 1
            else:
                invalid += 1
        if invalid:
            raise ValueError(f"on-target shot without standard period/team: {invalid}")
        return {"shot_count": len(shots),
                "sot_1h_h": counts[("FirstHalf", "h")],
                "sot_1h_a": counts[("FirstHalf", "a")],
                "sot_2h_h": counts[("SecondHalf", "h")],
                "sot_2h_a": counts[("SecondHalf", "a")],
                "blocked_on_target": blocked, "shotmap_complete": True,
                "label_source": "shotmap"}
    # Fallback: stats periods carry [home, away] ShotsOnTarget per period.
    periods = (content.get("stats") or {}).get("Periods") or {}
    values = {}
    for period, payload_p in periods.items():
        for section in (payload_p or {}).get("stats", []):
            for stat in section.get("stats", []):
                if stat.get("key") == "ShotsOnTarget":
                    raw = stat.get("stats") or []
                    if len(raw) == 2 and all(isinstance(v, (int, float)) for v in raw):
                        values[period] = [int(raw[0]), int(raw[1])]
                        break
            if period in values:
                break
    if "All" not in values:
        raise ValueError("missing ShotsOnTarget in match stats")
    if "FirstHalf" not in values or "SecondHalf" not in values:
        raise ValueError("stats payload has no half split")
    return {"shot_count": 0,
            "sot_1h_h": values["FirstHalf"][0], "sot_1h_a": values["FirstHalf"][1],
            "sot_2h_h": values["SecondHalf"][0], "sot_2h_a": values["SecondHalf"][1],
            "blocked_on_target": None, "shotmap_complete": True,
            "label_source": "stats"}


import threading  # noqa: E402
from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: E402

_thread_local = threading.local()


def _thread_client() -> httpx.Client:
    client = getattr(_thread_local, "client", None)
    if client is None:
        from stealth import proxy_url
        client = httpx.Client(headers=HEADERS, timeout=45,
                              follow_redirects=True, proxy=proxy_url())
        _thread_local.client = client
    return client


def fetch_item(item: dict, delay: float) -> dict:
    """Worker: fetch (or read from raw cache) one matchDetails payload and
    extract per-team halves. Returns an outcome dict; never raises."""
    mid = item["fotmob_match_id"]
    raw = RAW / f"{item['div']}_{item['season'].replace('/', '-')}_{mid}.json"
    was_cached = raw.exists()
    try:
        if was_cached:
            detail = json.loads(raw.read_text(encoding="utf-8"))
        else:
            detail = get(_thread_client(), "matchDetails",
                         {"matchId": mid}, delay)
            tmp = raw.with_suffix(f".tmp{threading.get_ident()}")
            tmp.write_text(json.dumps(detail, ensure_ascii=False), encoding="utf-8")
            tmp.replace(raw)
        return {"item": item, "fetched": not was_cached,
                "label": extract_halves(detail)}
    except RuntimeError as exc:  # get() provider-stop (401/403/429)
        return {"item": item, "fetched": not was_cached,
                "provider_stop": str(exc)}
    except Exception as exc:
        return {"item": item, "fetched": not was_cached, "error": repr(exc),
                "transient": isinstance(exc, (httpx.TransportError,
                                              httpx.HTTPStatusError))}


def run_parallel(args, spine, jobs, checkpoint) -> int:
    """Plan-then-fetch: league payloads + matching sequentially (cheap),
    matchDetails in a thread pool (single writer for all outputs)."""
    done_ids = set(checkpoint.get("done_ids", []))
    processed = set(checkpoint.get("processed", []))
    errors = checkpoint.get("errors", [])
    gaps_out = checkpoint.get("gaps", [])
    gap_sink = LabelSink(GAP_LABELS)
    xval_sink = LabelSink(XVAL_LABELS)
    labelled_ids = {r["fotmob_match_id"]
                    for r in gap_sink.existing + xval_sink.existing}

    groups: dict[tuple[str, str], list[str]] = {}
    for skey, (kind, row) in jobs.items():
        if skey not in processed:
            groups.setdefault((row["Div"], row["Season"]), []).append(skey)

    def group_order(item):
        (div, season), skeys = item
        kinds = {jobs[k][0] for k in skeys}
        return (0 if "sample" in kinds else 1, DIV_PRIORITY[div], season)

    plan: list[dict] = []
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for (div, season), skeys in sorted(groups.items(), key=group_order):
            group_rows = [r for r in spine
                          if r["Div"] == div and r["Season"] == season]
            payload = get(client, "leagues",
                          {"id": LEAGUES[div][0], "ccode3": LEAGUES[div][1],
                           "season": season_api(season)}, args.delay)
            fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
            matched, rejected = fixture_map_fixed(group_rows, fixtures)
            if len(group_rows) >= 20 and len(matched) < 0.5 * len(group_rows):
                raise RuntimeError(
                    f"implausible match rate for {div} {season}: "
                    f"{len(matched)}/{len(group_rows)} — aborting")
            by_key = {spine_key(it["csv"]): it for it in matched}
            rejected_by_key = {}
            for rec in rejected:
                if rec.get("csv_home"):
                    rejected_by_key[key_of(div, rec["date"], rec["csv_home"],
                                           rec["csv_away"])] = rec.get("status", "rejected")
            for skey in skeys:
                kind, row = jobs[skey]
                item = by_key.get(skey)
                if item is None:
                    if kind == "gap":
                        gaps_out.append({"div": div, "season": season,
                                         "date": row["Date"], "home": row["HomeTeam"],
                                         "away": row["AwayTeam"],
                                         "reason": "fotmob fixture " +
                                                   rejected_by_key.get(skey, "not found for date")})
                    processed.add(skey)
                    continue
                mid = item["mapping"]["fotmob_match_id"]
                if mid in done_ids or mid in labelled_ids:
                    processed.add(skey)
                    continue
                plan.append({"spine_key": skey, "kind": kind, "div": div,
                             "season": season, "date": row["Date"],
                             "home": row["HomeTeam"], "away": row["AwayTeam"],
                             "hst": row["HST"], "ast": row["AST"],
                             "fotmob_match_id": mid})
    if args.plan_limit:
        plan = plan[:args.plan_limit]
    print(f"plan: {len(plan)} matches to fetch "
          f"({sum(1 for p in plan if p['kind'] == 'gap')} gaps, "
          f"{sum(1 for p in plan if p['kind'] == 'sample')} sample)", flush=True)

    def save_checkpoint(finished=False):
        checkpoint.update({"done_ids": sorted(done_ids),
                           "processed": sorted(processed),
                           "errors": errors, "gaps": gaps_out,
                           "finished": finished,
                           "updated_utc": datetime.now(timezone.utc).isoformat()})
        atomic_json(CHECKPOINT, checkpoint)

    def record(outcome: dict) -> None:
        item = outcome["item"]
        skey = item["spine_key"]
        if "label" in outcome:
            label = outcome["label"]
            expected = int(float(item["hst"])) + int(float(item["ast"]))
            sot_ft = (label["sot_1h_h"] + label["sot_1h_a"] +
                      label["sot_2h_h"] + label["sot_2h_a"])
            out_row = {"div": item["div"], "season": item["season"],
                       "date": item["date"], "home": item["home"],
                       "away": item["away"],
                       "fotmob_match_id": item["fotmob_match_id"],
                       "csv_sot_ft": expected, "delta_sot_ft": sot_ft - expected,
                       "shot_count": label["shot_count"],
                       "sot_1h": label["sot_1h_h"] + label["sot_1h_a"],
                       "sot_2h": label["sot_2h_h"] + label["sot_2h_a"],
                       **label, "sot_ft": sot_ft,
                       "quality": ("reconciled" if label["shotmap_complete"] and
                                   sot_ft == expected else
                                   "full_only" if sot_ft == expected else "flagged")}
            (gap_sink if item["kind"] == "gap" else xval_sink).add(out_row)
            done_ids.add(item["fotmob_match_id"])
        else:
            errors.append({"fotmob_match_id": item["fotmob_match_id"],
                           "spine_key": skey, "error": outcome.get("error", "?")})
            if item["kind"] == "gap":
                gaps_out.append({"div": item["div"], "season": item["season"],
                                 "date": item["date"], "home": item["home"],
                                 "away": item["away"],
                                 "reason": "fetch/extract failed: " +
                                           outcome.get("error", "?")})
        processed.add(skey)

    fetched = completed = stops = 0
    recent: list[str] = []
    aborted = False
    retry_items: list[dict] = []
    started = datetime.now(timezone.utc)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_item, item, args.delay): item
                   for item in plan}
        for future in as_completed(futures):
            outcome = future.result()
            completed += 1
            if outcome.get("fetched"):
                fetched += 1
            if "provider_stop" in outcome:
                stops += 1
                recent.append("stop")
            elif "error" in outcome:
                recent.append("error")
                if outcome.get("transient"):
                    retry_items.append(outcome["item"])
                    processed.discard(outcome["item"]["spine_key"])
                    errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
                                   "spine_key": outcome["item"]["spine_key"],
                                   "error": "transient, queued for retry: " +
                                            outcome.get("error", "?")})
                    continue
            else:
                recent.append("ok")
            record(outcome)
            if completed % 25 == 0:
                save_checkpoint()
            if completed % 200 == 0:
                elapsed = (datetime.now(timezone.utc) - started).total_seconds()
                print(f"progress {completed}/{len(plan)} fetched={fetched} "
                      f"errors={len(errors)} stops={stops} "
                      f"{elapsed:.0f}s elapsed", flush=True)
            if len(recent) >= 30 and recent[-30:].count("stop") >= 15:
                aborted = True
                print("ABORT: sustained provider stops (FotMob blocking); "
                      "checkpoint saved — resume slower.", flush=True)
                break
    if retry_items and not aborted:
        print(f"retrying {len(retry_items)} transient failures once", flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(fetch_item, item, args.delay): item
                       for item in retry_items}
            for future in as_completed(futures):
                outcome = future.result()
                if "provider_stop" in outcome:
                    outcome = {**outcome, "error": "provider stop on retry"}
                    outcome.pop("provider_stop", None)
                record(outcome)
    gap_sink.close()
    xval_sink.close()
    if gaps_out:
        with GAPS_FILE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=GAP_FIELDS)
            writer.writeheader()
            writer.writerows(gaps_out)
    remaining = sum(1 for k in jobs if k not in processed)
    save_checkpoint(finished=(remaining == 0 and not aborted))
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    print(json.dumps({"mode": "parallel", "workers": args.workers,
                      "planned": len(plan), "completed": completed,
                      "fetched_http": fetched, "done_total": len(done_ids),
                      "errors": len(errors), "provider_stops": stops,
                      "gaps": len(gaps_out), "remaining_jobs": remaining,
                      "aborted": aborted, "elapsed_s": round(elapsed, 1)},
                     indent=2), flush=True)
    return 3 if aborted else 0


def read_checkpoint() -> dict:
    if not CHECKPOINT.exists():
        return {"done_ids": [], "processed": [], "errors": [], "gaps": [],
                "started_utc": datetime.now(timezone.utc).isoformat()}
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def load_existing_labels(path: Path) -> list[dict]:
    """Read an existing labels CSV, dropping a torn trailing line if present."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = []
    for row in csv.DictReader(lines):
        if None in row.values() or None in row or any(v is None for v in row.values()):
            break
        rows.append(row)
    if len(rows) + 1 != len([l for l in lines if l.strip()]):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=LABEL_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    return rows


class LabelSink:
    def __init__(self, path: Path):
        self.path = path
        self.existing = load_existing_labels(path)
        self.handle = path.open("a", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(self.handle, fieldnames=LABEL_FIELDS)
        if not self.existing and path.stat().st_size == 0:
            self.writer.writeheader()
            self.handle.flush()

    def add(self, row: dict) -> None:
        self.writer.writerow(row)
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def build_jobs(spine: list[dict], covered: set[str]) -> tuple[list[dict], list[dict]]:
    gaps, sample_pool = [], []
    for row in spine:
        if spine_key(row) in covered:
            sample_pool.append(row)
        else:
            gaps.append(row)
    rng = random.Random(SAMPLE_SEED)
    sample = rng.sample(sample_pool, min(SAMPLE_N, len(sample_pool)))
    return gaps, sample


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--batch", type=int, default=500,
                        help="max NEW matchDetails fetches this invocation")
    parser.add_argument("--workers", type=int, default=0,
                        help=">0: parallel plan-then-fetch mode with N workers")
    parser.add_argument("--plan-limit", type=int, default=0,
                        help="parallel mode: cap the fetch plan at N items")
    args = parser.parse_args()
    # Single-instance lock: two drivers sharing the label CSVs / checkpoint
    # corrupt each other's state (observed 2026-11-07).
    import fcntl
    lock_handle = (OUT / "gap_fill.lock").open("w")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another fill_halves_gaps instance holds the lock; exiting")
        return 2
    RAW.mkdir(parents=True, exist_ok=True)
    spine = load_master()
    covered = sofa_keys()
    gap_rows, sample_rows = build_jobs(spine, covered)
    jobs = {}  # spine_key -> (kind, row)
    for row in sample_rows:
        jobs[spine_key(row)] = ("sample", row)
    for row in gap_rows:
        jobs[spine_key(row)] = ("gap", row)
    print(f"spine={len(spine)} sofa_covered={len(covered)} gaps={len(gap_rows)} "
          f"sample={len(sample_rows)}", flush=True)

    if args.workers > 0:
        jobs_all = {}
        for row in sample_rows:
            jobs_all[spine_key(row)] = ("sample", row)
        for row in gap_rows:
            jobs_all[spine_key(row)] = ("gap", row)
        return run_parallel(args, spine, jobs_all, read_checkpoint())

    checkpoint = read_checkpoint()
    done_ids = set(checkpoint.get("done_ids", []))
    processed = set(checkpoint.get("processed", []))
    errors = checkpoint.get("errors", [])
    gaps_out = checkpoint.get("gaps", [])
    gap_sink = LabelSink(GAP_LABELS)
    xval_sink = LabelSink(XVAL_LABELS)
    labelled_ids = {r["fotmob_match_id"] for r in gap_sink.existing + xval_sink.existing}

    # Group jobs by (div, season); cross-validation groups first (small,
    # high information), then gap groups F1 -> SP1 -> E0 -> I1 -> D1.
    groups: dict[tuple[str, str], list[str]] = {}
    for skey, (kind, row) in jobs.items():
        if skey in processed:
            continue
        groups.setdefault((row["Div"], row["Season"]), []).append(skey)

    def group_order(item: tuple[tuple[str, str], list[str]]) -> tuple:
        (div, season), skeys = item
        kinds = {jobs[k][0] for k in skeys}
        return (0 if "sample" in kinds else 1, DIV_PRIORITY[div], season)

    fetched = 0
    # Same proxy-aware client construction as backfill_sot_fotmob.main.
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for (div, season), skeys in sorted(groups.items(), key=group_order):
            group_rows = [row for row in spine
                          if row["Div"] == div and row["Season"] == season]
            try:
                payload = get(client, "leagues",
                              {"id": LEAGUES[div][0], "ccode3": LEAGUES[div][1],
                               "season": season_api(season)}, args.delay)
            except RuntimeError:
                raise
            except Exception as exc:  # league payload unavailable: whole group gaps
                for skey in skeys:
                    kind, row = jobs[skey]
                    if kind == "gap":
                        gaps_out.append({"div": div, "season": season,
                                         "date": row["Date"], "home": row["HomeTeam"],
                                         "away": row["AwayTeam"],
                                         "reason": f"league payload unavailable: {exc!r}"})
                    processed.add(skey)
                continue
            fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
            matched, rejected = fixture_map_fixed(group_rows, fixtures)
            # Sanity guard: a healthy FotMob league payload matches ~all
            # spine rows of the group. A degraded/throttled payload (empty
            # fixture list, missing status flags) once made fixture_map
            # match almost nothing and thousands of jobs were falsely
            # recorded as gaps. Abort loudly instead of marking anything.
            if len(group_rows) >= 20 and len(matched) < 0.5 * len(group_rows):
                raise RuntimeError(
                    f"implausible match rate for {div} {season}: "
                    f"{len(matched)}/{len(group_rows)} spine rows matched from "
                    f"{len(fixtures)} payload fixtures — provider payload "
                    "looks degraded; aborting without marking jobs")
            print(f"group {div} {season}: payload_fixtures={len(fixtures)} "
                  f"matched={len(matched)}/{len(group_rows)} "
                  f"jobs={len(skeys)}", flush=True)
            by_key = {}
            for item in matched:
                by_key[spine_key(item["csv"])] = item
            rejected_by_key = {}
            for rec in rejected:
                if rec.get("csv_home"):
                    rejected_by_key[key_of(div, rec["date"], rec["csv_home"],
                                           rec["csv_away"])] = rec.get("status", "rejected")
            for skey in skeys:
                kind, row = jobs[skey]
                item = by_key.get(skey)
                if item is None:
                    if kind == "gap":
                        gaps_out.append({"div": div, "season": season,
                                         "date": row["Date"], "home": row["HomeTeam"],
                                         "away": row["AwayTeam"],
                                         "reason": "fotmob fixture " +
                                                   rejected_by_key.get(skey, "not found for date")})
                    processed.add(skey)
                    continue
                mid = item["mapping"]["fotmob_match_id"]
                if mid in done_ids or mid in labelled_ids:
                    processed.add(skey)
                    continue
                if fetched >= args.batch:
                    continue
                raw = RAW / f"{div}_{season.replace('/', '-')}_{mid}.json"
                try:
                    if raw.exists():
                        detail = json.loads(raw.read_text(encoding="utf-8"))
                    else:
                        detail = get(client, "matchDetails", {"matchId": mid}, args.delay)
                        fetched += 1
                        tmp = raw.with_suffix(".tmp")
                        tmp.write_text(json.dumps(detail, ensure_ascii=False), encoding="utf-8")
                        tmp.replace(raw)
                    label = extract_halves(detail)
                except RuntimeError:
                    raise
                except Exception as exc:
                    errors.append({"fotmob_match_id": mid, "spine_key": skey,
                                   "error": repr(exc)})
                    if kind == "gap":
                        gaps_out.append({"div": div, "season": season,
                                         "date": row["Date"], "home": row["HomeTeam"],
                                         "away": row["AwayTeam"],
                                         "reason": f"fetch/extract failed: {exc!r}"})
                    processed.add(skey)
                    checkpoint.update({"done_ids": sorted(done_ids),
                                       "processed": sorted(processed),
                                       "errors": errors, "gaps": gaps_out,
                                       "updated_utc": datetime.now(timezone.utc).isoformat()})
                    atomic_json(CHECKPOINT, checkpoint)
                    continue
                expected = int(float(row["HST"])) + int(float(row["AST"]))
                sot_ft = (label["sot_1h_h"] + label["sot_1h_a"] +
                          label["sot_2h_h"] + label["sot_2h_a"])
                out_row = {"div": div, "season": season, "date": row["Date"],
                           "home": row["HomeTeam"], "away": row["AwayTeam"],
                           "fotmob_match_id": mid, "csv_sot_ft": expected,
                           "delta_sot_ft": sot_ft - expected,
                           "shot_count": label["shot_count"],
                           "sot_1h": label["sot_1h_h"] + label["sot_1h_a"],
                           "sot_2h": label["sot_2h_h"] + label["sot_2h_a"],
                           **label, "sot_ft": sot_ft,
                           "quality": ("reconciled" if label["shotmap_complete"] and
                                       sot_ft == expected else
                                       "full_only" if sot_ft == expected else "flagged")}
                (gap_sink if kind == "gap" else xval_sink).add(out_row)
                done_ids.add(mid)
                processed.add(skey)
                checkpoint.update({"done_ids": sorted(done_ids),
                                   "processed": sorted(processed),
                                   "errors": errors, "gaps": gaps_out,
                                   "updated_utc": datetime.now(timezone.utc).isoformat()})
                atomic_json(CHECKPOINT, checkpoint)
            if fetched >= args.batch:
                break
    gap_sink.close()
    xval_sink.close()
    # Refresh the remaining-gaps file from checkpoint state.
    if gaps_out:
        with GAPS_FILE.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=GAP_FIELDS)
            writer.writeheader()
            writer.writerows(gaps_out)
    remaining = sum(1 for k in jobs if k not in processed)
    finished = remaining == 0
    checkpoint.update({"done_ids": sorted(done_ids), "processed": sorted(processed),
                       "errors": errors, "gaps": gaps_out, "finished": finished,
                       "updated_utc": datetime.now(timezone.utc).isoformat()})
    atomic_json(CHECKPOINT, checkpoint)
    print(json.dumps({"fetched_this_run": fetched, "done_total": len(done_ids),
                      "processed_total": len(processed), "gaps": len(gaps_out),
                      "errors": len(errors), "remaining_jobs": remaining,
                      "finished": finished}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
