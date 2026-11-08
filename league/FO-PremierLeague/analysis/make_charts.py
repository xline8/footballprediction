"""Generate the Phase A chart set from the frozen EDA summary."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
EDA = json.loads((HERE / "eda_summary.json").read_text())


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)
    print("wrote", name)


seasons = list(EDA["seasons"])
levels = EDA["seasons"]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(seasons, [levels[s]["goals"] for s in seasons], marker="o", label="goals")
ax.plot(seasons, [levels[s]["yellow_cards"] for s in seasons], marker="s", label="unified yellows")
ax.axvline("2026", color="grey", ls="--", lw=1)
ax.set_title("Faroe Premier League levels by season")
ax.set_ylabel("events / match")
ax.legend()
save(fig, "levels_by_season.png")

rel = EDA["reliability"]
labels = ["goals for", "goals against", "yellows for", "yellows against"]
vals = [rel["goals_for"], rel["goals_against"], rel["yellows_for"], rel["yellows_against"]]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh(labels[::-1], vals[::-1], color="#2e7d32")
ax.set_xlim(0, 1)
ax.set_xlabel("odd/even season split-half Pearson r")
ax.set_title("Team-trait reliability")
for i, v in enumerate(vals[::-1]):
    ax.text(v + .02, i, f"{v:.3f}", va="center")
save(fig, "trait_reliability.png")

h = EDA["pooled"]
names = ["goals", "unified yellows"]
shares = [h["goals_1h_share"], h["yellow_1h_share"]]
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar(names, shares, color="#37474f")
ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6)
ax.set_ylabel("first-half share")
ax.set_title("Frozen first-half presentation constants")
for i, v in enumerate(shares):
    ax.text(i, v + .015, f"{v:.3f}", ha="center")
save(fig, "halves_constants.png")
