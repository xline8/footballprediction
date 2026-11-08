"""Create the three charts from frozen eda_numbers.json only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)
    print("wrote", name)


seasons = sorted(DATA["per_season"])
labels = [s.replace("/", "–") for s in seasons]
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
for ax, (key, label) in zip(axes.flat, [("goals_per_match", "goals"),
                                        ("event_yellows_per_match", "event yellows"),
                                        ("home_goal_advantage", "home goal advantage")]):
    values = [DATA["per_season"][s]["regular"][key] for s in seasons]
    ax.bar(labels, values, color="#37474f")
    ax.set_title(label + " per match")
    ax.tick_params(axis="x", rotation=20, labelsize=7)
save(fig, "levels_by_season.png")

rel = DATA["reliability_dev_season_split_half"]
items = sorted([(k.replace("_", " "), v["r"]) for k, v in rel.items() if v["r"] is not None],
               key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32")
ax.axvline(.3, color="grey", ls="--", lw=1)
ax.set_xlim(0, 1)
ax.set_title("Thai League 2 trait split-half reliability (dev season only)")
save(fig, "trait_reliability.png")

h = DATA["halves_dev"]
names = ["goals", "event yellows"]
values = [h["goals"]["share_1h"], h["yellow_cards"]["share_1h"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, values, color="#37474f")
ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6)
ax.set_title("Frozen first-half shares — dev season, event-derived")
for i, value in enumerate(values):
    ax.text(i, value + .015, f"{value:.4f}", ha="center")
save(fig, "halves_constants.png")
print("charts done ->", OUT)
