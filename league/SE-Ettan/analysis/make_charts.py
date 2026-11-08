"""SE-Ettan charts (step 4): reads analysis/eda_summary.json and the
match CSV; writes analysis/charts/*.png. No fitting, no virgin-based
decisions: the charts only visualise numbers already in eda_summary.json.
Season 2026 is never read (it is not in eda_summary.json at all).
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

# 1. Levels by season: goals/match overall + per group (2025 = virgin,
# inventory only -- shown for format completeness, never used downstream)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(seasons, ss["goals_pm"], marker="o", label="goals/match (both groups)")
ax.plot(seasons, ss["goals_pm_norra"], marker="s", label="Ettan Norra")
ax.plot(seasons, ss["goals_pm_sodra"], marker="^", label="Ettan Södra")
ax.axvspan(3.5, 4.5, color="grey", alpha=.15)
ax.set_title("Goals/match by season (dev <=2024; 2025 virgin, inventory only)")
ax.set_ylabel("per match"); ax.grid(alpha=.3); ax.legend(fontsize=8)
ax.tick_params(axis="x", rotation=30)
fig.tight_layout(); fig.savefig(CH / "levels_by_season.png", dpi=110); plt.close(fig)

# 2. Feed coverage by season (share of matches)
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(seasons))
w = 0.2
for i, (col, lab) in enumerate([("stats", "stats"), ("events", "events"),
                                ("lineup_11", "lineup (11 starters)"),
                                ("referee", "referee named")]):
    ax.bar([v + (i - 1.5) * w for v in x], ss[col] / ss["n"], width=w, label=lab)
ax.set_xticks(list(x)); ax.set_xticklabels(seasons, rotation=30)
ax.set_title("Feed coverage by season (share of matches)\n"
             "stats/referee 0% every season; events 0% in 2021, 100% after")
ax.set_ylim(0, 1.05); ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(CH / "coverage_by_season.png", dpi=110); plt.close(fig)

# 3. Halves constants: goals 1H share (event times, dev 2022-2024) and
# the descriptive event-yellows 1H share (K evidence only, not a frozen
# constant for any built market).
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(["goals (event times, dev 2022-2024,\nn=4299 goals)",
         "event yellows (descriptive only,\nn=4840 yellows)"], [
    S["halves_dev"]["goals_events"]["share_1h"],
    S["halves_dev"]["yellows_events_descriptive"]["share_1h"]])
ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6)
ax.set_title("1H share of totals — dev era (frozen halves constant: goals only).\n"
             "SOT/corners/shots: NO stats splits exist in any season, no constant.")
fig.tight_layout(); fig.savefig(CH / "halves_constants.png", dpi=110); plt.close(fig)

# 4. Trait reliability (split-half r, dev era)
fig, ax = plt.subplots(figsize=(8, 4))
rel = S["trait_reliability_dev"]
names = ["goals_for (dev 2021-2024)", "goals_against (dev 2021-2024)",
         "goals_for (scored 2022-2024)", "goals_against (scored 2022-2024)",
         "event yellows (descriptive, 2022-2024)"]
vals = [rel["goals_for"]["split_half_r_dev_2021_2024"],
        rel["goals_against"]["split_half_r_dev_2021_2024"],
        rel["goals_for"]["split_half_r_scored_2022_2024"],
        rel["goals_against"]["split_half_r_scored_2022_2024"],
        rel["event_yellows_for"]["split_half_r_dev_2022_2024"]]
ax.barh(names, vals)
ax.set_xlim(0, 1)
ax.set_title("Trait reliability (split-half r, dev era).\n"
             "SOT/corners/shots/stats yellows/possession: target absent in dev,\n"
             "reliability not measurable — feature dropped on absence.")
fig.tight_layout(); fig.savefig(CH / "trait_reliability.png", dpi=110); plt.close(fig)
print("charts done:", sorted(p.name for p in CH.iterdir()))
