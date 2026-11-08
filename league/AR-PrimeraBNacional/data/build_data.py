"""Build the Argentina Primera B Nacional Phase-A analysis tables.

The warehouse is deliberately outside this worktree.  Resolve it through
FOTMOB_WAREHOUSE, then a repository-local data_enrichment directory, then the
shared footballprediction warehouse.  This script is strict: the verified
inventory is part of the input contract and a changed/incomplete warehouse
fails loudly.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
OUT = HERE.parent
LEAGUE_ID = "8965"
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]
EXPECTED_GROUP = {"2021": 578, "2022": 666, "2023": 648, "2024": 722,
                  "2025": 612, "2026": 648}
EXPECTED_PLAYOFF = {"2021": 12, "2022": 14, "2023": 21, "2024": 23,
                    "2025": 22, "2026": 0}


def warehouse_root() -> Path:
    candidates = []
    if os.environ.get("FOTMOB_WAREHOUSE"):
        candidates.append(Path(os.environ["FOTMOB_WAREHOUSE"]))
    candidates.append(REPO / "data_enrichment")
    candidates.append(Path("/home/hatch/workspace/footballprediction/data_enrichment"))
    for p in candidates:
        if (p / "fotmob_world_index.csv").is_file():
            return p
    raise FileNotFoundError("No warehouse with fotmob_world_index.csv found")


def payload_path(root: Path, rel: str) -> Path:
    p = Path(rel)
    # Index paths are relative to the footballprediction workspace parent;
    # a local copied index may therefore still point at the shared payloads.
    candidates = [root / p, root.parent / p,
                  Path("/home/hatch/workspace/footballprediction") / p]
    for q in candidates:
        if q.is_file():
            return q
    raise FileNotFoundError(f"payload not found for index path {rel}")


def events(content):
    value = ((content.get("matchFacts") or {}).get("events"))
    if isinstance(value, dict):
        return value.get("events") or []
    return value or []


def score(header):
    teams = header.get("teams") or []
    if len(teams) != 2 or any(t.get("score") is None for t in teams):
        raise AssertionError("missing finished score")
    return int(teams[0]["score"]), int(teams[1]["score"])


def tournament_name(x):
    g = x.get("general") or {}
    ib = ((x.get("content") or {}).get("matchFacts") or {}).get("infoBox") or {}
    t = ib.get("Tournament") or {}
    return str(t.get("leagueName") or g.get("leagueName") or "")


def is_playoff(x):
    name = tournament_name(x)
    gname = str((x.get("general") or {}).get("leagueName") or "")
    rnd = str((x.get("general") or {}).get("matchRound") or "")
    return "Playoff" in name or "Playoff" in gname or bool(
        re.fullmatch(r"(?:1/8|1/4|1/2|final)", rnd, re.I))


def zone(x):
    name = str((x.get("general") or {}).get("leagueName") or "")
    if re.search(r"Zona A", name, re.I):
        return "A"
    if re.search(r"Zona B", name, re.I):
        return "B"
    return ""


def referee(content):
    r = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {})
    return str(r.get("text") or "").strip() if isinstance(r, dict) else ""


def card_counts(evs, is_home, card):
    return sum(1 for e in evs if e.get("type") == "Card" and e.get("card") == card
               and e.get("isHome") is is_home)


def write_csv(path, rows):
    fields = []
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    root = warehouse_root()
    index_path = root / "fotmob_world_index.csv"
    with index_path.open(newline="", encoding="utf-8") as f:
        index = [r for r in csv.DictReader(f) if r.get("league_id") == LEAGUE_ID]
    assert len(index) == 3966, len(index)
    loaded = []
    canonical = {}
    for ir in index:
        with payload_path(root, ir["path"]).open(encoding="utf-8") as f:
            x = json.load(f)
        loaded.append((ir, x))
        for t in ((x.get("header") or {}).get("teams") or []):
            if t.get("id") is not None and t.get("name"):
                old = canonical.get(str(t["id"]))
                if old is None or ir["date"] >= old[0]:
                    canonical[str(t["id"])] = (ir["date"], t["name"])

    phase_counts = Counter(); season_group = Counter(); season_playoff = Counter()
    rows, team_rows = [], []
    group_event_mismatches = []
    nonempty_stats = nonempty_shots = stats_key_rows = 0
    no_event_season = Counter(); card_event_season = Counter(); yellow_event_season = Counter()
    referee_season = Counter()
    for ir, x in loaded:
        c = x.get("content") or {}
        evs = events(c)
        stats = c.get("stats")
        shots = (c.get("shotmap") or {}).get("shots") or []
        stats_key_rows += int(stats is not None)
        # 121 payloads expose the key but contain only Periods.All=None.
        # That is the verified index has_stats false-positive, not content.
        nonempty_stats += int(bool(stats and isinstance(stats, dict) and
                                   (stats.get("Periods") or {}).get("All") is not None))
        nonempty_shots += int(bool(shots))
        if not evs: no_event_season[ir["season"]] += 1
        card_event_season[ir["season"]] += sum(e.get("type") == "Card" for e in evs)
        yellow_event_season[ir["season"]] += sum(e.get("type") == "Card" and e.get("card") == "Yellow" for e in evs)
        if referee(c): referee_season[ir["season"]] += 1
        playoff = is_playoff(x)
        season = ir["season"]
        phase_counts["playoff" if playoff else "group"] += 1
        (season_playoff if playoff else season_group)[season] += 1
        if playoff:
            continue
        h, a = ((x.get("header") or {}).get("teams") or [{}, {}])
        hg, ag = score(x.get("header") or {})
        has_events = bool(evs)
        goal_events = [e for e in evs if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent", False)]
        eh = sum(e.get("isHome") is True for e in goal_events)
        ea = sum(e.get("isHome") is False for e in goal_events)
        if eh != hg or ea != ag:
            group_event_mismatches.append((ir["match_id"], hg, ag, eh, ea))
        ht_hg = sum(e.get("isHome") is True and isinstance(e.get("time"), (int, float))
                    and e["time"] <= 45 for e in goal_events) if has_events else math.nan
        ht_ag = sum(e.get("isHome") is False and isinstance(e.get("time"), (int, float))
                    and e["time"] <= 45 for e in goal_events) if has_events else math.nan
        # The target is intentionally unavailable before the complete 2023 feed.
        cards = {k: math.nan for k in ("yellow_home", "yellow_away", "red_home", "red_away",
                                       "yellowred_home", "yellowred_away", "ht_yellow_home",
                                       "ht_yellow_away")}
        if season >= "2023":
            cards = {
                "yellow_home": card_counts(evs, True, "Yellow"),
                "yellow_away": card_counts(evs, False, "Yellow"),
                "ht_yellow_home": sum(1 for e in evs if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") is True and isinstance(e.get("time"), int) and e["time"] <= 45) if has_events else math.nan,
                "ht_yellow_away": sum(1 for e in evs if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") is False and isinstance(e.get("time"), int) and e["time"] <= 45) if has_events else math.nan,
                "red_home": card_counts(evs, True, "Red"),
                "red_away": card_counts(evs, False, "Red"),
                "yellowred_home": card_counts(evs, True, "YellowRed"),
                "yellowred_away": card_counts(evs, False, "YellowRed"),
            }
        home_id, away_id = str(h.get("id")), str(a.get("id"))
        row = {
            "match_id": ir["match_id"], "season": season, "date": ir["date"],
            "round": str((x.get("general") or {}).get("matchRound") or ""),
            "zone": zone(x), "phase": "group", "home_id": home_id,
            "home_name": canonical[home_id][1], "away_id": away_id,
            "away_name": canonical[away_id][1], "hg": hg, "ag": ag,
            "ht_hg": ht_hg, "ht_ag": ht_ag, "referee": referee(c),
            "has_events": has_events, "stats_present": False,
            "shotmap_present": False, **cards,
        }
        rows.append(row)
        for side, tid, name, oid, oname in (("home", home_id, row["home_name"], away_id, row["away_name"]),
                                             ("away", away_id, row["away_name"], home_id, row["home_name"])):
            suffix = "home" if side == "home" else "away"
            other = "away" if side == "home" else "home"
            tr = {"match_id": row["match_id"], "season": season, "date": row["date"],
                  "round": row["round"], "zone": row["zone"], "phase": "group",
                  "team_id": tid, "team_name": name, "opponent_id": oid,
                  "opponent_name": oname, "home_away": side,
                  "goals_for": row["hg" if suffix == "home" else "ag"],
                  "goals_against": row["ag" if suffix == "home" else "hg"],
                  "ht_goals_for": row["ht_hg" if suffix == "home" else "ht_ag"],
                  "ht_goals_against": row["ht_ag" if suffix == "home" else "ht_hg"],
                  "yellow_for": row[f"yellow_{suffix}"], "yellow_against": row[f"yellow_{other}"],
                  "ht_yellow_for": row[f"ht_yellow_{suffix}"], "ht_yellow_against": row[f"ht_yellow_{other}"],
                  "red_for": row[f"red_{suffix}"], "red_against": row[f"red_{other}"],
                  "yellowred_for": row[f"yellowred_{suffix}"], "yellowred_against": row[f"yellowred_{other}"],
                  "referee": row["referee"], "has_events": row["has_events"]}
            team_rows.append(tr)
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    team_rows.sort(key=lambda r: (r["date"], int(r["match_id"]), r["home_away"]))
    assert phase_counts == Counter({"group": 3874, "playoff": 92}), phase_counts
    assert dict(season_group) == EXPECTED_GROUP, season_group
    assert season_playoff == Counter(EXPECTED_PLAYOFF), season_playoff
    assert len({r["match_id"] for r in rows}) == len(rows)
    assert len(team_rows) == 2 * len(rows)
    assert not group_event_mismatches, group_event_mismatches
    assert nonempty_stats == 0, nonempty_stats
    assert nonempty_shots == 0, nonempty_shots
    assert stats_key_rows == 121, stats_key_rows
    assert no_event_season == Counter({"2021": 75, "2022": 76}), no_event_season
    assert card_event_season == Counter({"2021": 145, "2022": 187, "2023": 3534,
                                         "2024": 3777, "2025": 3157, "2026": 3184}), card_event_season
    assert yellow_event_season == Counter({"2021": 0, "2022": 0, "2023": 3320,
                                           "2024": 3514, "2025": 2965, "2026": 2995}), yellow_event_season
    assert referee_season == Counter({"2022": 604, "2023": 634, "2024": 703,
                                      "2025": 615, "2026": 646}), referee_season
    assert {s: len({x["home_id"] for x in rows if x["season"] == s} |
                   {x["away_id"] for x in rows if x["season"] == s})
            for s in EXPECTED_GROUP} == {"2021": 35, "2022": 37, "2023": 37,
                                         "2024": 38, "2025": 36, "2026": 36}
    assert Counter((x["season"], x["zone"]) for x in rows) == Counter({
        ("2021", "A"): 272, ("2021", "B"): 306, ("2022", ""): 666,
        ("2023", "A"): 342, ("2023", "B"): 306, ("2024", ""): 722,
        ("2025", "A"): 306, ("2025", "B"): 306, ("2026", ""): 648})
    assert Counter(r["season"] for r in rows) == Counter(EXPECTED_GROUP)
    write_csv(OUT / "bnac_matches.csv", rows)
    write_csv(OUT / "team_matches.csv", team_rows)
    print(json.dumps({"warehouse": str(root), "index": len(index), "group": len(rows),
                      "playoff": phase_counts["playoff"], "team_rows": len(team_rows),
                      "per_season_group": dict(season_group),
                      "per_season_playoff": dict(season_playoff),
                      "nonempty_stats": nonempty_stats, "nonempty_shotmap": nonempty_shots,
                      "group_goal_event_mismatches": len(group_event_mismatches)}, indent=2))


if __name__ == "__main__":
    main()
