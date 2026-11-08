"""Build the Netherlands Tweede Divisie regular-season analysis tables.

Adapted from league/NL-EersteDivisie/data/build_data.py (same FotMob
matchDetails format, same jleague_lib helpers). Tweede Divisie is a
scores-only corpus: content.stats is None and the shotmap shot list is
empty in every one of the 1,638 payloads (verified by content, never by
the index has_* flags), so every stats/xG/shotmap column below is NaN/0
by construction. What the payloads DO carry: the official FT score,
a complete goal-event feed (reproduces scoreStr in 1,638/1,638 matches),
Half markers, and red-family card events only (Red + YellowRed; no
Yellow events anywhere). HT goals come from the event feed; the 53
matches with an empty event feed are all 0-0, so their HT is (0, 0)
by the same feed (recorded as ht_source 'events-zero').
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
# Fallback permits the build to run from the worktree while the coordinator
# has not yet provided the main-checkout warehouse symlink.
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


def event_card_counts(content):
    """(yellow, red) per side from the event feed. Yellows never occur
    in this corpus (0 in 1,638 matches); reds count Red + YellowRed."""
    vals = {"yellow": [0, 0], "red": [0, 0]}
    for event in events_of(content):
        if event.get("type") != "Card" or event.get("isHome") is None:
            continue
        side = 0 if event["isHome"] else 1
        if event.get("card") == "Yellow":
            vals["yellow"][side] += 1
        elif event.get("card") in ("Red", "YellowRed"):
            vals["red"][side] += 1
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
            if index_row.get("league_id") != "9195":
                continue
            rel = index_row["path"]
            p = ROOT / rel
            if not p.exists():
                # Payloads are gitignored: the worktree checkout has the
                # index but not the 24 GB warehouse; read from the main
                # checkout, which is the same warehouse.
                p = Path("/home/hatch/workspace/footballprediction") / rel
            payload = load(p)
            if (payload.get("general") or {}).get("leagueName") != "Tweede Divisie":
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
        ft_home, ft_away = score(payload)
        half_time = ht_from_events(content)
        ht_source = "events"
        if half_time is None and ft_home == 0 and ft_away == 0 and not events_of(content):
            # Empty event feed on a 0-0: HT is (0, 0) by the same feed.
            half_time, ht_source = (0, 0), "events-zero"
        elif half_time is None:
            ht_source = "none"
        events = events_of(content)
        shots = [shot for shot in shots_of(content) if shot.get("period") != "PenaltyShootout"]
        cards = event_card_counts(content)

        row = {
            "match_id": index_row["match_id"], "league": "NL-TweedeDivisie", "season": index_row["season"],
            "season_start": int(index_row["season"][:4]), "date": index_row["date"],
            "kickoff_utc": ((header.get("status") or {}).get("utcTime") or ""),
            "round": (payload.get("general") or {}).get("matchRound"),
            "phase": "regular", "home_team_id": home.get("id"), "home_team": home.get("name"),
            "away_team_id": away.get("id"), "away_team": away.get("name"),
            "coverage_level": (payload.get("general") or {}).get("coverageLevel"),
            "home_goals": ft_home, "away_goals": ft_away,
            "ht_home_goals": half_time[0] if half_time else nan(),
            "ht_away_goals": half_time[1] if half_time else nan(),
            "ht_source": ht_source,
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

        # No stats feed exists, so the event feed is the only card source:
        # yellows 0 everywhere, reds = Red + YellowRed events per side.
        row["stats_yellow_home"], row["stats_yellow_away"] = nan(), nan()
        row["event_yellow_home"], row["event_yellow_away"] = cards["yellow"]
        row["yellow_diff_home"] = nan()
        row["yellow_diff_away"] = nan()
        row["cards_source"] = "events-red-only"
        row["yellow_home"], row["yellow_away"] = cards["yellow"]
        row["event_red_home"], row["event_red_away"] = cards["red"]
        row["red_home"], row["red_away"] = cards["red"]
        for key in ("shots", "sot", "sot_incl_blocked", "xg", "xgot", "xgot_n", "xgot_n_on", "xgot_n_off"):
            row[f"sm_{key}_home"], row[f"sm_{key}_away"] = 0, 0
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
    write_csv(OUT / "nl_tweede_matches.csv", matches)
    write_csv(OUT / "team_matches.csv", team_matches)
    # 1638 is the frozen build-time count asserted as a floor for daily rebuilds.
    assert len(matches) >= 1638 and len({r["match_id"] for r in matches}) == len(matches)
    assert len(team_matches) == 2 * len(matches)
    print(json.dumps({"index_rows": len(selected), "matches": len(matches), "team_rows": len(team_matches), "excluded_name": excluded_name}, indent=2))


if __name__ == "__main__":
    main()
