"""Build Venezuela Primera División analysis CSVs from the FotMob warehouse."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "339"
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]
STAT_KEYS = [
    "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
    "big_chance", "BallPossesion", "accurate_passes", "yellow_cards",
    "red_cards", "fouls", "corners", "passes", "keeper_saves",
    "shots_inside_box", "shots_outside_box",
]
EXPECTED_PHASE = {
    "2021": (252, 51), "2022": (240, 37), "2023": (210, 13),
    "2024": (182, 52), "2025": (182, 51), "2026": (182, 45),
}
EXPECTED_STATS = {"2021": 0, "2022": 0, "2023": 0, "2024": 0, "2025": 117, "2026": 226}
EXPECTED_SPLITS = {"2021": 0, "2022": 0, "2023": 0, "2024": 0, "2025": 62, "2026": 226}
AWARDED = {"3575291", "1000018666"}


def number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.split()[0].replace("%", ""))
        except (ValueError, IndexError):
            return None
    return None


def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or [None, None]
                out[(period, stat.get("key"))] = (
                    number(vals[0]), number(vals[1]) if len(vals) > 1 else None
                )
    return out


def events_list(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def event_count(events, cards, home=None, period=None):
    total = 0
    for event in events:
        if event.get("type") != "Card" or event.get("card") not in cards:
            continue
        if home is not None and bool(event.get("isHome")) != home:
            continue
        t = event.get("time")
        if period == "1h" and not isinstance(t, (int, float)) or period == "1h" and t > 45:
            continue
        if period == "2h" and (not isinstance(t, (int, float)) or t <= 45):
            continue
        total += 1
    return total


def payload_path(index_path):
    direct = ROOT / index_path
    if direct.exists():
        return direct
    sibling = ROOT.parent / "footballprediction" / index_path
    if sibling.exists():
        return sibling
    raise FileNotFoundError(index_path)


def phase_for(general):
    round_text = str(general.get("matchRound") or "")
    league = str(general.get("leagueName") or "")
    text = f"{round_text} {league}".lower()
    return "playoff" if ("quadrangular" in text or "final" in text or any(
        marker.lower() in league.lower()
        for marker in ("Second stage", "Super Final", "Final Stage", "Fase Final")
    )) else "regular"


def main():
    with INDEX.open() as fh:
        index = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index.sort(key=lambda r: (r["date"], r["match_id"]))
    rows, variants = [], defaultdict(Counter)
    goal_events_total = score_goals_total = 0
    key_seen = set()
    for idx in index:
        path = payload_path(idx["path"])
        data = json.loads(path.read_text())
        general = data.get("general") or {}
        status = (data.get("header") or {}).get("status") or {}
        if status.get("finished") is not True:
            continue
        content = data.get("content") or {}
        facts = content.get("matchFacts") or {}
        info = facts.get("infoBox") or {}
        events = events_list(content)
        round_name = str(general.get("matchRound") or "")
        tournament = str(general.get("leagueName") or "")
        phase = phase_for(general)
        lower = f"{round_name} {tournament}".lower()
        if "apertura" in lower:
            stage = "Apertura"
        elif "clausura" in lower:
            stage = "Clausura"
        elif "super final" in lower or (idx["season"] == "2025" and idx["date"] >= "2025-07-01"):
            stage = "Clausura"
        elif idx["season"] == "2026" and idx["date"] < "2026-07-01":
            # 2026 Apertura regular rounds are bare 1..13 in both league-name variants.
            stage = "Apertura"
        else:
            stage = "single"
        score = (status.get("scoreStr") or "0 - 0").split("-")
        hgoals, agoals = int(score[0].strip()), int(score[1].strip())
        score_goals_total += hgoals + agoals
        awarded = idx["match_id"] in AWARDED
        goals = [] if awarded else [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
        goal_events_total += len(goals)
        flat = flat_stats(content)
        for (period, key) in flat:
            key_seen.add(key)

        def stat(period, key, side):
            pair = flat.get((period, key), (None, None))
            return pair[0 if side == "home" else 1]

        rec = {
            "match_id": idx["match_id"], "season": idx["season"], "date": idx["date"],
            "round": round_name, "round_name": round_name, "tournament": tournament,
            "stage": stage, "phase": phase,
            "home_team_id": general["homeTeam"]["id"], "home_team": general["homeTeam"]["name"],
            "away_team_id": general["awayTeam"]["id"], "away_team": general["awayTeam"]["name"],
            "home_goals": hgoals, "away_goals": agoals, "awarded": int(awarded),
            "ht_home_goals": None if awarded else sum(1 for e in goals if e.get("isHome") is True and isinstance(e.get("time"), (int, float)) and e["time"] <= 45),
            "ht_away_goals": None if awarded else sum(1 for e in goals if e.get("isHome") is False and isinstance(e.get("time"), (int, float)) and e["time"] <= 45),
            "ht_source": "none" if awarded else "events",
            "events_complete": int(any(e.get("type") == "Half" for e in events) and any(e.get("type") == "Substitution" for e in events)),
            "events_incomplete": int(not (any(e.get("type") == "Half" for e in events) and any(e.get("type") == "Substitution" for e in events))),
            "stats_present": int(bool((content.get("stats") or {}).get("Periods"))),
            "period_splits_present": int(all(p in ((content.get("stats") or {}).get("Periods") or {}) for p in ("FirstHalf", "SecondHalf"))),
            "referee": (info.get("Referee") or {}).get("text") or "",
            "shotmap_n": len((content.get("shotmap") or {}).get("shots") or []),
        }
        for key in STAT_KEYS:
            for period, suffix in (("All", ""), ("FirstHalf", "_1h"), ("SecondHalf", "_2h")):
                for side in ("home", "away"):
                    rec[f"{key}_{side}{suffix}"] = stat(period, key, side)
        for prefix, cards in (("event_yellow", ("Yellow",)), ("event_yellow_unified", ("Yellow", "YellowRed")), ("event_red", ("Red", "YellowRed"))):
            for side_bool, side in ((True, "home"), (False, "away")):
                rec[f"{prefix}_{side}"] = event_count(events, cards, side_bool)
                if prefix == "event_yellow_unified":
                    rec[f"{prefix}_{side}_1h"] = event_count(events, cards, side_bool, "1h")
                    rec[f"{prefix}_{side}_2h"] = event_count(events, cards, side_bool, "2h")
        rec["stats_yellow_home"] = rec["yellow_cards_home"]
        rec["stats_yellow_away"] = rec["yellow_cards_away"]
        rows.append(rec)
        for side in ("home", "away"):
            variants[general[f"{side}Team"]["id"]][general[f"{side}Team"]["name"]] += 1

    assert len(rows) == 1497, len(rows)
    by_season = defaultdict(list)
    for row in rows:
        by_season[row["season"]].append(row)
    for season, expected in EXPECTED_PHASE.items():
        got = (sum(r["phase"] == "regular" for r in by_season[season]), sum(r["phase"] == "playoff" for r in by_season[season]))
        assert got == expected, (season, got, expected)
        assert sum(r["stats_present"] for r in by_season[season]) == EXPECTED_STATS[season]
        assert sum(r["period_splits_present"] for r in by_season[season]) == EXPECTED_SPLITS[season]
    assert goal_events_total == score_goals_total - 6, (goal_events_total, score_goals_total)
    assert sum(r["shotmap_n"] for r in rows) == 0
    canon = {tid: names.most_common(1)[0][0] for tid, names in variants.items()}
    for row in rows:
        row["home_team"] = canon[row["home_team_id"]]
        row["away_team"] = canon[row["away_team_id"]]
    with (OUT / "ve_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    team_rows = []
    for row in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            x = {"match_id": row["match_id"], "season": row["season"], "date": row["date"], "round": row["round"], "round_name": row["round_name"], "stage": row["stage"], "phase": row["phase"], "team_id": row[f"{side}_team_id"], "team": row[f"{side}_team"], "venue": side}
            for name, key in (("goals", "goals"), ("sot", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots"), ("possession", "BallPossesion"), ("big_chances", "big_chance"), ("yellow", "stats_yellow")):
                x[f"{name}_for"] = row[f"{side}_goals"] if key == "goals" else row[f"{key}_{side}"]
                x[f"{name}_against"] = row[f"{opp}_goals"] if key == "goals" else row[f"{key}_{opp}"]
            team_rows.append(x)
    with (OUT / "ve_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0])); writer.writeheader(); writer.writerows(team_rows)
    print(json.dumps({"matches": len(rows), "team_rows": len(team_rows), "regular": sum(r["phase"] == "regular" for r in rows), "playoff": sum(r["phase"] == "playoff" for r in rows), "goal_events": goal_events_total, "score_goals": score_goals_total, "goal_gap_awarded": score_goals_total - goal_events_total, "shotmap_n": sum(r["shotmap_n"] for r in rows), "stats_present": {s: sum(r["stats_present"] for r in by_season[s]) for s in SEASONS}, "period_splits_present": {s: sum(r["period_splits_present"] for r in by_season[s]) for s in SEASONS}, "stat_keys_seen": sorted(key_seen)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
