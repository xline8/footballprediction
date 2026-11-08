"""Build the Indonesia Super League Phase A analysis tables.

The warehouse is the shared FotMob world index in the main checkout.  This
script deliberately measures JSON content, rather than trusting index
flags (the index `has_stats` flag is a key-presence test and lies for this
league in both directions). It writes one row per finished match and a
two-row-per-match team table. No fitting or engine code belongs here.

League-specific facts measured from the payloads (see DATA_UNDERSTANDING):
- The stats feed, when present at all, carries only BallPossesion,
  total_shots, ShotsOnTarget and corners under Periods.All. There are no
  period splits, no expected_goals, no fouls and no stats-feed cards
  anywhere, and the shotmap is empty in every payload.
- Stats coverage is an era, not a constant: 2021/2022 from 2022-01-13
  (140/306), 2022/2023 complete (306/306), 2023/2024 only until
  2023-10-30 (153/314), 2024/2025 only 8 scattered matches, 2025/2026
  and 2026/2027 zero.
- Cards therefore come from the event feed by construction (the stats
  feed has no cards key at all). Event yellows are unified as direct
  Yellow + YellowRed (RU-1Division precedent). The event feed itself is
  truncated for part of the corpus (in 2023/2024 many matches carry
  goals/half markers only), so card targets are only scored on matches
  flagged events_complete (feed contains Substitution and Half events;
  substitutions occur in effectively every real match, so their absence
  marks a truncated feed, not a cardless match).
- Phases: the 8 matches with content.hasPlayoff == True in 2023/2024
  are the championship series (knockout) and are flagged
  championship_playoff; the 2 rows the index labels season "2021/2023"
  (Bali United vs PSM Makassar, June 2023) are a two-legged AFC playoff
  between champions of two different seasons, flagged stray_playoff.
  Everything else is regular. Engines use regular rows only.
- Half-time splits for goals and cards come from event order relative
  to the half-time Half marker (stoppage-time safe), not from the
  minute field.
- Teams are keyed on FotMob team ids: names change under a stable id
  (e.g. id 185749 Bhayangkara rebrands; id 1665351 Malut United is
  listed as "Java United F.C." in 2026/2027).
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
INDEX = WAREHOUSE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "8983"

STAT_KEYS = ["BallPossesion", "total_shots", "ShotsOnTarget", "corners"]


def number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    """Return (period, key) -> (home, away), preserving last duplicate key."""
    result = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    if not isinstance(periods, dict):
        return result
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                values = stat.get("stats") or [None, None]
                result[(period, stat.get("key"))] = (
                    number(values[0] if len(values) > 0 else None),
                    number(values[1] if len(values) > 1 else None),
                )
    return result


def pair(stats, period, key):
    return stats.get((period, key), (None, None))


def event_rows(content):
    facts = (content or {}).get("matchFacts") or {}
    events = (facts.get("events") or {}).get("events") or []
    return events


def split_at_ht(events):
    """Split events into (first_half, second_half) by list order vs the HT marker."""
    first, second = [], []
    seen_ht = False
    for event in events:
        if (event.get("type") == "Half"
                and (event.get("halfStrKey") == "halftime_short"
                     or event.get("halfStrShort") == "HT")):
            seen_ht = True
            continue
        (second if seen_ht else first).append(event)
    if not seen_ht:  # fall back to the minute field
        first = [e for e in events if (number(e.get("time")) or 0) <= 45]
        second = [e for e in events if (number(e.get("time")) or 0) > 45]
    return first, second


def count(events, event_type, is_home=None, card=None):
    total = 0
    for event in events:
        if event.get("type") != event_type:
            continue
        if is_home is not None and bool(event.get("isHome")) != is_home:
            continue
        if card is not None and event.get("card") != card:
            continue
        total += 1
    return total


def phase_for(row, content):
    if row["season"] == "2021/2023":
        return "stray_playoff"
    if (content or {}).get("hasPlayoff") is True:
        return "championship_playoff"
    return "regular"


def build_match(row):
    # Payload root derived from INDEX at call time: the daily runner
    # overrides INDEX to its own repo root (rebuild_csv_world), while
    # standalone runs use the WAREHOUSE-based default above.
    path = Path(INDEX).parents[1] / row["path"]
    payload = json.load(path.open())
    general = payload.get("general") or {}
    header = payload.get("header") or {}
    status = header.get("status") or {}
    if not status.get("finished") or status.get("cancelled"):
        return None
    content = payload.get("content") or {}
    stats = flat_stats(content)
    home = general.get("homeTeam") or {}
    away = general.get("awayTeam") or {}
    if home.get("id") is None or away.get("id") is None:
        raise ValueError(f"missing team id in {row['match_id']}")
    score = str(status.get("scoreStr") or "").split("-")
    if len(score) != 2:
        raise ValueError(f"bad score in {row['match_id']}: {status.get('scoreStr')}")
    events = event_rows(content)
    tournament = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Tournament") or {}
    referee = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
    types = {e.get("type") for e in events}
    events_complete = int("Substitution" in types and "Half" in types)
    first, second = split_at_ht(events) if events else ([], [])
    rec = {
        "match_id": row["match_id"], "date": row["date"],
        "season": row["season"] if row["season"] != "2021/2023" else "2022/2023",
        "season_label_raw": row["season"],
        "round": str(general.get("matchRound") or tournament.get("roundName") or ""),
        "phase": phase_for(row, content),
        "tournament_id": tournament.get("id"),
        "tournament_name": tournament.get("leagueName"),
        "home_team_id": home["id"], "home_team": home.get("name"),
        "away_team_id": away["id"], "away_team": away.get("name"),
        "home_goals": int(float(score[0].strip())), "away_goals": int(float(score[1].strip())),
        "referee": (referee.get("text") or None) if isinstance(referee, dict) else None,
        "has_events": int(bool(events)),
        "events_complete": events_complete,
    }
    goal_events = [e for e in events if e.get("type") == "Goal"
                   and not e.get("isPenaltyShootoutEvent")]
    rec["ev_goals_home"] = count(goal_events, "Goal", True)
    rec["ev_goals_away"] = count(goal_events, "Goal", False)
    rec["goals_events_match_score"] = int(
        rec["ev_goals_home"] == rec["home_goals"] and rec["ev_goals_away"] == rec["away_goals"])
    for side, is_home in (("home", True), ("away", False)):
        rec[f"ht_{side}_goals"] = count(first, "Goal", is_home) if events else None
        rec[f"ev_yellow_{side}"] = (count(events, "Card", is_home, "Yellow")
                                    + count(events, "Card", is_home, "YellowRed"))
        rec[f"ev_yellow_direct_{side}"] = count(events, "Card", is_home, "Yellow")
        rec[f"ev_yellowred_{side}"] = count(events, "Card", is_home, "YellowRed")
        rec[f"ev_red_{side}"] = count(events, "Card", is_home, "Red")
        rec[f"ev_cards_{side}"] = (rec[f"ev_yellow_direct_{side}"]
                                   + rec[f"ev_yellowred_{side}"]
                                   + rec[f"ev_red_{side}"])
        rec[f"ev_yellow_1h_{side}"] = (count(first, "Card", is_home, "Yellow")
                                       + count(first, "Card", is_home, "YellowRed"))
    rec["ht_source"] = "events" if events else "none"
    for key in STAT_KEYS:
        h, a = pair(stats, "All", key)
        rec[f"{key}_home"], rec[f"{key}_away"] = h, a
        for period, prefix in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
            h, a = pair(stats, period, key)
            rec[f"{prefix}_{key}_home"], rec[f"{prefix}_{key}_away"] = h, a
    # Frozen cards target: event-unified yellows, scored only where the
    # event feed is complete. The stats feed has no cards key at all.
    for side in ("home", "away"):
        rec[f"yellow_{side}"] = float(rec[f"ev_yellow_{side}"]) if events_complete else None
        rec[f"red_{side}"] = float(rec[f"ev_red_{side}"]) if events_complete else None
    rec["cards_source"] = "events" if events_complete else "none"
    rec["has_stats"] = int(all(
        pair(stats, "All", key)[0] is not None and pair(stats, "All", key)[1] is not None
        for key in ("total_shots", "ShotsOnTarget", "corners")))
    rec["has_splits"] = 0  # no Periods.FirstHalf/SecondHalf anywhere in this league
    shotmap = content.get("shotmap") or {}
    shots = shotmap.get("shots") or [] if isinstance(shotmap, dict) else []
    rec["has_shotmap"] = int(bool(shots))
    return rec


def write_csv(path, rows):
    fields = list(rows[0].keys())
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    with INDEX.open() as fh:
        index_rows = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = [built for r in index_rows if (built := build_match(r)) is not None]
    if len(rows) != len(index_rows):
        raise AssertionError(f"finished rows {len(rows)} != index rows {len(index_rows)}")
    if len({r["match_id"] for r in rows}) != len(rows):
        raise AssertionError("duplicate match ids")
    write_csv(OUT / "id_matches.csv", rows)
    team_rows = []
    for row in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": row["match_id"], "date": row["date"], "season": row["season"],
                 "round": row["round"], "phase": row["phase"],
                 "team_id": row[f"{side}_team_id"], "team": row[f"{side}_team"],
                 "venue": side}
            t.update({"goals_for": row[f"{side}_goals"], "goals_against": row[f"{opp}_goals"]})
            for key in STAT_KEYS:
                t[f"{key}_for"], t[f"{key}_against"] = row[f"{key}_{side}"], row[f"{key}_{opp}"]
            t["yellow_for"], t["yellow_against"] = row[f"yellow_{side}"], row[f"yellow_{opp}"]
            t["red_for"], t["red_against"] = row[f"red_{side}"], row[f"red_{opp}"]
            t["ev_cards_for"], t["ev_cards_against"] = row[f"ev_cards_{side}"], row[f"ev_cards_{opp}"]
            team_rows.append(t)
    write_csv(OUT / "id_team_matches.csv", team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
