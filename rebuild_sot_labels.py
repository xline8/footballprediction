"""Rebuild backfill labels from cached FotMob payloads, including stats fallback."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from backfill_sot_fotmob import LABELS, MAPPING, MASTER, RAW, extract

OUT = LABELS.parent


def main() -> int:
    with MASTER.open(encoding="utf-8", newline="") as handle:
        master = {(row["Div"], row["Date"], row["HomeTeam"], row["AwayTeam"]): row
                  for row in csv.DictReader(handle)}
    with MAPPING.open(encoding="utf-8", newline="") as handle:
        mapping = list(csv.DictReader(handle))
    by_mid = {row.get("fotmob_match_id"): row for row in mapping if row.get("fotmob_match_id")}
    labels = []
    errors = []
    for raw in sorted(RAW.glob("*.json")):
        parts = raw.stem.rsplit("_", 1)
        if len(parts) != 2:
            continue
        prefix, mid = parts
        div, season = prefix.split("_", 1)
        link = by_mid.get(mid)
        if not link or link.get("status") in {"unmatched", "ambiguous"}:
            continue
        key = (div, link.get("date", ""), link.get("csv_home", ""), link.get("csv_away", ""))
        row = master.get(key)
        if row is None:
            errors.append({"match_id": mid, "error": "master row not found"})
            continue
        try:
            label = extract(json.loads(raw.read_text(encoding="utf-8")))
            expected = int(float(row["HST"])) + int(float(row["AST"]))
            labels.append({"div": div, "season": season.replace("-", "/"), "date": row["Date"],
                           "home": row["HomeTeam"], "away": row["AwayTeam"],
                           "fotmob_match_id": mid, "csv_sot_ft": expected,
                           "delta_sot_ft": label["sot_ft"] - expected, **label,
                           "quality": "reconciled" if label["sot_ft"] == expected else "flagged"})
        except Exception as exc:
            errors.append({"match_id": mid, "error": repr(exc)})
    fields = list(labels[0]) if labels else []
    with LABELS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(labels)
    (OUT / "rebuild_summary.json").write_text(json.dumps({"labels": len(labels), "errors": errors}, indent=2), encoding="utf-8")
    print(json.dumps({"labels": len(labels), "errors": len(errors)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
