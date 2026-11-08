"""Build the Iraq Stars League Phase A tables from the shared warehouse.

This is deliberately payload-first: index rows locate JSON payloads, while
finished status, score, teams, round, events, and coverage are measured from
the payload itself. No model fitting is performed here.
"""
import csv
import json
from pathlib import Path

WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
INDEX = WAREHOUSE / "data_enrichment/fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "524"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]


def events_from(content):
    return ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []


def is_ht(event):
    return event.get("type") == "Half" and event.get("halfStrKey") == "halftime_short"


def first_half(events):
    """Return events before the explicit HT marker; never infer from minutes."""
    out = []
    for event in events:
        if is_ht(event):
            break
        out.append(event)
    return out if any(is_ht(e) for e in events) else None


def count_goals(events, home):
    return sum(e.get("type") == "Goal" and bool(e.get("isHome")) == home
               and not e.get("isPenaltyShootoutEvent") for e in events)


def count_reds(events, home):
    return sum(e.get("type") == "Card" and e.get("card") in {"Red", "YellowRed"}
               and bool(e.get("isHome")) == home for e in events)


def phase(round_value):
    return "playoff" if str(round_value) in {"1/2", "final"} else "regular"


def build(row):
    payload = json.load((WAREHOUSE / row["path"]).open())
    general = payload.get("general") or {}
    status = (payload.get("header") or {}).get("status") or {}
    # Warehouse index rows with a score are the played-match universe here.
    # Some historical payloads retain finished=False despite a valid final score.
    if status.get("cancelled"):
        return None
    score = [x.strip() for x in str(status.get("scoreStr") or "").split("-")]
    if len(score) != 2 or not all(x.isdigit() for x in score):
        # Index rows can be scheduled placeholders. Played-only inclusion is
        # defined by a final score in the payload; do not turn them into 0-0.
        return None
    home = general.get("homeTeam") or {}
    away = general.get("awayTeam") or {}
    if home.get("id") is None or away.get("id") is None:
        raise ValueError(f"missing team id for {row['match_id']}")
    content = payload.get("content") or {}
    events = events_from(content)
    before_ht = first_half(events) if events else None
    match_round = str(general.get("matchRound") or "")
    rec = {
        "match_id": row["match_id"], "season": row["season"], "date": row["date"],
        "round": match_round, "phase": phase(match_round),
        "home_team_id": home["id"], "home_team": home.get("name"),
        "away_team_id": away["id"], "away_team": away.get("name"),
        "home_goals": int(score[0]), "away_goals": int(score[1]),
        "events_present": int(bool(events)),
        "goals_1h_home": None if before_ht is None else count_goals(before_ht, True),
        "goals_1h_away": None if before_ht is None else count_goals(before_ht, False),
        "event_goals_home": count_goals(events, True) if events else None,
        "event_goals_away": count_goals(events, False) if events else None,
        "event_goal_score_reconciles": None if not events else int(
            count_goals(events, True) == int(score[0]) and count_goals(events, False) == int(score[1])),
        "red_cards_home": None if not events else count_reds(events, True),
        "red_cards_away": None if not events else count_reds(events, False),
    }
    if content.get("stats") is not None:
        raise AssertionError(f"unexpected stats payload in {row['match_id']}")
    if ((content.get("shotmap") or {}).get("shots") or []):
        raise AssertionError(f"unexpected shotmap payload in {row['match_id']}")
    if content.get("lineup") is not None:
        raise AssertionError(f"unexpected lineup payload in {row['match_id']}")
    referee = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
    if referee.get("text"):
        raise AssertionError(f"unexpected referee text in {row['match_id']}")
    return rec


def write(path, rows):
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INDEX.open() as fh:
        index = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    coverage = {"stats": 0, "shots": 0, "lineup": 0, "referee": 0}
    for r in index:
        payload = json.load((WAREHOUSE / r["path"]).open())
        content = payload.get("content") or {}
        coverage["stats"] += content.get("stats") is None
        coverage["shots"] += not ((content.get("shotmap") or {}).get("shots") or [])
        coverage["lineup"] += content.get("lineup") is None
        referee = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
        coverage["referee"] += not referee.get("text")
    assert coverage == {"stats": 2032, "shots": 2032, "lineup": 2032, "referee": 2032}, coverage
    rows = [x for r in sorted(index, key=lambda x: (x["date"], x["match_id"])) if (x := build(r))]
    assert len(index) == 2032
    assert len(rows) == 1983, len(rows)
    assert len({r["match_id"] for r in rows}) == len(rows)
    write(OUT / "iqsl_matches.csv", rows)
    team_rows = []
    for r in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": r["match_id"], "season": r["season"], "date": r["date"],
                "round": r["round"], "phase": r["phase"], "team_id": r[f"{side}_team_id"],
                "team": r[f"{side}_team"], "venue": side,
                "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
            })
    write(OUT / "iqsl_team_matches.csv", team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
