"""Make the three frozen NG EDA chart families from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
seasons = list(D["trait_reliability_per_season"])
# Levels are frozen in EDA/inventory and are recomputed from the built CSV by
# the data audit; this chart script intentionally consumes the frozen numbers.
I = json.loads((HERE / "inventory_summary.json").read_text())["by_season"]
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for a, key, title in zip(ax, ("goals_per_match", "home_win_rate", "over25_rate"),
                         ("goals per match", "home-win rate", "over 2.5 rate")):
    a.bar(seasons, [I[s][key] for s in seasons], color="#37474f"); a.set_title(title)
    a.tick_params(axis="x", rotation=35, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4)); x = range(len(seasons) + 1)
ax.plot(list(x), [D["trait_reliability_per_season"][s]["r_attack"] for s in seasons] + [D["trait_reliability_pooled"]["r_attack"]], "o-", label="attack")
ax.plot(list(x), [D["trait_reliability_per_season"][s]["r_defence"] for s in seasons] + [D["trait_reliability_pooled"]["r_defence"]], "o-", label="defence")
ax.set_xticks(list(x), seasons + ["pooled"], rotation=35); ax.axhline(0, color="grey", lw=.8); ax.legend(); ax.set_title("Trait split-half reliability")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4)); vals = [0.4814, 0.5079, 0.4700, 0.4756, 0.4837, 0.4649, 0.4796]
ax.bar(seasons + ["pooled"], vals, color="#37474f"); ax.axhline(0.4796, color="#c62828", ls="--", label="frozen pooled 0.4796"); ax.legend(); ax.set_ylim(0, .6); ax.set_title("First-half goal share")
ax.tick_params(axis="x", rotation=35); fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written")
