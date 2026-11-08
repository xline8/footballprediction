"""Make the three required Stage 1 GR2 charts from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
seasons = DATA["seasons"]

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
ax = axes[0]
ax.bar(seasons, [DATA["per_season"][s]["goals"] for s in seasons], color="#37474f")
ax.set_title("goals per match"); ax.tick_params(axis="x", labelrotation=30, labelsize=8)
ax = axes[1]
ax.bar(seasons, [DATA["per_season"][s]["ou25_over_rate"] for s in seasons], color="#37474f")
ax.axhline(0.5, color="grey", linestyle="--", linewidth=1)
ax.set_title("OU2.5 over-rate"); ax.tick_params(axis="x", labelrotation=30, labelsize=8)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

traits = dict(DATA["reliability"])
items = sorted(((k, v) for k, v in traits.items() if v is not None), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32")
ax.axvline(.3, color="grey", linestyle="--", linewidth=1)
ax.set_title("GR2 trait split-half reliability (career-pooled, 60 splits)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

half = DATA["half_shares"]["goals"]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(["goals"], [half["share_ratio_of_sums"]], color="#37474f")
ax.axhline(.5, color="grey", linestyle="--", linewidth=1); ax.set_ylim(0, .6)
ax.set_title("GR2 frozen first-half share — goals, validated event subset (n=%d)" % half["n"])
ax.text(0, half["share_ratio_of_sums"] + .015, f"{half['share_ratio_of_sums']:.4f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
