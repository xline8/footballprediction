import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
seasons = list(D["levels"].keys())

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (key, label) in zip(axes.flat, [("goals", "goals"), ("sot", "SOT"), ("corners", "corners"),
                                        ("yellows", "event yellows"), ("shots", "total shots"),
                                        ("home_goals", "home goals")]):
    ax.bar(seasons, [D["levels"][s][key] for s in seasons], color="#37474f")
    ax.set_title(label + " per match")
    ax.tick_params(axis="x", rotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

items = []
for market, sides in D["reliability"].items():
    for side, v in sides.items():
        items.append((f"{market} {side}", v["r"]))
items.sort(key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32")
ax.axvline(.3, color="grey", ls="--")
ax.set_title("AT-2Liga trait split-half reliability")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
for ax, key, label in ((axes[0], "halves_goals", "goals"), (axes[1], "halves_yellows", "yellows")):
    v = D[key]["const_ratio_of_sums"]
    ax.bar([label], [v], color="#37474f"); ax.axhline(.5, color="grey", ls="--"); ax.set_ylim(0, .6)
    ax.set_title(f"Frozen first-half share — {label}")
    ax.text(0, v + .015, f"{v:.4f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written")
