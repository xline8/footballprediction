"""Make the Phase-1 charts from frozen JSON summaries only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
E = json.loads((HERE / "eda_summary.json").read_text())
seasons = list(E["season_levels"])


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)


levels = E["season_levels"]
fig, ax = plt.subplots(figsize=(9, 4.5))
for key, label in (("goals_per_match", "goals"), ("sot", "SOT"), ("corners", "corners"), ("cards_events", "event yellows"), ("total_shots", "shots")):
    ax.plot(seasons, [levels[s][key] for s in seasons], marker="o", label=label)
ax.set_title("NL Eerste Divisie levels by season")
ax.set_ylabel("per match")
ax.legend(ncol=3)
save(fig, "levels_by_season.png")

reliability = E["reliability"]
items = [(key, value["r"]) for key, value in reliability.items() if value.get("r") is not None]
items.sort(key=lambda item: item[1])
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh([item[0] for item in items], [item[1] for item in items], color="#2e7d32")
ax.axvline(0.3, color="grey", linestyle="--")
ax.set_xlim(-1, 1)
ax.set_title("Team-trait split-half reliability")
save(fig, "trait_reliability.png")

halves = E["halves"]
names = list(halves)
fig, ax = plt.subplots(figsize=(8, 4.5))
values = [halves[name]["share_1h"] for name in names]
ax.bar(names, values, color="#37474f")
ax.axhline(0.5, color="grey", linestyle="--")
ax.set_ylim(0, 0.6)
ax.set_title("First-half shares (true variance in JSON)")
for i, value in enumerate(values):
    ax.text(i, value + 0.01, f"{value:.3f}", ha="center")
save(fig, "halves_constants.png")

ref = E["referees"]
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["referee cards", "possession", "big chances", "box touches"]
values = [ref["card_rate_split_half"]["r"] or 0, reliability["possession_for"]["r"] or 0, reliability["big_chances_for"]["r"] or 0, reliability["touches_opp_box_for"]["r"] or 0]
ax.bar(labels, values, color=["#2e7d32", "#90a4ae", "#90a4ae", "#90a4ae"])
ax.set_ylim(-1, 1)
ax.set_title("Referee and territorial reliability")
save(fig, "referee_and_territory.png")

