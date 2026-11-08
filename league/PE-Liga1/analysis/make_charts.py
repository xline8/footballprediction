"""Charts for PE-Liga1 EDA (step 4). Reads eda_summary.json only."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
blocks = list(S["levels_by_block"].keys())
short = [b.replace(" - ", "\n") for b in blocks]

def series(key):
    return [S["levels_by_block"][b][key] for b in blocks]

fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for ax, key, title in zip(axes.flat, ["goals", "sot", "corners", "total_shots", "ev_yellow_inc2nd", "home_win_rate"],
                          ["Goals/match", "SOT/match (stats rows)", "Corners/match (stats rows)",
                           "Total shots raw/match (mixed def.)", "Event yellows/match (broken pre-2023)", "Home win rate"]):
    ax.plot(short, series(key), marker="o"); ax.set_title(title); ax.tick_params(labelsize=7)
    ax.axvline(7.5, color="grey", ls="--", lw=0.8)
fig.suptitle("PE-Liga1 levels by tournament block (regular, non-awarded; dashed = virgin 2025)")
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=110); plt.close(fig)

tr = S["traits"]
labels = ["goals_for", "goals_against", "sot_for", "sot_against", "corners_for", "corners_against",
          "shots_for", "shots_against", "touches_for", "touches_against", "poss_for", "bigchance_for"]
vals = [tr[k]["r"] for k in labels]
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(range(len(labels)), vals); ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
ax.axhline(0.3, color="grey", ls="--", lw=0.8); ax.set_ylabel("split-half r")
ax.set_title("PE-Liga1 team trait reliability (career split-half; cards traits in EDA.md, era 2023+)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=110); plt.close(fig)

h = S["halves"]
names = ["goals", "sot", "corners", "total_shots", "cards_events_2023plus"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(names, [h[k]["pooled_share"] for k in names])
ax.set_ylabel("1H share of FT total"); ax.set_title("PE-Liga1 frozen half-share constants (presentation only)")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=110); plt.close(fig)

alt = S["altitude"]["by_class"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar([a["class"] for a in alt], [a["home_edge_gd"] for a in alt])
ax.set_ylabel("home GD per match"); ax.set_title("PE-Liga1 home edge by home-city altitude class (no altitude premium)")
fig.tight_layout(); fig.savefig(OUT / "altitude_home_edge.png", dpi=110); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
