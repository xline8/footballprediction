"""Reproducible inventory and descriptive EDA for NL-TweedeDivisie.

Adapted from league/NL-EersteDivisie/analysis/inventory.py. Tweede
Divisie is scores-only: no stats, shotmap, lineup, player stats,
xG, or referee text exists in any payload, so only goals (FT + HT
from events) and red-family event counts are measured. It does not
fit a model, choose a model arm, or read a virgin outcome window
for anything beyond design-level aggregates.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
ROOT = HERE.parents[2]
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


M = read(DATA / "nl_tweede_matches.csv")
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


def levels(rows):
    goals = arr(rows, "home_goals") + arr(rows, "away_goals")
    return {
        "n_matches": len(rows), "goals_per_match": mean(goals),
        "home_goals": mean(arr(rows, "home_goals")), "away_goals": mean(arr(rows, "away_goals")),
        "home_draw_away_pct": [100 * sum(num(r, "home_goals") > num(r, "away_goals") for r in rows) / len(rows),
                               100 * sum(num(r, "home_goals") == num(r, "away_goals") for r in rows) / len(rows),
                               100 * sum(num(r, "home_goals") < num(r, "away_goals") for r in rows) / len(rows)],
        "btts_pct": 100 * float(np.mean((arr(rows, "home_goals") > 0) & (arr(rows, "away_goals") > 0))),
        "over1_5_pct": 100 * float(np.mean(goals > 1.5)),
        "over2_5_pct": 100 * float(np.mean(goals > 2.5)),
        "over3_5_pct": 100 * float(np.mean(goals > 3.5)),
        "goals_variance": variance(goals),
        "red_cards_per_match": mean(arr(rows, "red_home") + arr(rows, "red_away")),
    }


def team_groups(rows, min_matches=24):
    groups = defaultdict(list)
    for row in rows:
        groups[row["team"]].append(row)
    return {team: values for team, values in groups.items() if len(values) >= min_matches}


def half_shares(rows):
    usable = []
    for row in rows:
        first = num(row, "ht_home_goals") + num(row, "ht_away_goals")
        full = num(row, "home_goals") + num(row, "away_goals")
        if np.isfinite(first) and np.isfinite(full) and full > 0:
            usable.append((row, first, full))
    shares = np.asarray([first / full for _, first, full in usable])
    # Binomial noise floor uses the POOLED league share p for every match:
    # the plug-in per-match share is 0/1 whenever a match has 1 goal, which
    # understates the noise (the same correction the NL-Eerste coordinator
    # applied to that league's first-pass floor).
    pooled_p = float(np.sum([x[1] for x in usable]) / np.sum([x[2] for x in usable]))
    noise_floor = float(np.mean([pooled_p * (1 - pooled_p) / f for _, _, f in usable])) if usable else None
    groups = defaultdict(list)
    for row, first, full in usable:
        groups[row["home_team"]].append({"share": first / full})
        groups[row["away_team"]].append({"share": first / full})
    groups = {k: v for k, v in groups.items() if len(v) >= 16}
    return {"n_matches": len(usable),
            "share_1h": float(np.sum([x[1] for x in usable]) / np.sum([x[2] for x in usable])) if usable else None,
            "observed_variance": variance(shares),
            "noise_floor_per_match": noise_floor,
            "true_variance": float(variance(shares) - noise_floor) if len(shares) > 1 else None,
            "team_share_split_half": split_half(groups, lambda row: row["share"]) if groups else None}


def main():
    assert len(M) == 1638
    inventory = {}
    season_levels = {}
    for season in SEASONS:
        rows = [row for row in M if row["season"] == season]
        inventory[season] = {
            "n_matches": len(rows), "rounds": sorted({int(row["round"]) for row in rows}),
            "coverage_pct": {key: coverage(rows, key) for key in ("has_stats_all", "has_stats_half", "has_events", "has_lineup", "has_player_stats", "has_shotmap")},
            "score_coverage_pct": 100 * sum(np.isfinite(num(row, "home_goals")) and np.isfinite(num(row, "away_goals")) for row in rows) / len(rows),
            "referee_nonempty_pct": 100 * sum(bool(row.get("referee")) for row in rows) / len(rows),
            "xg_key_presence_pct": 100 * sum(np.isfinite(num(row, "expected_goals_home")) for row in rows) / len(rows),
            "shotmap_nonempty_count": sum(row.get("has_shotmap") == "True" for row in rows),
            "score_events_mismatch_count": sum(row.get("score_events_mismatch") == "True" for row in rows),
            "ht_derived_count": sum(row.get("ht_source") in ("events", "events-zero") for row in rows),
            "distinct_teams": len({row["home_team"] for row in rows} | {row["away_team"] for row in rows}),
            "date_range": [min(row["date"] for row in rows), max(row["date"] for row in rows)],
        }
        season_levels[season] = levels(rows)

    groups = team_groups(T)
    reliability = {
        "goals_for": split_half(groups, lambda row: num(row, "ev_goals")),
        "goals_against": split_half(groups, lambda row: num(row, "ev_goals_against")),
        "red_cards_for": split_half(groups, lambda row: num(row, "red")),
    }
    reliability_by_season = {}
    for season in SEASONS:
        sg = team_groups([row for row in T if row["season"] == season], min_matches=8)
        reliability_by_season[season] = {
            "goals_for": split_half(sg, lambda row: num(row, "ev_goals")),
            "goals_against": split_half(sg, lambda row: num(row, "ev_goals_against")),
        }

    halves = {"goals": half_shares(M)}

    jong = sorted({row["team"] for row in T if row["team"].startswith("Jong ")})
    jong_groups = {team: rows for team, rows in groups.items() if team in jong}
    non_jong_groups = {team: rows for team, rows in groups.items() if team not in jong}
    jong_summary = {"teams": jong, "n_teams": len(jong),
                    "reliability": {"goals_for": split_half(jong_groups, lambda r: num(r, "ev_goals")),
                                    "goals_against": split_half(jong_groups, lambda r: num(r, "ev_goals_against"))},
                    "goals_for_variance": variance([num(r, "ev_goals") for r in T if r["team"] in jong]),
                    "goals_against_variance": variance([num(r, "ev_goals_against") for r in T if r["team"] in jong]),
                    "non_jong_comparison": {"reliability": {"goals_for": split_half(non_jong_groups, lambda r: num(r, "ev_goals")),
                                                            "goals_against": split_half(non_jong_groups, lambda r: num(r, "ev_goals_against"))},
                                            "goals_for_variance": variance([num(r, "ev_goals") for r in T if r["team"] not in jong]),
                                            "goals_against_variance": variance([num(r, "ev_goals_against") for r in T if r["team"] not in jong])}}

    # Movers: entrants are clubs absent from this league the prior season.
    # Cross-check against the parent tier: were any entrants in the Eerste
    # Divisie (FotMob 111) the previous season? (Dutch pyramid: no
    # promotion/relegation between Eerste and Tweede Divisie.)
    eerste_names = defaultdict(set)
    with open(ROOT / "data_enrichment" / "fotmob_world_index.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("league_id") == "111":
                eerste_names[r["season"]].add(r["home"])
                eerste_names[r["season"]].add(r["away"])
    movers = {}
    pooled_gf, pooled_ga, pooled_n = [], [], 0
    for i in range(1, len(SEASONS)):
        season, previous = SEASONS[i], SEASONS[i - 1]
        now = {r["home_team"] for r in M if r["season"] == season} | {r["away_team"] for r in M if r["season"] == season}
        before = {r["home_team"] for r in M if r["season"] == previous} | {r["away_team"] for r in M if r["season"] == previous}
        entrants = sorted(now - before)

        def entrant_gap(teams):
            rows = [r for r in M if r["season"] == season and (r["home_team"] in teams or r["away_team"] in teams)]
            gf = [num(r, "home_goals") if r["home_team"] in teams else num(r, "away_goals") for r in rows]
            ga = [num(r, "away_goals") if r["home_team"] in teams else num(r, "home_goals") for r in rows]
            league_team_mean = season_levels[season]["goals_per_match"] / 2
            return {"teams": sorted(teams), "n_teams": len(teams), "n_team_matches": len(rows),
                    "gf_per_match": mean(gf), "ga_per_match": mean(ga), "league_team_goal_mean": league_team_mean,
                    "gf_gap": mean(gf) - league_team_mean if mean(gf) is not None else None,
                    "ga_gap": mean(ga) - league_team_mean if mean(ga) is not None else None}

        gap = entrant_gap(entrants)
        if season in ("2022/2023", "2023/2024", "2024/2025"):
            # Pooled magnitudes use DEV transitions only: the 2025/2026
            # (virgin) transition is described per-season but excluded
            # from the frozen X2 magnitudes, so no virgin outcome sets
            # an arm parameter.
            pooled_gf += [num(r, "home_goals") if r["home_team"] in entrants else num(r, "away_goals")
                          for r in M if r["season"] == season and (r["home_team"] in entrants or r["away_team"] in entrants)]
            pooled_ga += [num(r, "away_goals") if r["home_team"] in entrants else num(r, "home_goals")
                          for r in M if r["season"] == season and (r["home_team"] in entrants or r["away_team"] in entrants)]
        movers[season] = {"entrants_absent_prior": entrants,
                          "entrants_in_eerste_prev_season": sorted(set(entrants) & eerste_names[previous]),
                          "entrant_gap": gap,
                          "jong_entrants": [x for x in entrants if x in jong]}
    pooled_mean = sum(pooled_gf) / len(pooled_gf)
    pooled_ga_mean = sum(pooled_ga) / len(pooled_ga)
    # League team-goal mean over the same DEV seasons, match-weighted.
    dev_rows = [r for r in M if r["season"] in ("2022/2023", "2023/2024", "2024/2025")]
    league_mu = (sum(num(r, "home_goals") for r in dev_rows) + sum(num(r, "away_goals") for r in dev_rows)) / (2 * len(dev_rows))
    movers["pooled_complete_transitions"] = {"n_team_matches": len(pooled_gf),
                                             "gf_per_match": pooled_mean, "ga_per_match": pooled_ga_mean,
                                             "league_team_goal_mean": league_mu,
                                             "gf_gap": pooled_mean - league_mu, "ga_gap": pooled_ga_mean - league_mu}

    reds = {"per_match": mean(arr(M, "red_home") + arr(M, "red_away")),
            "total": int(sum(arr(M, "red_home") + arr(M, "red_away"))),
            "yellow_events_total": int(sum(arr(M, "yellow_home") + arr(M, "yellow_away"))),
            "matches_with_red": int(sum((arr(M, "red_home") + arr(M, "red_away")) > 0))}

    result_inventory = {"league": "NL-TweedeDivisie", "fotmob_id": 9195, "league_name": "Tweede Divisie",
                        "index_rows": len(M), "seasons": inventory,
                        "phase_rule": "regular season only; rounds 1-34; no play-off rows in this feed",
                        "format": {"teams": 18, "rounds": 34},
                        "parent_tier": {"league": "NL-EersteDivisie", "fotmob_id": 111},
                        "reserve_teams": jong}
    result_eda = {"league": "NL-TweedeDivisie", "season_levels": season_levels, "pooled_levels": levels(M),
                  "home_advantage_goals": mean(arr(M, "home_goals") - arr(M, "away_goals")),
                  "reliability": reliability, "reliability_by_season": reliability_by_season,
                  "halves": halves, "jong_comparison": jong_summary, "movers": movers, "reds": reds,
                  "virgin_design_aggregate_note": "2025/2026 levels are descriptive only; no fitting, arm selection, or gate setting was performed.",
                  "star_absence": "Not measured; excluded from Phase 1 feature set."}
    (HERE / "inventory_summary.json").write_text(json.dumps(result_inventory, indent=2, allow_nan=False))
    (HERE / "eda_summary.json").write_text(json.dumps(result_eda, indent=2, allow_nan=False))
    print(json.dumps({"matches": len(M), "team_rows": len(T),
                      "seasons": {s: inventory[s]["n_matches"] for s in SEASONS},
                      "pooled_goals_per_match": result_eda["pooled_levels"]["goals_per_match"],
                      "movers_pooled": movers["pooled_complete_transitions"], "reds": reds}, indent=2))


if __name__ == "__main__":
    main()
