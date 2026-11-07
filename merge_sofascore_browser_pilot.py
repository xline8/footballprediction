"""Join Chrome-collected SofaScore event details to Bundesliga 2017/18 CSV rows."""
import csv
import json
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

BASE = Path(__file__).resolve().parent
MASTER = BASE / "all_matches_clean.csv"
EVENTS = BASE / "data_enrichment" / "sot_sofascore" / "browser_d1_1718_detail.json"
OUT = BASE / "data_enrichment" / "sot_sofascore" / "browser_d1_1718_labels.csv"


def norm(value):
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return " ".join(value.replace("fc ", "").replace("1. ", "").split())


def similarity(left, right):
    a, b = norm(left), norm(right)
    if a == b:
        return 1.0
    ta, tb = set(a.split()), set(b.split())
    if ta and tb and (ta <= tb or tb <= ta):
        return 0.96
    return SequenceMatcher(None, a, b).ratio()


with MASTER.open(encoding="utf-8", newline="") as handle:
    rows = [row for row in csv.DictReader(handle) if row["Div"] == "D1" and row["Season"] == "2017/18"]
with EVENTS.open(encoding="utf-8") as handle:
    events = json.load(handle)["events"]
by_date = {}
for row in rows:
    by_date.setdefault(row["Date"], []).append(row)
labels = []
for event in events:
    date = datetime.fromtimestamp(event["startTimestamp"], timezone.utc).date().isoformat()
    candidates = by_date.get(date, [])
    if not candidates:
        continue
    row = max(candidates, key=lambda r: similarity(r["HomeTeam"], event["home"]) + similarity(r["AwayTeam"], event["away"]))
    score = similarity(row["HomeTeam"], event["home"]) + similarity(row["AwayTeam"], event["away"])
    if score < 1.6:
        continue
    p = event["periods"]
    ft = int(float(row["HST"])) + int(float(row["AST"]))
    labels.append({"div": "D1", "season": "2017/18", "date": row["Date"], "home": row["HomeTeam"],
                   "away": row["AwayTeam"], "sofascore_event_id": event["id"], "match_score": round(score, 4),
                   "sot_1h": sum(p["1ST"]), "sot_2h": sum(p["2ND"]), "sot_ft": sum(p["ALL"]),
                   "csv_sot_ft": ft, "delta_sot_ft": sum(p["ALL"])-ft,
                   "shotmap_sot_1h": event["shotmapSot1"], "shotmap_sot_2h": event["shotmapSot2"],
                   "shotmap_matches_stats": event["shotmapSot1"] == sum(p["1ST"])
                   and event["shotmapSot2"] == sum(p["2ND"]),
                   "quality": "reconciled" if sum(p["ALL"]) == ft else "flagged"})
with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(labels[0])); writer.writeheader(); writer.writerows(labels)
print(json.dumps({"rows": len(rows), "labels": len(labels), "exact": sum(x["delta_sot_ft"] == 0 for x in labels), "shotmap_exact": sum(x["shotmap_matches_stats"] for x in labels)}, indent=2))
