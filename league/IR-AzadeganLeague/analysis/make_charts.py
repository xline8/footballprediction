"""Make the Phase-1 charts from frozen JSON summaries only."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
E = json.loads((HERE / "eda_summary.json").read_text())
seasons = list(E["season_levels"])


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)


levels = E["season_levels"]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(seasons, [levels[s]["goals_per_match"] for s in seasons], marker="o", label="goals/match")
ax.set_ylabel("goals per match")
ax2 = ax.twinx()
ax2.plot(seasons, [levels[s]["over2_5_pct"] for s in seasons], marker="s", color="#c62828", label="over-2.5 %")
ax2.set_ylabel("over-2.5 %")
ax.set_title("IR Azadegan League levels by season")
fig.legend(loc="upper center", ncol=2)
save(fig, "levels_by_season.png")

reliability = E["reliability"]
items = [(key, value["r_chronological"]) for key, value in reliability.items() if value.get("r_chronological") is not None]
items.sort(key=lambda item: item[1])
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.barh([item[0] for item in items], [item[1] for item in items], color="#2e7d32")
ax.axvline(0.3, color="grey", linestyle="--")
ax.set_xlim(-1, 1)
ax.set_title("Team-trait split-half reliability (goals + reds)")
save(fig, "trait_reliability.png")

halves = E["halves"]["goals"]
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.bar(["1H share", "observed var", "noise floor", "true var"],
       [halves["share_1h"], halves["observed_variance"], halves["noise_floor_per_match"], halves["true_variance"]],
       color=["#2e7d32", "#757575", "#bdbdbd", "#c62828"])
ax.set_title("Goals 1H share: observed variance vs binomial noise floor (true var <= 0)")
save(fig, "halves_constants.png")
print("charts written to", OUT)
