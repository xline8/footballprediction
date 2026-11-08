"""Build the Denmark 2. Division Phase A goals-only analysis tables."""
import csv
import json
from pathlib import Path

WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
INDEX = WAREHOUSE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "239"


def number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def events_for(content):
    return ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []


def phase_for(round_value):
    try:
        round_number = int(str(round_value))
    except (TypeError, ValueError):
        raise ValueError(f"bad round: {round_value!r}")
    if 1 <= round_number <= 22:
        return "regular"
    if 23 <= round_number <= 32:
        return "split"
    raise ValueError(f"round outside DK-2 format: {round_number}")


def build_match(index_row):
    payload = json.load((WAREHOUSE / index_row["path"]).open())
    header = payload.get("header") or {}
    status = header.get("status") or {}
    if not status.get("finished") or status.get("cancelled"):
        return None
    general = payload.get("general") or {}
    content = payload.get("content") or {}
    home = general.get("homeTeam") or {}
    away = general.get("awayTeam") or {}
    if home.get("id") is None or away.get("id") is None:
        raise ValueError(f"missing team id in {index_row['match_id']}")
    score = str(status.get("scoreStr") or "").split("-")
    if len(score) != 2:
        raise ValueError(f"bad score in {index_row['match_id']}: {status.get('scoreStr')}")
    round_value = general.get("matchRound")
    events = events_for(content)
    ht = next(
        (e for e in events if e.get("type") == "Half" and e.get("halfStrShort") == "HT"
         and e.get("homeScore") is not None and e.get("awayScore") is not None),
        None,
    )
    red = {"home": 0, "away": 0}
    for event in events:
        if event.get("type") == "Card" and event.get("card") in {"Red", "YellowRed"}:
            red["home" if bool(event.get("isHome")) else "away"] += 1
    referee = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    return {
        "match_id": index_row["match_id"],
        "date": index_row["date"],
        "season": index_row["season"],
        "round": str(round_value),
        "phase": phase_for(round_value),
        "home_team_id": home["id"],
        "home_team": home.get("name") or "",
        "away_team_id": away["id"],
        "away_team": away.get("name") or "",
        "home_goals": int(float(score[0].strip())),
        "away_goals": int(float(score[1].strip())),
        "ht_home_goals": ht.get("homeScore") if ht else "",
        "ht_away_goals": ht.get("awayScore") if ht else "",
        "red_cards_home": red["home"],
        "red_cards_away": red["away"],
        "referee": referee,
        "events_present": int(bool(events)),
        "ht_present": int(ht is not None),
    }


def write_csv(path, rows):
    fields = list(rows[0])
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INDEX.open() as fh:
        index_rows = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = [built for row in index_rows if (built := build_match(row)) is not None]
    if len(rows) != len(index_rows):
        raise AssertionError(f"finished rows {len(rows)} != index rows {len(index_rows)}")
    if len({r["match_id"] for r in rows}) != len(rows):
        raise AssertionError("duplicate match ids")
    write_csv(OUT / "dk2_matches.csv", rows)
    team_rows = []
    for row in rows:
        for side, opponent in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": row["match_id"], "date": row["date"], "season": row["season"],
                "round": row["round"], "phase": row["phase"], "team_id": row[f"{side}_team_id"],
                "team": row[f"{side}_team"], "venue": side,
                "goals_for": row[f"{side}_goals"], "goals_against": row[f"{opponent}_goals"],
            })
    write_csv(OUT / "dk2_team_matches.csv", team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
