"""Reproducible inventory and descriptive EDA for NL-EersteDivisie.

This script computes coverage, levels, reliability, half-share variance,
referee diagnostics, and mover/Jong diagnostics from the Phase-1 CSVs.  It
does not fit a model, choose a model arm, or read a virgin outcome window for
anything beyond design-level aggregates.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


M = read(DATA / "nl_eerste_matches.csv")
T = read(DATA / "team_matches.csv")


def num(row, key):
    try:
        return float(row.get(key, ""))
    except (TypeError, ValueError):
        return np.nan


def arr(rows, key):
    return np.asarray([num(row, key) for row in rows], dtype=float)


def finite(values):
    values = np.asarray(values, dtype=float)
    return values[np.isfinite(values)]


def mean(values):
    values = finite(values)
    return float(np.mean(values)) if len(values) else None


def variance(values):
    values = finite(values)
    return float(np.var(values, ddof=1)) if len(values) > 1 else None


def coverage(rows, key):
    return 100.0 * sum(str(row.get(key, "")).lower() in ("true", "1") for row in rows) / len(rows) if rows else None


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    good = np.isfinite(x) & np.isfinite(y)
    if good.sum() < 3 or np.std(x[good]) == 0 or np.std(y[good]) == 0:
        return None
    return float(np.corrcoef(x[good], y[good])[0, 1])


def split_half(groups, value, seed=90210, repetitions=60, min_matches=2):
    rng = np.random.default_rng(seed)
    repeated = []
    for _ in range(repetitions):
        first, second = [], []
        for rows in groups.values():
            values = finite([value(row) for row in rows])
            if len(values) < min_matches:
                continue
            order = rng.permutation(len(values))
            n = len(values) // 2
            first.append(np.mean(values[order[:n]]))
            second.append(np.mean(values[order[n:]]))
        correlation = pearson(first, second)
        if correlation is not None:
            repeated.append(correlation)
    odd, even = [], []
    for rows in groups.values():
        values = finite([value(row) for row in rows])
        if len(values) > 1:
            odd.append(np.mean(values[::2]))
            even.append(np.mean(values[1::2]))
    return {"r": mean(repeated), "n_splits": len(repeated), "odd_even_r": pearson(odd, even)}


def split_half_ratio(groups, numerator, denominator, min_matches=8, seed=90210):
    rng = np.random.default_rng(seed)
    repeated = []
    for _ in range(60):
        first, second = [], []
        for rows in groups.values():
            values = [(num(row, numerator), num(row, denominator)) for row in rows]
            values = [(a, b) for a, b in values if np.isfinite(a) and np.isfinite(b) and b > 0]
            if len(values) < 2 * min_matches:
                continue
            order = rng.permutation(len(values))
            n = len(values) // 2
            first.append(sum(values[i][0] for i in order[:n]) / sum(values[i][1] for i in order[:n]))
            second.append(sum(values[i][0] for i in order[n:]) / sum(values[i][1] for i in order[n:]))
        correlation = pearson(first, second)
        if correlation is not None:
            repeated.append(correlation)
    return {"r": mean(repeated), "n_splits": len(repeated), "method": "ratio_of_sums", "min_matches": min_matches}


def levels(rows):
    goals = arr(rows, "home_goals") + arr(rows, "away_goals")
    shots = arr(rows, "total_shots_home") + arr(rows, "total_shots_away")
    sot = arr(rows, "ShotsOnTarget_home") + arr(rows, "ShotsOnTarget_away")
    corners = arr(rows, "corners_home") + arr(rows, "corners_away")
    stats_cards = arr(rows, "stats_yellow_home") + arr(rows, "stats_yellow_away")
    event_cards = arr(rows, "event_yellow_home") + arr(rows, "event_yellow_away")
    return {
        "n_matches": len(rows), "goals_per_match": mean(goals),
        "home_goals": mean(arr(rows, "home_goals")), "away_goals": mean(arr(rows, "away_goals")),
        "home_draw_away_pct": [100 * sum(num(r, "home_goals") > num(r, "away_goals") for r in rows) / len(rows),
                               100 * sum(num(r, "home_goals") == num(r, "away_goals") for r in rows) / len(rows),
                               100 * sum(num(r, "home_goals") < num(r, "away_goals") for r in rows) / len(rows)],
        "btts_pct": 100 * np.mean((arr(rows, "home_goals") > 0) & (arr(rows, "away_goals") > 0)),
        "over2_5_pct": 100 * np.mean(goals > 2.5), "total_shots": mean(shots), "sot": mean(sot),
        "corners": mean(corners), "cards_stats": mean(stats_cards), "cards_events": mean(event_cards),
        "total_shots_variance": variance(shots), "sot_variance": variance(sot),
        "corners_variance": variance(corners), "cards_events_variance": variance(event_cards),
    }


def team_groups(rows, min_matches=24):
    groups = defaultdict(list)
    for row in rows:
        groups[row["team"]].append(row)
    return {team: values for team, values in groups.items() if len(values) >= min_matches}


def half_shares(rows, market, first_home, first_away, full_home, full_away, all_event_goal=False):
    usable = []
    for row in rows:
        first = num(row, first_home) + num(row, first_away)
        full = num(row, full_home) + num(row, full_away)
        if np.isfinite(first) and np.isfinite(full) and full > 0:
            usable.append((row, first, full))
    shares = np.asarray([first / full for _, first, full in usable])
    noise_floor = np.mean([share * (1 - share) / full for share, (_, _, full) in zip(shares, usable)]) if len(usable) else None
    groups = defaultdict(list)
    for row, first, full in usable:
        share = first / full
        groups[row["home_team"]].append({"share": share})
        groups[row["away_team"]].append({"share": share})
    groups = {k: v for k, v in groups.items() if len(v) >= 16}
    out = {"n_matches": len(usable), "share_1h": float(np.sum([x[1] for x in usable]) / np.sum([x[2] for x in usable])) if usable else None,
           "observed_variance": variance(shares), "noise_floor_per_match": float(noise_floor) if noise_floor is not None else None,
           "true_variance": float(variance(shares) - noise_floor) if len(shares) > 1 else None,
           "team_share_split_half": split_half(groups, lambda row: row["share"]) if groups else None}
    if all_event_goal:
        event_first = arr(rows, "ht_home_goals") + arr(rows, "ht_away_goals")
        event_full = arr(rows, "home_goals") + arr(rows, "away_goals")
        out["events_all_matches_goals_share"] = float(np.nansum(event_first) / np.nansum(event_full))
    return out


def main():
    assert len(M) == 2039
    inventory = {}
    season_levels = {}
    for season in SEASONS:
        rows = [row for row in M if row["season"] == season]
        inventory[season] = {
            "n_matches": len(rows), "rounds": sorted({int(row["round"]) for row in rows}),
            "coverage_pct": {key: coverage(rows, key) for key in ("has_stats_all", "has_stats_half", "has_events", "has_lineup", "has_player_stats", "has_shotmap")},
            "score_coverage_pct": 100 * sum(np.isfinite(num(row, "home_goals")) and np.isfinite(num(row, "away_goals")) for row in rows) / len(rows),
            "referee_nonempty_pct": 100 * sum(bool(row.get("referee")) for row in rows) / len(rows),
            "touches_opp_box_coverage_pct": 100 * sum(np.isfinite(num(row, "touches_opp_box_home")) for row in rows) / len(rows),
            "xg_key_presence_pct": 100 * sum(np.isfinite(num(row, "expected_goals_home")) for row in rows) / len(rows),
            "shotmap_nonempty_count": sum(row.get("has_shotmap") == "True" for row in rows),
            "score_events_mismatch_count": sum(row.get("score_events_mismatch") == "True" for row in rows),
            "distinct_teams": len({row["home_team"] for row in rows} | {row["away_team"] for row in rows}),
            "date_range": [min(row["date"] for row in rows), max(row["date"] for row in rows)],
        }
        season_levels[season] = levels(rows)

    groups = team_groups(T)
    reliability = {}
    for name, key in {"goals": "ev_goals", "SOT": "ShotsOnTarget", "corners": "corners", "cards": "yellow", "shots": "total_shots", "possession": "BallPossesion", "big_chances": "big_chance", "touches_opp_box": "touches_opp_box"}.items():
        reliability[name + "_for"] = split_half(groups, lambda row, key=key: num(row, key))
        reliability[name + "_against"] = split_half(groups, lambda row, key=key: num(row, key + "_against"))
    reliability_by_season = {}
    for season in SEASONS:
        season_team_groups = team_groups([row for row in T if row["season"] == season], min_matches=8)
        reliability_by_season[season] = {}
        for name, key in {"goals": "ev_goals", "SOT": "ShotsOnTarget", "corners": "corners", "cards": "yellow", "shots": "total_shots", "possession": "BallPossesion", "big_chances": "big_chance", "touches_opp_box": "touches_opp_box"}.items():
            reliability_by_season[season][name + "_for"] = split_half(season_team_groups, lambda row, key=key: num(row, key))
            reliability_by_season[season][name + "_against"] = split_half(season_team_groups, lambda row, key=key: num(row, key + "_against"))

    halves = {
        "goals": half_shares(M, "goals", "ht_home_goals", "ht_away_goals", "home_goals", "away_goals", True),
        "SOT": half_shares([r for r in M if r["season"] >= "2023/2024"], "SOT", "fh_ShotsOnTarget_home", "fh_ShotsOnTarget_away", "ShotsOnTarget_home", "ShotsOnTarget_away"),
        "corners": half_shares([r for r in M if r["season"] >= "2023/2024"], "corners", "fh_corners_home", "fh_corners_away", "corners_home", "corners_away"),
        "total_shots": half_shares([r for r in M if r["season"] >= "2023/2024"], "total_shots", "fh_total_shots_home", "fh_total_shots_away", "total_shots_home", "total_shots_away"),
        "yellows": half_shares([r for r in M if r["season"] >= "2023/2024"], "yellows", "fh_yellow_cards_home", "fh_yellow_cards_away", "yellow_home", "yellow_away"),
    }

    referees = defaultdict(list)
    for row in M:
        if row.get("referee"):
            referees[row["referee"]].append(row)
    referees = {k: v for k, v in referees.items() if len(v) >= 20}
    referee_summary = {"coverage_pct": 100 * sum(bool(row.get("referee")) for row in M) / len(M),
                       "coverage_by_season": {s: inventory[s]["referee_nonempty_pct"] for s in SEASONS},
                       "eligible_referees_min20": len(referees),
                       "card_rate_split_half": split_half(referees, lambda row: num(row, "event_yellow_home") + num(row, "event_yellow_away")) if referees else None}

    jong = sorted({row["team"] for row in T if row["team"].startswith("Jong ")})
    jong_groups = {team: rows for team, rows in groups.items() if team in jong}
    non_jong_groups = {team: rows for team, rows in groups.items() if team not in jong}
    jong_summary = {"teams": jong, "n_teams": len(jong),
                    "reliability": {"goals_for": split_half(jong_groups, lambda r: num(r, "ev_goals")), "goals_against": split_half(jong_groups, lambda r: num(r, "ev_goals_against"))},
                    "goals_for_variance": variance([num(r, "ev_goals") for r in T if r["team"] in jong]),
                    "goals_against_variance": variance([num(r, "ev_goals_against") for r in T if r["team"] in jong]),
                    "non_jong_comparison": {"reliability": {"goals_for": split_half(non_jong_groups, lambda r: num(r, "ev_goals")), "goals_against": split_half(non_jong_groups, lambda r: num(r, "ev_goals_against"))},
                                             "goals_for_variance": variance([num(r, "ev_goals") for r in T if r["team"] not in jong]),
                                             "goals_against_variance": variance([num(r, "ev_goals_against") for r in T if r["team"] not in jong])}}

    movers = {}
    for i in range(1, len(SEASONS)):
        season, previous = SEASONS[i], SEASONS[i - 1]
        now = {r["home_team"] for r in M if r["season"] == season} | {r["away_team"] for r in M if r["season"] == season}
        before = {r["home_team"] for r in M if r["season"] == previous} | {r["away_team"] for r in M if r["season"] == previous}
        entrants = sorted(now - before)
        relegated_from_eredivisie = []  # No cross-tier warehouse table is read in Phase 1.
        promoted_from_tweede = entrants
        def entrant_gap(teams):
            rows = [r for r in M if r["season"] == season and (r["home_team"] in teams or r["away_team"] in teams)]
            gf = [num(r, "home_goals") if r["home_team"] in teams else num(r, "away_goals") for r in rows]
            ga = [num(r, "away_goals") if r["home_team"] in teams else num(r, "home_goals") for r in rows]
            league_team_mean = season_levels[season]["goals_per_match"] / 2
            return {"teams": sorted(teams), "n_teams": len(teams), "gf_per_match": mean(gf), "ga_per_match": mean(ga), "league_team_goal_mean": league_team_mean,
                    "gf_gap": mean(gf) - league_team_mean if mean(gf) is not None else None, "ga_gap": mean(ga) - league_team_mean if mean(ga) is not None else None}
        movers[season] = {"entrants_absent_prior": entrants, "relegated_from_Eredivisie": entrant_gap(relegated_from_eredivisie), "promoted_from_Tweede_Divisie_proxy": entrant_gap(promoted_from_tweede), "Jong_entrants": [x for x in entrants if x in jong]}

    # Stats-vs-events card target comparison is intentionally descriptive and is
    # the early preprocessing source check requested by the brief.
    card_check = {}
    for season in SEASONS:
        rows = [r for r in M if r["season"] == season]
        comparisons = [(num(r, "stats_yellow_home") + num(r, "stats_yellow_away"), num(r, "event_yellow_home") + num(r, "event_yellow_away")) for r in rows]
        usable = [(a, b) for a, b in comparisons if np.isfinite(a) and np.isfinite(b)]
        card_check[season] = {"n_usable": len(usable), "mismatch_count": sum(a != b for a, b in usable), "mismatch_rate_pct": 100 * sum(a != b for a, b in usable) / len(usable) if usable else None,
                              "stats_total": sum(a for a, _ in usable), "events_total": sum(b for _, b in usable)}

    result_inventory = {"league": "NL-EersteDivisie", "fotmob_id": 111, "league_name": "Eerste Divisie", "index_rows": len(M), "seasons": inventory,
                        "phase_rule": "regular season only; rounds 1-38; no play-off rows in this feed", "format": {"teams": 20, "rounds": 38},
                        "parent_tier": {"league": "NL-Eredivisie", "fotmob_id": 57}, "reserve_teams": jong}
    result_eda = {"league": "NL-EersteDivisie", "season_levels": season_levels, "pooled_levels": levels(M), "home_advantage_goals": mean(arr(M, "home_goals") - arr(M, "away_goals")),
                  "reliability": reliability, "reliability_by_season": reliability_by_season, "halves": halves, "referees": referee_summary, "jong_comparison": jong_summary, "movers": movers, "cards_source_check": card_check,
                  "virgin_design_aggregate_note": "2025/2026 levels are descriptive only; no fitting, arm selection, or gate setting was performed.",
                  "star_absence": "Not measured; excluded from Phase 1 feature set."}
    (HERE / "inventory_summary.json").write_text(json.dumps(result_inventory, indent=2, allow_nan=False))
    (HERE / "eda_summary.json").write_text(json.dumps(result_eda, indent=2, allow_nan=False))
    print(json.dumps({"matches": len(M), "team_rows": len(T), "seasons": {s: inventory[s]["n_matches"] for s in SEASONS}, "pooled_goals_per_match": result_eda["pooled_levels"]["goals_per_match"], "card_check": card_check}, indent=2))


if __name__ == "__main__":
    main()
