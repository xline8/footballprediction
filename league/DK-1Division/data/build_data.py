"""Build the Denmark 1. Division Phase A analysis tables.

The warehouse is the shared FotMob world index in the main checkout.  This
script deliberately measures JSON content, rather than trusting index flags.
It writes one row per finished match and a two-row-per-match team table.
No fitting or engine code belongs here.
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WAREHOUSE = Path("/home/hatch/workspace/footballprediction")
INDEX = WAREHOUSE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "85"

STAT_KEYS = [
    "BallPossesion", "expected_goals", "expected_goals_open_play",
    "expected_goals_set_play", "total_shots", "ShotsOnTarget",
    "ShotsOffTarget", "corners", "yellow_cards", "red_cards", "fouls",
    "touches_opp_box", "big_chance",
]
HALF_KEYS = ["expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "total_shots", "ShotsOnTarget",
             "corners", "yellow_cards", "red_cards", "fouls",
             "touches_opp_box"]


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


def event_count(events, event_type, side=None, card=None, max_time=None):
    total = 0
    for event in events:
        if event.get("type") != event_type:
            continue
        if side is not None and bool(event.get("isHome")) != side:
            continue
        if card is not None and event.get("card") != card:
            continue
        if max_time is not None and number(event.get("time")) is not None and number(event.get("time")) > max_time:
            continue
        total += 1
    return total


def phase_for(round_value, tournament):
    text = " ".join(str(tournament.get(k) or "") for k in ("leagueName", "roundName", "link")).lower()
    try:
        rnd = int(str(round_value))
    except (TypeError, ValueError):
        rnd = None
    if rnd is not None and rnd <= 22:
        return "regular"
    if "promotion" in text or "championship" in text:
        return "championship"
    if "relegation" in text:
        return "relegation"
    if rnd is not None and 23 <= rnd <= 32:
        return "other"
    if "playoff" in text:
        return "playoff"
    return "other"


def build_match(row):
    path = WAREHOUSE / row["path"]
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
    rec = {
        "match_id": row["match_id"], "date": row["date"], "season": row["season"],
        "round": str(general.get("matchRound") or tournament.get("roundName") or ""),
        "phase": phase_for(general.get("matchRound"), tournament),
        "tournament_id": tournament.get("id"),
        "tournament_name": tournament.get("leagueName"),
        "home_team_id": home["id"], "home_team": home.get("name"),
        "away_team_id": away["id"], "away_team": away.get("name"),
        "home_goals": int(float(score[0].strip())), "away_goals": int(float(score[1].strip())),
        "referee": referee.get("text") or None,
        "has_events": int(bool(events)),
    }
    goals = [e for e in events if e.get("type") == "Goal"]
    for side, is_home in (("home", True), ("away", False)):
        rec[f"ht_{side}_goals"] = sum(
            1 for e in goals if bool(e.get("isHome")) == is_home and number(e.get("time")) is not None and number(e.get("time")) <= 45
        ) if events else None
        rec[f"ev_yellow_{side}"] = event_count(events, "Card", is_home, "Yellow")
        rec[f"ev_yellowred_{side}"] = event_count(events, "Card", is_home, "YellowRed")
        rec[f"ev_red_{side}"] = event_count(events, "Card", is_home, "Red")
        rec[f"ev_cards_{side}"] = sum(rec[f"ev_{kind}_{side}"] for kind in ("yellow", "yellowred", "red"))
    rec["ht_source"] = "events" if events else "none"
    for key in STAT_KEYS:
        h, a = pair(stats, "All", key)
        rec[f"{key}_home"], rec[f"{key}_away"] = h, a
        for period, prefix in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
            h, a = pair(stats, period, key)
            rec[f"{prefix}_{key}_home"], rec[f"{prefix}_{key}_away"] = h, a
    rec["yellow_home"], rec["yellow_away"] = rec["yellow_cards_home"], rec["yellow_cards_away"]
    rec["red_home"], rec["red_away"] = rec["red_cards_home"], rec["red_cards_away"]
    # The frozen cards target is the stats feed.  Early 2021/2022 rows retain
    # event counts for audit, but are intentionally not silently substituted.
    rec["cards_source"] = "stats" if all(rec[f"yellow_cards_{s}"] is not None and rec[f"red_cards_{s}"] is not None for s in ("home", "away")) else "none"
    rec["has_stats"] = int(all(pair(stats, "All", key)[0] is not None and pair(stats, "All", key)[1] is not None for key in ("total_shots", "ShotsOnTarget", "corners")))
    # Complete market splits: total shots, SOT, corners and cards.  xG and
    # box-touch splits are not required for the halves presentation and are
    # tracked by their own nullable columns.
    split_keys = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards", "red_cards"]
    rec["has_splits"] = int(all(pair(stats, p, key)[0] is not None and pair(stats, p, key)[1] is not None for p in ("FirstHalf", "SecondHalf") for key in split_keys))
    rec["has_stats_half"] = int(bool((content.get("stats") or {}).get("Periods", {}).get("FirstHalf")))
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
    write_csv(OUT / "dk1_matches.csv", rows)
    team_rows = []
    for row in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            t = {"match_id": row["match_id"], "date": row["date"], "season": row["season"], "round": row["round"], "phase": row["phase"], "team_id": row[f"{side}_team_id"], "team": row[f"{side}_team"], "venue": side}
            t.update({"goals_for": row[f"{side}_goals"], "goals_against": row[f"{opp}_goals"]})
            for key in STAT_KEYS:
                t[f"{key}_for"], t[f"{key}_against"] = row[f"{key}_{side}"], row[f"{key}_{opp}"]
            t["yellow_for"], t["yellow_against"] = row[f"yellow_{side}"], row[f"yellow_{opp}"]
            t["red_for"], t["red_against"] = row[f"red_{side}"], row[f"red_{opp}"]
            t["ev_cards_for"], t["ev_cards_against"] = row[f"ev_cards_{side}"], row[f"ev_cards_{opp}"]
            team_rows.append(t)
    write_csv(OUT / "dk1_team_matches.csv", team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
