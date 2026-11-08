"""Extract the DK-1Division goals-only parent-tier corpus for X2."""
import csv
import json
from pathlib import Path

WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
INDEX = WAREHOUSE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
SEASONS = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}


def main():
    with INDEX.open() as fh:
        index_rows = [r for r in csv.DictReader(fh) if r["league_id"] == "85" and r["season"] in SEASONS]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = []
    for index_row in index_rows:
        payload = json.load((WAREHOUSE / index_row["path"]).open())
        status = (payload.get("header") or {}).get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        general = payload.get("general") or {}
        home = general.get("homeTeam") or {}
        away = general.get("awayTeam") or {}
        score = str(status.get("scoreStr") or "").split("-")
        if len(score) != 2 or home.get("id") is None or away.get("id") is None:
            raise ValueError(f"invalid parent payload {index_row['match_id']}")
        rows.append({
            "match_id": index_row["match_id"], "date": index_row["date"], "season": index_row["season"],
            "home_team_id": home["id"], "home_team": home.get("name") or "",
            "away_team_id": away["id"], "away_team": away.get("name") or "",
            "home_goals": int(float(score[0].strip())), "away_goals": int(float(score[1].strip())),
        })
    if len(rows) != len(index_rows):
        raise AssertionError(f"finished parent rows {len(rows)} != index rows {len(index_rows)}")
    if len(rows) != 768:
        raise AssertionError(f"parent rows {len(rows)} != 768")
    counts = {season: sum(r["season"] == season for r in rows) for season in sorted(SEASONS)}
    if counts != {season: 192 for season in sorted(SEASONS)}:
        raise AssertionError(f"parent season counts {counts}")
    with (OUT / "dk1_parent_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"parent_matches={len(rows)} season_counts={counts}")


if __name__ == "__main__":
    main()
