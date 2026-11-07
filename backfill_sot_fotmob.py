"""Resumable FotMob half-by-half shots-on-target backfill."""
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
MASTER = BASE / "all_matches_clean.csv"
OUT = BASE / "data_enrichment" / "sot_backfill"
RAW = OUT / "raw"
LABELS = OUT / "sot_labels.csv"
MAPPING = OUT / "match_mapping.csv"
CHECKPOINT = OUT / "checkpoint.json"
API = "https://www.fotmob.com/api/data"
LEAGUES = {
    "E0": (47, "ENG"), "SP1": (87, "ESP"), "D1": (54, "GER"),
    "I1": (55, "ITA"), "F1": (53, "FRA"),
}
ALIASES = {
    "man united": "manchester united", "man city": "manchester city",
    "nottm forest": "nottingham forest", "nott m forest": "nottingham forest",
    "west ham": "west ham united", "wolves": "wolverhampton wanderers",
}
HEADERS = {"Accept": "application/json", "Referer": "https://www.fotmob.com/",
           "User-Agent": os.environ.get("FOOTBALL_ENRICHMENT_USER_AGENT",
                                         "football-data-personal-research/1.0")}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return ALIASES.get(re.sub(r"[^a-z0-9]+", " ", value).strip(),
                       re.sub(r"[^a-z0-9]+", " ", value).strip())


def score(left: str, right: str) -> float:
    a, b = norm(left), norm(right)
    if a == b:
        return 1.0
    ta, tb = set(a.split()), set(b.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return 0.96
    return SequenceMatcher(None, a, b).ratio()


def atomic_json(path: Path, value: object) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_master() -> list[dict]:
    with MASTER.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle)
                if row.get("Div") in LEAGUES and row.get("Date") and row.get("HST") and row.get("AST")]


def seasons(rows: list[dict], only: set[str] | None) -> list[str]:
    values = {row["Season"] for row in rows}
    return sorted(value for value in values if only is None or value in only)


def season_param(label: str) -> str:
    match = re.fullmatch(r"(\d{4})/(\d{2})", label)
    if not match:
        raise ValueError(f"unsupported season: {label}")
    return f"{match.group(1)}/{int(match.group(1)[:2] + match.group(2)) + 2000 - int(match.group(1)) + int(match.group(1)) - 2000:02d}"


def season_api(label: str) -> str:
    start, end = label.split("/")
    return f"{start}/20{end}"


def get(client: httpx.Client, path: str, params: dict, delay: float) -> dict:
    if delay:
        time.sleep(delay)
    response = client.get(f"{API}/{path}", params=params)
    if response.status_code in (401, 403, 429):
        raise RuntimeError(f"provider stopped: HTTP {response.status_code}")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(f"unexpected {path} payload")
    return payload


def fixture_map(rows: list[dict], fixtures: list[dict]) -> tuple[list[dict], list[dict]]:
    by_date: dict[str, list[dict]] = {}
    for row in rows:
        by_date.setdefault(row["Date"], []).append(row)
    matched, rejected = [], []
    used: set[int] = set()
    for fixture in fixtures:
        status = fixture.get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        date = str(status.get("utcTime") or "")[:10]
        home = (fixture.get("home") or {}).get("name") or ""
        away = (fixture.get("away") or {}).get("name") or ""
        candidates = [(i, row) for i, row in enumerate(by_date.get(date, [])) if i not in used]
        ranked = sorted((score(row["HomeTeam"], home) + score(row["AwayTeam"], away), i, row)
                        for i, row in candidates)
        if not ranked:
            rejected.append({"fotmob_id": str(fixture.get("id")), "reason": "date"})
            continue
        best_score, index, row = ranked[-1]
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


def _stats_sot(content: dict) -> dict:
    periods = (content.get("stats") or {}).get("Periods") or {}
    values = {}
    for period, payload in periods.items():
        for section in (payload or {}).get("stats", []):
            for stat in section.get("stats", []):
                if stat.get("key") == "ShotsOnTarget":
                    raw = stat.get("stats") or []
                    if len(raw) == 2 and all(isinstance(value, (int, float)) for value in raw):
                        values[period] = [int(raw[0]), int(raw[1])]
                        break
            if period in values:
                break
    if "All" not in values:
        raise ValueError("missing ShotsOnTarget in match stats")
    return {
        "shot_count": 0,
        "sot_1h": sum(values["FirstHalf"]) if "FirstHalf" in values else None,
        "sot_2h": sum(values["SecondHalf"]) if "SecondHalf" in values else None,
        "sot_ft": sum(values["All"]),
        "blocked_on_target": None,
        "shotmap_complete": "FirstHalf" in values and "SecondHalf" in values,
        "label_source": "stats",
    }


def extract(payload: dict) -> dict:
    content = payload.get("content") or {}
    shots = (content.get("shotmap") or {}).get("shots")
    if isinstance(shots, list) and shots:
        counts = {"FirstHalf": 0, "SecondHalf": 0}
        blocked = 0
        invalid = 0
        for shot in shots:
            if shot.get("isOwnGoal") or shot.get("isOnTarget") is not True:
                continue
            if shot.get("isBlocked") is True:
                blocked += 1
                continue
            period = shot.get("period")
            if period in counts:
                counts[period] += 1
            else:
                invalid += 1
        if invalid:
            raise ValueError(f"on-target shot without standard period: {invalid}")
        return {"shot_count": len(shots), "sot_1h": counts["FirstHalf"],
                "sot_2h": counts["SecondHalf"], "sot_ft": sum(counts.values()),
                "blocked_on_target": blocked, "shotmap_complete": True,
                "label_source": "shotmap"}
    return _stats_sot(content)


def read_checkpoint() -> dict:
    if not CHECKPOINT.exists():
        return {"done": [], "errors": [], "mapping": [], "started_utc": datetime.now(timezone.utc).isoformat()}
    return json.loads(CHECKPOINT.read_text(encoding="utf-8"))


def write_outputs(labels: list[dict], mapping: list[dict], errors: list[dict]) -> None:
    if labels:
        with LABELS.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(labels[0]))
            writer.writeheader(); writer.writerows(labels)
    if mapping:
        fields = sorted({key for row in mapping for key in row})
        with MAPPING.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader(); writer.writerows(mapping)
    atomic_json(OUT / "summary.json", {"labels": len(labels), "mapping": len(mapping),
                                       "errors": len(errors), "updated_utc": datetime.now(timezone.utc).isoformat()})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--batch", type=int, default=500)
    parser.add_argument("--seasons", nargs="*")
    args = parser.parse_args()
    for path in (RAW,):
        path.mkdir(parents=True, exist_ok=True)
    rows = load_master()
    wanted = set(args.seasons) if args.seasons else None
    checkpoint = read_checkpoint()
    done = set(checkpoint.get("done", []))
    errors = checkpoint.get("errors", [])
    labels = []
    mapping = checkpoint.get("mapping", [])
    with LABELS.open(encoding="utf-8", newline="") if LABELS.exists() else open(os.devnull) as handle:
        labels = list(csv.DictReader(handle)) if LABELS.exists() else []
    # Client via the explicit egress proxy (stealth.proxy_url), not a bare
    # httpx.Client: on this VM a bare client crashes parsing the proxy env
    # (no_proxy IPv6 entries) before any request leaves — same fix as
    # fotmob_fixtures._make_client.
    from stealth import proxy_url
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for div in sorted(LEAGUES):
            div_rows = [row for row in rows if row["Div"] == div and row["Season"] in seasons(rows, wanted)]
            for season in seasons(div_rows, wanted):
                payload = get(client, "leagues", {"id": LEAGUES[div][0], "ccode3": LEAGUES[div][1],
                                                    "season": season_api(season)}, args.delay)
                fixtures = (payload.get("fixtures") or {}).get("allMatches") or []
                matched, rejected = fixture_map([row for row in div_rows if row["Season"] == season], fixtures)
                mapping.extend(item["mapping"] for item in matched); mapping.extend(rejected)
                for item in matched:
                    mid = item["mapping"]["fotmob_match_id"]
                    if mid in done or len(done) >= args.batch:
                        continue
                    raw = RAW / f"{div}_{season.replace('/', '-')}_{mid}.json"
                    try:
                        if raw.exists():
                            detail = json.loads(raw.read_text(encoding="utf-8"))
                        else:
                            detail = get(client, "matchDetails", {"matchId": mid}, args.delay)
                            tmp = raw.with_suffix(".tmp")
                            tmp.write_text(json.dumps(detail, ensure_ascii=False), encoding="utf-8")
                            os.replace(tmp, raw)
                        label = extract(detail)
                        row = item["csv"]
                        expected = int(float(row["HST"])) + int(float(row["AST"]))
                        labels.append({"div": div, "season": season, "date": row["Date"],
                                       "home": row["HomeTeam"], "away": row["AwayTeam"],
                                       "fotmob_match_id": mid, "csv_sot_ft": expected,
                                       "delta_sot_ft": label["sot_ft"] - expected, **label,
                                       "quality": (
                                           "reconciled" if label["shotmap_complete"] and
                                           label["sot_ft"] == expected else
                                           "full_only" if label["sot_ft"] == expected else
                                           "flagged")})
                        done.add(mid)
                    except Exception as exc:
                        errors.append({"fotmob_match_id": mid, "error": repr(exc)})
                    checkpoint.update({"done": sorted(done), "errors": errors, "mapping": mapping,
                                       "updated_utc": datetime.now(timezone.utc).isoformat()})
                    atomic_json(CHECKPOINT, checkpoint)
                    write_outputs(labels, mapping, errors)
                if len(done) >= args.batch:
                    print(f"batch complete: {len(done)} labels", flush=True)
                    return 0
    checkpoint.update({"done": sorted(done), "errors": errors, "mapping": mapping,
                       "finished_utc": datetime.now(timezone.utc).isoformat()})
    atomic_json(CHECKPOINT, checkpoint); write_outputs(labels, mapping, errors)
    print(json.dumps({"labels": len(labels), "errors": len(errors)}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
