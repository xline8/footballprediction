"""FI-Ykkonen charts (from eda_summary.json): levels by season,
Kakkonen group levels, trait reliability, halves-constant evidence.
Virgin 2025 / reserve 2026 appear only as inventory points, never
as analysis inputs.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = json.loads((HERE / "eda_summary.json").read_text())
ch = HERE / "charts"
ch.mkdir(exist_ok=True)

ss = OUT["seasons"]
seasons = sorted(ss, key=int)
gpm = [ss[s]["goals_pm"] for s in seasons]
hw = [ss[s]["home_win_rate"] for s in seasons]
ou = [ss[s]["over25_rate"] for s in seasons]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seasons, gpm, marker="o", label="goals/match")
ax.plot(seasons, ou, marker="s", label="OU2.5 over-rate")
ax.plot(seasons, hw, marker="^", label="home-win rate")
ax.axvspan(3.5, 4.5, color="gray", alpha=0.15)
ax.text(3.55, 3.55, "Ykkonen era", fontsize=8)
ax.set_title("FI-Ykkonen levels by season (dev <= 2024; virgin 2025; reserve 2026)")
ax.set_ylim(0.3, 3.8)
ax.legend()
ax.grid(alpha=.3)
fig.tight_layout()
fig.savefig(ch / "levels_by_season.png", dpi=110)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(seasons, [ss[s]["stats"] / ss[s]["n"] for s in seasons], label="stats coverage")
ax.bar(seasons, [ss[s]["events"] / ss[s]["n"] for s in seasons], alpha=.6, label="events coverage")
ax.legend()
ax.set_title("Feed coverage by season (stats 0% everywhere; events ~97%)")
ax.grid(alpha=.3)
fig.tight_layout()
fig.savefig(ch / "coverage_by_season.png", dpi=110)
plt.close(fig)

# Kakkonen group levels (dev era, regular groups only) + Ykkonen 2024 split
gl = OUT["kakkonen_group_levels"]
labels = ["Kakkonen A\n2021-2023", "Kakkonen B\n2021-2023", "Kakkonen C\n2021-2023",
          "Ykkonen reg.\n2024", "Ykkonen champ.\n2024", "Ykkonen releg.\n2024"]
vals = [gl["kakkonen_a"]["goals_pm"], gl["kakkonen_b"]["goals_pm"], gl["kakkonen_c"]["goals_pm"],
        OUT["phase_levels"]["2024:ykkonen"]["goals_pm"],
        OUT["phase_levels"]["2024:ykkonen_championship"]["goals_pm"],
        OUT["phase_levels"]["2024:ykkonen_relegation"]["goals_pm"]]
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(labels, vals)
ax.axhline(OUT["era_levels"]["kakkonen_2021_2023"]["goals_pm"], color="k", lw=.8, ls="--",
           label="Kakkonen mean 3.36")
ax.set_ylabel("goals/match")
ax.set_title("Goals/match by Kakkonen group and Ykkonen 2024 phase")
ax.legend()
ax.grid(alpha=.3, axis="y")
fig.tight_layout()
fig.savefig(ch / "levels_by_group.png", dpi=110)
plt.close(fig)

# Trait reliability
tr = OUT["trait_reliability_dev"]
names = ["goals_for", "goals_against"]
vals = [tr[k]["split_half_r"] for k in names]
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(names, vals)
ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.8)
ax.set_title("Trait reliability (split-half r, dev era, n=55 teams)")
fig.tight_layout()
fig.savefig(ch / "trait_reliability.png", dpi=110)
plt.close(fig)

# Halves constants
hv = OUT["halves_dev"]["goals_events"]["share_1h"]
hbe = OUT["halves_by_era"]
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(["goals 1H share (dev)", "Kakkonen 2021-2023", "Ykkonen 2024"],
        [hv, hbe["kakkonen_2021_2023"]["share_1h"], hbe["ykkonen_2024"]["share_1h"]])
ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6)
ax.set_title("1H share of goals — dev era (frozen halves constant 0.4463)")
fig.tight_layout()
fig.savefig(ch / "halves_constants.png", dpi=110)
plt.close(fig)
print("charts done:", sorted(p.name for p in ch.glob("*.png")))
