"""Charts for AE-ProLeague from eda_numbers.json (frozen EDA numbers)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
N = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
seasons = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]
lv = N["levels"]

fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, key, title in zip(axes.flat, ("goals", "sot", "corners", "shots", "cards_stats", "home_win"),
                          ("Goals/match", "SOT/match", "Corners/match", "Total shots/match", "Yellows (stats)/match", "Home-win rate")):
    ax.plot(seasons, [lv[s][key] for s in seasons], marker="o")
    ax.set_title(title); ax.tick_params(axis="x", rotation=30)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=110); plt.close(fig)

rel = N["reliability"]
names = [k for k in rel if isinstance(rel[k], dict) and "r" in rel[k] and rel[k]["r"] is not None]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.barh(names, [rel[k]["r"] for k in names])
ax.axvline(0, color="k", lw=0.8); ax.set_title("Split-half trait reliability (career-pooled)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=110); plt.close(fig)

h = N["halves"]
keys = ["ShotsOnTarget", "corners", "total_shots", "yellow_cards"]
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["goals (events)"] + keys, [N["halves"]["goals_events"]["share"]] + [h[k]["share"] for k in keys])
ax.set_title("Frozen 1H shares (splits era 2023/2024-2025/2026; goals from events)")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=110); plt.close(fig)
print("charts written")
