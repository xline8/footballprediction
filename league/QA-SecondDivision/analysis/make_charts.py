"""QA-SecondDivision charts (step 4): reads analysis/eda_summary.json and the
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

# 1. Levels by season
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ax = axes[0]
ax.plot(seasons, ss["goals_pm"], marker="o", label="goals/match")
ax.set_title("Goals/match by season (G dev 2024/2025,\nG virgin 2025/2026, S/C/T/K virgin 2026/2027)")
ax.set_ylabel("per match"); ax.grid(alpha=.3); ax.legend()
ax.tick_params(axis="x", rotation=30)
ax = axes[1]
for col, lab in [("sot_pm", "SOT"), ("corners_pm", "corners")]:
    ax.plot(seasons, ss[col], marker="o", label=lab)
ax.plot(seasons, ss["shots_pm"] / 3, marker="s", label="shots / 3")
ax.plot(seasons, ss["yell_ev_pm"], marker="^", label="yellows (events)")
ax.set_title("Stats-market levels by season\n(2024/2025 = 38 stats matches only)")
ax.grid(alpha=.3); ax.legend(fontsize=8)
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
ax.set_title("Feed coverage by season (share of matches)")
ax.set_ylim(0, 1.05); ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(CH / "coverage_by_season.png", dpi=110); plt.close(fig)

# 3. Halves constants (dev era only, per candidate)
fig, ax = plt.subplots(figsize=(8, 4))
labels = ["goals 24/25\n(events, n=146)",
          "SOT 25/26\n(splits, n=484)",
          "corners 25/26\n(splits, n=545)",
          "shots 25/26\n(splits, n=1295)",
          "yellows 25/26\n(events, n=292)"]
vals = [S["halves_dev"]["goals_2024_2025_events"]["share_1h"],
        S["halves_dev"]["sot_2025_2026_splits"]["share_1h"],
        S["halves_dev"]["corners_2025_2026_splits"]["share_1h"],
        S["halves_dev"]["shots_2025_2026_splits"]["share_1h"],
        S["halves_dev"]["yell_events_2025_2026_times"]["share_1h"]]
ax.barh(labels, vals)
ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6)
ax.set_title("1H share of totals — dev era per candidate (frozen halves constants).\nTrue SD ≈ 0 for goals/SOT/shots; corners 0.010, yellows (events) 0.089.")
fig.tight_layout(); fig.savefig(CH / "halves_constants.png", dpi=110); plt.close(fig)

# 4. Trait reliability (split-half r, pre-scored-window pools; n=8-9 teams)
fig, ax = plt.subplots(figsize=(8, 4))
rel = S["trait_reliability"]
names = ["stats_pool_sot_for", "stats_pool_shots_for", "stats_pool_corners_for",
         "stats_pool_goals_for", "stats_pool_yellow_for", "g_dev_goals_for"]
labs = ["SOT-for (pool)", "shots-for (pool)", "corners-for (pool)",
        "goals-for (pool)", "yellows-for (pool)", "goals-for (G dev 24/25)"]
vals = [rel[k]["split_half_r"] for k in names]
ax.barh(labs, vals)
ax.axvline(0, color="k", lw=.8)
ax.set_xlim(-1, 1)
ax.set_title("Trait reliability (split-half r, odd/even). n=8-9 teams: SE ~0.35.\n"
             "No trait clears a reliability bar; SOT/shots positive but wide-CI.")
fig.tight_layout(); fig.savefig(CH / "trait_reliability.png", dpi=110); plt.close(fig)
print("charts done:", sorted(p.name for p in CH.iterdir()))
