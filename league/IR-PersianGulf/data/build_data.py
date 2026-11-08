"""Build the Iran Persian Gulf Pro League regular-season analysis tables.

Adapted from the Azadegan builder (same FotMob matchDetails format and
same jleague_lib helpers). The league identity uses parentLeagueId 523
and the two observed league names, never general.leagueId (a
season-edition id). Two non-league playoff rows are excluded:
1000015890 (Asian Qualifiers Play-offs - Semi-Final) and 1000015891
(Asian Qualifiers Play-offs - Final), both phase=playoff/non-numeric
matchRound. content.stats is null and the shotmap shot list is empty in
all 1,245 payloads, while event cards provide Yellow, Red, and
YellowRed counts. Two goal-event/FT mismatches (3765423 and 3765395)
are flagged and their HT is set to NaN. Played league n = 1,243.
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
    in this corpus (0 in 1,564 matches); reds count Red + YellowRed."""
    vals = {"yellow": [0, 0], "red": [0, 0], "yellowred": [0, 0]}
    for event in events_of(content):
        if event.get("type") != "Card" or event.get("isHome") is None:
            continue
        side = 0 if event["isHome"] else 1
        if event.get("card") == "Yellow":
            vals["yellow"][side] += 1
        elif event.get("card") == "YellowRed":
            vals["yellowred"][side] += 1
            vals["red"][side] += 1
        elif event.get("card") == "Red":
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
    index_rows = 0
    excluded_name = 0
    excluded_playoff = 0
    excluded_unplayed = 0
    with open(INDEX, newline="") as fh:
        for index_row in csv.DictReader(fh):
            if index_row.get("league_id") != "523":
                continue
            index_rows += 1
            rel = index_row["path"]
            p = ROOT / rel
            if not p.exists():
                # Payloads are gitignored: the worktree checkout has the
                # index but not the 24 GB warehouse; read from the main
                # checkout, which is the same warehouse.
                p = Path("/home/hatch/workspace/footballprediction") / rel
            payload = load(p)
            general = payload.get("general") or {}
            if general.get("parentLeagueId") != 523 or general.get("leagueName") not in ("Persian Gulf Pro League", "Persian Gulf"):
                excluded_name += 1
                continue
            match_round = general.get("matchRound")
            try:
                int(str(match_round))
            except (TypeError, ValueError):
                # Asian Qualifiers Play-offs - Semi-Final (1000015890)
                # and Final (1000015891) are not league matches.
                excluded_playoff += 1
                continue
            if not ((payload.get("header") or {}).get("status") or {}).get("finished", False):
                # Placeholder 0-0 rows for matches never played (started
                # False): 3743953 (2021/2022) and 5098083 (2025/2026).
                excluded_unplayed += 1
                continue
            selected.append((index_row, payload))

    matches, team_matches = [], []
    score_agreement = 0
    for index_row, payload in selected:
        content = payload.get("content") or {}
        header = payload.get("header") or {}
        teams = header.get("teams") or [{}, {}]
        home, away = teams[0], teams[1]
        stats = flat_stats(content)
        conflicts = stats_conflicts(content)
        ft_home, ft_away = score(payload)
        index_score = index_row.get("score", "")
        if index_score and f"{ft_home}-{ft_away}" == index_score.replace("–", "-"):
            score_agreement += 1
        events = events_of(content)
        ev_goals_home = sum(1 for e in events if e.get("type") == "Goal" and e.get("isHome") is True)
        ev_goals_away = sum(1 for e in events if e.get("type") == "Goal" and e.get("isHome") is False)
        mismatch = bool(events) and not math.isnan(ft_home) and (ev_goals_home != ft_home or ev_goals_away != ft_away)
        half_time = ht_from_events(content)
        ht_source = "events"
        if mismatch:
            # Event feed disagrees with the FT score (3 matches: two
            # undercount goals, one attributes them to the wrong side):
            # the HT split from that feed cannot be trusted, so it is NaN.
            half_time, ht_source = None, "events-incomplete"
        elif half_time is None and ft_home == 0 and ft_away == 0 and not events:
            # Empty event feed on a 0-0: HT is (0, 0) by the same feed.
            half_time, ht_source = (0, 0), "events-zero"
        elif half_time is None:
            ht_source = "none"
        shots = [shot for shot in shots_of(content) if shot.get("period") != "PenaltyShootout"]
        cards = event_card_counts(content)

        row = {
            "match_id": index_row["match_id"], "league": "IR-PersianGulf", "season": index_row["season"],
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
            "ev_goals_home": ev_goals_home,
            "ev_goals_away": ev_goals_away,
            "referee": (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
            "has_events": bool(events), "has_lineup": bool(content.get("lineup")),
            "has_player_stats": bool(content.get("playerStats")), "has_stats_all": any(p == "All" for p, _ in stats),
            "has_stats_half": any(p in ("FirstHalf", "SecondHalf") for p, _ in stats),
            "has_shotmap": bool(shots_of(content)), "n_shootout_shots": len(shots_of(content)) - len(shots),
            "stats_conflict_count": conflicts if isinstance(conflicts, int) else len(conflicts),
        }
        row["score_events_mismatch"] = mismatch
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
        row["event_yellowred_home"], row["event_yellowred_away"] = cards["yellowred"]
        row["yellow_diff_home"] = nan()
        row["yellow_diff_away"] = nan()
        row["cards_source"] = "events"
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
    write_csv(OUT / "ir_persiangulf_matches.csv", matches)
    write_csv(OUT / "team_matches.csv", team_matches)
    assert len(matches) == 1243 and len({r["match_id"] for r in matches}) == len(matches)
    assert len(team_matches) == 2 * len(matches)
    assert score_agreement == len(matches)
    expected_season_counts = {"2021/2022": 240, "2022/2023": 240, "2023/2024": 240,
                              "2024/2025": 240, "2025/2026": 178, "2026/2027": 105}
    actual_season_counts = {s: sum(r["season"] == s for r in matches) for s in expected_season_counts}
    assert actual_season_counts == expected_season_counts
    print(json.dumps({"index_rows": index_rows, "matches": len(matches), "team_rows": len(team_matches),
                      "excluded_name": excluded_name, "excluded_playoff": excluded_playoff,
                      "excluded_unplayed": excluded_unplayed, "score_agreement": score_agreement,
                      "season_counts": actual_season_counts}, indent=2))


if __name__ == "__main__":
    main()
