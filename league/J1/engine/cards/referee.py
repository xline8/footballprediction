"""Efficient extraction of referee identities from J1 warehouse snapshots."""
import csv, json
from pathlib import Path


def extract(csv_path, warehouse_root, output):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            path = Path(warehouse_root) / r["season"] / (r["match_id"] + ".json")
            name = ""
            if path.exists():
                with open(path, encoding="utf-8") as jf:
                    data = json.load(jf)
                value = (data.get("content", {}).get("matchFacts", {})
                         .get("infoBox", {}).get("Referee", {}))
                name = str(value.get("text", "") or "").strip() if isinstance(value, dict) else ""
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": r["date"], "kickoff_utc": r["kickoff_utc"],
                         "referee": name, "referee_known": str(bool(name)).lower()})
    with open(output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["match_id", "season", "date", "kickoff_utc", "referee", "referee_known"])
        w.writeheader(); w.writerows(rows)
    return rows
