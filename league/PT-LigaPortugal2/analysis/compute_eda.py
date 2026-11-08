#!/usr/bin/env python3
"""Compute descriptive EDA for PT-LigaPortugal2; no fitting is performed."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data/pt2_matches.csv"
OUT = Path(__file__).resolve().parent / "eda_summary.json"


def num(x):
    try:
        return float(x) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def pearson(a, b):
    if len(a) < 2:
        return None
    ma, mb = mean(a), mean(b)
    da, db = [x - ma for x in a], [x - mb for x in b]
    den = math.sqrt(sum(x * x for x in da) * sum(x * x for x in db))
    return sum(x * y for x, y in zip(da, db)) / den if den else None


def pair_total(rows, left, right):
    return [num(r[left]) + num(r[right]) for r in rows
            if num(r[left]) is not None and num(r[right]) is not None]


def flag(value):
    return str(value).lower() in {"1", "true", "yes"}


def split_reliability(rows, metric, min_half=10):
    by_team = defaultdict(list)
    for r in rows:
        for side in ("home", "away"):
            value = metric(r, side)
            if value is not None:
                by_team[r[f"{side}_id"]].append((r["date"], int(r["match_id"]), value))
    first, second = [], []
    for values in by_team.values():
        values.sort()
        mid = len(values) // 2
        if mid < min_half or len(values) - mid < min_half:
            continue
        first.append(sum(x[2] for x in values[:mid]) / len(values[:mid]))
        second.append(sum(x[2] for x in values[mid:]) / len(values[mid:]))
    return {"r": pearson(first, second), "n_teams": len(first),
            "min_half_matches": min_half}


def season_levels(rows):
    out = {}
    for season in sorted({r["season"] for r in rows}):
        rs = [r for r in rows if r["season"] == season]
        results = [(num(r["home_goals"]), num(r["away_goals"])) for r in rs]
        goals = [h + a for h, a in results]
        item = {
            "n": len(rs), "teams": len({r["home_id"] for r in rs} | {r["away_id"] for r in rs}),
            "mean_home_goals": mean(h for h, _ in results),
            "mean_away_goals": mean(a for _, a in results),
            "mean_total_goals": mean(goals),
            "home_win_rate": sum(h > a for h, a in results) / len(rs),
            "draw_rate": sum(h == a for h, a in results) / len(rs),
            "away_win_rate": sum(h < a for h, a in results) / len(rs),
            "stats_matches": sum(flag(r["has_stats"]) for r in rs),
            "mean_sot_total": mean(pair_total(rs, "sot_home", "sot_away")),
            "mean_corners_total": mean(pair_total(rs, "corners_home", "corners_away")),
            "mean_total_shots": mean(pair_total(rs, "total_shots_home", "total_shots_away")),
            "mean_event_yellows_total": mean(pair_total(rs, "event_yellows_home", "event_yellows_away")),
            "mean_stats_yellows_total": mean(pair_total(rs, "stats_yellows_home", "stats_yellows_away")),
            "ht_goal_share": (sum(num(r["ht_home"]) + num(r["ht_away"]) for r in rs) / sum(goals)
                              if all(num(r["ht_home"]) is not None and num(r["ht_away"]) is not None for r in rs)
                              and sum(goals) else None),
            "referee_named": sum(bool(r["referee"].strip()) for r in rs),
            "shotmap_shots_positive": sum(num(r["shot_count"]) > 0 for r in rs),
            "period_split_matches": sum(flag(r["has_period_splits"]) for r in rs),
            "expected_goals_matches": sum(flag(r["expected_goals_present"]) for r in rs),
            "card_event_matches": sum(flag(r["has_card_event"]) for r in rs),
            "lineup_matches": sum(flag(r["lineup_present"]) for r in rs),
        }
        out[season] = item
    return out


def mover_measurement(rows):
    """Use only completed/current season content to describe tier transitions."""
    index_path = BASE.parents[1] / "data_enrichment/fotmob_world_index.csv"
    warehouse = Path("/home/hatch/workspace/footballprediction/data_enrichment")
    if not warehouse.exists():
        warehouse = BASE.parents[1] / "data_enrichment"
    matches = {"61": defaultdict(list), "185": defaultdict(list)}
    with open(index_path, newline="") as fh:
        for ix in csv.DictReader(fh):
            if ix["league_id"] not in matches:
                continue
            with open(warehouse.parent / ix["path"]) as pf:
                d = json.load(pf)
            st = (d.get("header") or {}).get("status") or {}
            if not st.get("finished"):
                continue
            teams = (d.get("header") or {}).get("teams") or [{}, {}]
            for side, other in ((0, 1), (1, 0)):
                team = teams[side]
                opp = teams[other]
                matches[ix["league_id"]][ix["season"]].append({
                    "team_id": str(team.get("id", "")), "gf": num(team.get("score")),
                    "ga": num(opp.get("score")),
                })
    memberships = {lg: {s: {x["team_id"] for x in rs} for s, rs in seasons.items()}
                   for lg, seasons in matches.items()}
    seasons = sorted(set(memberships["61"]) | set(memberships["185"]))
    result = {}
    for i, season in enumerate(seasons):
        if i == 0:
            continue
        prior = seasons[i - 1]
        pairs = []
        for direction, old_lg, new_lg in (("PT1_to_PT2", "61", "185"), ("PT2_to_PT1", "185", "61")):
            movers = sorted(memberships[old_lg].get(prior, set()) & memberships[new_lg].get(season, set()))
            changes = []
            for team in movers:
                old = [x for x in matches[old_lg][prior] if x["team_id"] == team]
                new = [x for x in matches[new_lg][season] if x["team_id"] == team]
                changes.append({"team_id": team, "gf_change": mean(x["gf"] for x in new) - mean(x["gf"] for x in old),
                                "ga_change": mean(x["ga"] for x in new) - mean(x["ga"] for x in old)})
            pairs.append((direction, {"prior_season": prior, "n": len(movers),
                                      "mean_gf_change": mean(x["gf_change"] for x in changes),
                                      "mean_ga_change": mean(x["ga_change"] for x in changes),
                                      "clubs": changes}))
        result[season] = dict(pairs)
    return result


def main():
    with open(CSV, newline="") as fh:
        rows = list(csv.DictReader(fh))
    seasons = sorted({r["season"] for r in rows})
    metrics = {
        "goals_for": lambda r, s: num(r[f"{s}_goals"]),
        "goals_against": lambda r, s: num(r[f"{'away' if s == 'home' else 'home'}_goals"]),
        "sot_for_stats": lambda r, s: num(r[f"sot_{s}"]),
        "corners_for_stats": lambda r, s: num(r[f"corners_{s}"]),
        "total_shots_for_stats": lambda r, s: num(r[f"total_shots_{s}"]),
        "event_yellows_for": lambda r, s: num(r[f"event_yellows_{s}"]),
    }
    reliability = {}
    for name, metric in metrics.items():
        reliability[name] = split_reliability(rows, metric)
        reliability[name]["valid_team_match_values"] = sum(metric(r, s) is not None for r in rows for s in ("home", "away"))
    per_season = {name: {s: split_reliability([r for r in rows if r["season"] == s], metric)
                         for s in seasons} for name, metric in metrics.items()}
    all_ht = [(num(r["ht_home"]) + num(r["ht_away"]), num(r["home_goals"]) + num(r["away_goals"]))
              for r in rows if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
    overlap_2526 = [r for r in rows if r["season"] == "2025/2026" and flag(r["has_stats"]) and flag(r["has_card_event"])]
    summary = {
        "n_matches": len(rows), "seasons": season_levels(rows),
        "trait_reliability": reliability, "trait_reliability_by_season": per_season,
        "movers": mover_measurement(rows),
        "halves": {"ht_goal_matches": len(all_ht), "n_matches": len(rows),
                    "goals_1h_share": sum(x for x, _ in all_ht) / sum(y for _, y in all_ht),
                    "period_split_matches": sum(flag(r["has_period_splits"]) for r in rows),
                    "frozen_constants": {}},
        "referee_coverage": {s: season_levels(rows)[s]["referee_named"] for s in seasons},
        "cards_stats_vs_events": {"both_stats_and_events": sum(flag(r["has_stats"]) and flag(r["has_card_event"]) for r in rows),
                                   "2025_2026_both_stats_and_events": len(overlap_2526),
                                   "stats_yellow_available": sum(num(r["stats_yellows_home"]) is not None and num(r["stats_yellows_away"]) is not None for r in rows),
                                   "exact_agreement_rate": None, "mean_difference_stats_minus_events": None,
                                   "disagreement_at_4_5": None},
    }
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(f"Wrote {OUT}")
    for s, item in summary["seasons"].items():
        print(s, item)
    print("movers", json.dumps(summary["movers"], sort_keys=True))
    print("reliability", json.dumps(summary["trait_reliability"], sort_keys=True))


if __name__ == "__main__":
    main()
