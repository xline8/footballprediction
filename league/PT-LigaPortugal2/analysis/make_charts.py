#!/usr/bin/env python3
"""Render the four descriptive EDA charts from eda_summary.json."""
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CHARTS = HERE / "charts"


def main():
    data = json.load(open(HERE / "eda_summary.json"))
    seasons = list(data["seasons"])
    x = range(len(seasons))
    CHARTS.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    for key, label, marker in (("mean_total_goals", "Goals", "o"),
                               ("mean_sot_total", "SOT (stats era)", "s"),
                               ("mean_corners_total", "Corners (stats era)", "^"),
                               ("mean_total_shots", "Total shots (stats era)", "D"),
                               ("mean_event_yellows_total", "Event yellows", "x")):
        ys = [data["seasons"][s][key] for s in seasons]
        ax.plot(list(x), [float("nan") if y is None else y for y in ys], marker=marker, label=label)
    ax.set_xticks(list(x), seasons, rotation=30, ha="right")
    ax.set_ylabel("Mean per match")
    ax.set_title("PT-LigaPortugal2 levels by season")
    ax.legend(ncol=2)
    fig.tight_layout(); fig.savefig(CHARTS / "levels_by_season.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    names = ["Goals for", "Goals against", "SOT for\n(stats)", "Corners for\n(stats)", "Total shots\n(stats)", "Event yellows\n(supplementary)"]
    keys = ["goals_for", "goals_against", "sot_for_stats", "corners_for_stats", "total_shots_for_stats", "event_yellows_for"]
    vals = [data["trait_reliability"][k]["r"] for k in keys]
    ax.bar(range(len(names)), vals, color=["#315f8c", "#315f8c", "#6e9f79", "#6e9f79", "#6e9f79", "#b77b4c"])
    ax.axhline(0, color="black", linewidth=.8); ax.set_ylim(-1, 1); ax.set_ylabel("Split-half Pearson r")
    ax.set_xticks(range(len(names)), names); ax.set_title("Career-pooled trait reliability")
    fig.tight_layout(); fig.savefig(CHARTS / "trait_reliability.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ht = [100 * (data["seasons"][s]["ht_goal_share"] is not None) for s in seasons]
    split = [100 * data["seasons"][s]["period_split_matches"] / data["seasons"][s]["n"] for s in seasons]
    ax.bar(list(x), split, label="Period-split stats coverage", color="#b77b4c")
    ax.plot(list(x), ht, "o-", label="HT goals recoverable", color="#315f8c")
    ax.set_ylim(0, 110); ax.set_ylabel("Matches / season (%)"); ax.set_xticks(list(x), seasons, rotation=30, ha="right")
    ax.set_title("Halves availability — no frozen halves constants")
    ax.legend(); fig.tight_layout(); fig.savefig(CHARTS / "halves_constants.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    ref = [100 * data["seasons"][s]["referee_named"] / data["seasons"][s]["n"] for s in seasons]
    ax.bar(list(x), ref, color="#777777"); ax.set_ylim(0, 100); ax.set_ylabel("Named referee (%)")
    ax.set_xticks(list(x), seasons, rotation=30, ha="right"); ax.set_title("Referee coverage")
    fig.tight_layout(); fig.savefig(CHARTS / "referee_coverage.png", dpi=160); plt.close(fig)
    print(f"Wrote charts to {CHARTS}")


if __name__ == "__main__":
    main()
