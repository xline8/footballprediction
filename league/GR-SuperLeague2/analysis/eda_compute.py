"""Measured Stage 1 EDA for GR-SuperLeague2 (FotMob 8815).

Scores-only league: no stats, no shotmap, no referee in any payload, so
every reliability / level figure here is goals-only (plus event-feed
counts, which are descriptive only — no cards/SOT/corners/shots target
exists). No model is fit and no dev/virgin prediction is evaluated.
"""
import csv
import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROWS = list(csv.DictReader((HERE.parent / "data" / "gr2_matches.csv").open()))
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
            indices = list(range(len(sample)))
            random.shuffle(indices)
            cut = len(indices) // 2
            first.append(st.mean([sample[i] for i in indices[:cut]]))
            second.append(st.mean([sample[i] for i in indices[cut:]]))
        result = corr(first, second)
        if result is not None:
            values.append(result)
    return (round(st.mean(values), 3), len(eligible)) if values else (None, 0)


def goal_series(against=False):
    values = defaultdict(list)
    for r in ROWS:
        values[r["home_team_id"]].append(int(r["home_goals"]) if not against else int(r["away_goals"]))
        values[r["away_team_id"]].append(int(r["away_goals"]) if not against else int(r["home_goals"]))
    return values


def ht_share_stats(rows):
    shares, weights, num, den = [], [], 0, 0
    for r in rows:
        if r["ht_validated"] != "1":
            continue
        total = int(r["home_goals"]) + int(r["away_goals"])
        ht = int(r["ht_home_goals"]) + int(r["ht_away_goals"])
        if total == 0:
            continue
        shares.append(ht / total)
        weights.append(total)
        num += ht
        den += total
    if len(shares) < 30:
        return {"n": len(shares)}
    observed = st.variance(shares)
    p = st.mean(shares)
    noise = st.mean([p * (1 - p) / w for w in weights])
    return {"n": len(shares), "share_ratio_of_sums": round(num / den, 4),
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
        "home_goals": mean([int(r["home_goals"]) for r in rs]),
        "away_goals": mean([int(r["away_goals"]) for r in rs]),
        "home_win_pct": round(100 * sum(int(r["home_goals"]) > int(r["away_goals"]) for r in rs) / len(rs), 1),
        "draw_pct": round(100 * sum(int(r["home_goals"]) == int(r["away_goals"]) for r in rs) / len(rs), 1),
        "away_win_pct": round(100 * sum(int(r["home_goals"]) < int(r["away_goals"]) for r in rs) / len(rs), 1),
        "ou25_over_rate": round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in rs) / len(rs), 3),
        "events_pct": round(100 * sum(r["has_events"] == "1" for r in rs) / len(rs), 1),
        "ht_validated_pct": round(100 * sum(r["ht_validated"] == "1" for r in rs) / len(rs), 1),
        "b_team_match_pct": round(100 * sum(r["is_b_home"] == "1" or r["is_b_away"] == "1" for r in rs) / len(rs), 1),
        "b_teams": len({r[f"{s}_team_id"] for r in rs for s in ("home", "away")
                        if r[f"is_b_{s}"] == "1"}),
        "awarded_no_events": sum(r["has_events"] == "0" and (int(r["home_goals"]), int(r["away_goals"])) in [(3, 0), (0, 3)] for r in rs),
        "stats_pct": 0.0, "shotmap_pct": 0.0, "referee_pct": 0.0,
    }
out["per_season"] = per

# Phase levels (pooled complete seasons + per season counts).
out["phase_levels"] = {}
for s in seasons:
    out["phase_levels"][s] = {}
    for phase in ("regular", "playoff_promotion", "playoff_relegation", "playoff", "supercup"):
        rs = [r for r in ROWS if r["season"] == s and r["phase"] == phase]
        if rs:
            out["phase_levels"][s][phase] = {"n": len(rs), "goals": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in rs])}
pooled_phase = {}
for phase in ("regular", "playoff_promotion", "playoff_relegation", "playoff", "supercup"):
    rs = [r for r in ROWS if r["season"] != "2026/2027" and r["phase"] == phase]
    if rs:
        pooled_phase[phase] = {"n": len(rs), "goals": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in rs])}
out["phase_levels_pooled_complete"] = pooled_phase

# Event-feed goal validation (HT provenance).
ev_rows = [r for r in ROWS if r["has_events"] == "1"]
out["event_goal_validation"] = {
    "n_events_matches": len(ev_rows),
    "n_validated": sum(r["ht_validated"] == "1" for r in ev_rows),
    "n_mismatch": sum(r["ht_validated"] == "0" for r in ev_rows),
    "n_no_events": sum(r["has_events"] == "0" for r in ROWS),
    "no_events_0_0": sum(r["has_events"] == "0" and int(r["home_goals"]) == 0 and int(r["away_goals"]) == 0 for r in ROWS),
}

# Goals trait reliability (career-pooled split-half).
out["reliability"] = {}
out["reliability_nteams"] = {}
for name, against in (("goals_for", False), ("goals_against", True)):
    out["reliability"][name], out["reliability_nteams"][name] = split_half(goal_series(against))

# Halves: goals only, validated event subset, all complete seasons.
out["half_shares"] = {"goals": ht_share_stats([r for r in ROWS if r["season"] != "2026/2027"])}
out["half_shares_by_season"] = {s: ht_share_stats([r for r in ROWS if r["season"] == s]) for s in seasons}

# Newcomers, split by origin. SL1 membership comes from the SL1 warehouse
# payloads themselves (FotMob 135, general.homeTeam/awayTeam ids).
sl1_teams = {}
index = list(csv.DictReader((ROOT / "data_enrichment" / "fotmob_world_index.csv").open()))
for r in index:
    if r["league_id"] != "135":
        continue
    d = json.loads((ROOT / r["path"]).read_text())
    g = d.get("general") or {}
    sl1_teams.setdefault(r["season"], set()).update(
        [str((g.get("homeTeam") or {}).get("id")), str((g.get("awayTeam") or {}).get("id"))])
season_teams = {s: {r[f"{side}_team_id"] for r in ROWS if r["season"] == s for side in ("home", "away")} for s in seasons}
id2name = {}
for r in ROWS:
    id2name.setdefault(r["home_team_id"], r["home_team"])
    id2name.setdefault(r["away_team_id"], r["away_team"])
newcomers = []
for i, season in enumerate(seasons[1:], 1):
    prior = season_teams[seasons[i - 1]]
    for team in sorted(season_teams[season] - prior):
        matches = []
        for r in ROWS:
            if r["season"] != season:
                continue
            if r["home_team_id"] == team:
                matches.append((int(r["home_goals"]), int(r["away_goals"])))
            elif r["away_team_id"] == team:
                matches.append((int(r["away_goals"]), int(r["home_goals"])))
        newcomers.append({"season": season, "team_id": team, "team": id2name.get(team),
                          "n": len(matches), "gf": mean([x[0] for x in matches]),
                          "ga": mean([x[1] for x in matches]),
                          "origin": "SL1-relegated" if team in sl1_teams.get(seasons[i - 1], set()) else "GammaEthniki/other"})
league_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in ROWS for side, other in (("home", "away"), ("away", "home"))]
lg_gf, lg_ga = mean([x[0] for x in league_team_rows]), mean([x[1] for x in league_team_rows])
out["newcomers"] = newcomers
def gap(group):
    if not group:
        return {"n": 0}
    return {"n": len(group), "gf": mean([x["gf"] for x in group]), "ga": mean([x["ga"] for x in group]),
            "gf_gap": round(mean([x["gf"] for x in group]) - lg_gf, 3),
            "ga_gap": round(mean([x["ga"] for x in group]) - lg_ga, 3)}
out["newcomer_gaps"] = {"league_team_gf": lg_gf, "league_team_ga": lg_ga,
                        "all": gap(newcomers),
                        "sl1_relegated": gap([x for x in newcomers if x["origin"] == "SL1-relegated"]),
                        "gamma_other": gap([x for x in newcomers if x["origin"] != "SL1-relegated"]),
                        "dev_transitions": gap([x for x in newcomers if x["season"] in ("2022/2023", "2023/2024", "2024/2025")]),
                        "dev_sl1_relegated": gap([x for x in newcomers if x["season"] in ("2022/2023", "2023/2024", "2024/2025") and x["origin"] == "SL1-relegated"])}
out["newcomer_gaps"]["by_transition"] = {}
for season in seasons[1:]:
    group = [x for x in newcomers if x["season"] == season]
    if group:
        out["newcomer_gaps"]["by_transition"][season] = gap(group)

# B-team sensitivity: B teams' own scoring, and B-involved match levels.
b_rows = []
nb_rows = []
for r in ROWS:
    (b_rows if (r["is_b_home"] == "1" or r["is_b_away"] == "1") else nb_rows).append(r)
b_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in ROWS for side, other in (("home", "away"), ("away", "home")) if r[f"is_b_{side}"] == "1"]
nb_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in ROWS for side, other in (("home", "away"), ("away", "home")) if r[f"is_b_{side}"] == "0"]
out["b_team"] = {
    "matches_involving_b": len(b_rows), "pct": round(100 * len(b_rows) / len(ROWS), 1),
    "goals_per_match_b_involved": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in b_rows]),
    "goals_per_match_no_b": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in nb_rows]),
    "home_win_pct_b_involved": round(100 * sum(int(r["home_goals"]) > int(r["away_goals"]) for r in b_rows) / len(b_rows), 1),
    "home_win_pct_no_b": round(100 * sum(int(r["home_goals"]) > int(r["away_goals"]) for r in nb_rows) / len(nb_rows), 1),
    "b_team_gf": mean([x[0] for x in b_team_rows]), "b_team_ga": mean([x[1] for x in b_team_rows]),
    "non_b_team_gf": mean([x[0] for x in nb_team_rows]), "non_b_team_ga": mean([x[1] for x in nb_team_rows]),
    "b_team_gf_gap": round(mean([x[0] for x in b_team_rows]) - lg_gf, 3),
    "b_team_ga_gap": round(mean([x[1] for x in b_team_rows]) - lg_ga, 3),
    "b_team_home_gf": mean([int(r["home_goals"]) for r in ROWS if r["is_b_home"] == "1"]),
    "b_team_home_ga": mean([int(r["away_goals"]) for r in ROWS if r["is_b_home"] == "1"]),
    "b_team_away_gf": mean([int(r["away_goals"]) for r in ROWS if r["is_b_away"] == "1"]),
    "b_team_away_ga": mean([int(r["home_goals"]) for r in ROWS if r["is_b_away"] == "1"]),
}

complete = [r for r in ROWS if r["season"] != "2026/2027"]
out["pooled_complete"] = {"n": len(complete),
                          "home_goals": mean([int(r["home_goals"]) for r in complete]),
                          "away_goals": mean([int(r["away_goals"]) for r in complete]),
                          "goals": mean([int(r["home_goals"]) + int(r["away_goals"]) for r in complete]),
                          "home_win_pct": round(100 * sum(int(r["home_goals"]) > int(r["away_goals"]) for r in complete) / len(complete), 1),
                          "draw_pct": round(100 * sum(int(r["home_goals"]) == int(r["away_goals"]) for r in complete) / len(complete), 1),
                          "away_win_pct": round(100 * sum(int(r["home_goals"]) < int(r["away_goals"]) for r in complete) / len(complete), 1),
                          "ou25_over_rate": round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in complete) / len(complete), 3)}
dev = [r for r in ROWS if r["season"] in ("2021/2022", "2022/2023", "2023/2024", "2024/2025")]
scored = [r for r in ROWS if r["season"] in ("2022/2023", "2023/2024", "2024/2025")]
out["dev_over_rates"] = {"goals": {"2.5": {"n": len(dev), "over_rate": round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in dev) / len(dev), 3)}}}
out["scored_dev_over_rates"] = {"goals": {"2.5": {"n": len(scored), "over_rate": round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in scored) / len(scored), 3)}}}
out["primary_lines"] = {"goals": 2.5}
out["dev_n"] = len(dev)
out["scored_dev_n"] = len(scored)
out["virgin_n"] = per["2025/2026"]["n"]
out["confirmatory_n"] = per["2026/2027"]["n"]

(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=2) + "\n")
(HERE / "inventory_summary.json").write_text(json.dumps({
    "league_id": 8815, "n_index_rows": out["n"], "n_match_rows": out["n"],
    "n_team_match_rows": out["n"] * 2, "seasons": out["per_season"],
    "phase_rule": "phase from general.leagueName; all phases ordinary rows in every fit/window; no phase feature; B teams kept as ordinary teams",
    "phase_levels": out["phase_levels"],
    "event_goal_validation": out["event_goal_validation"],
    "stats_xg_era": [], "shotmap_xg_era": [], "xgot_era": [],
}, indent=2) + "\n")
print(json.dumps(out, indent=2))
