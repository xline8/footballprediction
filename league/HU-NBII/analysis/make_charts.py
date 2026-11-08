"""Create the three descriptive HU-NBII charts and summary JSON files."""

import csv
import json
import math
import os
import statistics
from collections import Counter, defaultdict

import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
LEAGUE = os.path.dirname(HERE)
CSV_PATH = os.path.join(LEAGUE, "data", "hu_nbii_matches.csv")
CHART_DIR = os.path.join(HERE, "charts")


def rows():
    out = []
    with open(CSV_PATH, newline="") as handle:
        for row in csv.DictReader(handle):
            for key in ("home_goals", "away_goals", "total_goals", "home_win", "draw", "away_win", "over_1_5", "over_2_5", "over_3_5", "btts", "has_half_marker"):
                row[key] = int(row[key])
            for key in ("goals_1h_home", "goals_1h_away"):
                row[key] = None if row[key] == "" else int(row[key])
            out.append(row)
    return out


def corr(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den if den else None


def team_split(rows_for_season):
    teams = defaultdict(list)
    for row in sorted(rows_for_season, key=lambda r: (r["date"], r["match_id"])):
        teams[row["home_team"]].append(row["home_goals"])
        teams[row["away_team"]].append(row["away_goals"])
    first, second = [], []
    for values in teams.values():
        cut = len(values) // 2
        first.append(sum(values[:cut]) / cut)
        second.append(sum(values[cut:]) / (len(values) - cut))
    return first, second, corr(first, second)


def main():
    data = rows()
    seasons = ["2025/2026", "2026/2027"]
    levels = {}
    for season in seasons + ["pooled"]:
        subset = data if season == "pooled" else [r for r in data if r["season"] == season]
        n = len(subset)
        over = sum(r["over_2_5"] for r in subset) / n
        levels[season] = {
            "n": n, "goals": sum(r["total_goals"] for r in subset),
            "goals_per_match": sum(r["total_goals"] for r in subset) / n,
            "home_win": sum(r["home_win"] for r in subset) / n,
            "draw": sum(r["draw"] for r in subset) / n,
            "away_win": sum(r["away_win"] for r in subset) / n,
            "over_1_5": sum(r["over_1_5"] for r in subset) / n,
            "over_2_5": over, "over_2_5_se": math.sqrt(over * (1 - over) / n),
            "over_3_5": sum(r["over_3_5"] for r in subset) / n,
            "btts": sum(r["btts"] for r in subset) / n,
        }
    half = [r for r in data if r["has_half_marker"]]
    half_goals = sum((r["goals_1h_home"] or 0) + (r["goals_1h_away"] or 0) for r in half)
    half_summary = {"n": len(half), "first_half_goals_from_events": half_goals,
                    "full_time_goals_from_score": sum(r["total_goals"] for r in half),
                    "share": half_goals / sum(r["total_goals"] for r in half)}
    reliability = {}
    for season in seasons:
        first, second, value = team_split([r for r in data if r["season"] == season])
        reliability[season] = {"teams": len(first), "first_half_gf_game": first, "second_half_gf_game": second, "r": value}

    with open(os.path.join(HERE, "eda_summary.json"), "w") as handle:
        json.dump({"levels": levels, "half_share": half_summary, "split_half_team_gf": reliability}, handle, indent=2)

    # Inventory counts are payload facts, not index flags: inspect every JSON.
    warehouse = os.path.expanduser("~/workspace/footballprediction")
    index_path = os.path.join(warehouse, "data_enrichment", "fotmob_world_index.csv")
    inventory = {"league": "HU-NBII", "fotmob_id": 9117, "index_rows": 344, "seasons": {}}
    with open(index_path, newline="") as handle:
        index = [r for r in csv.DictReader(handle) if r["league_id"] == "9117"]
    for season in seasons:
        subset = [r for r in index if r["season"] == season]
        counts = Counter()
        rounds = Counter()
        dates = []
        for row in subset:
            dates.append(row["date"]); rounds[row["score"] if False else "rows"] += 1
            with open(os.path.join(warehouse, row["path"])) as handle:
                payload = json.load(handle)
            status = payload["header"]["status"]
            counts["scoreStr"] += int(bool(status.get("scoreStr")))
            counts["finished"] += int(bool(status.get("finished")))
            counts["finished_and_scoreStr"] += int(bool(status.get("finished") and status.get("scoreStr")))
            counts["events_nonempty"] += int(bool(payload["content"]["matchFacts"]["events"].get("events")))
            counts["referee_nonblank"] += int(bool(payload["content"]["matchFacts"]["infoBox"].get("Referee", {}).get("text")))
            counts["stats_nonempty"] += int(bool(payload["content"].get("stats")))
            counts["shotmap_shots_nonempty"] += int(bool((payload["content"].get("shotmap") or {}).get("shots")))
            counts["lineup_nonempty"] += int(bool(payload["content"].get("lineup")))
            counts["periods_nonempty"] += int(bool((payload["content"].get("stats") or {}).get("Periods")))
        inventory["seasons"][season] = {"n": len(subset), "date_min": min(dates), "date_max": max(dates), "coverage": dict(counts)}
    with open(os.path.join(HERE, "inventory_summary.json"), "w") as handle:
        json.dump(inventory, handle, indent=2)

    os.makedirs(CHART_DIR, exist_ok=True)
    plt.figure(figsize=(6, 4)); values = [levels[s]["goals_per_match"] for s in seasons]
    bars = plt.bar(seasons, values, color=["#5078a0", "#d07a3a"])
    plt.ylabel("Goals per match"); plt.title("HU-NBII genuine goals/match")
    for bar, season in zip(bars, seasons): plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{levels[season]['goals_per_match']:.3f}\nn={levels[season]['n']}", ha="center", va="bottom")
    plt.tight_layout(); plt.savefig(os.path.join(CHART_DIR, "goals_by_season.png"), dpi=160); plt.close()

    plt.figure(figsize=(6, 4)); observed = half_summary["share"]
    bars = plt.bar(["HU-NBII\nfinished-only", "J1 reference"], [observed, 0.412], color=["#5078a0", "#a9a9a9"])
    plt.ylim(0, .6); plt.ylabel("1H share of goals"); plt.title("Descriptive half share (no constant frozen)")
    plt.axhline(.412, color="#555", linestyle="--", linewidth=1)
    plt.text(0, observed, f"{observed:.3f}\nn={half_summary['n']}", ha="center", va="bottom"); plt.text(1, .412, "0.412", ha="center", va="bottom")
    plt.tight_layout(); plt.savefig(os.path.join(CHART_DIR, "half_share_vs_j1.png"), dpi=160); plt.close()

    plt.figure(figsize=(6, 4))
    for season, color in zip(seasons, ["#5078a0", "#d07a3a"]):
        first, second, _ = team_split([r for r in data if r["season"] == season])
        plt.scatter(first, second, label=season, color=color)
    lo, hi = 0, max(max(r["home_goals"] for r in data), max(r["away_goals"] for r in data))
    plt.xlabel("First chronological half GF/game"); plt.ylabel("Second chronological half GF/game")
    plt.title("Team GF/game split-half reliability"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, "team_gf_split_half.png"), dpi=160); plt.close()
    print(json.dumps({"levels": levels, "half_share": half_summary, "split_half_team_gf": {s: reliability[s]["r"] for s in seasons}}, indent=2))


if __name__ == "__main__":
    main()
