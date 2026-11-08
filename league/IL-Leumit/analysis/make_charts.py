#!/usr/bin/env python3
"""Charts for IL-Leumit EDA (from eda_summary.json; goals-only corpus)."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "eda_summary.json")))
OUT = os.path.join(HERE, "charts"); os.makedirs(OUT, exist_ok=True)
seasons = [s for s in S["by_season"]]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seasons, [S["by_season"][s]["goals_per_match"] for s in seasons], marker="o", label="goals/match")
ax.plot(seasons, [S["by_season"][s]["home_adv"] for s in seasons], marker="s", label="home advantage (goals)")
ax.axhline(2.55, ls="--", lw=0.8, label="J1 reference 2.55")
ax.legend(); ax.set_title("IL-Leumit levels by season"); plt.xticks(rotation=30, ha="right")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "levels_by_season.png"), dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(5, 4))
rel = S["split_half_reliability"]
ax.bar(["goals_for", "goals_against"], [rel["goals_for"][0], rel["goals_against"][0]])
ax.axhline(0.3, ls="--", lw=0.8); ax.set_ylim(0, 1)
ax.set_title(f"Split-half trait reliability (n={rel['goals_for'][1]} teams)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "trait_reliability.png"), dpi=120); plt.close()

fig, ax = plt.subplots(figsize=(6, 4))
ms = S["mover_summary"]
labels = ["down_from_haal", "up_from_tier3"]
x = range(len(labels))
ax.bar([i - 0.2 for i in x], [ms[k]["gf_delta"] for k in labels], width=0.4, label="GF delta vs mu")
ax.bar([i + 0.2 for i in x], [ms[k]["ga_delta"] for k in labels], width=0.4, label="GA delta vs mu")
ax.axhline(0, lw=0.8); ax.set_xticks(list(x)); ax.set_xticklabels(labels); ax.legend()
ax.set_title("Mover entry-season deltas (8 team-seasons each)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "mover_gap.png"), dpi=120); plt.close()
print("charts written to", OUT)
