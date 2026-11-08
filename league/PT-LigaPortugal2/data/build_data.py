#!/usr/bin/env python3
"""Build the flat, content-measured Liga Portugal 2 match table.

This is a data/EDA builder only. It does not fit or import any model code.
The index is read from this checkout; the JSON warehouse is resolved with the
same fallback convention as league/PT-LigaPortugal/data/build_data.py.
"""
import csv
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from league.jleague_lib import events_of, flat_stats, ht_from_events, shots_of  # noqa: E402

LEAGUE_ID = "185"
OUT = Path(__file__).resolve().parent


def warehouse_root():
    explicit = os.environ.get("FOOTMOB_WORLD_ROOT")
    if explicit:
        return Path(explicit)
    local = REPO / "data_enrichment"
    if (local / "fotmob_world").exists():
        return local
    return Path("/home/hatch/workspace/footballprediction/data_enrichment")


def load_index():
    with open(REPO / "data_enrichment/fotmob_world_index.csv", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]


def value(x):
    return "" if x is None else x


def event_yellows(events):
    out = [0, 0]
    for e in events:
        if e.get("type") == "Card" and str(e.get("card", "")).lower() == "yellow":
            out[0 if e.get("isHome") else 1] += 1
    return out


def stat_pair(stats, key):
    h, a = stats.get(("All", key), (None, None))
    return value(h), value(a)


def main():
    index = load_index()
    assert len(index) == 1619, len(index)
    root = warehouse_root()
    rows = []
    for ix in index:
        with open(root.parent / ix["path"]) as fh:
            payload = json.load(fh)
        header = payload.get("header") or {}
        status = header.get("status") or {}
        if not status.get("finished"):
            continue
        teams = header.get("teams") or [{}, {}]
        home, away = teams[0], teams[1]
        content = payload.get("content") or {}
        stats = flat_stats(content)
        events = events_of(content)
        eh, ea = event_yellows(events)
        ht = ht_from_events(content)
        if ht is None:
            ht = (None, None)
        info = (content.get("matchFacts") or {}).get("infoBox") or {}
        referee = ((info.get("Referee") or {}).get("text") or "").strip()
        periods = ((content.get("stats") or {}).get("Periods") or {})
        shot_count = len(shots_of(content))
        row = {
            "match_id": ix["match_id"], "season": ix["season"], "date": ix["date"],
            "home_team": home.get("name", ""), "away_team": away.get("name", ""),
            "home_id": home.get("id", ""), "away_id": away.get("id", ""),
            "home_goals": value(home.get("score")), "away_goals": value(away.get("score")),
            "ht_home": value(ht[0]), "ht_away": value(ht[1]), "referee": referee,
            "has_stats": int(bool((content.get("stats") or {}).get("Periods"))),
            "has_shotmap": int(shot_count > 0), "shot_count": shot_count,
            "has_period_splits": int("FirstHalf" in periods or "SecondHalf" in periods),
            "expected_goals_present": int(any(k[1] == "expected_goals" for k in stats)),
            "lineup_present": int(bool(content.get("lineup"))),
            "has_card_event": int(any(e.get("type") == "Card" for e in events)),
            "event_yellows_home": eh, "event_yellows_away": ea,
            # Kept separate from events. This source currently has no such key.
            "stats_yellows_home": "", "stats_yellows_away": "",
        }
        for name, key in (("sot", "ShotsOnTarget"), ("corners", "corners"),
                          ("total_shots", "total_shots"), ("stats_yellows", "yellow_cards"),
                          ("xg", "expected_goals"), ("touches", "touches_opp_box")):
            h, a = stat_pair(stats, key)
            row[f"{name}_home"], row[f"{name}_away"] = h, a
            if name == "stats_yellows":
                row["stats_yellows_home"], row["stats_yellows_away"] = h, a
        rows.append(row)

    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    assert len(rows) == 1619, len(rows)
    fields = list(rows[0])
    out = OUT / "pt2_matches.csv"
    OUT.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}: {len(rows)} rows")
    for season in sorted({r["season"] for r in rows}):
        print(season, sum(r["season"] == season for r in rows))


if __name__ == "__main__":
    main()
