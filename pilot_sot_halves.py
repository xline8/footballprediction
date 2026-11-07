"""Pilot: match FotMob shotmap halves to football-data E0 2024/25."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import httpx

BASE = Path(__file__).resolve().parent
DATA = BASE / "all_matches_clean.csv"
OUT = BASE / "data_enrichment" / "pilot_sot" / "E0_2024-25"
SUMMARY = OUT / "summary.json"

API = "https://www.fotmob.com/api/data"
LEAGUE = {"id": 47, "ccode3": "ENG", "season": "2024/2025"}
HEADERS = {
    "Accept": "application/json",
    "Referer": "https://www.fotmob.com/",
    "User-Agent": os.environ.get(
        "FOOTBALL_ENRICHMENT_USER_AGENT",
        "football-data-personal-research/1.0",
    ),
}
ALIASES = {
    "man united": "manchester united",
    "man city": "manchester city",
    "nottm forest": "nottingham forest",
    "nott m forest": "nottingham forest",
    "sheffield utd": "sheffield united",
    "west ham": "west ham united",
    "wolves": "wolverhampton wanderers",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return ALIASES.get(value, value)


def similarity(left: str, right: str) -> float:
    a, b = norm(left), norm(right)
    if a == b:
        return 1.0
    ta, tb = set(a.split()), set(b.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return 0.96
    return SequenceMatcher(None, a, b).ratio()


def get(client: httpx.Client, path: str, params: dict, delay: float) -> dict:
    time.sleep(delay)
    response = client.get(f"{API}/{path}", params=params)
    if response.status_code == 429:
        retry_after = float(response.headers.get("Retry-After", "60"))
        raise RuntimeError(f"HTTP 429; Retry-After={retry_after:g}s")
    response.raise_for_status()
    return response.json()


def load_csv() -> list[dict]:
    with DATA.open(encoding="utf-8", newline="") as handle:
        return [
            row for row in csv.DictReader(handle)
            if row.get("Div") == "E0" and row.get("Season") == "2024/25"
        ]


def match_rows(csv_rows: list[dict], fixtures: list[dict]) -> tuple[list[dict], list[dict]]:
    by_date: dict[str, list[dict]] = {}
    for row in csv_rows:
        by_date.setdefault(row["Date"], []).append(row)
    matched, unmatched = [], []
    used_csv: set[int] = set()
    for fixture in fixtures:
        status = fixture.get("status") or {}
        date = str(status.get("utcTime") or "")[:10]
        home = (fixture.get("home") or {}).get("name") or ""
        away = (fixture.get("away") or {}).get("name") or ""
        candidates = [
            (index, row) for index, row in enumerate(by_date.get(date, []))
            if id(row) not in used_csv
        ]
        if not candidates:
            unmatched.append({"fotmob_id": str(fixture.get("id")), "reason": "date"})
            continue
        ranked = sorted(
            (
                similarity(row["HomeTeam"], home)
                + similarity(row["AwayTeam"], away),
                index,
                row,
            )
            for index, row in candidates
        )
        score, _, best = ranked[-1]
        second = ranked[-2][0] if len(ranked) > 1 else 0.0
        status = "exact" if score == 2.0 else "fuzzy"
        if score < 1.60:
            status = "unmatched"
        elif len(ranked) > 1 and score - second < 0.10:
            status = "ambiguous"
        if status in ("unmatched", "ambiguous"):
            unmatched.append({
                "fotmob_id": str(fixture.get("id")), "reason": status,
                "fotmob_home": home, "fotmob_away": away,
                "csv_home": best["HomeTeam"], "csv_away": best["AwayTeam"],
                "score": round(score, 3), "second_score": round(second, 3),
            })
            continue
        used_csv.add(id(best))
        matched.append({
            "fixture": fixture, "csv": best, "match_score": round(score, 3),
            "mapping_status": status,
        })
    return matched, unmatched


def extract(payload: dict) -> dict:
    content = payload.get("content") or {}
    shotmap = content.get("shotmap") or {}
    shots = shotmap.get("shots")
    if not isinstance(shots, list):
        raise ValueError("shotmap.shots missing or not a list")
    periods = {"FirstHalf": 0, "SecondHalf": 0}
    seen_periods = set()
    on_target_without_period = 0
    blocked_on_target = 0
    for shot in shots:
        if shot.get("isOwnGoal") or shot.get("isOnTarget") is not True:
            continue
        period = shot.get("period")
        if period in periods:
            seen_periods.add(period)
        if shot.get("isBlocked") is True:
            blocked_on_target += 1
            continue
        if period in periods:
            periods[period] += 1
        else:
            on_target_without_period += 1
    return {
        "shot_count": len(shots),
        "sot_1h": periods["FirstHalf"],
        "sot_2h": periods["SecondHalf"],
        "sot_ft": periods["FirstHalf"] + periods["SecondHalf"],
        "blocked_on_target": blocked_on_target,
        "on_target_without_standard_period": on_target_without_period,
        "periods": sorted({str(s.get("period")) for s in shots}),
        "shotmap_complete": bool(shots) and not on_target_without_period and
        seen_periods == set(periods),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    csv_rows = load_csv()
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True) as client:
        league = get(client, "leagues", LEAGUE, 0)
        fixtures = (league.get("fixtures") or {}).get("allMatches") or []
        fixtures = [f for f in fixtures if (f.get("status") or {}).get("finished")]
        matched, unmatched = match_rows(csv_rows, fixtures)
        results, errors = [], []
        for index, item in enumerate(matched, 1):
            fixture = item["fixture"]
            mid = str(fixture.get("id"))
            cache = OUT / f"{mid}.json"
            try:
                if cache.exists():
                    payload = json.loads(cache.read_text(encoding="utf-8"))
                else:
                    payload = get(client, "matchDetails", {"matchId": mid}, args.delay)
                    tmp = cache.with_suffix(".tmp")
                    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                    os.replace(tmp, cache)
                label = extract(payload)
                row = item["csv"]
                expected = int(float(row["HST"])) + int(float(row["AST"]))
                results.append({
                    "div": row["Div"], "season": row["Season"], "date": row["Date"],
                    "home": row["HomeTeam"], "away": row["AwayTeam"],
                    "fotmob_match_id": mid, "match_score": item["match_score"],
                    "mapping_status": item["mapping_status"],
                    "csv_sot_ft": expected, "delta_sot_ft": label["sot_ft"] - expected,
                    **label,
                    "total_matches": 1,
                    "matches_csv_total": label["sot_ft"] == expected,
                    "within_one_csv_total": abs(label["sot_ft"] - expected) <= 1,
                })
            except Exception as exc:
                errors.append({"fotmob_id": mid, "error": repr(exc)})
            if index % 25 == 0 or index == len(matched):
                print(f"processed {index}/{len(matched)}", flush=True)
    valid = [r for r in results if r["shot_count"] > 0]
    compared = [r for r in valid if r["csv_sot_ft"] is not None]
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pilot": "E0 2024/25",
        "csv_rows": len(csv_rows),
        "fotmob_finished_fixtures": len(fixtures),
        "matched": len(matched),
        "mapping_exact": sum(r["mapping_status"] == "exact" for r in results),
        "mapping_fuzzy": sum(r["mapping_status"] == "fuzzy" for r in results),
        "ambiguous": sum(x["reason"] == "ambiguous" for x in unmatched),
        "unmatched": sum(x["reason"] == "unmatched" for x in unmatched),
        "date_unmatched": sum(x["reason"] == "date" for x in unmatched),
        "details_ok": len(results),
        "details_errors": len(errors),
        "shotmap_nonempty": len(valid),
        "shotmap_empty": len(results) - len(valid),
        "shotmap_complete": sum(r["shotmap_complete"] for r in valid),
        "shotmap_incomplete": sum(not r["shotmap_complete"] for r in valid),
        "sot_total_equal_csv": sum(r["matches_csv_total"] for r in compared),
        "sot_total_within_one_csv": sum(r["within_one_csv_total"] for r in compared),
        "sot_total_mismatch_csv": sum(not r["matches_csv_total"] for r in compared),
        "delta_distribution": dict(sorted(
            ((str(delta), sum(r["delta_sot_ft"] == delta for r in compared))
             for delta in {r["delta_sot_ft"] for r in compared}),
            key=lambda item: int(item[0]),
        )),
        "period_values": sorted({p for r in results for p in r["periods"]}),
        "unmatched_rows": unmatched,
        "errors": errors,
    }
    with (OUT / "sot_halves.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = list(results[0]) if results else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    with (OUT / "mismatches.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = list(results[0]) if results else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(r for r in results if not r["matches_csv_total"])
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
