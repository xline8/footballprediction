#!/usr/bin/env python3
"""Charts for PT-LigaPortugal EDA (from eda_summary.json, frozen numbers)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
seasons = sorted(S["seasons"])

fig, axes = plt.subplots(2, 3, figsize=(13, 7))
for ax, (key, title) in zip(axes.flat, [
    ("mean_total_goals", "Goals / match"), ("mean_sot_total", "SOT / match"),
    ("mean_corners_total", "Corners / match"), ("mean_yellows_total", "Yellows / match"),
    ("mean_total_shots", "Total shots / match"), ("mean_xg_total", "xG / match")]):
    ax.plot(seasons, [S["seasons"][s][key] for s in seasons], marker="o")
    ax.set_title(title); ax.tick_params(axis="x", rotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=110); plt.close(fig)

tr = S["trait_split_half"]
names = sorted(tr, key=lambda k: tr[k]["r"] or 0)
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(names, [tr[k]["r"] or 0 for k in names])
ax.axvline(0.3, color="r", ls="--", lw=1); ax.set_xlabel("split-half r")
ax.set_title("PT trait reliabilities (team, chronological split-half)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=110); plt.close(fig)

hs = S["half_shares"]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(list(hs), [hs[k]["ratio_of_sums"] for k in hs])
ax.set_ylabel("1H share (ratio of sums, 2023/24-2025/26)")
ax.set_title("Frozen half-share constants")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=110); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
cov = S["referee_coverage"]
ax.bar(list(cov), [cov[s] / S["seasons"][s]["n"] * 100 for s in seasons])
ax.set_ylabel("referee coverage %"); ax.set_title("Referee coverage by season")
fig.tight_layout(); fig.savefig(OUT / "referee_coverage.png", dpi=110); plt.close(fig)
print("charts written to", OUT)
