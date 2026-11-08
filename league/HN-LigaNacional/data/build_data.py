#!/usr/bin/env python3
"""Build the payload-measured Honduras Liga Nacional match table."""
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from league.jleague_lib import events_of, ht_from_events, shots_of  # noqa: E402

LEAGUE_ID = "337"
INDEX_COUNT = 1132
OUT = Path(__file__).resolve().parent

def warehouse_root():
    explicit = os.environ.get("FOOTMOB_WORLD_ROOT")
    if explicit: return Path(explicit)
    local = REPO / "data_enrichment"
    if (local / "fotmob_world").exists(): return local
    return Path("/home/hatch/workspace/footballprediction/data_enrichment")

def load_index():
    for path in (REPO / "data_enrichment/fotmob_world_index.csv", Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")):
        if path.exists():
            with open(path, newline="") as fh: return [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    raise FileNotFoundError("fotmob_world_index.csv not found")

def event_counts(events):
    yellows = [0, 0]; cards = Counter()
    for event in events:
        if event.get("type") != "Card": continue
        cards[str(event.get("card", ""))] += 1
        if str(event.get("card", "")).lower() == "yellow": yellows[0 if event.get("isHome") else 1] += 1
    return yellows, cards

def numeric_round(value): return bool(re.fullmatch(r"\d+", str(value).strip()))

def main():
    index = load_index(); assert len(index) == INDEX_COUNT, len(index)
    root = warehouse_root(); rows, card_types = [], Counter(); payload_files = 0
    for ix in index:
        path = root.parent / ix["path"]; assert path.exists(), path; payload_files += 1
        with open(path) as fh: payload = json.load(fh)
        header = payload.get("header") or {}; assert (header.get("status") or {}).get("finished") is True
        teams = header.get("teams") or [{}, {}]; home, away = teams[0], teams[1]
        content = payload.get("content") or {}; events = events_of(content); shots = shots_of(content)
        awarded = int(bool((header.get("status") or {}).get("awarded")))
        ht = (None, None) if awarded else (ht_from_events(content) or (None, None))
        # Awarded fixtures keep the official FT score; event feeds can describe
        # an abandoned/administrative match and must not supply an HT score.
        yellows, cards = event_counts(events); card_types.update(cards)
        info = (content.get("matchFacts") or {}).get("infoBox") or {}; tournament = info.get("Tournament") or {}
        round_name = str(tournament.get("roundName", tournament.get("round", "")))
        referee = str((info.get("Referee") or {}).get("text") or "").strip(); stats = content.get("stats")
        periods = (stats or {}).get("Periods") or {}
        rows.append({
            "match_id": ix["match_id"], "season": ix["season"], "phase": "Apertura" if "Apertura" in ix["season"] else "Clausura", "date": ix["date"],
            "home_id": home.get("id", ""), "home": home.get("name", ""), "away_id": away.get("id", ""), "away": away.get("name", ""),
            "home_goals": home.get("score", ""), "away_goals": away.get("score", ""), "ht_home": "" if ht[0] is None else ht[0], "ht_away": "" if ht[1] is None else ht[1],
            "stage": "pending", "round": round_name, "awarded": awarded, "has_stats": int(bool(stats)),
            "has_shotmap": int(len(shots) > 0), "shot_count": len(shots), "has_period_splits": int("FirstHalf" in periods or "SecondHalf" in periods),
            "referee_named": int(bool(referee)), "event_yellows_home": yellows[0], "event_yellows_away": yellows[1], "event_cards_total": sum(cards.values()),
            "has_card_event": int(bool(cards)), "events_present": int(bool(events)), "lineup_present": int(bool(content.get("lineup"))),
        })
    assert payload_files == INDEX_COUNT
    for key in sorted({(r["season"], r["phase"]) for r in rows}):
        group = [r for r in rows if (r["season"], r["phase"]) == key]
        numeric = [r for r in group if numeric_round(r["round"])]
        max_round = max(int(r["round"]) for r in numeric); lastreg = max(r["date"] for r in numeric if int(r["round"]) == max_round)
        for r in group: r["stage"] = "regular" if numeric_round(r["round"]) and r["date"] <= lastreg else "playoff"
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    regular = Counter(r["season"] for r in rows if r["stage"] == "regular"); playoff = Counter(r["season"] for r in rows if r["stage"] == "playoff")
    expected = {s: (84 if s == "2026/2027 - Apertura" else 110 if s.startswith("2025/2026") else 90) for s in regular}
    assert dict(regular) == expected, regular; assert sum(regular.values()) == 1024 and sum(playoff.values()) == 108
    out = OUT / "hn_matches.csv"
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    inventory = {"index_rows": len(index), "payload_files": payload_files, "finished_rows": len(rows), "stats_none": sum(not r["has_stats"] for r in rows), "shotmap_zero": sum(not r["has_shotmap"] for r in rows), "lineup_absent": sum(not r["lineup_present"] for r in rows), "referee_empty": sum(not r["referee_named"] for r in rows), "events_present": sum(r["events_present"] for r in rows), "events_absent": sum(not r["events_present"] for r in rows), "event_card_types": dict(sorted(card_types.items())), "stage_counts": {"regular": sum(regular.values()), "playoff": sum(playoff.values())}, "regular_by_season": dict(sorted(regular.items())), "playoff_by_season": dict(sorted(playoff.items())), "awarded_match_ids": sorted(r["match_id"] for r in rows if r["awarded"]), "team_ids": sorted({str(r["home_id"]) for r in rows} | {str(r["away_id"]) for r in rows})}
    with open(OUT.parent / "analysis/inventory_summary.json", "w") as fh: json.dump(inventory, fh, indent=2, sort_keys=True)
    print(f"Wrote {out}: {len(rows)} rows"); print("regular", dict(sorted(regular.items()))); print("playoff", dict(sorted(playoff.items()))); print("inventory", json.dumps(inventory, sort_keys=True))

if __name__ == "__main__": main()
