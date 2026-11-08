"""Make the standard CN-SuperLeague Phase-A chart set from frozen JSON."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
eda = json.loads((HERE / "eda_summary.json").read_text())
movers = json.loads((HERE / "mover_gap.json").read_text())

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)
    print("wrote", name)

seasons = eda["seasons"]
fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)
for ax, key, title in zip(axes.flat, ("goals", "sot", "total_shots", "corners"),
                          ("Goals", "Shots on target", "Total shots", "Corners")):
    ax.plot(seasons, [eda["per_season"][s][key]["mean"] for s in seasons], marker="o")
    ax.set_title(title)
    ax.set_ylabel("per match")
    ax.grid(alpha=.2)
fig.suptitle("China Super League levels by season")
save(fig, "levels_by_season.png")

rel = eda["reliability_by_block"]["dev_2023-2025"]
traits = [("SOT for", "ShotsOnTarget_for"), ("SOT against", "ShotsOnTarget_against"),
          ("corners for", "corners_for"), ("shots for", "total_shots_for"),
          ("shots against", "total_shots_against"), ("goals for", "goals_for"),
          ("yellow for", "yellow_cards_for"), ("yellow against", "yellow_cards_against")]
labels = [x[0] for x in traits][::-1]
vals = [rel[x[1]]["r"] for x in traits][::-1]
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.barh(labels, vals, color=["#2e7d32" if v >= .6 else "#ef6c00" if v >= .3 else "#c62828" for v in vals])
ax.set_xlim(-1, 1); ax.axvline(0, color="grey", lw=1)
ax.set_title("CN team-trait reliability, split-half r (dev 2023–2025)")
for i, v in enumerate(vals): ax.text(v + (.02 if v >= 0 else -.08), i, f"{v:.2f}", va="center")
save(fig, "trait_reliability.png")

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(["GF gap", "GA gap"], [movers["mean_league_gf_gap"], movers["mean_league_ga_gap"]],
       color=["#1565c0", "#ad1457"])
ax.axhline(0, color="grey", lw=1)
ax.set_ylabel("goals / match vs season mean")
ax.set_title(f"First-season movers appearing in 2023+ (n={movers['n_teams']})")
save(fig, "tier_gap.png")

h = eda["halves"]
names = ["goals", "SOT", "corners", "total shots", "yellow cards"]
shares = [h["goals_events_all_seasons"]["share_1h"], h["sot"]["share_1h"],
          h["corners"]["share_1h"], h["total_shots"]["share_1h"], h["yellow_cards"]["share_1h"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6); ax.set_title("Frozen first-half shares — presentation only")
for i, v in enumerate(shares): ax.text(i, v + .015, f"{v:.3f}", ha="center")
save(fig, "halves_constants.png")

fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
rr = eda["referee_reliability_by_block"]["dev_2023-2025"]["r"]
axes[0].bar(["referee\nstrictness r"], [rr], color="#c62828")
axes[0].set_ylim(-1, 1); axes[0].axhline(0, color="grey", lw=1)
axes[0].set_title("Referee signal is unusable")
touch = [eda["per_season"][s]["touches_opp_box"]["coverage_pct"] for s in seasons]
axes[1].plot(seasons, touch, marker="o", color="#1565c0")
axes[1].set_ylim(0, 110); axes[1].set_ylabel("matches with touches (%)")
axes[1].set_title("Opp-box-touch coverage")
save(fig, "referee_and_territory.png")
print("charts done ->", OUT)
