"""NI-Premiership data builder: FotMob warehouse JSONs -> match CSV.

Usage: ``python3 build_data.py [BASE]``.  BASE defaults to the repository
root and is the checkout containing ``data_enrichment/``; the coordinator's
normal invocation passes ``/home/hatch/workspace/footballprediction``.

The Northern Ireland Premiership is one true competition: parentLeagueId
129 in all 1,242 payloads.  The main phase uses leagueName ``Premiership``;
the warehouse names split phases ``Premiership Championship Group`` and
``Premiership Relegation Group`` and names playoffs ``Premiership ECL
Playoff`` (an observed warehouse naming discrepancy from the brief's claim
that leagueName is ``Premiership`` throughout).  Full seasons have
12 teams: 33 single-table rounds (198 matches), then top-six and bottom-six
split groups for five rounds (30 matches), plus three one-legged European
playoff matches.  Playoffs are excluded from model data because they are a
different phase and can include extra time (for example match 3873126).
The 2021/2022 split matches reuse round labels ``1``-``5`` under season
league IDs 878453/878454; phase is therefore determined by playoff labels,
not round labels alone.  From 2022/2023 split labels are 34-38.

Coverage is scores-only: content.stats is null, shotmap.shots is empty,
coverageLevel is lower, and no referee, xG, lineup, or usable period-split
feed is present.  Cards are fragmentary and only Red and YellowRed occur;
there are no plain Yellow events.  Goal events provide halves, with minute
<=45 (including stoppage-time goals represented at minute 45) counted in
the first half.  Match 3907917 has a header score of 3-0 but an internally
consistent event trail of 1-3; the header score is used and both half fields
are left empty.  All other event/header goal totals agree, and HT events
agree with goal-time first-half totals wherever both exist.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent / "ni_matches.csv"
LEAGUE_ID = "129"
EXCEPTION = "3907917"

COLUMNS = [
    "match_id", "season", "date", "home_team", "away_team", "home_team_id", "away_team_id", "league_name",
    "home_goals", "away_goals", "round_label", "season_league_id", "phase", "is_playoff",
    "goals_1h", "goals_2h", "notes",
    # Reproducible feed inventory used by the CSV-only EDA and charts.
    "has_stats", "has_shotmap", "referee_named", "has_events", "goal_events", "half_events",
    "card_events", "yellow_events", "red_events", "yellowred_events",
]


def build():
    with open(INDEX, newline="") as f:
        index_rows = [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    assert len(index_rows) == 1242, f"index rows: {len(index_rows)} != 1242"
    rows, log = [], Counter(index_rows=len(index_rows))
    ht_disagreements = []
    event_mismatches = []

    for ir in index_rows:
        path = BASE / ir["path"]
        d = json.loads(path.read_text())
        g, h = d["general"], d["header"]
        assert g["parentLeagueId"] == 129, ir
        assert g["leagueName"] in {"Premiership", "Premiership Championship Group",
                                    "Premiership Relegation Group", "Premiership ECL Playoff"}, ir
        assert h["status"]["finished"] is True, ir
        home, away = h["teams"]
        hg, ag = home["score"], away["score"]
        assert hg is not None and ag is not None, ir
        assert h["status"].get("scoreStr") == f"{hg} - {ag}", ir

        mf = d["content"].get("matchFacts") or {}
        events = (mf.get("events") or {}).get("events") or []
        goals = [e for e in events if e.get("type") == "Goal"]
        halves = [e for e in events if e.get("type") == "Half"]
        cards = [e for e in events if e.get("type") == "Card"]
        yellows = [e for e in cards if e.get("card") == "Yellow"]
        reds = [e for e in cards if e.get("card") == "Red"]
        yellowreds = [e for e in cards if e.get("card") == "YellowRed"]
        if len(goals) != hg + ag and str(g["matchId"]) != EXCEPTION:
            event_mismatches.append(g["matchId"])
        if str(g["matchId"]) == EXCEPTION:
            assert (hg, ag, len(goals)) == (3, 0, 4)

        g1 = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45)
        g2 = sum(1 for e in goals if e.get("time") is not None and e["time"] > 45)
        ht = [e for e in halves if e.get("halfStrShort") == "HT"]
        if ht and str(g["matchId"]) != EXCEPTION:
            ht_home, ht_away = ht[-1].get("homeScore"), ht[-1].get("awayScore")
            event_home = sum(1 for e in goals if e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
            event_away = sum(1 for e in goals if not e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
            if (ht_home, ht_away) != (event_home, event_away):
                ht_disagreements.append(g["matchId"])

        label = g.get("leagueRoundName") or ""
        playoff = label in {"1/4", "1/2", "final"}
        notes = "header score/event trail discrepancy; halves missing" if str(g["matchId"]) == EXCEPTION else ""
        stats = d["content"].get("stats")
        shotmap = d["content"].get("shotmap") or {}
        ref = (mf.get("infoBox") or {}).get("Referee") or {}
        rows.append({
            "match_id": g["matchId"], "season": ir["season"], "date": ir["date"],
            "home_team": home["name"], "away_team": away["name"],
            "home_team_id": home["id"], "away_team_id": away["id"],
            "league_name": g["leagueName"],
            "home_goals": hg, "away_goals": ag, "round_label": label,
            "season_league_id": g["leagueId"], "phase": "playoff" if playoff else "regular",
            "is_playoff": int(playoff), "goals_1h": "" if str(g["matchId"]) == EXCEPTION else g1,
            "goals_2h": "" if str(g["matchId"]) == EXCEPTION else g2, "notes": notes,
            "has_stats": int(stats is not None), "has_shotmap": int(bool(shotmap.get("shots"))),
            "referee_named": int(bool(ref.get("text"))), "has_events": int(bool(events)),
            "goal_events": len(goals), "half_events": len(halves), "card_events": len(cards),
            "yellow_events": len(yellows), "red_events": len(reds), "yellowred_events": len(yellowreds),
        })

    assert not event_mismatches, f"unexpected score/event mismatches: {event_mismatches}"
    assert not ht_disagreements, f"HT disagreements: {ht_disagreements}"
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1242
    expected = {"2021/2022": 231, "2022/2023": 231, "2023/2024": 231,
                "2024/2025": 231, "2025/2026": 231, "2026/2027": 87}
    assert Counter(r["season"] for r in rows) == expected
    assert sum(r["phase"] == "regular" for r in rows) == 1227
    assert sum(r["phase"] == "playoff" for r in rows) == 15
    for season, n in expected.items():
        sr = [r for r in rows if r["season"] == season]
        expected_playoffs = 3 if season != "2026/2027" else 0
        assert sum(r["phase"] == "regular" for r in sr) == n - expected_playoffs
        assert sum(r["phase"] == "playoff" for r in sr) == expected_playoffs
    assert sum(str(r["match_id"]) == EXCEPTION for r in rows) == 1
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    print("index/payloads:", len(index_rows), len(rows), "regular/playoff:", 1227, 15)
    print("seasons:", dict(Counter(r["season"] for r in rows)))
    print("goal-event mismatches: 1 (3907917); HT disagreements: 0")


if __name__ == "__main__":
    build()
