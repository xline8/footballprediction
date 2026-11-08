"""Reproducible South Africa PSL inventory and EDA; deliberately performs no fitting."""
import csv
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "za_matches.csv").open()))
random.seed(42)


def f(row, key):
    try:
        return None if row.get(key) in (None, "", "None") else float(row[key])
    except (TypeError, ValueError):
        return None


def avg(values):
    return round(st.mean(values), 3) if values else None


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def corr(xs, ys):
    if len(xs) < 5:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den, 3) if den else None


def total(row, key):
    home, away = f(row, f"{key}_home"), f(row, f"{key}_away")
    return home + away if home is not None and away is not None else None


def goals_total(row):
    return int(row["home_goals"]) + int(row["away_goals"])


SEASONS = sorted({r["season"] for r in ROWS})
GOALS_DEV = {"2022/2023", "2023/2024", "2024/2025"}
STATS_DEV = {"2023/2024", "2024/2025"}
SPLIT_DEV = {"2022/2023", "2023/2024", "2024/2025"}
VIRGIN = "2025/2026"
CONFIRMATORY = "2026/2027"


def coverage(rows, key):
    return pct(sum(f(r, key) is not None for r in rows), len(rows))


def market_values(rows, key):
    return [total(r, key) for r in rows if total(r, key) is not None]


def rates(values, lines):
    return {str(line): {"over_rate": round(sum(v > line for v in values) / len(values), 3), "n": len(values)}
            for line in lines} if values else {str(line): {"over_rate": None, "n": 0} for line in lines}


def levels(rows):
    goals = [goals_total(r) for r in rows]
    out = {
        "matches": len(rows), "goals_per_match": avg(goals),
        "home_win_rate": round(sum(int(r["home_goals"]) > int(r["away_goals"]) for r in rows) / len(rows), 3) if rows else None,
        "draw_rate": round(sum(int(r["home_goals"]) == int(r["away_goals"]) for r in rows) / len(rows), 3) if rows else None,
        "away_win_rate": round(sum(int(r["home_goals"]) < int(r["away_goals"]) for r in rows) / len(rows), 3) if rows else None,
        "ou2_5_over_rate": round(sum(v > 2.5 for v in goals) / len(goals), 3) if goals else None,
        "home_advantage": {"goals": avg([int(r["home_goals"]) - int(r["away_goals"]) for r in rows]) if rows else None},
        "coverage": {"stats_all": pct(sum(r["has_stats_all"] == "1" for r in rows), len(rows)),
                     "period_splits": pct(sum(r["has_period_splits_content"] == "1" for r in rows), len(rows)),
                     "shotmap": pct(sum(r["has_shotmap"] == "1" for r in rows), len(rows)),
                     "referee": pct(sum(bool(r["referee"]) for r in rows), len(rows))},
    }
    specs = {"sot": ("ShotsOnTarget", [8.5, 9.5, 10.5]),
             "corners": ("corners", [8.5, 9.5, 10.5]),
             "cards": ("yellow_cards", [3.5, 4.5, 5.5]),
             "total_shots": ("total_shots", [24.5, 25.5, 26.5, 27.5, 28.5])}
    for name, (key, lines) in specs.items():
        values = market_values(rows, key)
        out[name] = {"mean": avg(values), "n": len(values), "over_rates": rates(values, lines),
                     "home_advantage": avg([f(r, f"{key}_home") - f(r, f"{key}_away") for r in rows
                                              if f(r, f"{key}_home") is not None and f(r, f"{key}_away") is not None])}
        out["coverage"][name] = pct(len(values), len(rows))
    return out


def season_inventory(rows, season):
    selected = [r for r in rows if r["season"] == season]
    team_counts = defaultdict(int)
    for row in selected:
        team_counts[row["home_team_id"]] += 1
        team_counts[row["away_team_id"]] += 1
    return {"distinct_team_ids": len(team_counts),
            "matches_per_team": {"min": min(team_counts.values()), "max": max(team_counts.values())},
            "referee_coverage": pct(sum(bool(r["referee"]) for r in selected), len(selected))}


per_season = {season: {**levels([r for r in ROWS if r["season"] == season]),
                       **season_inventory(ROWS, season),
                       "date_range": [min(r["date"] for r in ROWS if r["season"] == season),
                                      max(r["date"] for r in ROWS if r["season"] == season)]}
              for season in SEASONS}


def trait_values(rows, key, against=False):
    out = defaultdict(list)
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            value = f(row, f"{key}_{other if against else side}")
            if value is not None:
                out[(row[f"{side}_team_id"], row["season"])].append(value)
    return out


def goal_trait_values(rows, against=False):
    out = defaultdict(list)
    for row in rows:
        for side, other in (("home", "away"), ("away", "home")):
            out[(row[f"{side}_team_id"], row["season"])].append(float(row[f"{other if against else side}_goals"]))
    return out


def odd_even_reliability(series, minimum=8):
    odd, even = [], []
    for values in series.values():
        if len(values) < minimum:
            continue
        a, b = values[::2], values[1::2]
        if a and b:
            odd.append(st.mean(a)); even.append(st.mean(b))
    return {"r": corr(odd, even), "n_team_seasons": len(odd)}


def reliability(rows, stats_only=False):
    specs = {"goals_for": (None, False), "goals_against": (None, True),
             "sot_for": ("ShotsOnTarget", False), "sot_against": ("ShotsOnTarget", True),
             "corners_for": ("corners", False), "corners_against": ("corners", True),
             "total_shots_for": ("total_shots", False), "total_shots_against": ("total_shots", True),
             "yellow_cards_for": ("yellow_cards", False), "yellow_cards_against": ("yellow_cards", True),
             "possession_for": ("BallPossesion", False), "possession_against": ("BallPossesion", True),
             "big_chance_for": ("big_chance", False), "big_chance_against": ("big_chance", True),
             "touches_opp_box_for": ("touches_opp_box", False), "touches_opp_box_against": ("touches_opp_box", True)}
    out = {}
    for name, (key, against) in specs.items():
        series = goal_trait_values(rows, against) if key is None else trait_values(rows, key, against)
        out[name] = odd_even_reliability(series)
    return out


def referee_reliability(rows):
    series = defaultdict(list)
    for row in sorted(rows, key=lambda r: (r["referee"], r["date"], r["match_id"])):
        if row["referee"] and total(row, "yellow_cards") is not None:
            series[row["referee"]].append(total(row, "yellow_cards"))
    return {"r": odd_even_reliability(series, minimum=8)["r"],
            "n_referees": sum(len(v) >= 8 for v in series.values()),
            "n_matches": sum(len(v) for v in series.values())}


reliability_dev = reliability([r for r in ROWS if r["season"] in GOALS_DEV])
ref_reliability = referee_reliability([r for r in ROWS if r["season"] in GOALS_DEV])


def half_stats(rows, name, fh_key, ft_key, noise_kind="poisson"):
    shares, first, full = [], [], []
    for row in rows:
        fh, ft = total(row, fh_key), total(row, ft_key)
        if fh is None or ft is None or ft <= 0 or fh < 0:
            continue
        shares.append(fh / ft); first.append(fh); full.append(ft)
    if not shares:
        return {"n": 0, "share_1h": None, "observed_variance": None, "noise_expectation": None, "true_variance": None}
    p = sum(first) / sum(full)
    noise = st.mean([p * (1 - p) / value for value in full])
    observed = st.variance(shares) if len(shares) > 1 else 0.0
    return {"n": len(shares), "share_1h": round(p, 4), "observed_variance": round(observed, 5),
            "noise_expectation": round(noise, 5), "true_variance": round(observed - noise, 5),
            "noise_ratio": round(observed / noise, 3) if noise else None, "noise_model": noise_kind}


split_rows = [r for r in ROWS if r["season"] in SPLIT_DEV]
# Use the same total() helper for the event-derived goal half as for stat markets.
for row in split_rows:
    row["ht_goals_home"] = row["ht_home_goals"]
    row["ht_goals_away"] = row["ht_away_goals"]
    row["goals_home"] = row["home_goals"]
    row["goals_away"] = row["away_goals"]
halves = {
    "goals": half_stats(split_rows, "goals", "ht_goals", "goals"),
    "sot": half_stats(split_rows, "sot", "fh_ShotsOnTarget", "ShotsOnTarget"),
    "corners": half_stats(split_rows, "corners", "fh_corners", "corners"),
    "total_shots": half_stats(split_rows, "total_shots", "fh_total_shots", "total_shots"),
    "yellow_cards": half_stats(split_rows, "yellow_cards", "fh_yellow_cards", "yellow_cards"),
    "definition": "2022/2023 rows with splits plus complete 2023/2024 and 2024/2025; goals use HT events.",
}


def team_goal_record(rows, season, team_id):
    gf, ga = [], []
    for row in rows:
        if row["season"] != season:
            continue
        if str(row["home_id"]) == str(team_id):
            gf.append(row["home_goals"]); ga.append(row["away_goals"])
        elif str(row["away_id"]) == str(team_id):
            gf.append(row["away_goals"]); ga.append(row["home_goals"])
    return {"matches": len(gf), "gf_per_match": avg(gf), "ga_per_match": avg(ga)}


t1_teams = {s: {str(r[k]) for r in ROWS if r["season"] == s for k in ("home_team_id", "away_team_id")} for s in SEASONS}
league_goal_mean = {s: avg([int(r[k]) for r in ROWS if r["season"] == s for k in ("home_goals", "away_goals")]) for s in SEASONS}
movers = []
for i, season in enumerate(SEASONS[1:], 1):
    prior = SEASONS[i - 1]
    for team_id in sorted(t1_teams[season] - t1_teams[prior]):
        current = team_goal_record([{"season": r["season"], "home_id": r["home_team_id"], "away_id": r["away_team_id"],
                                     "home_goals": int(r["home_goals"]), "away_goals": int(r["away_goals"])} for r in ROWS], season, team_id)
        name = next((r["home_team"] if str(r["home_team_id"]) == team_id else r["away_team"] for r in ROWS
                     if r["season"] == season and team_id in (str(r["home_team_id"]), str(r["away_team_id"]))), team_id)
        entry = {"season": season, "team_id": team_id, "team": name,
                 "direction": "entrant", "first_t1": current,
                 "gap_vs_t1_mean": {"gf": round(current["gf_per_match"] - league_goal_mean[season], 3),
                                     "ga": round(current["ga_per_match"] - league_goal_mean[season], 3)}}
        entry["previous_tier"] = "not_observed_no_tier2_in_warehouse"
        movers.append(entry)
mover_groups = {}
for group in sorted({m["previous_tier"] for m in movers}):
    selected = [m for m in movers if m["previous_tier"] == group]
    mover_groups[group] = {"n": len(selected), "gf_gap_mean": avg([m["gap_vs_t1_mean"]["gf"] for m in selected]),
                           "ga_gap_mean": avg([m["gap_vs_t1_mean"]["ga"] for m in selected]),
                           "first_t1_gf_mean": avg([m["first_t1"]["gf_per_match"] for m in selected]),
                           "first_t1_ga_mean": avg([m["first_t1"]["ga_per_match"] for m in selected])}


def cards_artifact(rows):
    out = {}
    for season in SEASONS:
        selected = [r for r in rows if r["season"] == season and total(r, "yellow_cards") is not None]
        event_values = [int(r["ev_yellow_home"]) + int(r["ev_yellow_away"]) for r in selected]
        stats_values = [total(r, "yellow_cards") for r in selected]
        team_agreements = sum(f(r, "yellow_cards_home") == int(r["ev_yellow_home"]) for r in selected)
        team_agreements += sum(f(r, "yellow_cards_away") == int(r["ev_yellow_away"]) for r in selected)
        plain_yellow = sum(int(r[event_card]) for r in rows if r["season"] == season
                           for event_card in ("ev_yellow_direct_home", "ev_yellow_direct_away"))
        out[season] = {"stats_n": len(selected), "stats_mean": avg(stats_values), "event_unified_mean": avg(event_values),
                       "exact_agreement_rate_team_matches": round(team_agreements / (2 * len(selected)), 3) if selected else None,
                       "plain_yellow_event_count": plain_yellow}
    return out


dev_rows = [r for r in ROWS if r["season"] in STATS_DEV]
line_tables = {}
for name, key, lines in (("sot", "ShotsOnTarget", [8.5, 9.5, 10.5]), ("corners", "corners", [8.5, 9.5, 10.5]),
                         ("cards", "yellow_cards", [3.5, 4.5, 5.5]), ("total_shots", "total_shots", [24.5, 25.5, 26.5, 27.5, 28.5])):
    vals = market_values(dev_rows, key)
    line_tables[name] = {"candidate_lines": rates(vals, lines), "primary_line": min(lines, key=lambda x: abs((sum(v > x for v in vals) / len(vals)) - 0.5)), "n": len(vals)}
line_tables["goals"] = {"candidate_lines": rates([goals_total(r) for r in ROWS if r["season"] in GOALS_DEV], [2.5]),
                        "primary_line": 2.5, "n": sum(r["season"] in GOALS_DEV for r in ROWS)}


name_sets = defaultdict(set)
for row in ROWS:
    name_sets[str(row["home_team_id"])].add(row["home_team"])
    name_sets[str(row["away_team_id"])].add(row["away_team"])
multi_name_teams = {team_id: sorted(names) for team_id, names in name_sets.items() if len(names) > 1}


inventory = {"league": "ZA-PSL", "league_id": "537", "rows": len(ROWS), "team_rows": len(ROWS) * 2,
             "seasons": per_season, "distinct_team_ids": len({r[k] for r in ROWS for k in ("home_team_id", "away_team_id")}),
             "multi_name_team_ids": multi_name_teams,
             "phase_values": sorted({r["phase"] for r in ROWS}), "cards_source_counts": {k: sum(r["cards_source"] == k for r in ROWS) for k in ("stats", "none")},
             "dev_definitions": {"goals": sorted(GOALS_DEV), "stats_markets": sorted(STATS_DEV), "split_halves": sorted(SPLIT_DEV)},
             "virgin": VIRGIN, "confirmatory": CONFIRMATORY}

out = {"league": "ZA-PSL", "league_id": "537", "n": len(ROWS), "seasons": SEASONS,
       "per_season": per_season, "pooled_levels": levels(ROWS), "pooled_dev_levels": levels(dev_rows),
       "reliability": reliability_dev, "referee_reliability": ref_reliability,
       "halves": halves, "movers": movers, "mover_groups": mover_groups,
       "cards_artifact": cards_artifact(ROWS), "dev_line_tables": line_tables,
       "windows": {"goals_dev": sorted(GOALS_DEV), "stats_market_dev": sorted(STATS_DEV), "virgin": VIRGIN, "confirmatory": CONFIRMATORY,
                   "split_half_reliability": sorted(GOALS_DEV), "halves": sorted(SPLIT_DEV)},
       "inventory": inventory}
(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=2) + "\n")
(HERE / "inventory_summary.json").write_text(json.dumps(inventory, indent=2) + "\n")
print(json.dumps({"n": out["n"], "seasons": out["seasons"], "dev_lines": out["dev_line_tables"],
                  "reliability": out["reliability"], "halves": out["halves"], "mover_groups": out["mover_groups"]}, indent=2))
