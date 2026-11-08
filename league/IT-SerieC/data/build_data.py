"""Build the Italy Serie C analysis CSV from the FotMob world warehouse.

One row per finished match (parent league_id 147).  The warehouse contains
regular-season group matches and separately labelled playoff/playout matches;
the phase and group columns preserve that distinction for analysis.
"""
import csv
import json
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent


def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "147"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(MAIN_REPO / r["path"]))
        gen = d.get("general") or {}
        status = (d.get("header") or {}).get("status") or {}
        if not status.get("finished"):
            continue
        content = d.get("content") or {}
        league_name = gen.get("leagueName") or ""
        group = league_name.rsplit(" ", 1)[-1] if league_name.startswith("Serie C Grp. ") else ""
        if group not in {"A", "B", "C"}:
            group = ""
        score = (status.get("scoreStr") or "0 - 0").split("-")
        facts = content.get("matchFacts") or {}
        events = (facts.get("events") or {}).get("events") or []
        shots = (content.get("shotmap") or {}).get("shots") or []
        referee = ((facts.get("infoBox") or {}).get("Referee") or {}).get("text") or ""
        out.append({
            "match_id": r["match_id"], "league": "IT-SerieC", "season": r["season"],
            "date": r["date"], "round": str(gen.get("matchRound") or ""),
            "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
            "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
            "coverage_level": gen.get("coverageLevel"),
            "home_goals": int(score[0]), "away_goals": int(score[1]),
            "group": group, "phase": "regular" if group else league_name,
            "has_stats": int(content.get("stats") is not None),
            "has_shotmap": int(len(shots) > 0), "has_events": int(len(events) > 0),
            "referee": referee,
        })
    assert len(out) >= 6100, len(out)
    ids = [r["match_id"] for r in out]
    assert len(set(ids)) == len(ids)
    with open(OUT / "itseriec_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    team_rows = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            team_rows.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                              "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"],
                              "venue": side, "goals_for": r[f"{side}_goals"],
                              "goals_against": r[f"{opp}_goals"], "group": r["group"],
                              "phase": r["phase"]})
    with open(OUT / "itseriec_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0].keys())); w.writeheader(); w.writerows(team_rows)
    print(f"matches {len(out)} team_rows {len(team_rows)}")


if __name__ == "__main__":
    main()
