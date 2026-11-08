"""Build the Argentina Primera B Metropolitana Phase-A match table.

The parent FotMob league 9213 contains PBM and Federal A.  This builder
keeps only payloads whose general.leagueName contains ``Metropolitana`` and
then keeps the regular/group phases defined by the Phase-A brief.
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
LEAGUE_ID = "9213"
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]
EXPECTED_INDEX = 2236
EXPECTED_GROUP = {"2021": 272, "2022": 272, "2023": 272, "2024": 462,
                  "2025": 420, "2026": 462}
EXPECTED_EXCLUDED = {"2021": 23, "2022": 10, "2023": 14, "2024": 15,
                     "2025": 14, "2026": 0}
EXPECTED_NAMES = {
    ("2021", "Promotion Playoff"): 9, ("2022", "Promotion Playoff"): 10,
    ("2023", "Promotion Playoff"): 12, ("2024", "Promotion Playoff"): 12,
    ("2025", "Promotion Playoff"): 14,
    ("2021", "Championship Playoff"): 2, ("2023", "Championship Playoff"): 2,
    ("2024", "Championship Playoff"): 2,
    ("2021", "Complemento Group A"): 3, ("2021", "Complemento Group B"): 3,
    ("2021", "Complemento Group C"): 3, ("2021", "Complemento Final Stage"): 3,
    ("2024", "Fase Tercer Ascenso"): 1,
}


def warehouse_root() -> Path:
    candidates = []
    if os.environ.get("FOTMOB_WAREHOUSE"):
        candidates.append(Path(os.environ["FOTMOB_WAREHOUSE"]))
    local = REPO / "data_enrichment"
    if (local / "fotmob_world_index.csv").is_file() and (local / "fotmob_world").is_dir():
        candidates.append(local)
    candidates.append(Path("/home/hatch/workspace/footballprediction/data_enrichment"))
    for root in candidates:
        if (root / "fotmob_world_index.csv").is_file() and (root / "fotmob_world").is_dir():
            return root
    raise FileNotFoundError("No valid FotMob warehouse found")


def payload_path(root: Path, rel: str) -> Path:
    p = Path(rel)
    for candidate in (root / p, root.parent / p,
                      Path("/home/hatch/workspace/footballprediction") / p):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(rel)


def events(content):
    value = ((content.get("matchFacts") or {}).get("events"))
    if isinstance(value, dict):
        return value.get("events") or []
    return value or []


def tournament_name(payload):
    general = payload.get("general") or {}
    info = (((payload.get("content") or {}).get("matchFacts") or {}).get("infoBox") or {})
    tournament = info.get("Tournament") or {}
    return str(tournament.get("leagueName") or general.get("leagueName") or "")


def is_pbm(payload):
    return "Metropolitana" in str((payload.get("general") or {}).get("leagueName") or "")


def exclusion_bucket(name: str) -> str | None:
    for needle in ("Promotion Playoff", "Championship Playoff", "Complemento Group A",
                   "Complemento Group B", "Complemento Group C", "Complemento Final Stage",
                   "Fase Tercer Ascenso"):
        if needle in name:
            return needle
    return None


def score(payload):
    teams = (payload.get("header") or {}).get("teams") or []
    if len(teams) != 2 or any(t.get("score") is None for t in teams):
        raise AssertionError("missing finished score")
    return int(teams[0]["score"]), int(teams[1]["score"])


def referee(content):
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    value = info.get("Referee") or {}
    return str(value.get("text") or "").strip() if isinstance(value, dict) else ""


def write_csv(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    root = warehouse_root()
    with (root / "fotmob_world_index.csv").open(newline="", encoding="utf-8") as fh:
        parent = [r for r in csv.DictReader(fh) if r.get("league_id") == LEAGUE_ID]
    loaded = []
    canonical = {}
    for ir in parent:
        with payload_path(root, ir["path"]).open(encoding="utf-8") as fh:
            payload = json.load(fh)
        if not is_pbm(payload):
            continue
        loaded.append((ir, payload))
        for team in ((payload.get("header") or {}).get("teams") or []):
            tid, name = team.get("id"), team.get("name")
            if tid is not None and name and (tid not in canonical or ir["date"] >= canonical[tid][0]):
                canonical[tid] = (ir["date"], name)

    assert len(parent) == 5455, len(parent)
    assert len(loaded) == EXPECTED_INDEX, len(loaded)
    assert {ir["season"] for ir, _ in loaded} == set(SEASONS)
    assert min(ir["date"] for ir, _ in loaded) == "2021-03-06"
    assert max(ir["date"] for ir, _ in loaded) == "2026-11-02"

    phase_counts = Counter(); exclusion_counts = Counter(); season_group = Counter()
    rows = []; mismatch = []; nonempty_stats = 0; nonempty_shots = 0; nonempty_ref = 0
    empty_events = Counter(); cards = Counter(); red_by_season = Counter(); boundary = Counter(); missing_goal_times = []
    for ir, payload in loaded:
        content = payload.get("content") or {}
        evs = events(content)
        name = tournament_name(payload)
        for event in evs:
            if event.get("type") == "Card":
                cards[event.get("card")] += 1
                if event.get("card") == "Red":
                    red_by_season[ir["season"]] += 1
        bucket = exclusion_bucket(name)
        if bucket:
            phase_counts["excluded"] += 1
            exclusion_counts[(ir["season"], bucket)] += 1
            continue
        phase_counts["group"] += 1; season_group[ir["season"]] += 1
        hg, ag = score(payload)
        teams = (payload.get("header") or {}).get("teams") or []
        goals = [e for e in evs if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent", False)]
        eh = sum(e.get("isHome") is True for e in goals)
        ea = sum(e.get("isHome") is False for e in goals)
        if (eh, ea) != (hg, ag):
            mismatch.append((ir["match_id"], hg, ag, eh, ea))
        if not evs:
            empty_events[ir["season"]] += 1
            assert (hg, ag) == (0, 0), (ir["match_id"], hg, ag)
        ht_h = ht_a = 0
        for event in goals:
            time = event.get("time")
            if not isinstance(time, int):
                missing_goal_times.append(ir["match_id"])
                continue
            if time in (45, 46):
                boundary[str(time)] += 1
            if time <= 45:
                if event.get("isHome") is True: ht_h += 1
                elif event.get("isHome") is False: ht_a += 1
        if missing_goal_times and missing_goal_times[-1] == ir["match_id"] and (hg + ag) > 0:
            raise AssertionError(f"non-zero match has goal without integer event time: {ir['match_id']}")
        stats = content.get("stats") or {}
        stats_all = isinstance(stats, dict) and (stats.get("Periods") or {}).get("All") is not None
        shotmap = (content.get("shotmap") or {}).get("shots") or []
        nonempty_stats += int(stats_all); nonempty_shots += int(bool(shotmap)); nonempty_ref += int(bool(referee(content)))
        home, away = teams
        row = {
            "match_id": ir["match_id"], "season": ir["season"], "date": ir["date"],
            "round": str((payload.get("general") or {}).get("matchRound") or ""),
            "tournament": name, "phase": "group",
            "home_team_id": home.get("id"), "home_team": canonical[home.get("id")][1],
            "away_team_id": away.get("id"), "away_team": canonical[away.get("id")][1],
            "home_goals": hg, "away_goals": ag,
            "ht_home_goals": ht_h if evs or (hg == 0 and ag == 0) else math.nan,
            "ht_away_goals": ht_a if evs or (hg == 0 and ag == 0) else math.nan,
            "ht_source": "events" if evs else "none",
            "event_goals_home": eh, "event_goals_away": ea,
            "referee": referee(content), "has_events": bool(evs),
            "stats_nonempty": bool(stats_all), "has_shotmap": bool(shotmap),
            "red_home": sum(e.get("type") == "Card" and e.get("card") == "Red" and e.get("isHome") is True for e in evs),
            "red_away": sum(e.get("type") == "Card" and e.get("card") == "Red" and e.get("isHome") is False for e in evs),
            "yellowred_home": sum(e.get("type") == "Card" and e.get("card") == "YellowRed" and e.get("isHome") is True for e in evs),
            "yellowred_away": sum(e.get("type") == "Card" and e.get("card") == "YellowRed" and e.get("isHome") is False for e in evs),
        }
        rows.append(row)

    assert phase_counts == Counter({"group": 2160, "excluded": 76}), phase_counts
    assert dict(season_group) == EXPECTED_GROUP, season_group
    assert {s: sum(v for (season, _), v in exclusion_counts.items() if season == s) for s in SEASONS} == EXPECTED_EXCLUDED
    for key, expected in EXPECTED_NAMES.items():
        assert exclusion_counts[key] == expected, (key, exclusion_counts[key])
    assert len({r["match_id"] for r in rows}) == len(rows)
    assert not mismatch, mismatch[:3]
    assert nonempty_stats == 0, nonempty_stats
    assert nonempty_shots == 0, nonempty_shots
    assert nonempty_ref == 0, nonempty_ref
    assert cards["Yellow"] == 0, cards
    assert dict(red_by_season) == {"2021": 58, "2022": 73, "2023": 66, "2024": 124, "2025": 145, "2026": 120}, red_by_season
    assert sum(cards.values()) > 0
    assert boundary == {"45": boundary["45"], "46": boundary["46"]}
    assert not missing_goal_times, missing_goal_times[:3]
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    write_csv(OUT / "pbm_matches.csv", rows)
    print(json.dumps({"warehouse": str(root), "parent_index": len(parent), "pbm_index": len(loaded),
                      "group": len(rows), "excluded": phase_counts["excluded"],
                      "per_season_group": dict(season_group), "per_season_excluded": dict(EXPECTED_EXCLUDED),
                      "boundary_goal_times": dict(boundary), "empty_events": dict(empty_events),
                      "cards": dict(cards), "nonempty_stats": nonempty_stats,
                      "nonempty_shotmap": nonempty_shots, "referee_nonempty": nonempty_ref}, indent=2))


if __name__ == "__main__":
    main()
