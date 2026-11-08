"""Charts for RU-SecondLeague EDA (goals only — no other target exists)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
seasons = [s for s in D["seasons"] if s != "2025"]  # fragment excluded from charts

fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
axes[0].bar(seasons, [D["per_season"][s]["mean_goals"] for s in seasons], color="#37474f")
axes[0].set_title("goals per match")
axes[0].tick_params(axis="x", rotation=30, labelsize=7)
axes[1].bar(seasons, [D["per_season"][s]["home_win"] for s in seasons], color="#37474f")
axes[1].set_title("home win rate")
axes[1].tick_params(axis="x", rotation=30, labelsize=7)
axes[2].bar(seasons, [D["per_season"][s]["over25"] for s in seasons], color="#37474f")
axes[2].set_title("over 2.5 rate")
axes[2].tick_params(axis="x", rotation=30, labelsize=7)
fig.tight_layout()
fig.savefig(OUT / "levels_by_season.png", dpi=130)
plt.close(fig)

items = sorted((k, v) for k, v in D["reliability"].items() if isinstance(v, dict) is False)
rel = [("goals for (pooled)", D["reliability"]["goals_for_split_half"]["pooled_fisher_z"]),
       ("goals against (pooled)", D["reliability"]["goals_against_split_half"]["pooled_fisher_z"])]
fig, ax = plt.subplots(figsize=(7, 3))
ax.barh([x[0] for x in rel], [x[1] for x in rel], color="#2e7d32")
ax.axvline(.3, color="grey", ls="--")
ax.set_title("RU-SecondLeague trait split-half reliability (pooled)")
fig.tight_layout()
fig.savefig(OUT / "trait_reliability.png", dpi=130)
plt.close(fig)

g = D["half_period"]["goals"]
fig, ax = plt.subplots(figsize=(5.5, 3.8))
ax.bar(["goals"], [g["share_ratio_of_sums"]], color="#37474f")
ax.axhline(.5, color="grey", ls="--")
ax.set_ylim(0, .6)
ax.set_title("Frozen first-half share — goals (true SD 0.0000)")
ax.text(0, g["share_ratio_of_sums"] + .015, f"{g['share_ratio_of_sums']:.4f}", ha="center")
fig.tight_layout()
fig.savefig(OUT / "halves_constants.png", dpi=130)
plt.close(fig)
print("charts written")
