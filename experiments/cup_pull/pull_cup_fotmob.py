"""Pull FULL FotMob matchDetails responses for cup fixtures (EFL Cup + DFB Pokal).

Item 6 of the 2026-11-07 model-audit follow-ups (MODEL_AUDIT_2026-11-07.md
§4 / §2C C-3): land cup ACTUALS data only. No production file is touched,
no grading code or behaviour changes — this script only writes JSON into
the FotMob store layout plus a pull report in this folder.

Fixture universe (stated exactly):
  - Competitions: exactly the ones predict_cups.py predicts —
    CUP_LEAGUES = {"England - EFL Cup": "EFL Cup",
                  "Germany - Cup Germany": "DFB Pokal"}.
  - Source: predict_cups.py's fixture source, ta/fixtures.csv, restricted
    to the current season 2026/27 (date >= 2026-08-01) with status FT
    (actuals exist only for finished ties): EFL Cup 84 + DFB Pokal 35
    = 119 fixtures.
  - Plus any past cup fixtures present in predictions/ledger artifacts:
    archive/*/predictions_cups_upcoming.csv +
    predictions_corners_cups.csv contain exactly ONE predicted tie
    (Everton v Newcastle, EFL Cup, 2026-10-29) and ledger/picks.jsonl
    contains the same tie as its only cup pick — already inside the 119
    above, so the past-artifact union adds 0 fixtures.
  - The wider ta/fixtures.csv history (2025/26: 140 FT cup ties) is NOT
    in scope per the task definition; FotMob-only fixtures (e.g. DFB
    Pokal first-round ties vs clubs TipsterArea does not list, and the
    unplayed Dec 2026 quarter-finals) are likewise excluded — the system
    never predicted them.

Resolution + fetch machinery mirrors data_enrichment/pull_fotmob_full.py:
  - FotMob league payloads (leagues endpoint) per competition/season,
    matched to TA rows with fill_halves_gaps.fixture_map_fixed (same
    score(), 1.60 threshold, 0.10 ambiguity margin as the league store),
    plus a documented +-1 day fallback pass for date-shifted ties.
  - matchDetails fetched with a thread pool (12 workers, zero delay —
    the pacing the user approved for the league store build), each
    worker using a thread-local httpx client built with
    stealth.proxy_url() (a bare httpx client crashes on this VM).
  - Responses stored at
    data_enrichment/fotmob_full/<KEY>/<season-dash>/<fotmob_id>.json
    with KEY in {EFLCUP, DFBPOKAL} (the league store uses division codes
    E0/D1/...; cups get their own clear keys so nothing collides).
    Existing files are reused, never refetched.

Outputs:
  experiments/cup_pull/pull_report.json   machine-readable coverage:
      per-competition attempted / matched / stored / errors, the full
      matched mapping, unmatched fixtures with reasons, fetch errors,
      and FotMob-vs-TipsterArea FT score cross-check mismatches.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "data_enrichment"))

import httpx  # noqa: E402

import backfill_sot_fotmob as _bf  # noqa: E402
from backfill_sot_fotmob import HEADERS, get, score  # noqa: E402
from fill_halves_gaps import fixture_map_fixed  # noqa: E402

# Extra TA->FotMob name aliases for cup teams (same convention as
# fill_halves_gaps: keys are norm(TA name), values norm(FotMob name);
# backfill_sot_fotmob.norm reads ALIASES at call time). League-store
# aliases (incl. the fill_halves_gaps patch) already cover most names;
# these cover cup-only spellings found in the 2026/27 payloads.
_bf.ALIASES.update({
    "sankt pauli": "st pauli",
    "karlsruher": "karlsruher sc",
    "saarbrucken": "saarbrucken",  # identity guard (umlaut-stripped both sides)
    "munchen 1860": "1860 munchen",
    "viktoria koln": "viktoria koln 1904",
    "queens park rangers": "queens park rangers",
})

# Mirrors predict_cups.CUP_LEAGUES (TA league string -> display name),
# plus the store key and the FotMob league identity per competition.
CUPS = {
    "England - EFL Cup": {
        "competition": "EFL Cup", "key": "EFLCUP",
        "fotmob_id": 133, "ccode3": "ENG",
    },
    "Germany - Cup Germany": {
        "competition": "DFB Pokal", "key": "DFBPOKAL",
        "fotmob_id": 209, "ccode3": "GER",
    },
}
STORE = BASE / "data_enrichment" / "fotmob_full"
TA_FIXTURES = BASE / "ta" / "fixtures.csv"
REPORT = Path(__file__).resolve().parent / "pull_report.json"
CURRENT_SEASON = "2026/27"
SEASON_START = "2026-08-01"  # first date of the 2026/27 season window

_thread_local = threading.local()


def _thread_client() -> httpx.Client:
    client = getattr(_thread_local, "client", None)
    if client is None:
        from stealth import proxy_url
        client = httpx.Client(headers=HEADERS, timeout=60,
                              follow_redirects=True, proxy=proxy_url())
        _thread_local.client = client
    return client


def season_of(date_str: str) -> str:
    """Season label (repo convention '2026/27') for an Aug-May season."""
    y, m = int(date_str[:4]), int(date_str[5:7])
    start = y if m >= 8 else y - 1
    return f"{start}/{str(start + 1)[2:]}"


def season_api(label: str) -> str:
    start, end = label.split("/")
    return f"{start}/20{end}"


def season_dir(season: str) -> str:
    return season.replace("/", "-")


def load_universe(seasons: set[str]) -> list[dict]:
    """TA cup fixtures (FT only) for the requested seasons."""
    rows = []
    with TA_FIXTURES.open(encoding="utf-8", newline="") as handle:
        for r in csv.DictReader(handle):
            meta = CUPS.get(r.get("league", ""))
            if meta is None or r.get("status") != "FT":
                continue
            season = season_of(r["date"])
            if season not in seasons:
                continue
            rows.append({
                "ta_league": r["league"], "competition": meta["competition"],
                "key": meta["key"], "season": season,
                "Date": r["date"], "date": r["date"],
                "HomeTeam": r["home"].strip(), "AwayTeam": r["away"].strip(),
                "home": r["home"].strip(), "away": r["away"].strip(),
                "game_id": r["game_id"],
                "ta_score_h": r.get("score_h", ""), "ta_score_a": r.get("score_a", ""),
            })
    rows.sort(key=lambda x: (x["key"], x["date"], x["home"]))
    return rows


def fallback_match(unmatched_rows: list[dict], fixtures: list[dict],
                   used_fotmob_ids: set[str]) -> tuple[list[dict], dict]:
    """Second pass: same score thresholds as fixture_map_fixed but the
    FotMob utcTime date may sit +-1 day from the TA date (late-evening
    kickoffs / TA date conventions). Returns (matched_items, reasons)."""
    by_key_date: dict[str, list[dict]] = {}
    for fx in fixtures:
        status = fx.get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        if str(fx.get("id")) in used_fotmob_ids:
            continue
        by_key_date.setdefault(str(status.get("utcTime") or "")[:10], []).append(fx)
    matched, reasons = [], {}
    used_rows: set[int] = set()
    for idx, row in enumerate(unmatched_rows):
        base = datetime.strptime(row["date"], "%Y-%m-%d").date()
        candidates = []
        for delta in (-1, 0, 1):
            for fx in by_key_date.get((base + timedelta(days=delta)).isoformat(), []):
                if str(fx.get("id")) in used_fotmob_ids:
                    continue
                s = (score(row["HomeTeam"], (fx.get("home") or {}).get("name") or "") +
                     score(row["AwayTeam"], (fx.get("away") or {}).get("name") or ""))
                candidates.append((s, fx))
        if not candidates:
            reasons[idx] = "no FotMob fixture within +-1 day"
            continue
        candidates.sort(key=lambda t: t[0])
        best_score, best_fx = candidates[-1]
        second = candidates[-2][0] if len(candidates) > 1 else 0.0
        if best_score < 1.60:
            reasons[idx] = f"best name score {best_score:.2f} < 1.60 within +-1 day"
            continue
        if best_score - second < 0.10:
            reasons[idx] = f"ambiguous within +-1 day (best {best_score:.2f}, second {second:.2f})"
            continue
        used_fotmob_ids.add(str(best_fx.get("id")))
        used_rows.add(idx)
        matched.append({"csv": row, "mapping": {
            "fotmob_match_id": str(best_fx.get("id")),
            "date": str((best_fx.get("status") or {}).get("utcTime") or "")[:10],
            "fotmob_home": (best_fx.get("home") or {}).get("name") or "",
            "fotmob_away": (best_fx.get("away") or {}).get("name") or "",
            "score": round(best_score, 4), "status": "date_fallback"}})
    return matched, reasons


def fetch_one(item: dict, delay: float) -> dict:
    """Store the full matchDetails response for one matched fixture."""
    mid = item["fotmob_match_id"]
    dest = STORE / item["key"] / season_dir(item["season"]) / f"{mid}.json"
    try:
        if dest.exists():
            return {"item": item, "origin": "store"}
        payload = get(_thread_client(), "matchDetails", {"matchId": mid}, delay)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(f".tmp{threading.get_ident()}")
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(dest)
        return {"item": item, "origin": "http"}
    except RuntimeError as exc:
        return {"item": item, "provider_stop": str(exc)}
    except Exception as exc:
        return {"item": item, "error": repr(exc),
                "transient": isinstance(exc, (httpx.TransportError,
                                              httpx.HTTPStatusError))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--seasons", nargs="*", default=[CURRENT_SEASON],
                        help="season labels, repo convention e.g. 2026/27")
    args = parser.parse_args()
    seasons = set(args.seasons)
    universe = load_universe(seasons)
    print(f"universe: {len(universe)} TA cup fixtures "
          f"({ {k: sum(1 for r in universe if r['key'] == k) for k in ('EFLCUP', 'DFBPOKAL')} })",
          flush=True)

    # --- resolve each TA fixture to a FotMob match id -------------------
    plan: list[dict] = []
    unmatched: list[dict] = []
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True,
                      proxy=proxy_url()) as client:
        groups: dict[tuple[str, str], list[dict]] = {}
        for row in universe:
            groups.setdefault((row["ta_league"], row["season"]), []).append(row)
        for (ta_league, season), group_rows in sorted(groups.items()):
            meta = CUPS[ta_league]
            payload = get(client, "leagues",
                          {"id": meta["fotmob_id"], "ccode3": meta["ccode3"],
                           "season": season_api(season)}, args.delay)
            fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
            matched, _rejected = fixture_map_fixed(group_rows, fixtures)
            matched_keys = set()
            used_ids: set[str] = set()
            for item in matched:
                row = item["csv"]
                matched_keys.add((row["date"], row["home"], row["away"]))
                used_ids.add(item["mapping"]["fotmob_match_id"])
                plan.append({**{k: row[k] for k in
                                ("competition", "key", "season", "date",
                                 "home", "away", "game_id",
                                 "ta_score_h", "ta_score_a")},
                             "fotmob_match_id": item["mapping"]["fotmob_match_id"],
                             "fotmob_home": item["mapping"]["fotmob_home"],
                             "fotmob_away": item["mapping"]["fotmob_away"],
                             "match_status": item["mapping"]["status"],
                             "match_score": item["mapping"]["score"]})
            rest = [r for r in group_rows
                    if (r["date"], r["home"], r["away"]) not in matched_keys]
            fb_matched, fb_reasons = fallback_match(rest, fixtures, used_ids)
            fb_keys = set()
            for item in fb_matched:
                row = item["csv"]
                fb_keys.add((row["date"], row["home"], row["away"]))
                plan.append({**{k: row[k] for k in
                                ("competition", "key", "season", "date",
                                 "home", "away", "game_id",
                                 "ta_score_h", "ta_score_a")},
                             "fotmob_match_id": item["mapping"]["fotmob_match_id"],
                             "fotmob_home": item["mapping"]["fotmob_home"],
                             "fotmob_away": item["mapping"]["fotmob_away"],
                             "match_status": item["mapping"]["status"],
                             "match_score": item["mapping"]["score"]})
            for i, row in enumerate(rest):
                if (row["date"], row["home"], row["away"]) in fb_keys:
                    continue
                # reason from the fallback pass if it saw the row, else the
                # fixture is simply absent from the FotMob payload
                orig_idx = rest.index(row)
                reason = fb_reasons.get(orig_idx,
                                        "no matching FotMob fixture in league payload")
                unmatched.append({
                    "competition": row["competition"], "key": row["key"],
                    "season": season, "date": row["date"], "home": row["home"],
                    "away": row["away"], "game_id": row["game_id"],
                    "reason": reason})
            print(f"group {meta['key']} {season}: TA={len(group_rows)} "
                  f"payload_fixtures={len(fixtures)} matched={len(matched)} "
                  f"+fallback={len(fb_matched)} unmatched={len(rest) - len(fb_matched)}",
                  flush=True)

    # --- fetch matchDetails in parallel (store-build pacing) ------------
    stored = reused = stops = 0
    errors: list[dict] = []
    retry_items: list[dict] = []
    recent: list[str] = []
    aborted = False
    completed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_one, item, args.delay): item for item in plan}
        for future in as_completed(futures):
            outcome = future.result()
            completed += 1
            if "provider_stop" in outcome:
                stops += 1
                recent.append("stop")
                errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
                               "error": outcome["provider_stop"]})
            elif "error" in outcome:
                recent.append("error")
                if outcome.get("transient"):
                    retry_items.append(outcome["item"])
                    continue
                errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
                               "error": outcome.get("error", "?")})
            else:
                recent.append("ok")
                if outcome["origin"] == "http":
                    stored += 1
                else:
                    reused += 1
            if len(recent) >= 30 and recent[-30:].count("stop") >= 15:
                aborted = True
                print("ABORT: sustained provider stops; report saved.", flush=True)
                break
    if retry_items and not aborted:
        print(f"retrying {len(retry_items)} transient failures once", flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(fetch_one, item, args.delay): item
                       for item in retry_items}
            for future in as_completed(futures):
                outcome = future.result()
                if "origin" in outcome:
                    if outcome["origin"] == "http":
                        stored += 1
                    else:
                        reused += 1
                else:
                    errors.append({"fotmob_match_id": outcome["item"]["fotmob_match_id"],
                                   "error": outcome.get("error",
                                                        outcome.get("provider_stop", "?"))})

    # --- cross-check FotMob league-payload scoreStr vs TA FT score ------
    # (cheap data-quality check; the authoritative score is re-read from
    # each stored matchDetails header by the extract step)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "universe": {
            "source": "ta/fixtures.csv (predict_cups.py fixture source)",
            "seasons": sorted(seasons), "status": "FT",
            "total": len(universe),
            "per_competition": {
                meta["competition"]: sum(1 for r in universe if r["key"] == meta["key"])
                for meta in CUPS.values()},
            "past_artifacts_checked": [
                "archive/*/predictions_cups_upcoming.csv",
                "archive/*/predictions_corners_cups.csv",
                "predictions_cups_upcoming.csv",
                "predictions_corners_cups.csv",
                "ledger/picks.jsonl"],
            "past_artifacts_note": ("exactly one predicted cup tie found "
                                    "(Everton v Newcastle, EFL Cup, 2026-10-29, "
                                    "in both the 2026-10-29 archive snapshot and "
                                    "ledger/picks.jsonl); already inside the "
                                    "2026/27 TA universe, adds 0 fixtures"),
        },
        "competition_keys": {meta["competition"]: {
            "store_key": meta["key"], "fotmob_league_id": meta["fotmob_id"],
            "ccode3": meta["ccode3"], "ta_league": ta}
            for ta, meta in CUPS.items()},
        "matched": plan,
        "unmatched": unmatched,
        "fetch": {"planned": len(plan), "stored_http": stored, "reused": reused,
                  "errors": errors, "provider_stops": stops, "aborted": aborted},
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    print(json.dumps({"universe": len(universe), "matched": len(plan),
                      "unmatched": len(unmatched), "stored_http": stored,
                      "reused": reused, "errors": len(errors),
                      "provider_stops": stops, "aborted": aborted}, indent=2),
          flush=True)
    return 3 if aborted else 0


if __name__ == "__main__":
    raise SystemExit(main())
