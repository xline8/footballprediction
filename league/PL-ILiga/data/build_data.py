"""Build the PL-ILiga Stage 1 tables from the FotMob world warehouse.

I Liga has score-only payloads: stats, shotmaps, and referee text are absent.
Cards are therefore deliberately *not* fabricated: ``yellow_*`` and
``red_*`` are always null and ``cards_source`` is ``none``.  Event diagnostics
retain Red and YellowRed counts; ``ev_yellow_*`` is always zero with this
provenance because the feed contains no plain Yellow events anywhere in this
league.  Half-time goals are event-derived only when an events block exists.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
SHARED_ROOT = Path("/home/hatch/workspace/footballprediction")
OUT = Path(__file__).resolve().parent
STAT_KEYS = [
    "BallPossesion", "expected_goals", "expected_goals_open_play",
    "expected_goals_set_play", "expected_goals_non_penalty", "total_shots",
    "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box",
    "shots_outside_box", "big_chance", "touches_opp_box", "corners",
    "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
]


def number(value):
    if value is None or value == "": return None
    if isinstance(value, (int, float)): return float(value)
    try: return float(str(value).split(" ")[0].replace("%", ""))
    except (TypeError, ValueError): return None


def flat_stats(content):
    result = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                values = stat.get("stats") or []
                home = number(values[0]) if values else None
                away = number(values[1]) if len(values) > 1 else None
                if home is not None or away is not None: result[(period, stat.get("key"))] = (home, away)
    return result


def events_block(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def event_count(events, card, home):
    return sum(1 for e in events if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == home)


def parse_score(score):
    parts = (score or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def payload_path(index_row):
    local = ROOT / index_row["path"]
    return local if local.exists() else SHARED_ROOT / index_row["path"]


def build_match(index_row):
    payload = json.loads(payload_path(index_row).read_text())
    general, header = payload.get("general") or {}, payload.get("header") or {}
    status, content = header.get("status") or {}, payload.get("content") or {}
    stats, events = flat_stats(content), events_block(content)
    home_goals, away_goals = parse_score(status.get("scoreStr") or index_row.get("score"))
    home_team, away_team = general.get("homeTeam") or {}, general.get("awayTeam") or {}
    rnd = str(general.get("matchRound") or "")
    row = {
        "match_id": index_row["match_id"], "league": "PL-ILiga", "season": index_row["season"],
        "date": index_row["date"], "round": rnd, "phase": "playoff" if rnd in ("1/2", "final") else "regular",
        "league_name_raw": general.get("leagueName"), "parent_league_id": general.get("parentLeagueId"),
        "home_team_id": home_team.get("id"), "home_team": home_team.get("name"),
        "away_team_id": away_team.get("id"), "away_team": away_team.get("name"),
        "coverage_level": general.get("coverageLevel"), "home_goals": home_goals, "away_goals": away_goals,
    }
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    if events:
        row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        row["ht_source"] = "events"
    else:
        row["ht_home_goals"] = row["ht_away_goals"] = None; row["ht_source"] = "none"
    for side in (True, False):
        prefix = "home" if side else "away"
        row[f"ev_yellow_{prefix}"] = 0
        row[f"ev_yellowred_{prefix}"] = event_count(events, "YellowRed", side)
        row[f"ev_red_{prefix}"] = event_count(events, "Red", side) + row[f"ev_yellowred_{prefix}"]
    for key in STAT_KEYS:
        for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
            home, away = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = home, away
    row.update({"yellow_home": None, "yellow_away": None, "red_home": None, "red_away": None, "cards_source": "none"})
    row["referee"] = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    row["has_stats_all"] = int(("All", "corners") in stats); row["has_stats_half"] = int(("FirstHalf", "corners") in stats)
    row["has_events"] = int(bool(events)); row["has_period_splits_content"] = int(any(p in ((content.get("stats") or {}).get("Periods") or {}) for p in ("FirstHalf", "SecondHalf")))
    shots = ((content.get("shotmap") or {}).get("shots") or []); regular_shots = [s for s in shots if s.get("period") != "PenaltyShootout"]
    row["has_shotmap"] = int(bool(regular_shots)); row["n_shootout_shots"] = len(shots) - len(regular_shots)
    for side, team_id in (("home", home_team.get("id")), ("away", away_team.get("id"))):
        ss = [s for s in regular_shots if s.get("teamId") == team_id]
        row[f"sm_shots_{side}"] = len(ss); row[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked"))
        row[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4); xgot = [s.get("expectedGoalsOnTarget") for s in ss if s.get("expectedGoalsOnTarget") is not None]
        row[f"sm_xgot_{side}"] = round(sum(xgot), 4); row[f"sm_xgot_n_{side}"] = len(xgot); row[f"sm_shots_fh_{side}"] = sum(1 for s in ss if s.get("period") == "FirstHalf")
    if not row["has_events"] and not row["has_shotmap"]:
        for key in STAT_KEYS:
            for prefix in ("", "fh_", "sh_"): row[f"{prefix}{key}_home"] = row[f"{prefix}{key}_away"] = None
        for side in ("home", "away"):
            for key in ("sm_shots", "sm_sot", "sm_xg", "sm_xgot", "sm_xgot_n", "sm_shots_fh"): row[f"{key}_{side}"] = None
    return row


def main():
    index_rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "197"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = [build_match(r) for r in index_rows]
    assert len(rows) == 1671, len(rows); assert len({r["match_id"] for r in rows}) == 1671
    by_season = {}
    for season in sorted({r["season"] for r in rows}):
        rs = [r for r in rows if r["season"] == season]
        by_season[season] = (sum(r["phase"] == "regular" for r in rs), sum(r["phase"] == "playoff" for r in rs))
    for season in sorted(by_season)[:-1]: assert by_season[season] == (306, 3), (season, by_season[season])
    assert by_season["2026/2027"] == (126, 0), by_season["2026/2027"]
    with (OUT / "iliga_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    team_rows = []
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            item = {"match_id": row["match_id"], "season": row["season"], "date": row["date"], "phase": row["phase"], "team_id": row[f"{side}_team_id"], "team": row[f"{side}_team"], "venue": side, "goals_for": row[f"{side}_goals"], "goals_against": row[f"{other}_goals"]}
            for key in ("expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"):
                item[f"{key}_for"] = item[f"{key}_against"] = None
            item.update({"sm_xg_for": None, "sm_shots_for": None, "sm_xgot_for": None, "sm_xgot_n_for": None})
            team_rows.append(item)
    with (OUT / "iliga_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0])); writer.writeheader(); writer.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)}"); print("season_counts=" + repr(by_season))


if __name__ == "__main__": main()
