"""Tunisia Ligue I data builder: FotMob warehouse JSONs -> match CSV.

Usage: ``python3 build_data.py [BASE]``.  BASE defaults to the repository
root and is the checkout containing ``data_enrichment/fotmob_world/``;
the warehouse payloads are gitignored, so in a worktree pass the main
checkout explicitly, e.g. ``python3 build_data.py
/home/hatch/workspace/footballprediction``.

Tunisia Ligue I (FotMob parent league id 544) is a scores-only league.
``content.stats`` is null and ``content.shotmap.shots`` is empty in ALL
1,060 payloads, so there are no SOT / corner / xG / total-shots targets.
Card events carry ONLY Red and YellowRed (no plain Yellow anywhere);
the referee text is empty in every payload.  The only model target is
goals, from ``header.teams[].score``.

Format (verified from payloads, ``general.leagueName`` + parent 544):
- 2021/2022: Grp. A (8 teams) + Grp. B (8) double round robin (112),
  Championship Group (6, double RR, 30), Relegation Group (4, double
  RR, 12), Placement Matches (2 one-off) = 156.
- 2022/2023: groups 112 + Championship Group (8, double RR, 56) +
  Relegation Group (6, double RR, 30) = 198.
- 2023/2024: groups of 7 + 7, double RR (84) + Championship Group
  (6, 30) + Relegation Group (8, double RR, 56) = 170.  Only 14 teams
  play the group phase (Sportif de Chebba, banned, is absent).
- 2024/2025 on: single table, 16 teams, 30 rounds = 240/season.
All phases are league matches with 90-minute scores (no extra time
and no penalty shootout anywhere in the corpus), so ALL phases enter
the model data — the regular phase is modelled honestly, phase and
all, with no split-group exclusion.  The two Placement Matches are
ordinary FT league matches and are included.

Nine matches are AWARDED (``header.status.awarded == True``, reason
``AW``): the header score is a forfeit score (0-2 / 2-0 / 0-3) that
disagrees with the played event trail (e.g. 5178447 played 3-2,
awarded 0-2).  Following the AE-ProLeague precedent, awarded matches
are kept in the CSV with ``is_awarded=1`` but are EXCLUDED from every
fit and every score.  All other matches have goal-event counts equal
to the header goal totals, and HT Half events agree with goal-time
first-half counts wherever both exist.

Team identity is the FotMob team id, NOT the name string: id 8153
appears as both "Esperance" and "Espérance" (and similar accent
variants exist for Etoile Metlaoui / Olympique de Beja in 2026/27).
Halves come from goal-event times (minute <= 45 counts as first
half, including stoppage-time goals recorded at minute 45) and are
cross-checked against the HT Half event score.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent / "tn_matches.csv"
LEAGUE_ID = "544"

COLUMNS = [
    "match_id", "season", "date", "home_team", "away_team", "home_team_id", "away_team_id", "league_name",
    "home_goals", "away_goals", "round_label", "season_league_id", "phase", "is_awarded",
    "goals_1h", "goals_2h", "notes",
    # Reproducible feed inventory used by the CSV-only EDA and charts.
    "has_stats", "has_shotmap", "referee_named", "has_events", "goal_events", "half_events",
    "card_events", "yellow_events", "red_events", "yellowred_events",
]


def build():
    with open(INDEX, newline="") as f:
        index_rows = [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    assert len(index_rows) == 1060, f"index rows: {len(index_rows)} != 1060"
    rows, log = [], Counter(index_rows=len(index_rows))
    ht_disagreements = []
    event_mismatches = []
    awarded = []

    for ir in index_rows:
        path = BASE / ir["path"]
        d = json.loads(path.read_text())
        g, h = d["general"], d["header"]
        assert g["parentLeagueId"] == 544, ir
        assert g["leagueName"] in {
            "Ligue I", "Ligue I Grp. A", "Ligue I Grp. B",
            "Ligue I Championship Group", "Ligue I Relegation Group",
            "Ligue I Placement Matches"}, ir
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
        is_awarded = 1 if h["status"].get("awarded") else 0
        if is_awarded:
            awarded.append(str(g["matchId"]))
            assert h["status"].get("reason", {}).get("short") == "AW", ir
        if not is_awarded and len(goals) != hg + ag:
            event_mismatches.append(g["matchId"])
        if not is_awarded and events and len(goals) != hg + ag:
            event_mismatches.append(g["matchId"])

        g1 = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45)
        g2 = sum(1 for e in goals if e.get("time") is not None and e["time"] > 45)
        if not events and hg + ag > 0 and not is_awarded:
            # No event feed and goals were scored: halves are UNKNOWN,
            # not 0-0. (In this corpus the only such matches are the
            # two awarded ones, whose halves are blank anyway; the
            # guard keeps the builder honest if the feed ever changes.)
            raise AssertionError(f"no-events match with goals: {g['matchId']}")
        halves_known = bool(events) or hg + ag == 0
        ht = [e for e in halves if e.get("halfStrShort") == "HT"]
        if ht and not is_awarded:
            ht_home, ht_away = ht[-1].get("homeScore"), ht[-1].get("awayScore")
            event_home = sum(1 for e in goals if e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
            event_away = sum(1 for e in goals if not e.get("isHome") and e.get("time") is not None and e["time"] <= 45)
            if (ht_home, ht_away) != (event_home, event_away):
                ht_disagreements.append(g["matchId"])

        label = g.get("leagueRoundName") or ""
        if g["leagueName"] in ("Ligue I Grp. A", "Ligue I Grp. B"):
            phase = "group"
        elif g["leagueName"] == "Ligue I Championship Group":
            phase = "championship"
        elif g["leagueName"] == "Ligue I Relegation Group":
            phase = "relegation"
        elif g["leagueName"] == "Ligue I Placement Matches":
            phase = "placement"
        else:
            phase = "regular"
        notes = ""
        if is_awarded:
            notes = "awarded match (forfeit score); excluded from every fit and score"
        stats = d["content"].get("stats")
        shotmap = d["content"].get("shotmap") or {}
        ref = (mf.get("infoBox") or {}).get("Referee") or {}
        rows.append({
            "match_id": g["matchId"], "season": ir["season"], "date": ir["date"],
            "home_team": home["name"], "away_team": away["name"],
            "home_team_id": home["id"], "away_team_id": away["id"],
            "league_name": g["leagueName"],
            "home_goals": hg, "away_goals": ag, "round_label": label,
            "season_league_id": g["leagueId"], "phase": phase, "is_awarded": is_awarded,
            "goals_1h": "" if (is_awarded or not halves_known) else g1,
            "goals_2h": "" if (is_awarded or not halves_known) else g2, "notes": notes,
            "has_stats": int(stats is not None), "has_shotmap": int(bool(shotmap.get("shots"))),
            "referee_named": int(bool(ref.get("text"))), "has_events": int(bool(events)),
            "goal_events": len(goals), "half_events": len(halves), "card_events": len(cards),
            "yellow_events": len(yellows), "red_events": len(reds), "yellowred_events": len(yellowreds),
        })

    assert not event_mismatches, f"unexpected score/event mismatches (non-awarded): {event_mismatches}"
    assert not ht_disagreements, f"HT disagreements: {ht_disagreements}"
    assert len(awarded) == 9, f"awarded: {awarded}"
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == 1060
    expected = {"2021/2022": 156, "2022/2023": 198, "2023/2024": 170,
                "2024/2025": 240, "2025/2026": 240, "2026/2027": 56}
    assert Counter(r["season"] for r in rows) == expected
    assert Counter(r["season"] for r in rows if r["is_awarded"] == 0) == {
        "2021/2022": 156, "2022/2023": 195, "2023/2024": 170,
        "2024/2025": 237, "2025/2026": 237, "2026/2027": 56}
    assert sum(r["is_awarded"] for r in rows) == 9
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    print("seasons:", dict(Counter(r["season"] for r in rows)))
    print("awarded (excluded):", awarded)
    print("goal-event mismatches (non-awarded): 0; HT disagreements: 0")


if __name__ == "__main__":
    build()
