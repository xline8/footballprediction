"""Measured Stage 1 EDA for PL-Ekstraklasa.

All figures used by the accompanying documents are emitted here.  No model is
fit and no dev/virgin prediction is evaluated in this script.
"""
import csv
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "pl_matches.csv").open()))
random.seed(42)


def f(row, key):
    value = row.get(key)
    return None if value in (None, "", "None") else float(value)


def mean(values):
    return round(st.mean(values), 3) if values else None


def corr(xs, ys):
    if len(xs) < 5:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den, 3) if den else None


def split_half(series, min_n=20, reps=60):
    eligible = {team: values for team, values in series.items() if len(values) >= min_n}
    values = []
    for _ in range(reps):
        first, second = [], []
        for sample in eligible.values():
            indices = list(range(len(sample))); random.shuffle(indices)
            cut = len(indices) // 2
            first.append(st.mean([sample[i] for i in indices[:cut]]))
            second.append(st.mean([sample[i] for i in indices[cut:]]))
        result = corr(first, second)
        if result is not None: values.append(result)
    return (round(st.mean(values), 3), len(eligible)) if values else (None, 0)


def split_ratio(series, min_n=20, reps=60):
    eligible = {team: pairs for team, pairs in series.items() if len(pairs) >= min_n}
    values = []
    for _ in range(reps):
        first, second = [], []
        for sample in eligible.values():
            indices = list(range(len(sample))); random.shuffle(indices)
            cut = len(indices) // 2
            for indices_part, target in ((indices[:cut], first), (indices[cut:], second)):
                numerator = sum(sample[i][0] for i in indices_part)
                denominator = sum(sample[i][1] for i in indices_part)
                if denominator: target.append(numerator / denominator)
        result = corr(first, second)
        if result is not None: values.append(result)
    return (round(st.mean(values), 3), len(eligible)) if values else (None, 0)


def team_series(key, against=False, seasons=None):
    result = defaultdict(list)
    for row in ROWS:
        if seasons and row["season"] not in seasons: continue
        for side, other in (("home", "away"), ("away", "home")):
            value = f(row, f"{key}_{other if against else side}")
            if value is not None: result[row[f"{side}_team_id"]].append(value)
    return result


def team_pairs(numerator, denominator, seasons=None, shotmap=False):
    result = defaultdict(list)
    for row in ROWS:
        if seasons and row["season"] not in seasons: continue
        for side in ("home", "away"):
            prefix = "sm_" if shotmap else ""
            n, d = f(row, f"{prefix}{numerator}_{side}"), f(row, f"{prefix}{denominator}_{side}")
            if n is not None and d is not None and d > 0: result[row[f"{side}_team_id"]].append((n, d))
    return result


def coverage(rows, key):
    return round(100 * sum(f(row, key) is not None for row in rows) / len(rows), 1) if rows else 0.0


def total_mean(rows, key):
    values = [f(row, f"{key}_home") + f(row, f"{key}_away") for row in rows if f(row, f"{key}_home") is not None and f(row, f"{key}_away") is not None]
    return mean(values)


def half_stats(rows, key):
    shares, weights, numerator, denominator = [], [], 0.0, 0.0
    for row in rows:
        first = [f(row, f"fh_{key}_{side}") for side in ("home", "away")]
        full = [f(row, f"{key}_{side}") for side in ("home", "away")]
        if any(x is None for x in first + full) or sum(full) <= 0: continue
        n, d = sum(first), sum(full)
        shares.append(n / d); weights.append(d); numerator += n; denominator += d
    if len(shares) < 30: return {"n": len(shares)}
    observed = st.variance(shares); p = st.mean(shares)
    noise = st.mean([p * (1 - p) / weight for weight in weights])
    return {"n": len(shares), "share_ratio_of_sums": round(numerator / denominator, 4),
            "observed_var": round(observed, 4), "true_var": round(observed - noise, 4),
            "true_sd": round(math.sqrt(max(0.0, observed - noise)), 4)}


def goal_half_stats(rows):
    shares, weights, numerator, denominator = [], [], [], []
    for row in rows:
        total = int(row["home_goals"]) + int(row["away_goals"])
        ht = int(row["ht_home_goals"]) + int(row["ht_away_goals"])
        if total: shares.append(ht / total); weights.append(total); numerator.append(ht); denominator.append(total)
    if len(shares) < 30: return {"n": len(shares)}
    observed = st.variance(shares); p = st.mean(shares)
    noise = st.mean([p * (1 - p) / weight for weight in weights])
    return {"n": len(shares), "share_ratio_of_sums": round(sum(numerator) / sum(denominator), 4),
            "observed_var": round(observed, 4), "true_var": round(observed - noise, 4),
            "true_sd": round(math.sqrt(max(0.0, observed - noise)), 4)}


seasons = sorted({row["season"] for row in ROWS})
out = {"n": len(ROWS), "seasons": seasons,
       "team_ids": len({row[f"{side}_team_id"] for row in ROWS for side in ("home", "away")})}
per = {}
for season in seasons:
    rs = [r for r in ROWS if r["season"] == season]
    per[season] = {
        "n": len(rs), "teams": len({r[f"{s}_team_id"] for r in rs for s in ("home", "away")}),
        "goals": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in rs]),
        "home_goals": mean([int(r["home_goals"]) for r in rs]), "away_goals": mean([int(r["away_goals"]) for r in rs]),
        "sot": total_mean(rs, "ShotsOnTarget"), "corners": total_mean(rs, "corners"),
        "shots": total_mean(rs, "total_shots"), "yellows": total_mean(rs, "yellow"),
        "xg_stats": total_mean(rs, "expected_goals"), "xg_set_play": total_mean(rs, "expected_goals_set_play"),
        "coverage": {"stats_all": round(100 * sum(r["has_stats_all"] == "1" for r in rs) / len(rs), 1),
                     "period_splits": round(100 * sum(r["has_stats_half"] == "1" for r in rs) / len(rs), 1),
                     "referee": round(100 * sum(bool(r["referee"]) for r in rs) / len(rs), 1),
                     "box_touches": coverage(rs, "touches_opp_box_home"),
                     "stats_xg": coverage(rs, "expected_goals_home"),
                     "stats_xg_set_play": coverage(rs, "expected_goals_set_play_home"),
                     "shotmap": round(100 * sum(r["has_shotmap"] == "1" for r in rs) / len(rs), 1),
                     "shotmap_xg": round(100 * sum(f(r, "sm_xg_home") is not None and f(r, "sm_xg_away") is not None and r["has_shotmap"] == "1" for r in rs) / len(rs), 1)},
    }
out["per_season"] = per

# Cards comparison is deliberately independent of the unified target.
card_rows = [r for r in ROWS if f(r, "yellow_cards_home") is not None and r["has_events"] == "1"]
diffs = [(f(r, "yellow_cards_home") + f(r, "yellow_cards_away")) - int(r["ev_yellow_home"]) - int(r["ev_yellow_away"]) for r in card_rows]
out["cards_check"] = {"n": len(card_rows), "exact_agree_pct": round(100 * sum(d == 0 for d in diffs) / len(diffs), 1),
                       "stats_lower_pct": round(100 * sum(d < 0 for d in diffs) / len(diffs), 1),
                       "stats_higher_pct": round(100 * sum(d > 0 for d in diffs) / len(diffs), 1),
                       "mean_stats_minus_events": round(st.mean(diffs), 3), "max_abs_diff": max(abs(d) for d in diffs),
                       "unified_target": "stats yellow_cards, events fallback when stats card absent"}
diffs_yellowred = [(f(r, "yellow_cards_home") + f(r, "yellow_cards_away")) - int(r["ev_yellow_home"]) - int(r["ev_yellow_away"]) - int(r["ev_yellowred_home"]) - int(r["ev_yellowred_away"]) for r in card_rows]
out["cards_check"]["exact_agree_including_yellowred_pct"] = round(100 * sum(d == 0 for d in diffs_yellowred) / len(diffs_yellowred), 1)

# Reliability: career-pooled random half split, with ratio traits as ratios of sums.
reliability = {}
for name, key, against in [("goals_for", None, False), ("goals_against", None, True),
                            ("sot_for", "ShotsOnTarget", False), ("sot_against", "ShotsOnTarget", True),
                            ("corners_for", "corners", False), ("corners_against", "corners", True),
                            ("yellows_for", "yellow", False), ("yellows_against", "yellow", True),
                            ("shots_for", "total_shots", False), ("shots_against", "total_shots", True),
                            ("box_touches_for", "touches_opp_box", False), ("box_touches_against", "touches_opp_box", True),
                            ("possession", "BallPossesion", False), ("big_chances", "big_chance", False)]:
    if key is None:
        values = defaultdict(list)
        for r in ROWS:
            values[r["home_team_id"]].append(int(r["home_goals"]) if not against else int(r["away_goals"]))
            values[r["away_team_id"]].append(int(r["away_goals"]) if not against else int(r["home_goals"]))
    else:
        values = team_series(key, against)
    reliability[name], _ = split_half(values)
out["reliability"] = reliability
out["reliability_nteams"] = {}
for name, key, against in [("goals_for", None, False), ("goals_against", None, True),
                            ("sot_for", "ShotsOnTarget", False), ("sot_against", "ShotsOnTarget", True),
                            ("corners_for", "corners", False), ("corners_against", "corners", True),
                            ("yellows_for", "yellow", False), ("yellows_against", "yellow", True),
                            ("shots_for", "total_shots", False), ("shots_against", "total_shots", True),
                            ("box_touches_for", "touches_opp_box", False), ("box_touches_against", "touches_opp_box", True),
                            ("possession", "BallPossesion", False), ("big_chances", "big_chance", False)]:
    if key is None:
        values = defaultdict(list)
        for r in ROWS:
            values[r["home_team_id"]].append(int(r["home_goals"]) if not against else int(r["away_goals"]))
            values[r["away_team_id"]].append(int(r["away_goals"]) if not against else int(r["home_goals"]))
    else:
        values = team_series(key, against)
    out["reliability_nteams"][name] = split_half(values)[1]

# xG-for is an era-aware reliability check, not an all-corpus number.
xg_era = {s for s in seasons if per[s]["coverage"]["stats_xg"] > 0}
out["stats_xg_era"] = sorted(xg_era)
out["stats_xg_reliability"], out["stats_xg_reliability_nteams"] = split_half(team_series("expected_goals", seasons=xg_era))
out["stats_xg_set_play_reliability"], out["stats_xg_set_play_reliability_nteams"] = split_ratio(team_pairs("expected_goals_set_play", "expected_goals", seasons=xg_era))

ref_series = defaultdict(list)
for r in ROWS:
    if r["referee"] and f(r, "yellow_home") is not None and f(r, "yellow_away") is not None:
        ref_series[r["referee"]].append(f(r, "yellow_home") + f(r, "yellow_away"))
out["referee_reliability"], out["referee_reliability_nrefs"] = split_half(ref_series)
out["referee_count"] = len(ref_series)

for name, numerator, denominator, seasons_filter, shotmap in [
    ("stats_xg_per_shot", "expected_goals", "total_shots", None, False),
    ("shotmap_xg_per_shot", "xg", "shots", None, True),
    ("xgot_per_shot", "xgot", "shots", None, True),
    ("set_play_xg_share", "expected_goals_set_play", "expected_goals", None, False),
    ("on_target_rate", "sot", "shots", None, True),
]:
    if shotmap:
        pairs = defaultdict(list)
        for r in ROWS:
            for side in ("home", "away"):
                nkey = {"xg": "sm_xg", "xgot": "sm_xgot", "sot": "sm_sot"}[numerator]
                n, d = f(r, f"{nkey}_{side}"), f(r, f"sm_{denominator}_{side}")
                if n is not None and d and d > 0: pairs[r[f"{side}_team_id"]].append((n, d))
    else:
        pairs = team_pairs(numerator, denominator, seasons_filter)
    if name == "shotmap_xg_per_shot":
        valid_seasons = {s for s in seasons if per[s]["coverage"]["shotmap_xg"] > 50}
        pairs = defaultdict(list)
        for r in ROWS:
            if r["season"] not in valid_seasons: continue
            for side in ("home", "away"):
                n, d = f(r, f"sm_xg_{side}"), f(r, f"sm_shots_{side}")
                if n is not None and d and d > 0: pairs[r[f"{side}_team_id"]].append((n, d))
        out["shotmap_xg_era"] = sorted(valid_seasons)
    if name == "xgot_per_shot":
        valid_seasons = {s for s in seasons if sum((f(r, "sm_xgot_n_home") or 0) + (f(r, "sm_xgot_n_away") or 0) for r in ROWS if r["season"] == s) / max(1, sum((f(r, "sm_shots_home") or 0) + (f(r, "sm_shots_away") or 0) for r in ROWS if r["season"] == s)) > .9}
        pairs = defaultdict(list)
        for r in ROWS:
            if r["season"] not in valid_seasons: continue
            for side in ("home", "away"):
                n, d = f(r, f"sm_xgot_{side}"), f(r, f"sm_xgot_n_{side}")
                if n is not None and d and d > 0: pairs[r[f"{side}_team_id"]].append((n, d))
        out["xgot_era"] = sorted(valid_seasons)
    out.setdefault("ratio_reliability", {})[name], nteams = split_ratio(pairs, min_n=10 if name == "xgot_per_shot" else 20)
    out.setdefault("ratio_reliability_nteams", {})[name] = nteams

# Half shares: content, not index flags, determine the complete era.
complete_half_seasons = [s for s in seasons if s != "2026/2027" and per[s]["coverage"]["period_splits"] >= 90]
out["half_complete_seasons"] = complete_half_seasons
half_rows = [r for r in ROWS if r["season"] in complete_half_seasons]
out["half_shares"] = {key: half_stats(half_rows, key) for key in ("ShotsOnTarget", "corners", "total_shots", "yellow_cards")}
out["half_shares"]["goals"] = goal_half_stats(half_rows)
out["half_shares"]["xg_stats"] = half_stats(half_rows, "expected_goals")

# Newcomers: same-league season-entry contrast, NL convention.
season_teams = {s: {r[f"{side}_team_id"] for r in ROWS if r["season"] == s for side in ("home", "away")} for s in seasons}
newcomers = []
for i, season in enumerate(seasons[1:], 1):
    prior = season_teams[seasons[i - 1]]
    for team in sorted(season_teams[season] - prior):
        matches = []
        for r in ROWS:
            if r["season"] != season: continue
            if r["home_team_id"] == team: matches.append((int(r["home_goals"]), int(r["away_goals"])))
            elif r["away_team_id"] == team: matches.append((int(r["away_goals"]), int(r["home_goals"])))
        newcomers.append({"season": season, "team_id": team, "n": len(matches), "gf": mean([x[0] for x in matches]), "ga": mean([x[1] for x in matches])})
league_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in ROWS for side, other in (("home", "away"), ("away", "home"))]
out["newcomers"] = newcomers
out["newcomer_gaps"] = {"n": len(newcomers), "expected_per_transition": 3,
                         "newcomer_gf": mean([x["gf"] for x in newcomers]), "newcomer_ga": mean([x["ga"] for x in newcomers]),
                         "league_team_gf": mean([x[0] for x in league_team_rows]), "league_team_ga": mean([x[1] for x in league_team_rows]),
                         "gf_gap": round(mean([x["gf"] for x in newcomers]) - mean([x[0] for x in league_team_rows]), 3),
                         "ga_gap": round(mean([x["ga"] for x in newcomers]) - mean([x[1] for x in league_team_rows]), 3)}
out["newcomer_gaps"]["by_transition"] = {}
for season in seasons[1:]:
    group = [x for x in newcomers if x["season"] == season]
    if group:
        out["newcomer_gaps"]["by_transition"][season] = {"n": len(group), "gf": mean([x["gf"] for x in group]), "ga": mean([x["ga"] for x in group])}

# Derived descriptive traits and primary count lines.
complete = [r for r in ROWS if r["season"] != "2026/2027"]
out["finishing"] = {s: round(sum(int(r["home_goals"]) + int(r["away_goals"]) for r in ROWS if r["season"] == s) / sum(f(r, "expected_goals_home") + f(r, "expected_goals_away") for r in ROWS if r["season"] == s and f(r, "expected_goals_home") is not None), 3) for s in seasons if any(f(r, "expected_goals_home") is not None for r in ROWS if r["season"] == s)}
out["on_target_rate"] = {s: round(sum((f(r, "ShotsOnTarget_home") or 0) + (f(r, "ShotsOnTarget_away") or 0) for r in ROWS if r["season"] == s) / sum((f(r, "total_shots_home") or 0) + (f(r, "total_shots_away") or 0) for r in ROWS if r["season"] == s), 3) for s in seasons}
out["pooled_complete"] = {"n": len(complete), "home_goals": mean([int(r["home_goals"]) for r in complete]), "away_goals": mean([int(r["away_goals"]) for r in complete]), "goals": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in complete]), "home_win_pct": round(100 * sum(int(r["home_goals"]) > int(r["away_goals"]) for r in complete) / len(complete), 1), "draw_pct": round(100 * sum(int(r["home_goals"]) == int(r["away_goals"]) for r in complete) / len(complete), 1), "away_win_pct": round(100 * sum(int(r["home_goals"]) < int(r["away_goals"]) for r in complete) / len(complete), 1)}

dev = [r for r in ROWS if r["season"] in ("2021/2022", "2022/2023", "2023/2024", "2024/2025")]
def over(key, line):
    values = [f(r, f"{key}_home") + f(r, f"{key}_away") for r in dev if f(r, f"{key}_home") is not None]
    return {"n": len(values), "over_rate": round(sum(v > line for v in values) / len(values), 3)}
out["dev_over_rates"] = {"goals": over("goals", 2.5) if False else {"n": len(dev), "over_rate": round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in dev) / len(dev), 3)}, "sot": {str(x): over("ShotsOnTarget", x) for x in (8.5, 9.5, 10.5)}, "corners": {str(x): over("corners", x) for x in (9.5, 10.5, 11.5)}, "yellows": {str(x): over("yellow", x) for x in (3.5, 4.5, 5.5)}, "shots": {str(x): over("total_shots", x) for x in (25.5, 26.5, 27.5)}}
out["dev_n"] = len(dev); out["virgin_n"] = per["2025/2026"]["n"]; out["confirmatory_n"] = per["2026/2027"]["n"]

(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=2) + "\n")
(HERE / "inventory_summary.json").write_text(json.dumps({
    "league_id": 196, "n_index_rows": out["n"], "n_match_rows": out["n"],
    "n_team_match_rows": out["n"] * 2, "seasons": out["per_season"],
    "phase_rule": "regular for every row; no split/play-off phase",
    "cards_check": out["cards_check"], "stats_xg_era": out["stats_xg_era"],
    "shotmap_xg_era": out["shotmap_xg_era"], "xgot_era": out["xgot_era"],
}, indent=2) + "\n")
print(json.dumps(out, indent=2))
