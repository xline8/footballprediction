"""Make the three required Stage 1 PL charts from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
seasons = DATA["seasons"]
def levels(name): return [DATA["per_season"][s].get(name) for s in seasons]

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, label) in zip(axes.flat, [("goals", "goals"), ("sot", "SOT"), ("corners", "corners"), ("yellows", "yellows"), ("shots", "total shots"), ("xg_stats", "stats xG")]):
    ax.bar(seasons, [x if x is not None else 0 for x in levels(name)], color="#37474f")
    ax.set_title(f"{label} per match"); ax.tick_params(axis="x", labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

traits = dict(DATA["reliability"])
traits.update({"stats xG-for": DATA["stats_xg_reliability"], "stats xG/shot": DATA["ratio_reliability"]["stats_xg_per_shot"], "shotmap xG/shot": DATA["ratio_reliability"]["shotmap_xg_per_shot"], "set-play xG share": DATA["ratio_reliability"]["set_play_xg_share"], "xGOT/shot": DATA["ratio_reliability"]["xgot_per_shot"], "referee yellows": DATA["referee_reliability"]})
items = sorted(((k, v) for k, v in traits.items() if v is not None), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 5)); ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32"); ax.axvline(.3, color="grey", linestyle="--", linewidth=1); ax.set_title("PL trait split-half reliability (career-pooled, 60 splits)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

half = DATA["half_shares"]; names = ["goals", "SOT", "corners", "total shots", "yellow cards"]; keys = ["goals", "ShotsOnTarget", "corners", "total_shots", "yellow_cards"]
shares = [half[k]["share_ratio_of_sums"] for k in keys]
fig, ax = plt.subplots(figsize=(8, 3.8)); ax.bar(names, shares, color="#37474f"); ax.axhline(.5, color="grey", linestyle="--", linewidth=1); ax.set_ylim(0, .6); ax.set_title("PL frozen first-half shares — complete split era")
for i, value in enumerate(shares): ax.text(i, value + .015, f"{value:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
