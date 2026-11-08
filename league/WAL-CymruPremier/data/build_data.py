"""Build the Wales Cymru Premier Phase A tables and payload inventory."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "116"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
FIELDS = ["match_id", "league", "season", "date", "round", "sub_tournament", "stage",
          "home_team_id", "home_team", "away_team_id", "away_team", "finished", "awarded",
          "home_goals", "away_goals", "has_events", "n_events", "n_goal_events", "n_card_events",
          "n_red_events", "ht_home_goals", "ht_away_goals", "ht_source", "ht_suspect",
          "has_stats_all", "has_stats_half", "has_shotmap", "referee", "has_lineup",
          "lineup_block", "eligible"]
TEAM_FIELDS = ["match_id", "season", "date", "stage", "sub_tournament", "team_id", "team",
               "venue", "goals_for", "goals_against"]


def score(value):
    a, b = str(value).replace(" ", "").split("-", 1)
    return int(a), int(b)


def parse(index_row, warehouse_root=MAIN_REPO):
    payload = json.loads((warehouse_root / index_row["path"]).read_text(encoding="utf-8"))
    general = payload.get("general") or {}
    status = (payload.get("header") or {}).get("status") or {}
    content = payload.get("content") or {}
    facts = content.get("matchFacts") or {}
    events = ((facts.get("events") or {}).get("events") or [])
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    cards = [e for e in events if e.get("type") == "Card"]
    half = next((e for e in events if e.get("type") == "Half" and str(e.get("time")) == "45"
                 and e.get("homeScore") is not None and e.get("awayScore") is not None), None)
    info = facts.get("infoBox") or {}
    tournament = info.get("Tournament") or {}
    sub = tournament.get("leagueName") or ""
    if sub == "Premier League": stage = "regular"
    elif sub == "Premier League Championship Group": stage = "championship"
    elif sub == "Premier League Relegation Group": stage = "relegation"
    elif sub in {"Premier League ECL Playoff", "Premier League CL Playoff"}: stage = "playoff"
    else: raise ValueError(f"unknown tournament {sub!r} for {index_row['match_id']}")
    home = general.get("homeTeam") or {}; away = general.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row["score"])
    stats = content.get("stats")
    periods = stats.get("Periods") if isinstance(stats, dict) else None
    shotmap = content.get("shotmap")
    shots = shotmap.get("shots") if isinstance(shotmap, dict) else None
    lineup = content.get("lineup")
    referee = ((info.get("Referee") or {}).get("text") or "").strip()
    awarded = int(status.get("awarded") is True or (status.get("reason") or {}).get("short") == "AW")
    finished = int(bool(status.get("finished", general.get("finished", False))))
    eventless_zero = not events and (hg, ag) == (0, 0)
    ht_source = "half_event" if half else ("implied_0_0" if eventless_zero else "")
    return {
        "match_id": index_row["match_id"], "league": "WAL-CymruPremier", "season": index_row["season"],
        "date": index_row["date"], "round": str(tournament.get("round") or ""),
        "sub_tournament": sub, "stage": stage,
        "home_team_id": home.get("id"), "home_team": home.get("name") or index_row["home"],
        "away_team_id": away.get("id"), "away_team": away.get("name") or index_row["away"],
        "finished": finished, "awarded": awarded, "home_goals": hg, "away_goals": ag,
        "has_events": int(bool(events)), "n_events": len(events), "n_goal_events": len(goals),
        "n_card_events": len(cards), "n_red_events": sum(e.get("card") in {"Red", "YellowRed"} for e in cards),
        "ht_home_goals": half.get("homeScore") if half else (0 if eventless_zero else ""),
        "ht_away_goals": half.get("awayScore") if half else (0 if eventless_zero else ""),
        "ht_source": ht_source, "ht_suspect": 0,
        "has_stats_all": int(isinstance(stats, dict) and bool(periods and (periods.get("All") or periods.get("ALL")))),
        "has_stats_half": int(isinstance(periods, dict) and bool(periods.get("FirstHalf") and periods.get("SecondHalf"))),
        "has_shotmap": int(bool(shots)), "referee": referee,
        "has_lineup": int(isinstance(lineup, dict) and bool((lineup.get("homeTeam") or {}).get("starters") or (lineup.get("awayTeam") or {}).get("starters"))),
        "lineup_block": int(isinstance(lineup, dict)), "eligible": int(stage != "playoff"),
    }, payload


def inventory(index_rows, built, payloads):
    by = {s: [r for r in built if r["season"] == s] for s in SEASONS}
    event_types, card_types = Counter(), Counter()
    team_ids = set(); teams_by = {}
    goal_agree = 0; parent_agree = 0; identity_agree = 0; coverage = {}
    rename_ids = defaultdict(set)
    for ir, r, payload_item in zip(index_rows, built, payloads):
        p = payload_item[1]
        g = p.get("general") or {}; c = p.get("content") or {}; facts = c.get("matchFacts") or {}
        ev = ((facts.get("events") or {}).get("events") or [])
        for e in ev:
            event_types[e.get("type", "")] += 1
            if e.get("type") == "Card": card_types[e.get("card", "")] += 1
        gh = sum(e.get("isHome") is True for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent"))
        ga = sum(e.get("isHome") is False for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent"))
        goal_agree += (gh, ga) == (r["home_goals"], r["away_goals"])
        parent_agree += g.get("parentLeagueId") == 116
        identity_agree += (g.get("homeTeam") or {}).get("name") == r["home_team"] and (g.get("awayTeam") or {}).get("name") == r["away_team"]
        for side in ("home", "away"):
            tid, name = r[f"{side}_team_id"], r[f"{side}_team"]
            team_ids.add(tid); rename_ids[str(tid)].add(name)
        s = r["season"]
        if s not in teams_by: teams_by[s] = set()
        teams_by[s] |= {r["home_team_id"], r["away_team_id"]}
    for s, rr in by.items():
        coverage[s] = {"rows": len(rr), "eligible": sum(r["eligible"] for r in rr), "events": sum(r["has_events"] for r in rr),
                       "ht_derivable": sum(bool(r["ht_source"]) for r in rr), "stats_all": sum(r["has_stats_all"] for r in rr),
                       "stats_half": sum(r["has_stats_half"] for r in rr), "shotmap": sum(r["has_shotmap"] for r in rr),
                       "lineup": sum(r["lineup_block"] for r in rr), "referee": sum(bool(r["referee"]) for r in rr)}
    inv = {"totals": {"index_rows": len(index_rows), "files_on_disk": len(set(x[0] for x in payloads)),
             "unique_match_ids": len({r["match_id"] for r in built}), "eligible": sum(r["eligible"] for r in built),
             "playoff": sum(r["stage"] == "playoff" for r in built), "finished": sum(r["finished"] for r in built),
             "awarded": sum(r["awarded"] for r in built), "eventless": sum(not r["has_events"] for r in built),
             "zero_zero_eventless": sum(not r["has_events"] and r["home_goals"] == r["away_goals"] == 0 for r in built),
             "goal_event_score_agree": int(goal_agree), "cards": sum(r["n_card_events"] for r in built),
             "red_events": sum(r["n_red_events"] for r in built), "parent_league_agree": int(parent_agree),
             "identity_agree": int(identity_agree)}, "by_season": coverage,
           "event_types": dict(event_types), "card_values": dict(card_types),
           "team_counts": {"distinct_ids": len(team_ids), "by_season": {s: len(v) for s, v in teams_by.items()}},
           "rename_map": {k: sorted(v) for k, v in rename_ids.items() if len(v) > 1}}
    (ROOT / "analysis").mkdir(parents=True, exist_ok=True)
    (ROOT / "analysis/inventory_summary.json").write_text(json.dumps(inv, indent=2, sort_keys=True) + "\n")
    return inv


def main():
    with INDEX.open(encoding="utf-8", newline="") as f:
        index_rows = sorted((r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID), key=lambda r: (r["date"], r["match_id"]))
    built, payloads = [], []
    for row in index_rows:
        r, p = parse(row); built.append(r); payloads.append((str(MAIN_REPO / row["path"]), p))
    assert len(built) == 1103 and len({r["match_id"] for r in built}) == 1103
    assert all(r["finished"] == 1 and r["awarded"] == 0 for r in built)
    assert {s: sum(r["eligible"] for r in built if r["season"] == s) for s in SEASONS} == {**{s: 192 for s in SEASONS[:5]}, "2026/2027": 127}
    assert sum(r["eligible"] for r in built) == 1087 and sum(r["stage"] == "playoff" for r in built) == 16
    assert sum(r["n_goal_events"] == r["home_goals"] + r["away_goals"] for r in built) == 1103
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "wal_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(built)
    team_rows = []
    for r in built:
        if not r["eligible"]: continue
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "stage": r["stage"], "sub_tournament": r["sub_tournament"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]})
    assert len(team_rows) == 2174
    with (HERE / "wal_team_matches.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TEAM_FIELDS); w.writeheader(); w.writerows(team_rows)
    inv = inventory(index_rows, built, payloads)
    print(json.dumps({"matches": len(built), "eligible": sum(r["eligible"] for r in built), "team_rows": len(team_rows), "inventory": inv["totals"]}, sort_keys=True))


if __name__ == "__main__": main()
