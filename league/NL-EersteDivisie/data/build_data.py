"""Build the Netherlands Eerste Divisie regular-season analysis tables.

This is a Phase-1 data builder.  It deliberately keeps the common stats/xG/
shotmap columns used by the other league builders; absent xG and shotmap
observations are represented as NaN/zero rather than being dropped.
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "league"))
from jleague_lib import flat_stats, stats_conflicts, shots_of, events_of, ht_from_events  # noqa: E402

INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
# This fallback permits the requested build to run from the worktree while the
# coordinator has not yet provided the main-checkout warehouse symlink.
if not INDEX.exists():
    INDEX = Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
WAREHOUSE = INDEX.parent / "fotmob_world"
OUT = HERE.parent

BASE_KEYS = [
    "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
    "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box",
    "corners", "yellow_cards", "red_cards", "fouls", "Offsides",
    "keeper_saves", "BallPossesion",
]
XG_KEYS = ["expected_goals", "expected_goals_open_play", "expected_goals_set_play", "expected_goals_non_penalty"]
HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards", "red_cards", "fouls", "expected_goals"]


def nan():
    return float("nan")


def load(path):
    with open(path) as fh:
        return json.load(fh)


def score(payload):
    status = ((payload.get("header") or {}).get("status") or {})
    raw = status.get("scoreStr")
    if isinstance(raw, str):
        try:
            a, b = raw.replace("–", "-").split("-")[:2]
            return int(a.strip()), int(b.strip())
        except (ValueError, AttributeError):
            pass
    teams = ((payload.get("header") or {}).get("teams") or [])
    if len(teams) >= 2 and teams[0].get("score") is not None and teams[1].get("score") is not None:
        return int(teams[0]["score"]), int(teams[1]["score"])
    return nan(), nan()


def event_yellows(content):
    vals = [0, 0]
    for event in events_of(content):
        if event.get("type") == "Card" and event.get("card") == "Yellow" and event.get("isHome") is not None:
            vals[0 if event["isHome"] else 1] += 1
    return vals


def write_csv(path, records):
    fields = []
    for record in records:
        for key in record:
            if key not in fields:
                fields.append(key)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def main():
    selected = []
    excluded_name = 0
    with open(INDEX, newline="") as fh:
        for index_row in csv.DictReader(fh):
            if index_row.get("league_id") != "111":
                continue
            payload = load(ROOT / index_row["path"] if (ROOT / index_row["path"]).exists() else INDEX.parent.parent / index_row["path"])
            if (payload.get("general") or {}).get("leagueName") != "Eerste Divisie":
                excluded_name += 1
                continue
            if not ((payload.get("header") or {}).get("status") or {}).get("finished", False):
                continue
            selected.append((index_row, payload))

    matches, team_matches = [], []
    for index_row, payload in selected:
        content = payload.get("content") or {}
        header = payload.get("header") or {}
        teams = header.get("teams") or [{}, {}]
        home, away = teams[0], teams[1]
        stats = flat_stats(content)
        conflicts = stats_conflicts(content)
        all_keys = {key for period, key in stats if period == "All"}
        ft_home, ft_away = score(payload)
        half_time = ht_from_events(content)
        events = events_of(content)
        shots = [shot for shot in shots_of(content) if shot.get("period") != "PenaltyShootout"]
        shotmap = {key: [0, 0] for key in ("shots", "sot", "sot_incl_blocked", "xg", "xgot", "xgot_n", "xgot_n_on", "xgot_n_off")}
        for shot in shots:
            side = 0 if shot.get("teamId") == home.get("id") else 1
            if shot.get("teamId") not in (home.get("id"), away.get("id")):
                continue
            shotmap["shots"][side] += 1
            if shot.get("isOnTarget") is True:
                shotmap["sot_incl_blocked"][side] += 1
            if shot.get("isOnTarget") is True and shot.get("isBlocked") is not True:
                shotmap["sot"][side] += 1
            if shot.get("expectedGoals") is not None:
                shotmap["xg"][side] += float(shot["expectedGoals"])
            if shot.get("expectedGoalsOnTarget") is not None:
                shotmap["xgot"][side] += float(shot["expectedGoalsOnTarget"])
                shotmap["xgot_n"][side] += 1
                shotmap["xgot_n_on" if shot.get("isOnTarget") is True else "xgot_n_off"][side] += 1

        row = {
            "match_id": index_row["match_id"], "league": "NL-EersteDivisie", "season": index_row["season"],
            "season_start": int(index_row["season"][:4]), "date": index_row["date"],
            "kickoff_utc": ((header.get("status") or {}).get("utcTime") or ""),
            "round": (payload.get("general") or {}).get("matchRound"),
            "phase": "regular", "home_team_id": home.get("id"), "home_team": home.get("name"),
            "away_team_id": away.get("id"), "away_team": away.get("name"),
            "coverage_level": (payload.get("general") or {}).get("coverageLevel"),
            "home_goals": ft_home, "away_goals": ft_away,
            "ht_home_goals": half_time[0] if half_time else nan(),
            "ht_away_goals": half_time[1] if half_time else nan(),
            "ht_source": "events" if half_time is not None else "none",
            "ev_goals_home": sum(1 for e in events if e.get("type") == "Goal" and e.get("isHome") is True),
            "ev_goals_away": sum(1 for e in events if e.get("type") == "Goal" and e.get("isHome") is False),
            "referee": (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
            "has_events": bool(events), "has_lineup": bool(content.get("lineup")),
            "has_player_stats": bool(content.get("playerStats")), "has_stats_all": any(p == "All" for p, _ in stats),
            "has_stats_half": any(p in ("FirstHalf", "SecondHalf") for p, _ in stats),
            "has_shotmap": bool(shots_of(content)), "n_shootout_shots": len(shots_of(content)) - len(shots),
            "stats_conflict_count": conflicts if isinstance(conflicts, int) else len(conflicts),
        }
        row["score_events_mismatch"] = not math.isnan(ft_home) and (
            row["ev_goals_home"] != ft_home or row["ev_goals_away"] != ft_away
        )
        for key in XG_KEYS + BASE_KEYS:
            values = stats.get(("All", key), (nan(), nan()))
            row[f"{key}_home"], row[f"{key}_away"] = values
        for period, prefix in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
            for key in HALF_KEYS:
                values = stats.get((period, key), (nan(), nan()))
                row[f"{prefix}_{key}_home"], row[f"{prefix}_{key}_away"] = values

        stats_yellow = stats.get(("All", "yellow_cards"), (nan(), nan()))
        event_yellow = event_yellows(content)
        row["stats_yellow_home"], row["stats_yellow_away"] = stats_yellow
        row["event_yellow_home"], row["event_yellow_away"] = event_yellow
        row["yellow_diff_home"] = stats_yellow[0] - event_yellow[0] if not math.isnan(stats_yellow[0]) else nan()
        row["yellow_diff_away"] = stats_yellow[1] - event_yellow[1] if not math.isnan(stats_yellow[1]) else nan()
        # Phase-1 measurement selects event-unified Yellow-only counts as the
        # target; stats_yellow_* remain the explicit cross-check columns.
        row["cards_source"] = "events" if events else "none"
        row["yellow_home"], row["yellow_away"] = event_yellow
        row["red_home"], row["red_away"] = stats.get(("All", "red_cards"), (nan(), nan()))
        for key, values in shotmap.items():
            row[f"sm_{key}_home"], row[f"sm_{key}_away"] = values
        matches.append(row)

        for side, label in ((0, "home"), (1, "away")):
            opponent = "away" if side == 0 else "home"
            team = {
                "match_id": row["match_id"], "season": row["season"], "date": row["date"],
                "team_id": row[f"{label}_team_id"], "team": row[f"{label}_team"],
                "opponent_id": row[f"{opponent}_team_id"], "opponent": row[f"{opponent}_team"],
                "home_away": label,
            }
            for key, value in row.items():
                if key.endswith("_home"):
                    base = key[:-5]
                    team[base] = row[key] if side == 0 else row.get(base + "_away")
                elif key.endswith("_away"):
                    base = key[:-5]
                    if base not in team:
                        team[base] = row[key] if side == 1 else row.get(base + "_home")
            for key in ("ev_goals", "total_shots", "ShotsOnTarget", "corners", "yellow", "yellow_cards", "red", "red_cards", "fouls", "big_chance", "touches_opp_box", "BallPossesion"):
                team[key + "_against"] = row.get(key + ("_away" if side == 0 else "_home"), nan())
            team_matches.append(team)

    matches.sort(key=lambda r: (r["date"], int(r["match_id"])))
    team_matches.sort(key=lambda r: (r["date"], int(r["match_id"]), r["home_away"]))
    write_csv(OUT / "nl_eerste_matches.csv", matches)
    write_csv(OUT / "team_matches.csv", team_matches)
    # 2039 is the frozen build-time count asserted as a floor for daily rebuilds.
    assert len(matches) >= 2039 and len({r["match_id"] for r in matches}) == len(matches)
    assert len(team_matches) == 2 * len(matches)
    print(json.dumps({"index_rows": len(selected), "matches": len(matches), "team_rows": len(team_matches), "excluded_name": excluded_name}, indent=2))


if __name__ == "__main__":
    main()
