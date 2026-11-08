"""Charts for BG-SecondLeague EDA (levels by season, trait reliability).
Halves/referee/tier charts from the J1 set are NOT produced: this league
has no period splits and no referee data (see DATA_UNDERSTANDING.md)."""
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "bg2_matches.csv")))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)

seasons = sorted(set(r["season"] for r in ROWS))
gm, ov = [], []
for s in seasons:
    ss = [r for r in ROWS if r["season"] == s]
    gm.append(sum(int(r["home_goals"]) + int(r["away_goals"]) for r in ss) / len(ss))
    ov.append(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in ss) / len(ss))
fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
ax[0].plot(seasons, gm, marker="o"); ax[0].set_title("Goals per match by season"); ax[0].tick_params(labelrotation=30)
ax[1].plot(seasons, ov, marker="o"); ax[1].set_title("Over 2.5 rate by season"); ax[1].tick_params(labelrotation=30)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=110); plt.close(fig)

# split-half trait reliability (odd/even match order within season)
import numpy as np
def sh(stat):
    xs, ys = [], []
    for s in seasons:
        ss = sorted([r for r in ROWS if r["season"] == s], key=lambda r: r["date"])
        teams = defaultdict(lambda: [[], []])
        for i, r in enumerate(ss):
            teams[r["home_team"]][i % 2].append((int(r["home_goals"]), int(r["away_goals"])))
            teams[r["away_team"]][i % 2].append((int(r["away_goals"]), int(r["home_goals"])))
        for v in teams.values():
            if len(v[0]) >= 5 and len(v[1]) >= 5:
                k = 0 if stat == "gf" else 1
                xs.append(sum(x[k] for x in v[0]) / len(v[0])); ys.append(sum(x[k] for x in v[1]) / len(v[1]))
    return xs, ys
fig, ax = plt.subplots(1, 2, figsize=(8, 3.5))
for a, stat, t in ((ax[0], "gf", "Goals for"), (ax[1], "ga", "Goals against")):
    xs, ys = sh(stat); r = float(np.corrcoef(xs, ys)[0, 1])
    a.scatter(xs, ys, s=12); a.set_title(f"{t} split-half r={r:.2f} (n={len(xs)})")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=110); plt.close(fig)
print("charts written")
