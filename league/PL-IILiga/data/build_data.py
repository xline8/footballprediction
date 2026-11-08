"""Build the Poland II Liga scores-only analysis tables.

The payload store is normally at data_enrichment/fotmob_world.  A read-only
sibling warehouse fallback is retained for this worktree because the large
payload store is not checked out here.  Assertions inspect every payload; the
index flags are never used as evidence for coverage.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
SIBLING = ROOT.parent / "footballprediction"
OUT = Path(__file__).resolve().parent

def payload_path(index_row):
    p = ROOT / index_row["path"]
    if not p.exists():
        p = SIBLING / index_row["path"]
    return p

def parse_score(score):
    a, b = (score or "0 - 0").split("-")[:2]
    return int(a.strip()), int(b.strip())

def events_block(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []

def event_goals(events):
    return [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]

def event_count(events, card, home):
    return sum(1 for e in events if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == home)

def build_match(index_row):
    payload = json.loads(payload_path(index_row).read_text())
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    content = payload.get("content") or {}
    assert content.get("stats") is None, f"stats present in {index_row['match_id']}"
    assert not ((content.get("shotmap") or {}).get("shots") or []), f"shotmap shots present in {index_row['match_id']}"
    assert general.get("coverageLevel") == "lower", index_row["match_id"]
    assert str(general.get("parentLeagueId")) == "8935", index_row["match_id"]
    events = events_block(content)
    goals = event_goals(events)
    hg, ag = parse_score(status.get("scoreStr"))
    home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    name = general.get("leagueName") or ""
    phase = {"2. Division": "regular", "II Liga": "regular", "II Liga Promotion Playoff": "playoff_promotion"}.get(name)
    assert phase is not None, (index_row["match_id"], name)
    eh = sum(bool(e.get("isHome")) for e in goals)
    ea = sum(not bool(e.get("isHome")) for e in goals)
    # A no-event 0-0 is a trivially known 0-0 half split; awarded walkovers
    # without events remain unvalidated.  The sole scored mismatch is also 0.
    validated = ((not goals and (hg, ag) == (0, 0)) or
                 (bool(goals) and (eh, ea) == (hg, ag)))
    row = {
        "match_id": index_row["match_id"], "league": "PL-IILiga", "season": index_row["season"], "date": index_row["date"],
        "round": str(general.get("matchRound") or ""), "league_round_name": str(general.get("leagueRoundName") or ""),
        "phase": phase, "league_name_raw": name, "parent_league_id": general.get("parentLeagueId"),
        "home_team_id": home.get("id"), "home_team": home.get("name"), "away_team_id": away.get("id"), "away_team": away.get("name"),
        "coverage_level": general.get("coverageLevel"), "home_goals": hg, "away_goals": ag,
        "is_b_home": int(str(home.get("id")) in {"585552", "585484", "556984", "1501585", "585596"}),
        "is_b_away": int(str(away.get("id")) in {"585552", "585484", "556984", "1501585", "585596"}),
        # For the frozen coverage number, "events present" means a goal
        # event feed. Card-only event blocks do not establish an HT split.
        "has_events": int(bool(goals)), "has_stats": 0, "has_shotmap": 0,
        "awarded": int(bool(status.get("awarded"))), "ht_home_goals": None, "ht_away_goals": None,
        "ht_source": "events" if goals else "none", "ht_validated": int(validated),
    }
    if goals:
        row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    elif validated:
        row["ht_home_goals"] = 0
        row["ht_away_goals"] = 0
    for side in (True, False):
        prefix = "home" if side else "away"
        # Feed fact: this league's event feed carries NO plain-Yellow
        # Card events (365 Card events in 1,679 matches are 173 Red +
        # 192 YellowRed only), so ev_yellow_* is 0 by construction.
        # ev_red_* counts dismissals (Red + YellowRed).
        row[f"ev_yellow_{prefix}"] = event_count(events, "Yellow", side)
        row[f"ev_yellowred_{prefix}"] = event_count(events, "YellowRed", side)
        row[f"ev_red_{prefix}"] = event_count(events, "Red", side) + row[f"ev_yellowred_{prefix}"]
    return row

def main():
    rows0 = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "8935"]
    rows = [build_match(r) for r in sorted(rows0, key=lambda r: (r["date"], r["match_id"]))]
    assert len(rows) == 1679
    assert len({r["match_id"] for r in rows}) == 1679
    expected = {s: {"regular": 306, "playoff_promotion": 3} for s in ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]}
    expected["2021/2022"]["2. Division"] = 196
    expected["2021/2022"]["II Liga"] = 110
    expected["2026/2027"] = {"regular": 134}
    for season, counts in expected.items():
        got = {}
        for r in rows:
            if r["season"] == season:
                key = r["league_name_raw"] if season == "2021/2022" else r["phase"]
                got[key] = got.get(key, 0) + 1
        if season == "2021/2022":
            assert got == {"2. Division": 196, "II Liga": 110, "II Liga Promotion Playoff": 3}, got
        else:
            assert got == counts, (season, got, counts)
    with (OUT / "plii_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"], "is_b_team": r[f"is_b_{side}"]})
    with (OUT / "plii_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")

if __name__ == "__main__":
    main()
