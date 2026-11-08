#!/usr/bin/env python3
"""Build the content-measured Portugal Liga 3 match table (Phase A only)."""
import csv
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from league.jleague_lib import events_of, ht_from_events, shots_of  # noqa: E402

LEAGUE_ID = "9112"
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
    for path in (REPO / "data_enrichment/fotmob_world_index.csv",
                 Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")):
        if path.exists():
            with open(path, newline="") as fh:
                return [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    raise FileNotFoundError("fotmob_world_index.csv not found")


def event_counts(events):
    yellows = [0, 0]
    cards = 0
    for event in events:
        if event.get("type") != "Card":
            continue
        cards += 1
        if str(event.get("card", "")).lower() == "yellow":
            yellows[0 if event.get("isHome") else 1] += 1
    return yellows, cards


def main():
    index = load_index()
    assert len(index) == 1652, len(index)
    root = warehouse_root()
    rows = []
    for ix in index:
        with open(root.parent / ix["path"]) as fh:
            payload = json.load(fh)
        header = payload.get("header") or {}
        if not (header.get("status") or {}).get("finished"):
            continue
        teams = header.get("teams") or [{}, {}]
        home, away = teams[0], teams[1]
        content = payload.get("content") or {}
        events = events_of(content)
        shots = shots_of(content)
        ht = ht_from_events(content) or (None, None)
        yellows, cards = event_counts(events)
        info = (content.get("matchFacts") or {}).get("infoBox") or {}
        tournament = info.get("Tournament") or {}
        referee = str((info.get("Referee") or {}).get("text") or "").strip()
        stats = content.get("stats")
        periods = (stats or {}).get("Periods") or {}
        stats_yellows = ""
        for block in periods.values():
            for group in (block or {}).get("stats", []) or []:
                for stat in group.get("stats", []) or []:
                    if stat.get("key") == "yellow_cards":
                        stats_yellows = stat.get("stats") or ""
        rows.append({
            "match_id": ix["match_id"], "season": ix["season"], "date": ix["date"],
            "home_id": home.get("id", ""), "home": home.get("name", ""),
            "away_id": away.get("id", ""), "away": away.get("name", ""),
            "home_goals": "" if home.get("score") is None else home.get("score"),
            "away_goals": "" if away.get("score") is None else away.get("score"),
            "ht_home": "" if ht[0] is None else ht[0], "ht_away": "" if ht[1] is None else ht[1],
            "phase": tournament.get("leagueName", ""),
            "round": tournament.get("roundName", tournament.get("round", "")),
            "has_stats": int(bool(stats)), "has_shotmap": int(bool(shots)),
            "has_period_splits": int("FirstHalf" in periods or "SecondHalf" in periods),
            "shot_count": len(shots), "xg_present": int(any("expectedGoals" in s for s in shots)),
            "referee_text": referee, "referee_named": int(bool(referee)),
            "event_yellows_home": yellows[0], "event_yellows_away": yellows[1],
            "event_cards_total": cards, "has_card_event": int(cards > 0),
            "lineup_present": int(bool(content.get("lineup"))),
            "stats_yellows_home": stats_yellows[0] if isinstance(stats_yellows, list) and len(stats_yellows) > 0 else "",
            "stats_yellows_away": stats_yellows[1] if isinstance(stats_yellows, list) and len(stats_yellows) > 1 else "",
            "stats_yellow_key_present": int(bool(stats_yellows)),
        })
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    # Five index rows have a 0-0 index score but header.status.finished=False
    # (unplayed/postponed shells), so the payload-truth finished table is 1,647.
    assert len(rows) == 1647, len(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "pt3_matches.csv"
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}: {len(rows)} rows")
    for season in sorted({r["season"] for r in rows}):
        print(season, sum(r["season"] == season for r in rows))


if __name__ == "__main__":
    main()
