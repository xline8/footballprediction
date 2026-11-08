"""Build the BG-SecondLeague analysis CSV from the FotMob world warehouse.

One row per played match (league_id 9096). This league's warehouse
payloads carry NO stats feed (content.stats is None in every file),
an EMPTY shotmap, empty referee and no period splits — the only
targets that exist are the FT score (header.status.scoreStr) and the
goal/card event list. The CSV therefore carries goals + coverage
flags only; nothing is fabricated.

Regenerate: .venv/bin/python league/BG-SecondLeague/data/build_data.py
Output (gitignored): league/BG-SecondLeague/data/bg2_matches.csv (+ team table)
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")  # warehouse lives in main checkout (gitignored data)
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "9096"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(MAIN_REPO / r["path"]))
        gen = d.get("general") or {}; hdr = d.get("header") or {}; st = hdr.get("status") or {}
        if not st.get("finished"):
            continue
        c = d.get("content") or {}
        ss = (st.get("scoreStr") or "0 - 0").split("-")
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        shots = ((c.get("shotmap") or {}).get("shots") or [])
        out.append({
            "match_id": r["match_id"], "league": "BG-SecondLeague", "season": r["season"],
            "date": r["date"], "round": str(gen.get("matchRound")),
            "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
            "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
            "coverage_level": gen.get("coverageLevel"),
            "home_goals": int(ss[0]), "away_goals": int(ss[1]),
            "has_stats": int(c.get("stats") is not None),
            "has_shotmap": int(len(shots) > 0),
            "has_events": int(len(evs) > 0),
            "referee": (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
        })
    assert len(out) >= 1700, len(out)  # floor: index also lists unplayed fixtures (13 at build time, incl. tonight)
    ids = [r["match_id"] for r in out]; assert len(set(ids)) == len(ids)
    with open(OUT / "bg2_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            tm.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                       "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                       "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]})
    with open(OUT / "bg2_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")

if __name__ == "__main__":
    main()
