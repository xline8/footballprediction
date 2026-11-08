"""Create the Phase A descriptive charts for SCO Championship."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
SUMMARY = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
SEASONS = SUMMARY["seasons"]
PER = SUMMARY["per_season"]

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (label, key) in zip(axes.flat, [
    ("goals", "goals_per_match"), ("SOT", "sot_per_match"),
    ("corners", "corners_per_match"), ("total shots", "total_shots_per_match"),
    ("event yellows", "event_yellows_per_match"), ("home goal share", "home_goal_share"),
]):
    values = [PER[s][key] for s in SEASONS]
    ax.bar(SEASONS, values, color="#37474f")
    ax.set_title(f"{label} by season")
    ax.tick_params(axis="x", labelrotation=30, labelsize=7)
fig.tight_layout()
fig.savefig(OUT / "levels_by_season.png", dpi=130)
plt.close(fig)

traits = {
    "goals-for": SUMMARY["reliability"]["goals"]["mean_for_r"],
    "goals-against": SUMMARY["reliability"]["goals"]["mean_against_r"],
    "SOT-for": SUMMARY["reliability"]["sot"]["mean_for_r"],
    "SOT-against": SUMMARY["reliability"]["sot"]["mean_against_r"],
    "corners-for": SUMMARY["reliability"]["corners"]["mean_for_r"],
    "corners-against": SUMMARY["reliability"]["corners"]["mean_against_r"],
    "shots-for": SUMMARY["reliability"]["total_shots"]["mean_for_r"],
    "shots-against": SUMMARY["reliability"]["total_shots"]["mean_against_r"],
    "yellows-for": SUMMARY["reliability"]["event_yellows"]["mean_for_r"],
    "yellows-against": SUMMARY["reliability"]["event_yellows"]["mean_against_r"],
    "possession-for": SUMMARY["reliability"]["possession"]["mean_for_r"],
    "possession-against": SUMMARY["reliability"]["possession"]["mean_against_r"],
}
items = sorted(traits.items(), key=lambda item: item[1])
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh([x[0] for x in items], [x[1] for x in items], color="#2e7d32")
ax.axvline(0.3, color="grey", linestyle="--", linewidth=1)
ax.set_xlim(-0.3, 1.0)
ax.set_title("SCO Championship split-half reliability")
fig.tight_layout()
fig.savefig(OUT / "trait_reliability.png", dpi=130)
plt.close(fig)

names = ["goals", "yellow cards"]
shares = [SUMMARY["halves"]["goals"]["pooled"]["share"], SUMMARY["halves"]["event_yellows"]["pooled"]["share"]]
fig, ax = plt.subplots(figsize=(6, 3.8))
ax.bar(names, shares, color="#37474f")
ax.axhline(0.5, color="grey", linestyle="--", linewidth=1)
ax.set_ylim(0, 0.6)
ax.set_title("Frozen first-half shares — the only halves mechanism")
for i, value in enumerate(shares):
    ax.text(i, value + 0.015, f"{value:.4f}", ha="center")
fig.tight_layout()
fig.savefig(OUT / "halves_constants.png", dpi=130)
plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
