"""Measured Phase A EDA for Poland II Liga (FotMob 8935).

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
ROWS = list(csv.DictReader((HERE.parent / "data" / "plii_matches.csv").open()))
random.seed(42)

SIBLING = ROOT.parent / "footballprediction"

def read_payload(index_row):
    path = ROOT / index_row["path"]
    if not path.exists():
        path = SIBLING / index_row["path"]
    return json.loads(path.read_text())


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

def season_trait_split(against=False):
    pairs = []
    for season in sorted({r["season"] for r in ROWS}):
        by = defaultdict(list)
        for r in ROWS:
            if r["season"] != season: continue
            for side, other in (("home", "away"), ("away", "home")):
                by[r[f"{side}_team_id"]].append((r["date"], int(r[f"{other}_goals"] if against else r[f"{side}_goals"])))
        for series in by.values():
            series.sort()
            if len(series) < 20: continue
            a = [v for i, (_, v) in enumerate(series) if i % 2 == 0]
            b = [v for i, (_, v) in enumerate(series) if i % 2 == 1]
            pairs.append((st.mean(a), st.mean(b)))
    return {"r": corr([a for a, b in pairs], [b for a, b in pairs]), "n": len(pairs)}


def ht_share_stats(rows):
    shares, weights, num, den = [], [], 0, 0
    validated_n = 0
    for r in rows:
        if r["ht_validated"] != "1":
            continue
        validated_n += 1
        total = int(r["home_goals"]) + int(r["away_goals"])
        ht = int(r["ht_home_goals"]) + int(r["ht_away_goals"])
        if total == 0:
            continue
        shares.append(ht / total)
        weights.append(total)
        num += ht
        den += total
    if len(shares) < 30:
        return {"n": validated_n}
    observed = st.variance(shares)
    p = st.mean(shares)
    noise = st.mean([p * (1 - p) / w for w in weights])
    return {"n": validated_n, "share_ratio_of_sums": round(num / den, 4),
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
    "n_validated": sum(r["ht_validated"] == "1" and r["has_events"] == "1" for r in ROWS),
    "n_mismatch": sum(r["ht_validated"] == "0" and r["has_events"] == "1" for r in ROWS),
    "n_no_events": sum(r["has_events"] == "0" for r in ROWS),
    "no_events_0_0": sum(r["has_events"] == "0" and int(r["home_goals"]) == 0 and int(r["away_goals"]) == 0 for r in ROWS),
}

# Goals trait reliability: date odd/even split by team-season.
out["reliability"] = {}
out["reliability_nteams"] = {}
for name, against in (("goals_for", False), ("goals_against", True)):
    result = season_trait_split(against)
    out["reliability"][name], out["reliability_nteams"][name] = result["r"], result["n"]

# Halves: goals only, validated event subset, all complete seasons.
out["half_shares"] = {"goals": ht_share_stats([r for r in ROWS if r["season"] != "2026/2027"])}
out["half_shares_by_season"] = {s: ht_share_stats([r for r in ROWS if r["season"] == s]) for s in seasons}

# Newcomers, split by origin. Prior-season I Liga membership comes from its
# warehouse payloads (FotMob 197), not memory or display names.
sl1_teams = {}
index = list(csv.DictReader((ROOT / "data_enrichment" / "fotmob_world_index.csv").open()))
for r in index:
    if r["league_id"] != "197":
        continue
    d = read_payload(r)
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
        season_rows = [r for r in ROWS if r["season"] == season]
        season_mean_gf = sum(int(r[f"{side}_goals"]) for r in season_rows for side in ("home", "away")) / (2 * len(season_rows))
        newcomers.append({"season": season, "team_id": team, "team": id2name.get(team), "season_lg_gf": season_mean_gf, "season_lg_ga": season_mean_gf,
                          "n": len(matches), "gf": mean([x[0] for x in matches]),
                          "ga": mean([x[1] for x in matches]),
                          "origin": "I-Liga-relegated" if team in sl1_teams.get(seasons[i - 1], set()) else "from-below"})
league_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in ROWS for side, other in (("home", "away"), ("away", "home"))]
lg_gf, lg_ga = mean([x[0] for x in league_team_rows]), mean([x[1] for x in league_team_rows])
out["newcomers"] = newcomers
def gap(group):
    if not group:
        return {"n": 0}
    return {"n": len(group), "gf": mean([x["gf"] for x in group]), "ga": mean([x["ga"] for x in group]),
            "gf_gap": round(mean([x["gf"] - x["season_lg_gf"] for x in group]), 3),
            "ga_gap": round(mean([x["ga"] - x["season_lg_ga"] for x in group]), 3)}
out["newcomer_gaps"] = {"league_team_gf": lg_gf, "league_team_ga": lg_ga,
                        "all_complete": gap([x for x in newcomers if x["season"] != "2026/2027"]),
                        "i_liga_relegated_complete": gap([x for x in newcomers if x["season"] != "2026/2027" and x["origin"] == "I-Liga-relegated"]),
                        "from_below_complete": gap([x for x in newcomers if x["season"] != "2026/2027" and x["origin"] != "I-Liga-relegated"]),
                        "dev_transitions": gap([x for x in newcomers if x["season"] in ("2022/2023", "2023/2024", "2024/2025")]),
                        "dev_i_liga_relegated": gap([x for x in newcomers if x["season"] in ("2022/2023", "2023/2024", "2024/2025") and x["origin"] == "I-Liga-relegated"])}
out["newcomer_gaps"]["by_transition"] = {}
for season in seasons[1:]:
    group = [x for x in newcomers if x["season"] == season]
    if group:
        out["newcomer_gaps"]["by_transition"][season] = gap(group)

# B-team sensitivity: B teams' own scoring, and B-involved match levels.
complete = [r for r in ROWS if r["season"] != "2026/2027"]
b_rows = []
nb_rows = []
for r in ROWS:
    if r["season"] == "2026/2027":
        continue
    (b_rows if (r["is_b_home"] == "1" or r["is_b_away"] == "1") else nb_rows).append(r)
b_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in complete for side, other in (("home", "away"), ("away", "home")) if r[f"is_b_{side}"] == "1"]
nb_team_rows = [(int(r[f"{side}_goals"]), int(r[f"{other}_goals"])) for r in complete for side, other in (("home", "away"), ("away", "home")) if r[f"is_b_{side}"] == "0"]
out["b_team"] = {
    "matches_involving_b": len(b_rows), "pct": round(100 * len(b_rows) / len(complete), 1),
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
    "league_id": 8935, "n_index_rows": out["n"], "n_match_rows": out["n"],
    "n_team_match_rows": out["n"] * 2, "seasons": out["per_season"],
    "phase_rule": "phase from general.leagueName; all phases ordinary rows in every fit/window; no phase feature; B teams kept as ordinary teams",
    "phase_levels": out["phase_levels"],
    "event_goal_validation": out["event_goal_validation"],
    "stats_xg_era": [], "shotmap_xg_era": [], "xgot_era": [],
}, indent=2) + "\n")
print(json.dumps(out, indent=2))
