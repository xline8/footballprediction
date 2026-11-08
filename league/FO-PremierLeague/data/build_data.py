#!/usr/bin/env python3
"""Build the Faroe Islands Premier League Phase A match table.

The warehouse index is the source of match identity and official score.  The
event feed supplies cards, played goal counts, and the explicit time-45
half-time score.  Match 3822183 is retained for audit with its played-event
score, but is marked excluded: its official result is 0-3/AW while the played
events say 3-1, so it must not enter a fitting corpus.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "250"
AWARDED_ID = "3822183"
SEASONS = {"2021": 135, "2022": 135, "2023": 135, "2024": 135,
           "2025": 135, "2026": 135}
FIELDS = [
    "match_id", "season", "date", "round", "home_team_id", "away_team_id",
    "home", "away", "home_goals", "away_goals", "ht_home_goals",
    "ht_away_goals", "yellow_home", "yellow_away", "yellowred_home",
    "yellowred_away", "red_home", "red_away", "cards_source", "awarded",
    "excluded",
]


def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def main(repo_root=None, out=None):
    # Runner contract (league/runner/run_daily.py rebuild_csv_world):
    # the runner points INDEX / MAIN_REPO at its checkout and calls
    # main() with no arguments; the table then goes to this league's
    # own data path. The CLI below passes repo_root / out explicitly.
    root = Path(repo_root) if repo_root is not None else MAIN_REPO
    index = INDEX if repo_root is None else root / "data_enrichment" / "fotmob_world_index.csv"
    with index.open(newline="") as fh:
        source = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    # Frozen build-time count asserted as a FLOOR (the TZ runner
    # pattern): the daily runner rebuilds this table as future
    # seasons grow the index, so exact equality would break it.
    assert len(source) >= 810, len(source)

    names = defaultdict(Counter)
    loaded = []
    for r in source:
        d = json.loads((root / r["path"]).read_text())
        g = d.get("general") or {}
        h, a = g.get("homeTeam") or {}, g.get("awayTeam") or {}
        names[str(h.get("id"))][h.get("name", "")] += 1
        names[str(a.get("id"))][a.get("name", "")] += 1
        loaded.append((r, d))
    canonical = {tid: counts.most_common(1)[0][0] for tid, counts in names.items()}

    rows = []
    ht_seen = 0
    non_awarded_goal_checks = 0
    for r, d in loaded:
        g, status, content = d.get("general") or {}, (d.get("header") or {}).get("status") or {}, d.get("content") or {}
        hs, as_ = g.get("homeTeam") or {}, g.get("awayTeam") or {}
        ev = events(content)
        goals = [e for e in ev if e.get("type") == "Goal"]
        cards = [e for e in ev if e.get("type") == "Card"]
        halfs = [e for e in ev if e.get("type") == "Half" and e.get("time") == 45]
        assert len(halfs) == 1, (r["match_id"], len(halfs))
        ht_seen += 1
        ht = halfs[0]
        official_h, official_a = (int(x.strip()) for x in r["score"].split("-"))
        event_h = sum(1 for e in goals if e.get("isHome") is True)
        event_a = sum(1 for e in goals if e.get("isHome") is False)
        awarded = (status.get("reason") or {}).get("short") == "AW"
        if not awarded:
            assert (event_h, event_a) == (official_h, official_a), (r["match_id"], event_h, event_a, official_h, official_a)
            non_awarded_goal_checks += 1
        def count(kind, home):
            return sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is home)
        # Unified yellows (the K-FO target, program convention): a second
        # yellow (YellowRed) counts as a yellow card; straight Red does not.
        # yellowred_* below is the breakdown, not an extra count.
        def unified_yellows(home):
            return count("Yellow", home) + count("YellowRed", home)
        rows.append({
            "match_id": r["match_id"], "season": r["season"], "date": r["date"],
            "round": g.get("leagueRoundName") or g.get("matchRound") or "",
            "home_team_id": hs.get("id"), "away_team_id": as_.get("id"),
            "home": canonical[str(hs.get("id"))], "away": canonical[str(as_.get("id"))],
            "home_goals": event_h, "away_goals": event_a,
            "ht_home_goals": ht.get("homeScore"), "ht_away_goals": ht.get("awayScore"),
            "yellow_home": unified_yellows(True), "yellow_away": unified_yellows(False),
            "yellowred_home": count("YellowRed", True), "yellowred_away": count("YellowRed", False),
            "red_home": count("Red", True), "red_away": count("Red", False),
            "cards_source": "events", "awarded": int(awarded), "excluded": int(awarded),
        })
    assert ht_seen == len(source)
    assert non_awarded_goal_checks >= 809
    assert sum(r["excluded"] == 0 for r in rows) >= 809
    assert sum(r["match_id"] == AWARDED_ID and r["excluded"] == 1 for r in rows) == 1
    assert {s: sum(r["season"] == s and r["excluded"] == 0 for r in rows) for s in SEASONS} == {"2021": 135, "2022": 134, "2023": 135, "2024": 135, "2025": 135, "2026": 135}
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    out = Path(out) if out is not None else HERE / "fo_premier_league_matches.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} source rows ({sum(r['excluded'] == 0 for r in rows)} eligible) -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", required=True)
    cli = ap.parse_args()
    main(cli.repo_root, cli.out)
