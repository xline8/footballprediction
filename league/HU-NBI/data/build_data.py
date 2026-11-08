#!/usr/bin/env python3
"""Build the Hungary NBI analysis table from the FotMob world warehouse.

The warehouse is read-only input.  Set FOTMOB_WORLD_ROOT and/or
FOTMOB_WORLD_INDEX when running outside the coordinator's usual checkout.
"""
from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = Path("/home/hatch/workspace/footballprediction")
WORLD_ROOT = Path(os.environ.get("FOTMOB_WORLD_ROOT", DEFAULT_ROOT))
INDEX = Path(os.environ.get("FOTMOB_WORLD_INDEX", HERE / "data_enrichment/fotmob_world_index.csv"))
OUT = HERE / "league/HU-NBI/data/hu_nbi.csv"
AUDIT = HERE / "league/HU-NBI/data/audit.json"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]

STAT_KEYS = ("BallPossesion", "total_shots", "ShotsOnTarget", "corners", "big_chance",
             "touches_opp_box", "fouls", "yellow_cards", "red_cards", "expected_goals")


def num(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.split()[0].replace("%", ""))
        except (ValueError, IndexError):
            return None
    return None


def stats(content):
    out = {}
    periods = ((content.get("stats") or {}).get("Periods") or {})
    for period, block in periods.items():
        for section in (block or {}).get("stats", []) or []:
            for item in section.get("stats", []) or []:
                values = item.get("stats") or []
                pair = (num(values[0]) if len(values) > 0 else None,
                        num(values[1]) if len(values) > 1 else None)
                if pair != (None, None):
                    out[(period, item.get("key"))] = pair
    return out


def events(content):
    return (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])


def event_count(ev, kind, home):
    # YellowRed is counted as a yellow and as a red: it is the second caution
    # that produces a sending-off, and preserving both facts is most useful.
    accepted = {"Yellow", "YellowRed"} if kind == "yellow" else {"Red", "YellowRed"}
    return sum(1 for e in ev if e.get("type") == "Card" and e.get("card") in accepted
               and bool(e.get("isHome")) == home)


def first_half(ev, event_type, home):
    # FotMob's integer time is the minute (45+stoppage remains time 45 in
    # this corpus).  The frozen rule is time <= 45; missing time is excluded.
    return sum(1 for e in ev if e.get("type") == event_type and e.get("time") is not None
               and e.get("time") <= 45 and bool(e.get("isHome")) == home)


def score(row, header):
    teams = header.get("teams") or []
    if len(teams) != 2 or any(t.get("score") is None for t in teams):
        text = row.get("score", "")
        h, a = text.split("-", 1)
        return int(h), int(a)
    return int(teams[0]["score"]), int(teams[1]["score"])


def main():
    rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "212"]
    rows.sort(key=lambda r: (r["season"], r["date"], int(r["match_id"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["match_id", "season", "date", "home_id", "away_id", "home_team", "away_team",
              "home_goals", "away_goals", "sot_h", "sot_a", "corners_h", "corners_a",
              "total_shots_h", "total_shots_a", "possession_h", "possession_a", "big_chances_h", "big_chances_a",
              "box_touches_h", "box_touches_a", "fouls_h", "fouls_a", "stats_yellow_h",
              "stats_yellow_a", "stats_red_h", "stats_red_a", "event_yellow_h", "event_yellow_a",
              "event_red_h", "event_red_a", "referee", "goals_1h_h", "goals_1h_a",
              "cards_1h_h", "cards_1h_a", "has_stats"]
    out, audit = [], {"seasons": {}, "stat_keys": {}, "section_keys": {}, "periods": {},
                     "team_names": {}, "playoff": {}, "round_names": {}, "shotmap_rows": 0,
                     "cards_values": Counter(), "referee_names": {}}
    for row in rows:
        path = WORLD_ROOT / row["path"]
        data = json.loads(path.read_text())
        content, header = data.get("content", {}), data.get("header", {})
        teams = header.get("teams") or []
        if len(teams) != 2:
            raise AssertionError(f"team header malformed: {path}")
        h, a = score(row, header)
        st = stats(content)
        ev = events(content)
        ref = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
        get = lambda key, side: st.get(("All", key), (None, None))[side]
        rec = {"match_id": row["match_id"], "season": row["season"], "date": row["date"],
               "home_id": teams[0].get("id"), "away_id": teams[1].get("id"),
               "home_team": teams[0].get("name", row["home"]), "away_team": teams[1].get("name", row["away"]),
               "home_goals": h, "away_goals": a,
               "sot_h": get("ShotsOnTarget", 0), "sot_a": get("ShotsOnTarget", 1),
               "corners_h": get("corners", 0), "corners_a": get("corners", 1),
               "total_shots_h": get("total_shots", 0), "total_shots_a": get("total_shots", 1),
               "possession_h": get("BallPossesion", 0), "possession_a": get("BallPossesion", 1),
               "big_chances_h": get("big_chance", 0), "big_chances_a": get("big_chance", 1),
               "box_touches_h": get("touches_opp_box", 0), "box_touches_a": get("touches_opp_box", 1),
               "fouls_h": get("fouls", 0), "fouls_a": get("fouls", 1),
               "stats_yellow_h": get("yellow_cards", 0), "stats_yellow_a": get("yellow_cards", 1),
               "stats_red_h": get("red_cards", 0), "stats_red_a": get("red_cards", 1),
               "event_yellow_h": event_count(ev, "yellow", True), "event_yellow_a": event_count(ev, "yellow", False),
               "event_red_h": event_count(ev, "red", True), "event_red_a": event_count(ev, "red", False),
               "referee": ref, "goals_1h_h": first_half(ev, "Goal", True), "goals_1h_a": first_half(ev, "Goal", False),
               "cards_1h_h": first_half([e for e in ev if e.get("card") in {"Yellow", "YellowRed"}], "Card", True),
               "cards_1h_a": first_half([e for e in ev if e.get("card") in {"Yellow", "YellowRed"}], "Card", False),
               "has_stats": int(bool(st))}
        out.append(rec)
        season = row["season"]
        ss = audit["seasons"].setdefault(season, {"matches": 0, "teams": set(), "stats": 0, "events": 0, "referee": 0,
                                                   "period_splits": set(), "shotmap": 0, "has_playoff": Counter(), "round_names": Counter(),
                                                   "key_counts": Counter(), "sections": Counter(), "stats_conflicts": 0})
        ss["matches"] += 1; ss["teams"].update([teams[0].get("id"), teams[1].get("id")]); ss["stats"] += bool(st); ss["events"] += bool(ev); ss["referee"] += bool(ref)
        ss["period_splits"].update((content.get("stats") or {}).get("Periods", {}).keys()); ss["shotmap"] += bool((content.get("shotmap") or {}).get("shots"))
        ss["has_playoff"][str(content.get("hasPlayoff"))] += 1
        round_name = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Round") or {}).get("text", "")
        if round_name: ss["round_names"][round_name] += 1
        for (period, key), value in st.items(): ss["key_counts"][key] += 1; audit["stat_keys"].setdefault(season, Counter())[key] += 1
        for g in (((content.get("stats") or {}).get("Periods") or {}).get("All", {}).get("stats", []) or []): ss["sections"][g.get("key")] += 1
        audit["team_names"].setdefault(str(teams[0].get("id")), set()).add(teams[0].get("name")); audit["team_names"].setdefault(str(teams[1].get("id")), set()).add(teams[1].get("name"))
        for e in ev:
            if e.get("type") == "Card": audit["cards_values"][e.get("card")] += 1
        if ref: audit["referee_names"].setdefault(season, Counter())[ref] += 1
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(out)
    def clean(x):
        if isinstance(x, (set, Counter)): return sorted(x) if isinstance(x, set) else dict(x)
        if isinstance(x, dict): return {str(k): clean(v) for k, v in x.items()}
        return x
    AUDIT.write_text(json.dumps(clean(audit), indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    assert len(out) == len(rows), (len(out), len(rows))
    assert len(out) >= 1067, len(out)
    print(f"wrote {OUT} ({len(out)} rows)")
    for s in SEASONS:
        a = audit["seasons"][s]; print(s, a["matches"], len(a["teams"]), a["stats"], a["events"], a["referee"])


if __name__ == "__main__": main()
