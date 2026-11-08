"""Create the Phase-A PBM chart set from the frozen EDA JSON only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
EDA = json.loads((HERE / "eda_summary.json").read_text())

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=130); plt.close(fig); print("wrote", name)

seasons = list(EDA["seasons"])
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(seasons, [EDA["seasons"][s]["goals_per_match"] for s in seasons], marker="o", color="#1565c0")
ax.axhline(2.84, color="grey", ls="--", lw=1, label="Top-5 spine mean (2.84)")
ax.set_title("PBM goals per match by season — EDA window")
ax.set_ylabel("goals / match"); ax.legend(); save(fig, "levels_by_season.png")

rel = EDA["reliability"]
labels = ["goals for", "goals against"]; vals = [rel["goals_for"]["r"], rel["goals_against"]["r"]]
fig, ax = plt.subplots(figsize=(7, 3.8))
colors = ["#2e7d32" if v >= .4 else "#ef6c00" if v >= .3 else "#c62828" for v in vals]
ax.barh(labels, vals, color=colors); ax.axvline(.3, color="grey", ls="--", lw=1); ax.set_xlim(-1, 1)
ax.set_title("PBM team-trait reliability, split-half r (2021–2025)");
for y, v in enumerate(vals): ax.text(v + .03 if v >= 0 else v - .03, y, f"{v:.2f}", va="center")
save(fig, "trait_reliability.png")

h = EDA["halves"]["goals"]
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.bar(["goals"], [h["share_1h"]], color="#37474f"); ax.axhline(.5, color="grey", ls="--", lw=1); ax.set_ylim(0, .6)
ax.set_title("PBM frozen 1H goals share test — presentation only")
ax.text(0, h["share_1h"] + .02, f"{h['share_1h']:.3f}", ha="center")
save(fig, "halves_constants.png")
