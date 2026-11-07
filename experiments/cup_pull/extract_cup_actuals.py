"""Extract FT cup actuals from stored FotMob matchDetails responses.

Reads experiments/cup_pull/pull_report.json (the matched mapping written
by pull_cup_fotmob.py) and the stored responses under
data_enrichment/fotmob_full/<KEY>/<season-dash>/<fotmob_id>.json, and
writes ONE grading-ready CSV:

  data_enrichment/cup_actuals.csv
  columns: competition, season, date, home, away, fotmob_match_id,
           goals_home, goals_away, corners_home, corners_away

Extraction rules (never fabricate — absent fields stay blank):
  - goals: header.teams[0].score / header.teams[1].score (the FT score,
    including extra time where a tie went to ET; penalty shootouts are
    NOT added). Fallback: header.status.scoreStr "H - A".
  - corners: content.stats.Periods.All, the stat with key "corners"
    ([home, away] pair) — the same stats block the league store carries.
  - competition / season / date / home / away come from the TipsterArea
    universe row (the system's own naming), so the CSV joins directly
    against predict_cups outputs and ta/results.csv.
  - A matched fixture whose response file is missing produces NO row;
    it is reported on stdout instead (rerun the pull first).

Also cross-checks FotMob goals against the TipsterArea FT score and
prints any mismatch (data-quality signal, reported in RESULTS.md).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
STORE = BASE / "data_enrichment" / "fotmob_full"
REPORT = HERE / "pull_report.json"
OUT = BASE / "data_enrichment" / "cup_actuals.csv"
FIELDS = ["competition", "season", "date", "home", "away", "fotmob_match_id",
          "goals_home", "goals_away", "corners_home", "corners_away"]


def season_dir(season: str) -> str:
    return season.replace("/", "-")


def extract_actuals(payload: dict) -> dict:
    header = payload.get("header") or {}
    teams = header.get("teams") or []
    goals_h = goals_a = None
    if len(teams) == 2:
        gh, ga = teams[0].get("score"), teams[1].get("score")
        if isinstance(gh, int) and isinstance(ga, int):
            goals_h, goals_a = gh, ga
    if goals_h is None:
        score_str = ((header.get("status") or {}).get("scoreStr") or "")
        parts = [p.strip() for p in score_str.split("-")]
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            goals_h, goals_a = int(parts[0]), int(parts[1])
    corners_h = corners_a = None
    periods = ((payload.get("content") or {}).get("stats") or {}).get("Periods") or {}
    all_period = periods.get("All") or {}
    for section in all_period.get("stats", []):
        for stat in section.get("stats", []):
            if stat.get("key") == "corners":
                raw = stat.get("stats") or []
                if len(raw) == 2 and all(isinstance(v, (int, float)) for v in raw):
                    corners_h, corners_a = int(raw[0]), int(raw[1])
                break
        if corners_h is not None:
            break
    finished = bool((header.get("status") or {}).get("finished"))
    return {"goals_home": goals_h, "goals_away": goals_a,
            "corners_home": corners_h, "corners_away": corners_a,
            "finished": finished}


def main() -> int:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    matched = report["matched"]
    rows, missing, mismatches = [], [], []
    for item in matched:
        path = (STORE / item["key"] / season_dir(item["season"]) /
                f"{item['fotmob_match_id']}.json")
        if not path.exists():
            missing.append(item)
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        act = extract_actuals(payload)
        rows.append({
            "competition": item["competition"], "season": item["season"],
            "date": item["date"], "home": item["home"], "away": item["away"],
            "fotmob_match_id": item["fotmob_match_id"],
            "goals_home": "" if act["goals_home"] is None else act["goals_home"],
            "goals_away": "" if act["goals_away"] is None else act["goals_away"],
            "corners_home": "" if act["corners_home"] is None else act["corners_home"],
            "corners_away": "" if act["corners_away"] is None else act["corners_away"],
        })
        # Cross-check vs TipsterArea FT score (both should be the FT score).
        try:
            ta_h, ta_a = int(item["ta_score_h"]), int(item["ta_score_a"])
        except (TypeError, ValueError):
            ta_h = ta_a = None
        if (ta_h is not None and act["goals_home"] is not None
                and (ta_h, ta_a) != (act["goals_home"], act["goals_away"])):
            mismatches.append({
                "competition": item["competition"], "date": item["date"],
                "home": item["home"], "away": item["away"],
                "fotmob_match_id": item["fotmob_match_id"],
                "ta_score": f"{ta_h}-{ta_a}",
                "fotmob_score": f"{act['goals_home']}-{act['goals_away']}"})
    rows.sort(key=lambda r: (r["competition"], r["date"], r["home"]))
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "matched_in_report": len(matched), "rows_written": len(rows),
        "rows_with_score": sum(1 for r in rows if r["goals_home"] != ""),
        "rows_with_corners": sum(1 for r in rows if r["corners_home"] != ""),
        "missing_files": len(missing),
        "ta_score_mismatches": mismatches,
    }
    print(json.dumps(summary, indent=2), flush=True)
    if missing:
        print("MISSING stored files (rerun pull):", file=sys.stderr)
        for item in missing:
            print(f"  {item['competition']} {item['date']} "
                  f"{item['home']} v {item['away']} id={item['fotmob_match_id']}",
                  file=sys.stderr)
    (HERE / "extract_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
