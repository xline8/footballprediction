"""Create the three Phase A charts from frozen eda_numbers.json only."""
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


seasons = DATA["seasons"]
labels = [s.replace("/", "–") for s in seasons]
fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (key, label) in zip(axes.flat, [("goals_per_match", "goals"), ("sot", "SOT"),
                                         ("corners", "corners"), ("cards", "event yellows"),
                                         ("total_shots", "total shots"), ("home_advantage", "home advantage")]):
    if key == "home_advantage":
        values = [DATA["per_season"][s][key]["goals"] for s in seasons]
    elif key in {"sot", "corners", "cards", "total_shots"}:
        values = [DATA["per_season"][s][key]["mean"] for s in seasons]
    else:
        values = [DATA["per_season"][s][key] for s in seasons]
    ax.bar(labels, [v if v is not None else 0 for v in values], color="#37474f")
    ax.set_title(label + (" per match" if key != "home_advantage" else ""))
    ax.tick_params(axis="x", rotation=30, labelsize=7)
save(fig, "levels_by_season.png")


rel = DATA["reliability"]
items = sorted([(k.replace("_", " "), v["r"]) for k, v in rel.items() if v["r"] is not None], key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32")
ax.axvline(.3, color="grey", ls="--", lw=1)
ax.set_xlim(0, 1)
ax.set_title("Bulgaria First League trait split-half reliability")
save(fig, "trait_reliability.png")


h = DATA["halves"]
names = ["goals", "event yellows"]
keys = ["goals", "yellow_cards"]
values = [h[k]["share_1h"] for k in keys]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, values, color="#37474f")
ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6)
ax.set_title("Frozen first-half shares — pooled pre-virgin era")
for i, value in enumerate(values):
    if value is not None: ax.text(i, value + .015, f"{value:.4f}", ha="center")
save(fig, "halves_constants.png")
print("charts done ->", OUT)
