"""Charts for Costa Rica Primera Division EDA (replicates the J1 chart set
where the data exists; no SOT/corners/shots/xG charts — those targets do
not exist in this league).

Reads analysis/eda_summary.json + data/cr_matches.csv, writes PNGs to
analysis/charts/. Usage: python3 league/CR-PrimeraDivision/analysis/make_charts.py
"""
import json
import os
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
EDA = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)

SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
SHORT = ["21/22", "22/23", "23/24", "24/25", "25/26", "26/27*"]
REG = EDA["levels_regular"]


def safe_save(fig, path, tries=40):
    for _ in range(tries):
        try:
            tmp = str(path) + ".tmp%d.png" % os.getpid()
            fig.savefig(tmp, dpi=120, bbox_inches="tight", format="png")
            if os.path.getsize(tmp) > 0:
                os.replace(tmp, path)
                return
        except (PermissionError, OSError):
            time.sleep(1.0)
    raise IOError("could not write %s" % path)


# 1. Levels by season: goals, yellows (unreliable era shaded), home-win %
fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
ax = axes[0]
ax.plot(SHORT, [REG[s]["goals_per_match"] for s in SEASONS], "o-")
ax.axhline(EDA["levels_pooled"]["regular"]["goals_per_match"], ls="--", lw=1, color="grey")
ax.set_ylabel("Goals / match")
ax.set_title("Costa Rica Primera Division — levels by season (regular season only)")
ax.grid(alpha=0.3)
ax = axes[1]
ax.plot(SHORT, [REG[s]["yellows_per_match"] for s in SEASONS], "o-", color="darkgoldenrod")
ax.axvspan(-0.5, 1.5, color="red", alpha=0.12)
ax.text(0.5, 4.6, "card feed unreliable\n(2021/22–2022/23)", ha="center", fontsize=8, color="darkred")
ax.set_ylabel("Yellows / match")
ax.grid(alpha=0.3)
ax = axes[2]
ax.plot(SHORT, [100 * REG[s]["home_win_pct"] for s in SEASONS], "o-", color="green")
ax.plot(SHORT, [100 * REG[s]["draw_pct"] for s in SEASONS], "s-", color="grey")
ax.set_ylabel("Home win / draw %")
ax.set_xlabel("Season (* 2026/2027 is a partial season in progress)")
ax.grid(alpha=0.3)
ax.legend(["Home win %", "Draw %"], fontsize=8)
safe_save(fig, OUT / "levels_by_season.png")
plt.close(fig)

# 2. Trait reliabilities (split-half r_random, with odd/even as markers)
rel = EDA["reliability"]
labels = ["Goals for", "Goals against", "Yellows for", "Yellows against"]
r_rand = [rel["goals_for"]["r_random"], rel["goals_against"]["r_random"],
          rel["yellows_for"]["r_random"], rel["yellows_against"]["r_random"]]
r_oe = [rel["goals_for"]["r_odd_even"], rel["goals_against"]["r_odd_even"],
        rel["yellows_for"]["r_odd_even"], rel["yellows_against"]["r_odd_even"]]
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(labels, r_rand, color="steelblue")
ax.plot(r_oe, labels, "D", color="darkred", label="odd/even split")
ax.axvline(0.3, ls="--", lw=1, color="grey")
ax.set_xlim(0, 1)
ax.set_xlabel("Split-half r (career-pooled, >=24 matches/team)")
ax.set_title("Team-trait reliabilities — Costa Rica Primera Division")
ax.legend(fontsize=8)
ax.grid(axis="x", alpha=0.3)
safe_save(fig, OUT / "trait_reliability.png")
plt.close(fig)

# 3. Halves constants: 1H shares by season with the pooled line
fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
ax = axes[0]
g = EDA["halves"]["goals"]["per_season"]
ax.plot(SHORT, [g[s]["share"] for s in SEASONS], "o-")
ax.axhline(EDA["halves"]["goals"]["pooled_share"], ls="--", lw=1, color="grey")
ax.set_title("Goals 1H share\n(pooled %.3f)" % EDA["halves"]["goals"]["pooled_share"])
ax.set_ylabel("1H share of total")
ax.grid(alpha=0.3)
ax = axes[1]
y = EDA["halves"]["yellows_reliable"]["per_season"]
vals = [y[s]["share"] if y[s]["share"] is not None else float("nan") for s in SEASONS]
ax.plot(SHORT, vals, "o-", color="darkgoldenrod")
ax.axhline(EDA["halves"]["yellows_reliable"]["pooled_share"], ls="--", lw=1, color="grey")
ax.set_title("Yellows 1H share, reliable era\n(pooled %.3f)"
             % EDA["halves"]["yellows_reliable"]["pooled_share"])
ax.grid(alpha=0.3)
fig.suptitle("Frozen halves constants — Costa Rica Primera Division")
safe_save(fig, OUT / "halves_constants.png")
plt.close(fig)

print("charts written:", sorted(p.name for p in OUT.glob("*.png")))
