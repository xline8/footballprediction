"""Descriptive EDA for the Uzbekistan Superliga scores-only table."""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE.parent / "data" / "uz_superliga_matches.csv"
OUT_PATH = HERE / "eda_summary.json"


def pearson(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return None if not den else round(num / den, 6)


def rate(n, d):
    return round(n / d, 6)


def main():
    with CSV_PATH.open(newline="") as fh:
        ms = list(csv.DictReader(fh))
    for m in ms:
        for k in ("round", "home_goals", "away_goals", "total_goals"):
            m[k] = int(m[k])
    n = len(ms)
    result_counts = Counter(m["result"] for m in ms)
    totals = Counter(min(m["total_goals"], 6) for m in ms)
    teams = defaultdict(lambda: {"gf": 0, "ga": 0, "matches": 0})
    halves = {"first": defaultdict(lambda: {"gf": 0, "ga": 0, "matches": 0}),
              "second": defaultdict(lambda: {"gf": 0, "ga": 0, "matches": 0})}
    rounds = defaultdict(list)
    for m in ms:
        teams[m["home"]]["gf"] += m["home_goals"]; teams[m["home"]]["ga"] += m["away_goals"]; teams[m["home"]]["matches"] += 1
        teams[m["away"]]["gf"] += m["away_goals"]; teams[m["away"]]["ga"] += m["home_goals"]; teams[m["away"]]["matches"] += 1
        rounds[m["round"]].append(m["total_goals"])
        half = "first" if m["round"] <= 13 else "second"
        for side, other in (("home", "away"), ("away", "home")):
            h = halves[half][m[side]]
            h["gf"] += m[f"{side}_goals"]; h["ga"] += m[f"{other}_goals"]; h["matches"] += 1
    team_rates = {
        t: {"matches": d["matches"], "gf_per_match": rate(d["gf"], d["matches"]), "ga_per_match": rate(d["ga"], d["matches"])}
        for t, d in sorted(teams.items())
    }
    reliability = {}
    for metric in ("gf", "ga"):
        first = [halves["first"][t][metric] / halves["first"][t]["matches"] for t in sorted(teams)]
        second = [halves["second"][t][metric] / halves["second"][t]["matches"] for t in sorted(teams)]
        reliability[f"{metric}_per_match"] = {"pearson_r": pearson(first, second), "n_teams": len(first), "split": "rounds 1-13 vs 14-27"}
    levels = {
        "n": n, "total_goals": sum(m["total_goals"] for m in ms),
        "goals_per_match": rate(sum(m["total_goals"] for m in ms), n),
        "home_goals_per_match": rate(sum(m["home_goals"] for m in ms), n),
        "away_goals_per_match": rate(sum(m["away_goals"] for m in ms), n),
        "home_win_rate": rate(result_counts["H"], n), "draw_rate": rate(result_counts["D"], n), "away_win_rate": rate(result_counts["A"], n),
        "over_1_5_rate": rate(sum(m["total_goals"] >= 2 for m in ms), n),
        "over_2_5_rate": rate(sum(m["total_goals"] >= 3 for m in ms), n),
        "over_3_5_rate": rate(sum(m["total_goals"] >= 4 for m in ms), n),
        "btts_rate": rate(sum(m["home_goals"] > 0 and m["away_goals"] > 0 for m in ms), n),
        "home_clean_sheet_rate": rate(sum(m["away_goals"] == 0 for m in ms), n),
        "away_clean_sheet_rate": rate(sum(m["home_goals"] == 0 for m in ms), n),
        "goal_distribution": {str(k): totals.get(k, 0) for k in range(7)},
    }
    # Halftime share, from the HT columns build_data.py derives from the
    # matchFacts Half event (partial coverage: 99/215, rounds 10, 14-27).
    # Descriptive only; NOT frozen as a constant (coverage is late-season
    # only and nothing ships under this verdict).
    ht_rows = [m for m in ms if m.get("home_goals_ht") not in (None, "")]
    ht_goals = sum(int(m["home_goals_ht"]) + int(m["away_goals_ht"]) for m in ht_rows)
    ht_ft_goals = sum(m["total_goals"] for m in ht_rows)
    halftime_share = {
        "n_matches_with_ht": len(ht_rows),
        "rounds_covered": sorted({m["round"] for m in ht_rows}),
        "ht_goals": ht_goals,
        "ft_goals_same_matches": ht_ft_goals,
        "ht_share_of_goals": round(ht_goals / ht_ft_goals, 6) if ht_ft_goals else None,
        "ht_goals_per_match": round(ht_goals / len(ht_rows), 6) if ht_rows else None,
        "coverage_note": "HT scores derivable only where the matchFacts Half event exists (99/215, rounds 10 and 14-27); not a frozen constant",
    }
    summary = {
        "league": "UZ-Superliga", "season": "2026", "scope": "descriptive scores-only EDA", "levels": levels,
        "team_attack_defence": team_rates, "split_half_reliability": reliability,
        "round_goals_per_match": {str(r): {"matches": len(v), "goals": sum(v), "goals_per_match": rate(sum(v), len(v))} for r, v in sorted(rounds.items())},
        "halftime_share": halftime_share,
        "absent_targets": ["shots", "shots on target", "corners", "cards", "xG", "referee effects"],
        "reference_points": {"J1_goals_per_match": 2.55, "J1_goals_per_match_label": "J1 EDA.md levels table, pooled (n=2,091)", "J1_home_win_rate": 0.413, "J1_draw_rate": 0.268, "J1_away_win_rate": 0.319, "J1_over_2_5_rate": 0.470, "J1_btts_rate": 0.504},
    }
    OUT_PATH.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {OUT_PATH}")
    print(json.dumps(levels, indent=2))
    print(json.dumps(reliability, indent=2))


if __name__ == "__main__":
    main()
