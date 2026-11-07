"""Build a separate SofaScore-labelled shots-on-target dataset."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

BASE = Path(__file__).resolve().parent
MASTER = BASE / "all_matches_clean.csv"
OUT = BASE / "data_enrichment" / "sot_sofascore"
OUTPUT = OUT / "sofascore_sot_dataset.csv"
REPORT = OUT / "dataset_report.json"
DIV_BY_TOURNAMENT = {17: "E0", 18: "E1", 24: "E2", 25: "E3",
                     8: "SP1", 23: "I1", 34: "F1", 35: "D1"}
ALIASES = {
    "man united": "manchester united", "man city": "manchester city",
    "nottm forest": "nottingham forest", "nott m forest": "nottingham forest",
    "west ham": "west ham united", "wolves": "wolverhampton wanderers",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode().lower()
    value = re.sub(r"\b(fc|cf|1\.)\b", " ", value)
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


def season_label(year: str) -> str:
    start, end = year.split("/")
    return f"20{start}/{end}" if len(start) == 2 else f"{start}/{end}"


def load_master() -> list[dict]:
    with MASTER.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_events() -> list[dict]:
    events = []
    seen_event_ids: set[str] = set()
    paths = sorted(OUT.glob("browser_*_stats.json"))
    running_paths = [OUT / "browser_all_running_snapshot.json",
                     OUT / "browser_full_snapshot.json"]
    paths.extend(path for path in running_paths if path.exists())
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if path.name in {"browser_all_running_snapshot.json",
                         "browser_full_snapshot.json"}:
            data = payload.get("data", [])
            grouped = {}
            for source_event in data:
                grouped.setdefault((source_event["div"], source_event["season"]), []).append({
                    "id": source_event["eventId"],
                    "startTimestamp": int(datetime.combine(
                        date.fromisoformat(source_event["date"]), datetime.min.time(),
                        tzinfo=timezone.utc).timestamp()),
                    "home": source_event["home"], "away": source_event["away"],
                    "periods": source_event.get("periods", {}),
                })
            seasons = [{"season": season, "events": events, "_div": div}
                       for (div, season), events in grouped.items()]
        else:
            div_lookup = {}
            div = DIV_BY_TOURNAMENT.get(payload.get("tournament"))
            if not div:
                match = re.match(r"browser_([a-z0-9]+)_", path.name)
                div = (match.group(1).upper() if match else None)
            if not div:
                continue
            if payload.get("events") and payload.get("job"):
                parts = str(payload["job"]).split("_", 1)
                season_value = parts[1] if len(parts) == 2 else ""
                seasons = [{"season": season_value, "events": payload["events"]}]
            else:
                seasons = payload.get("seasons") or ([payload] if payload.get("events") else [])
        for season in seasons:
            season_name = season_label(season["season"])
            for event in season.get("events", []):
                if path.name == "browser_all_running_snapshot.json":
                    event_div = season.get("_div")
                else:
                    event_div = div
                if "startTimestamp" not in event:
                    continue
                periods = event.get("periods") or {}
                if not all(period in periods and len(periods[period]) == 2
                           for period in ("ALL", "1ST", "2ND")):
                    continue
                event_date = datetime.fromtimestamp(
                    event["startTimestamp"], timezone.utc).date().isoformat()
                event_id = str(event["id"])
                if event_id in seen_event_ids:
                    continue
                seen_event_ids.add(event_id)
                events.append({
                    "div": event_div, "season": season_name, "date": event_date,
                    "event_id": event_id, "home": event["home"],
                    "away": event["away"], "periods": periods,
                })
    return events


def build() -> tuple[list[dict], dict]:
    master = load_master()
    events = load_events()
    by_key: dict[tuple[str, str, str], list[dict]] = {}
    for row in master:
        key = (row.get("Div", ""), row.get("Season", ""), row.get("Date", ""))
        by_key.setdefault(key, []).append(row)
    used_rows: set[int] = set()
    used_events: set[str] = set()
    output, unmatched = [], []
    for event in events:
        candidates = [(i, row) for i, row in enumerate(
            by_key.get((event["div"], event["season"], event["date"]), []))
            if id(row) not in used_rows]
        if not candidates:
            unmatched.append({**{k: event[k] for k in ("div", "season", "date", "event_id")},
                              "reason": "no_csv_date_row"})
            continue
        ranked = sorted((similarity(row["HomeTeam"], event["home"])
                         + similarity(row["AwayTeam"], event["away"]), i, row)
                        for i, row in candidates)
        score, _, row = ranked[-1]
        if score < 1.60:
            unmatched.append({"div": event["div"], "season": event["season"],
                              "date": event["date"], "event_id": event["event_id"],
                              "reason": "team_score", "score": round(score, 4)})
            continue
        periods = event["periods"]
        all_home, all_away = periods["ALL"]
        if not row.get("HST") or not row.get("AST"):
            continue
        old_ft = int(float(row["HST"])) + int(float(row["AST"]))
        new_ft = int(all_home) + int(all_away)
        delta = new_ft - old_ft
        delta_home = int(all_home) - int(float(row["HST"]))
        delta_away = int(all_away) - int(float(row["AST"]))
        quality = (
            "reconciled" if delta_home == 0 and delta_away == 0 else
            "flagged" if abs(delta_home) <= 2 and abs(delta_away) <= 2 else
            "quarantine")
        output.append({
            "div": event["div"], "season": event["season"], "date": event["date"],
            "home": row["HomeTeam"], "away": row["AwayTeam"],
            "sofascore_event_id": event["event_id"], "match_score": round(score, 4),
            "football_data_hst": row["HST"], "football_data_ast": row["AST"],
            "sofascore_hst": all_home, "sofascore_ast": all_away,
            "sofascore_1h_h": periods["1ST"][0], "sofascore_1h_a": periods["1ST"][1],
            "sofascore_2h_h": periods["2ND"][0], "sofascore_2h_a": periods["2ND"][1],
            "football_data_sot_ft": old_ft, "sofascore_sot_ft": new_ft,
            "delta_sot_ft": delta, "delta_home": delta_home,
            "delta_away": delta_away, "quality": quality,
            "source": "sofascore_statistics",
        })
        used_rows.add(id(row)); used_events.add(event["event_id"])
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "master_rows": len(master), "source_events": len(events),
        "dataset_rows": len(output), "unmatched": len(unmatched),
        "quality": {quality: sum(row["quality"] == quality for row in output)
                    for quality in ("reconciled", "flagged", "quarantine")},
        "by_division": {div: sum(row["div"] == div for row in output)
                        for div in sorted(DIV_BY_TOURNAMENT.values())},
        "unmatched_rows": unmatched,
    }
    return output, report


def main() -> int:
    rows, report = build()
    OUT.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
