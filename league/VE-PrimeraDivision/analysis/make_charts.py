"""Create the Step-3 chart set."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

A = Path(__file__).resolve().parent
C = A / "charts"
C.mkdir(exist_ok=True)
x = json.loads((A / "eda_numbers.json").read_text())
seasons = list(x["levels"])
fig, axs = plt.subplots(2, 2, figsize=(11, 7))
for ax, (key, title) in zip(axs.flat, [("goals_total", "Goals"), ("ShotsOnTarget", "SOT"), ("corners", "Corners"), ("total_shots", "Total shots")]):
    ax.plot(seasons, [x["levels"][s][key]["mean"] for s in seasons], marker="o")
    ax.set_title(title); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig(C / "levels_by_season.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 6))
traits = ["goals_for", "sot_for", "corners_for", "yellow_for", "total_shots_for", "possession_for", "on_target_rate"]
for trait in traits:
    ys = [x["reliability"][s][trait]["r"] for s in ["2025", "2026", "pooled_stats_era"]]
    ax.plot(["2025", "2026", "pooled"], ys, marker="o", label=trait)
ax.axhline(0, color="k", lw=.5); ax.set_ylim(-1, 1); ax.set_title("Split-half team-trait reliability"); ax.legend(ncol=3, fontsize=8); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig(C / "trait_reliability.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5))
names = ["goals", "ShotsOnTarget", "corners", "stats_yellow", "total_shots"]
ax.bar(names, [x["halves"][n]["share"] for n in names]); ax.axhline(.5, color="k", lw=.7); ax.set_ylim(0, 1); ax.set_title("Frozen first-half shares")
fig.tight_layout(); fig.savefig(C / "halves_constants.png", dpi=150); plt.close(fig)
print("wrote", C)
