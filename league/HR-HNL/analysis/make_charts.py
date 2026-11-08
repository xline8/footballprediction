"""Charts for HR-HNL EDA: levels by season, trait reliabilities, halves constants.
Reads eda_summary.json; writes PNGs into analysis/charts/."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "eda_summary.json"))
CH = HERE / "charts"; CH.mkdir(exist_ok=True)
COMPLETE = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]
lev = S["levels"]
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
for ax, key, title in [(axes[0,0], "goals", "Goals / match"), (axes[0,1], "sot", "SOT / match"),
                       (axes[1,0], "corners", "Corners / match"), (axes[1,1], "shots", "Total shots / match")]:
    ax.plot(COMPLETE, [lev[s][key] for s in COMPLETE], marker="o")
    ax.set_title(title); ax.set_xticklabels(COMPLETE, rotation=30, ha="left"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(CH / "levels_by_season.png", dpi=110); plt.close(fig)
tr = S["traits"]
names = [k for k in tr if tr[k]["r"] is not None]
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(names, [tr[k]["r"] for k in names]); ax.axvline(0.5, color="r", ls="--")
ax.set_title("Split-half trait reliability (career pooled, complete seasons)")
fig.tight_layout(); fig.savefig(CH / "trait_reliabilities.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["goals (events)", "SOT (splits)", "corners (splits)", "total shots (splits)"]
vals = [S["halves_goals_dev"]["share"], S["halves_splits_dev"]["ShotsOnTarget"]["share"],
        S["halves_splits_dev"]["corners"]["share"], S["halves_splits_dev"]["total_shots"]["share"]]
ax.bar(labels, vals); ax.axhline(0.5, color="r", ls="--"); ax.set_ylim(0, 0.6)
ax.set_title("Frozen 1H shares (dev era)")
fig.tight_layout(); fig.savefig(CH / "halves_constants.png", dpi=110); plt.close(fig)
print("charts written", sorted(p.name for p in CH.glob("*.png")))
