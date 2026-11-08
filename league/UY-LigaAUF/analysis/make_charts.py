"""UY-LigaAUF charts (step 4): reads analysis/eda_summary.json and the
match CSV; writes analysis/charts/*.png. No fitting, no virgin-based
decisions: the charts only visualise numbers already in eda_summary.json.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).parent
CH = HERE / "charts"
CH.mkdir(exist_ok=True)
S = json.loads((HERE / "eda_summary.json").read_text())
seasons = sorted(S["seasons"])
ss = pd.DataFrame({s: S["seasons"][s] for s in seasons}).T

# 1. Levels by season: goals (all seasons; virgin 2025 + reserve 2026
# shown for inventory only, not used for any decision)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seasons, ss["goals_pm"], marker="o", label="goals/match")
ax.axvspan(3.5, 4.5, color="grey", alpha=.15)
ax.set_title("Goals/match by season (dev <=2024, virgin 2025, reserve 2026)")
ax.set_ylabel("per match"); ax.grid(alpha=.3); ax.legend()
ax.tick_params(axis="x", rotation=30)
fig.tight_layout(); fig.savefig(CH / "levels_by_season.png", dpi=110); plt.close(fig)

# 2. Feed coverage by season
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(seasons))
w = 0.2
for i, (col, lab) in enumerate([("stats", "stats"), ("events", "events"),
                                ("lineup", "lineup (11 starters)"),
                                ("referee", "referee named")]):
    ax.bar([v + (i - 1.5) * w for v in x], ss[col] / ss["n"], width=w, label=lab)
ax.set_xticks(list(x)); ax.set_xticklabels(seasons, rotation=30)
ax.set_title("Feed coverage by season (share of matches)\nstats/referee: 0 in every season")
ax.set_ylim(0, 1.05); ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(CH / "coverage_by_season.png", dpi=110); plt.close(fig)

# 3. Halves constants: only the goals share is computable on dev
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(["goals (event times, dev,\nn=2664 goals)"], [S["halves_dev"]["goals_events"]["share_1h"]])
ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6)
ax.set_title("1H share of totals — dev era (frozen halves constant).\n"
             "SOT/corners/shots/yellows: NO splits exist in any season,\n"
             "no constant.")
fig.tight_layout(); fig.savefig(CH / "halves_constants.png", dpi=110); plt.close(fig)

# 4. Trait reliability (split-half r, dev era): only goals measurable
fig, ax = plt.subplots(figsize=(7, 4))
rel = S["trait_reliability_dev"]
names = [k for k, v in rel.items() if v["split_half_r"] is not None]
vals = [rel[k]["split_half_r"] for k in names]
ax.barh(names, vals)
ax.set_xlim(0, 1)
ax.set_title("Trait reliability (split-half r, dev era).\n"
             "SOT/corners/shots/yellows/possession: target absent in dev,\n"
             "reliability not measurable — feature dropped on absence.")
fig.tight_layout(); fig.savefig(CH / "trait_reliability.png", dpi=110); plt.close(fig)
print("charts done:", sorted(p.name for p in CH.iterdir()))
