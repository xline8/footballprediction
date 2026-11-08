"""Create the KR-KLeague3 EDA chart set from eda_summary.json only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).parent
EDA = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
SEASONS = sorted(EDA["levels"])

# Levels: the four goal-market quantities available in the verified summary.
fig, axes = plt.subplots(2, 2, figsize=(10, 7))
plots = [
    ("goals", "Goals per match"),
    ("hw_pct", "Home-win share"),
    ("draw_pct", "Draw share"),
    ("over25_pct", "Over 2.5 share"),
]
for ax, (key, title) in zip(axes.flat, plots):
    ax.plot(SEASONS, [EDA["levels"][s][key] for s in SEASONS], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Season")
    ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "levels_by_season.png", dpi=120)
plt.close(fig)

# Reliability: only the two verified goals traits exist in this league.
rel = EDA["reliability"]
labels = ["goals for", "goals against"]
values = [rel["goals_for"]["r"], rel["goals_against"]["r"]]
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(labels, values)
ax.set_xlim(0, 1)
ax.set_xlabel("split-half r (career-pooled)")
ax.set_title("Trait reliability")
fig.tight_layout()
fig.savefig(OUT / "trait_reliability.png", dpi=120)
plt.close(fig)

# Halves: season observations and the frozen pooled constant.
shares = EDA["halves"]["season_share_1h"]
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(SEASONS, [shares[s] for s in SEASONS], marker="o", label="season")
ax.axhline(EDA["halves"]["share_1h"], linestyle="--", label="frozen pooled")
ax.set_ylim(0, 1)
ax.set_ylabel("1H goal share")
ax.set_title("Goals halves constant")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "halves_constants.png", dpi=120)
plt.close(fig)

print("charts done")
