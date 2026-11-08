"""Build the North Macedonia Prva Liga match CSV from FotMob payloads.

Usage: ``/usr/bin/python3 build_data.py /home/hatch/workspace/footballprediction``.
The payload warehouse is intentionally outside this worktree.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
OUT = HERE / "mk_prva_liga_matches.csv"
LEAGUE_ID = "249"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
EXPECTED = {"2021/2022": 198, "2022/2023": 165, "2023/2024": 198,
            "2024/2025": 198, "2025/2026": 198, "2026/2027": 65}
EXPECTED_MODEL = {"2021/2022": 198, "2022/2023": 165, "2023/2024": 198,
                  "2024/2025": 186, "2025/2026": 197, "2026/2027": 65}
AWARDED_IDS = {"4580217", "4772199", "4773803", "4773799", "4773804", "4773809",
               "4773815", "4773810", "4773821", "4773817", "4773826", "4773823", "4904733"}
COLUMNS = ["match_id", "season", "date", "home_team", "away_team", "home_team_id", "away_team_id",
           "league_name", "home_goals", "away_goals", "round_label", "phase", "is_awarded",
           "goals_1h", "goals_2h", "notes", "has_stats", "has_shotmap", "referee_named",
           "has_events", "goal_events", "half_events", "card_events", "yellow_events", "red_events",
           "yellowred_events"]


def build():
    with INDEX.open(newline="") as f:
        index_rows = [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    assert len(index_rows) == 1022, len(index_rows)
    rows, awarded, mismatches, ht_bad = [], [], [], []
    for ir in index_rows:
        d = json.loads((BASE / ir["path"]).read_text())
        g, h, c = d["general"], d["header"], d["content"]
        assert g["leagueName"] == "Prva Liga" and g["parentLeagueId"] == 249
        assert h["status"]["finished"] is True
        home, away = h["teams"]
        assert h["status"].get("scoreStr") == f"{home['score']} - {away['score']}"
        hg, ag = home["score"], away["score"]
        mf = c.get("matchFacts") or {}
        events = ((mf.get("events") or {}).get("events") or [])
        goals = [e for e in events if e.get("type") == "Goal"]
        halves = [e for e in events if e.get("type") == "Half"]
        cards = [e for e in events if e.get("type") == "Card"]
        yellows = [e for e in cards if e.get("card") == "Yellow"]
        reds = [e for e in cards if e.get("card") == "Red"]
        yellowreds = [e for e in cards if e.get("card") == "YellowRed"]
        is_awarded = int(bool(h["status"].get("awarded")))
        assert is_awarded == int(ir["match_id"] in AWARDED_IDS)
        if is_awarded:
            awarded.append(str(g["matchId"]))
        elif len(goals) != hg + ag:
            mismatches.append(str(g["matchId"]))
        g1 = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45)
        g2 = sum(1 for e in goals if e.get("time") is not None and e["time"] > 45)
        if not is_awarded:
            ht = [e for e in halves if e.get("halfStrShort") == "HT"]
            if ht:
                eh = sum(1 for e in goals if e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
                ea = sum(1 for e in goals if not e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
                if (ht[-1].get("homeScore"), ht[-1].get("awayScore")) != (eh, ea):
                    ht_bad.append(str(g["matchId"]))
        has_events = int(bool(events))
        half_values = ("", "") if is_awarded or not has_events else (g1, g2)
        ref = (mf.get("infoBox") or {}).get("Referee") or {}
        shotmap = c.get("shotmap") or {}
        rows.append({
            "match_id": g["matchId"], "season": ir["season"], "date": ir["date"],
            "home_team": home["name"], "away_team": away["name"], "home_team_id": home["id"],
            "away_team_id": away["id"], "league_name": g["leagueName"], "home_goals": hg,
            "away_goals": ag, "round_label": g.get("leagueRoundName") or "", "phase": "regular",
            "is_awarded": is_awarded, "goals_1h": half_values[0], "goals_2h": half_values[1],
            "notes": "awarded match; excluded from every fit and score" if is_awarded else "",
            "has_stats": int(c.get("stats") is not None), "has_shotmap": int(bool(shotmap.get("shots"))),
            "referee_named": int(bool(ref.get("text"))), "has_events": has_events,
            "goal_events": len(goals), "half_events": len(halves), "card_events": len(cards),
            "yellow_events": len(yellows), "red_events": len(reds), "yellowred_events": len(yellowreds),
        })
    assert not mismatches, mismatches
    assert not ht_bad, ht_bad
    assert sorted(awarded) == sorted(AWARDED_IDS)
    assert len(rows) == 1022 and Counter(r["season"] for r in rows) == EXPECTED
    assert Counter(r["season"] for r in rows if not r["is_awarded"]) == EXPECTED_MODEL
    assert all(r["phase"] == "regular" for r in rows)
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    print("seasons:", dict(Counter(r["season"] for r in rows)))
    print("model rows:", dict(Counter(r["season"] for r in rows if not r["is_awarded"])))
    print("awarded (excluded):", sorted(awarded))
    print("goal-event mismatches (non-awarded): 0; HT disagreements: 0")


if __name__ == "__main__":
    build()
