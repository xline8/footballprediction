"""Build the Saudi First Division match and team-match tables.

The warehouse is intentionally read through the worktree-relative index.  This
league has no shotmap content or xG: shotmap columns are explicit zero/None
sentinels and must not be inferred from the stats feed.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = [
    "BallPossesion", "Offsides", "ShotsOffTarget", "ShotsOnTarget",
    "accurate_crosses", "accurate_passes", "aerials_won", "big_chance",
    "big_chance_missed_title", "blocked_shots", "clearances", "corners",
    "dribbles_succeeded", "duel_won", "fouls", "ground_duels_won",
    "interceptions", "keeper_saves", "long_balls_accurate",
    "matchstats.headers.tackles", "opposition_half_passes", "own_half_passes",
    "passes", "player_throws", "red_cards", "shot_blocks",
    "shots_inside_box", "shots_outside_box", "shots_woodwork", "total_shots",
    "touches_opp_box", "yellow_cards",
]
PERIODS = ("All", "FirstHalf", "SecondHalf")


def _num(value):
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
    result = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                key = stat.get("key")
                values = stat.get("stats") or [None, None]
                pair = (_num(values[0]), _num(values[1]) if len(values) > 1 else None)
                if key and (pair[0] is not None or pair[1] is not None):
                    result[(period, key)] = pair
    return result


def _events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def _score(score_str):
    home, away = (score_str or "0 - 0").split("-")[:2]
    return int(home.strip()), int(away.strip())


def _info(content, key):
    return (((content or {}).get("matchFacts") or {}).get("infoBox") or {}).get(key) or {}


def build_rows():
    index_rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "10721"]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    rows = []
    for ix in index_rows:
        payload = json.load((ROOT / ix["path"]).open())
        general = payload.get("general") or {}
        status = (payload.get("header") or {}).get("status") or {}
        content = payload.get("content") or {}
        stats = flat_stats(content)
        events = _events(content)
        round_name = str(general.get("matchRound") or "")
        home = general.get("homeTeam") or {}
        away = general.get("awayTeam") or {}
        hg, ag = _score(status.get("scoreStr"))
        row = {
            "match_id": ix["match_id"], "league": "SA-FirstDivision", "season": ix["season"],
            "date": ix["date"], "round": round_name,
            "phase": "playoff" if "Play-off" in round_name else "regular",
            "awarded": int(bool(status.get("awarded"))),
            "home_team_id": home.get("id"), "home_team": home.get("name"),
            "away_team_id": away.get("id"), "away_team": away.get("name"),
            "home_goals": hg, "away_goals": ag,
        }
        goals = [e for e in events if e.get("type") == "Goal" and e.get("time") is not None and e.get("time") <= 45]
        if events:
            row["ht_home_goals"] = sum(1 for e in goals if e.get("isHome"))
            row["ht_away_goals"] = sum(1 for e in goals if not e.get("isHome"))
            row["ht_source"] = "events"
        else:
            row.update(ht_home_goals=None, ht_away_goals=None, ht_source="none")
        for card in ("Yellow", "YellowRed"):
            for side in ("home", "away"):
                row[f"ev_{card.lower()}_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") == card and bool(e.get("isHome")) == (side == "home"))
        for side in ("home", "away"):
            row[f"fh_ev_yellow_{side}"] = sum(1 for e in events if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and e.get("time") is not None and e.get("time") <= 45 and bool(e.get("isHome")) == (side == "home"))
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                home_value, away_value = stats.get((period, key), (None, None))
                row[f"{prefix}{key}_home"] = home_value
                row[f"{prefix}{key}_away"] = away_value
        row["yellow_home"] = row["ev_yellow_home"] + row["ev_yellowred_home"]
        row["yellow_away"] = row["ev_yellow_away"] + row["ev_yellowred_away"]
        row["red_home"] = row["red_cards_home"]
        row["red_away"] = row["red_cards_away"]
        referee = _info(content, "Referee")
        stadium = _info(content, "Stadium")
        row["referee"] = referee.get("text") if isinstance(referee, dict) else referee
        row["stadium_name"] = stadium.get("name")
        row["stadium_city"] = stadium.get("city")
        row["stadium_lat"] = stadium.get("lat")
        row["has_stats_all"] = int(all(("All", key) in stats for key in STAT_KEYS))
        row["has_stats_half"] = int(all((period, key) in stats for period in ("FirstHalf", "SecondHalf") for key in STAT_KEYS))
        row["has_extra_time"] = int(any("Extra" in period for period in ((content.get("stats") or {}).get("Periods") or {})))
        row["has_shotmap"] = 0
        row["has_events"] = int(bool(events))
        row["n_shootout_shots"] = 0
        for side in ("home", "away"):
            row[f"sm_shots_{side}"] = 0
            row[f"sm_xg_{side}"] = None
            row[f"sm_xgot_{side}"] = None
        rows.append(row)

    # One canonical name per FotMob team id; preserve ids as the identity key.
    names = {}
    for side in ("home", "away"):
        for row in rows:
            names.setdefault(row[f"{side}_team_id"], Counter())[row[f"{side}_team"]] += 1
    canonical = {tid: counts.most_common(1)[0][0] for tid, counts in names.items()}
    for row in rows:
        row["home_team"] = canonical[row["home_team_id"]]
        row["away_team"] = canonical[row["away_team_id"]]
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def team_rows(matches):
    result = []
    for match in matches:
        for side, opponent in (("home", "away"), ("away", "home")):
            row = {
                "match_id": match["match_id"], "league": match["league"], "season": match["season"],
                "date": match["date"], "round": match["round"], "phase": match["phase"],
                "awarded": match["awarded"], "team_id": match[f"{side}_team_id"], "team": match[f"{side}_team"],
                "opponent_id": match[f"{opponent}_team_id"], "opponent": match[f"{opponent}_team"], "venue": side,
                "goals_for": match[f"{side}_goals"], "goals_against": match[f"{opponent}_goals"],
                "ht_goals_for": match[f"ht_{side}_goals"], "ht_goals_against": match[f"ht_{opponent}_goals"],
                "yellow_for": match[f"yellow_{side}"], "yellow_against": match[f"yellow_{opponent}"],
                "red_for": match[f"red_{side}"], "red_against": match[f"red_{opponent}"],
            }
            for key in STAT_KEYS:
                row[f"{key}_for"] = match[f"{key}_{side}"]
                row[f"{key}_against"] = match[f"{key}_{opponent}"]
                row[f"fh_{key}_for"] = match[f"fh_{key}_{side}"]
                row[f"fh_{key}_against"] = match[f"fh_{key}_{opponent}"]
                row[f"sh_{key}_for"] = match[f"sh_{key}_{side}"]
                row[f"sh_{key}_against"] = match[f"sh_{key}_{opponent}"]
            row.update(has_stats_all=match["has_stats_all"], has_stats_half=match["has_stats_half"], has_events=match["has_events"])
            result.append(row)
    return result


def main():
    matches = build_rows()
    write_csv(OUT / "safd_matches.csv", matches)
    write_csv(OUT / "safd_team_matches.csv", team_rows(matches))
    print(f"index rows {len(matches)}; matches {len(matches)}; team_rows {2 * len(matches)}")


if __name__ == "__main__":
    main()
