"""Build the RO-LigaII analysis tables from the FotMob world warehouse.

The Liga II payloads have no usable stats feed, shotmap shots, referee names,
or xG.  The match table therefore keeps only the measured match metadata,
goals, event-derived half-time goals and card audit counts.  Red counts are
Red + YellowRed events; straight yellows are explicitly zero because no
Yellow events occur anywhere in this corpus.  Reds are audit fields, not a
model target.

Regenerate with: python3 league/RO-LigaII/data/build_data.py
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INDEX = REPO / "data_enrichment" / "fotmob_world_index.csv"
WAREHOUSE = REPO / "data_enrichment"
OUT = Path(__file__).resolve().parent

FIELDS = [
    "match_id", "league", "season", "date", "round", "sub_league_id",
    "phase", "home_team_id", "home_team", "away_team_id", "away_team",
    "home_goals", "away_goals", "ht_home_goals", "ht_away_goals",
    "ht_source", "ev_red_home", "ev_red_away", "ev_yellowred_home",
    "ev_yellowred_away", "ev_yellow_home", "ev_yellow_away", "has_events",
    "referee", "has_stats", "has_shotmap", "n_shotmap_shots",
    "coverage_level",
]


def phase_of(league_name):
    if league_name == "Liga II":
        return "regular"
    if "Promotion Group" in league_name:
        return "promotion"
    if "Relegation Group A" in league_name:
        return "relegation_a"
    if "Relegation Group B" in league_name:
        return "relegation_b"
    if "Relegation Playoff" in league_name:
        return "relegation_playoff"
    raise ValueError(f"unrecognised Liga II tournament: {league_name!r}")


def events_for(payload):
    return (
        ((payload.get("content") or {}).get("matchFacts") or {})
        .get("events", {})
        .get("events", [])
        or []
    )


def event_count(events, card, home):
    return sum(
        1 for e in events
        if e.get("type") == "Card"
        and e.get("card") == card
        and bool(e.get("isHome")) == home
    )


def main():
    index_rows = [
        r for r in csv.DictReader(INDEX.open(newline=""))
        if r["league_id"] == "9113"
    ]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for idx in index_rows:
        payload = json.loads((WAREHOUSE / Path(idx["path"]).relative_to("data_enrichment")).read_text())
        general = payload["general"]
        status = (payload.get("header") or {}).get("status") or {}
        assert status.get("finished") is True, idx["match_id"]
        content = payload.get("content") or {}
        events = events_for(payload)
        score = [int(x.strip()) for x in status["scoreStr"].split("-")]
        goals = [e for e in events if e.get("type") == "Goal"]
        first_half = [
            e for e in goals
            if isinstance(e.get("time"), (int, float)) and e["time"] <= 45
        ]
        info = (content.get("matchFacts") or {}).get("infoBox") or {}
        referee = ((info.get("Referee") or {}).get("text")) or None
        shotmap = (content.get("shotmap") or {}).get("shots") or []
        tournament = general.get("leagueName") or ""
        row = {
            "match_id": idx["match_id"],
            "league": "RO-LigaII",
            "season": idx["season"],
            "date": idx["date"],
            "round": str(general.get("matchRound") or ""),
            "sub_league_id": general.get("leagueId"),
            "phase": phase_of(tournament),
            "home_team_id": general["homeTeam"]["id"],
            "home_team": general["homeTeam"]["name"],
            "away_team_id": general["awayTeam"]["id"],
            "away_team": general["awayTeam"]["name"],
            "home_goals": score[0],
            "away_goals": score[1],
            "ht_home_goals": sum(1 for e in first_half if e.get("isHome")) if events else None,
            "ht_away_goals": sum(1 for e in first_half if not e.get("isHome")) if events else None,
            "ht_source": "events" if events else "none",
            "ev_red_home": event_count(events, "Red", True),
            "ev_red_away": event_count(events, "Red", False),
            "ev_yellowred_home": event_count(events, "YellowRed", True),
            "ev_yellowred_away": event_count(events, "YellowRed", False),
            # There are zero straight-Yellow events in all 1,513 payloads.
            "ev_yellow_home": 0,
            "ev_yellow_away": 0,
            "has_events": int(bool(events)),
            "referee": referee,
            # content.stats is None in every payload; these are explicit audit flags.
            "has_stats": 0,
            "has_shotmap": 0,
            "n_shotmap_shots": len(shotmap),
            "coverage_level": general.get("coverageLevel"),
        }
        assert row["n_shotmap_shots"] == 0
        out.append(row)

    assert len(out) == len(index_rows) == 1513
    assert len({r["match_id"] for r in out}) == len(out)
    with (OUT / "rl2_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out)

    team_rows = []
    for row in out:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({
                "match_id": row["match_id"], "season": row["season"],
                "date": row["date"], "phase": row["phase"],
                "team_id": row[f"{side}_team_id"], "team": row[f"{side}_team"],
                "venue": side,
                "goals_for": row[f"{side}_goals"],
                "goals_against": row[f"{other}_goals"],
            })
    team_fields = list(team_rows[0])
    with (OUT / "rl2_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=team_fields)
        writer.writeheader()
        writer.writerows(team_rows)
    print(f"matches {len(out)} team_rows {len(team_rows)}")


if __name__ == "__main__":
    main()
