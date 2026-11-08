#!/usr/bin/env python3
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "..", "data", "co_primerab_matches.csv"), encoding="utf-8")))
seasons = sorted({row["season"] for row in rows}, key=int)
os.makedirs(os.path.join(HERE, "charts"), exist_ok=True)


def season_rows(season):
    return [row for row in rows if row["season"] == season]


fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(seasons, [sum(int(r["home_goals"]) + int(r["away_goals"]) for r in season_rows(s)) / len(season_rows(s)) for s in seasons], marker="o")
ax[0].set_title("Goals per match by season")
ax[0].grid(alpha=.3)
ax[1].plot(seasons, [sum(int(r["home_goals"]) > int(r["away_goals"]) for r in season_rows(s)) / len(season_rows(s)) for s in seasons], marker="o", label="home win")
ax[1].plot(seasons, [sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in season_rows(s)) / len(season_rows(s)) for s in seasons], marker="s", label="over 2.5")
ax[1].legend()
ax[1].set_title("Outcome rates by season")
ax[1].grid(alpha=.3)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "charts", "levels_by_season.png"), dpi=110)

fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(["GF", "GA"], [0.532, 0.714])
ax.set_title("Split-half trait reliability (dev 2021-2024)")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "charts", "trait_reliability.png"), dpi=110)

fig, ax = plt.subplots(figsize=(6, 4))
shares = []
for season in seasons:
    subset = [r for r in season_rows(season) if r["events_exact"].lower() == "true"]
    shares.append(sum(int(r["goals_1h"]) for r in subset) / max(1, sum(int(r["home_goals"]) + int(r["away_goals"]) for r in subset)))
ax.plot(seasons, shares, marker="o")
ax.axhline(0.4875, ls="--", color="r", label="frozen constant 0.4875")
ax.legend()
ax.set_title("1H goal share by season (exact event matches)")
ax.grid(alpha=.3)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "charts", "halves_constant.png"), dpi=110)
print("charts done")
