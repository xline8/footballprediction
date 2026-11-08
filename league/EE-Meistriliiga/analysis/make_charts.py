"""Render the committed descriptive EDA charts; no new model statistics."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
eda = json.loads((HERE / "eda_summary.json").read_text())
seasons = list(eda["levels"])

fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(seasons, [eda["levels"][s]["goals_per_match"] for s in seasons], marker="o", color="#37474f")
ax.set(title="EE-Meistriliiga goals per match by season", ylabel="goals / match"); fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

rel = eda["trait_reliability"]
fig, ax = plt.subplots(figsize=(7, 3.5)); labels = ["goals for", "goals against"]; vals = [rel["goals_for_r"], rel["goals_against_r"]]
ax.barh(labels, vals, color="#2e7d32"); ax.axvline(.3, color="grey", ls="--"); ax.set(xlim=(-.05, 1), title="EE-Meistriliiga goal-trait split-half reliability", xlabel="r (60 random splits)")
for i, v in enumerate(vals): ax.text(v + .02, i, f"{v:.2f}", va="center")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(8, 3.8)); x = range(len(seasons))
axes[0].plot(seasons, [eda["levels"][s]["ou25_over"] for s in seasons], marker="o"); axes[0].set(title="OU2.5 over-rate", ylim=(0, 1))
axes[1].plot(seasons, [eda["levels"][s]["btts"] for s in seasons], marker="o", color="#1565c0"); axes[1].set(title="BTTS rate", ylim=(0, 1))
fig.suptitle("EE-Meistriliiga descriptive levels"); fig.tight_layout(); fig.savefig(OUT / "market_levels_by_season.png", dpi=130); plt.close(fig)

print("charts written", sorted(p.name for p in OUT.glob("*.png")))
