"""Resumable SofaScore shots-on-target labels for football-data matches."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import httpx

BASE = Path(__file__).resolve().parent
MASTER = BASE / "all_matches_clean.csv"
OUT = BASE / "data_enrichment" / "sot_sofascore"
RAW = OUT / "raw"
LABELS = OUT / "sot_labels.csv"
MAPPING = OUT / "match_mapping.csv"
CHECKPOINT = OUT / "checkpoint.json"
API = "https://www.sofascore.com/api/v1"
TOURNAMENTS = {"D1": (35, "Bundesliga"), "E0": (17, "Premier League"),
               "SP1": (8, "LaLiga"), "I1": (23, "Serie A"), "F1": (34, "Ligue 1")}
ALIASES = {"man united": "manchester united", "man city": "manchester city",
           "nottm forest": "nottingham forest", "nott m forest": "nottingham forest",
           "west ham": "west ham united", "wolves": "wolverhampton wanderers"}
HEADERS = {"Accept": "application/json", "Referer": "https://www.sofascore.com/",
           "User-Agent": os.environ.get("FOOTBALL_ENRICHMENT_USER_AGENT",
                                         "football-data-personal-research/1.0")}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
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


def get(client: httpx.Client, path: str, delay: float) -> dict:
    if delay:
        time.sleep(delay)
    response = client.get(f"{API}{path}")
    if response.status_code in (401, 403, 429):
        raise RuntimeError(f"provider stopped: HTTP {response.status_code}")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(f"unexpected payload: {path}")
    return payload


def seasons(client: httpx.Client, tournament_id: int, delay: float) -> dict[str, int]:
    payload = get(client, f"/unique-tournament/{tournament_id}/seasons", delay)
    return {s["year"]: s["id"] for s in payload.get("seasons", []) if s and s.get("year")}


def extract_stats(payload: dict) -> dict:
    periods = {row.get("period"): row for row in payload.get("statistics", [])}
    values = {}
    for period, row in periods.items():
        for group in row.get("groups", []):
            for item in group.get("statisticsItems", []):
                if item.get("key") == "shotsOnGoal":
                    values[period] = [int(item["homeValue"]), int(item["awayValue"])]
                    break
    if not all(key in values for key in ("ALL", "1ST", "2ND")):
        raise ValueError(f"missing period stats: {sorted(values)}")
    return {"sot_1h": sum(values["1ST"]), "sot_2h": sum(values["2ND"]),
            "sot_ft": sum(values["ALL"]), "stats_home": values["ALL"][0],
            "stats_away": values["ALL"][1], "label_source": "sofascore_statistics"}


def validate_shotmap(payload: dict, label: dict) -> dict:
    shots = payload.get("shotmap") or []
    on_target = [shot for shot in shots if shot.get("shotType") in {"goal", "save"}]
    first = sum(shot.get("time", 0) <= 45 for shot in on_target)
    second = len(on_target) - first
    return {"shotmap_count": len(shots), "shotmap_sot_1h": first,
            "shotmap_sot_2h": second, "shotmap_matches_stats":
            first == label["sot_1h"] and second == label["sot_2h"]}


def load_master() -> list[dict]:
    with MASTER.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle)
                if row.get("Div") in TOURNAMENTS and row.get("Date") and row.get("HST") and row.get("AST")]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--batch", type=int, default=500)
    parser.add_argument("--div", choices=sorted(TOURNAMENTS))
    parser.add_argument("--season")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    rows = load_master()
    done = set(); labels = []; mappings = []; errors = []
    if LABELS.exists():
        with LABELS.open(encoding="utf-8", newline="") as handle: labels = list(csv.DictReader(handle))
        done = {row["sofascore_event_id"] for row in labels if row.get("sofascore_event_id")}
    with httpx.Client(headers=HEADERS, timeout=45, follow_redirects=True) as client:
        for div, (tid, _) in TOURNAMENTS.items():
            if args.div and div != args.div:
                continue
            div_rows = [row for row in rows if row["Div"] == div]
            season_ids = seasons(client, tid, args.delay)
            target_seasons = sorted({row["Season"] for row in div_rows})
            if args.season:
                target_seasons = [season for season in target_seasons if season == args.season]
            for season in target_seasons:
                start, end = season.split("/")
                key = f"{start[-2:]}/{end[-2:]}"
                sid = season_ids.get(key)
                if not sid:
                    continue
                for page in range(0, 20):
                    payload = get(client, f"/unique-tournament/{tid}/season/{sid}/events/last/{page}", args.delay)
                    events = payload.get("events", [])
                    if not events: break
                    for event in events:
                        if not event.get("status", {}).get("type") == "finished": continue
                        date = datetime.fromtimestamp(event["startTimestamp"], timezone.utc).date().isoformat()
                        candidates = [row for row in div_rows if row["Season"] == season and row["Date"] == date]
                        if not candidates: continue
                        home = event.get("homeTeam", {}).get("name", ""); away = event.get("awayTeam", {}).get("name", "")
                        best = max(candidates, key=lambda row: similarity(row["HomeTeam"], home)+similarity(row["AwayTeam"], away))
                        match_score = similarity(best["HomeTeam"], home)+similarity(best["AwayTeam"], away)
                        if match_score < 1.6: continue
                        eid = str(event["id"])
                        mappings.append({"div": div, "season": season, "date": date, "sofascore_event_id": eid,
                                         "sofa_home": home, "sofa_away": away, "csv_home": best["HomeTeam"],
                                         "csv_away": best["AwayTeam"], "score": round(match_score, 4)})
                        if eid in done or len(done) >= args.batch: continue
                        try:
                            stats = get(client, f"/event/{eid}/statistics", args.delay)
                            shotmap = get(client, f"/event/{eid}/shotmap", args.delay)
                            label = extract_stats(stats); label.update(validate_shotmap(shotmap, label))
                            expected = int(float(best["HST"])) + int(float(best["AST"]))
                            labels.append({"div": div, "season": season, "date": best["Date"], "home": best["HomeTeam"],
                                           "away": best["AwayTeam"], "sofascore_event_id": eid, "csv_sot_ft": expected,
                                           "delta_sot_ft": label["sot_ft"]-expected, **label,
                                           "quality": "reconciled" if label["sot_ft"] == expected else "flagged"})
                            done.add(eid)
                        except Exception as exc:
                            errors.append({"event_id": eid, "error": repr(exc)})
                        write_csv(LABELS, labels); write_csv(MAPPING, mappings)
                        (CHECKPOINT).write_text(json.dumps({"done": len(done), "errors": len(errors),
                            "updated_utc": datetime.now(timezone.utc).isoformat()}, indent=2), encoding="utf-8")
                    if len(done) >= args.batch: return 0
    print(json.dumps({"labels": len(labels), "errors": len(errors)}, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
