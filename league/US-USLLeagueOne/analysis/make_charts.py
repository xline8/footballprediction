import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
e = json.loads((HERE / "eda_summary.json").read_text())

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)

s = e["seasons"]
x = list(s)
fig, ax = plt.subplots(figsize=(8, 4))
for k, label in [("goals", "Goals"), ("sot", "SOT"), ("corners", "Corners")]:
    ax.plot(x, [s[y][k] for y in x], marker="o", label=label)
ax.set_title("USL League One levels by season")
ax.legend()
save(fig, "levels_by_season.png")

r = e["reliability"]
fig, ax = plt.subplots(figsize=(8, 5))
names = list(r)
ax.barh(names, [r[n]["r"] for n in names])
ax.axvline(.3, color="grey", ls="--")
ax.set_title("USL League One split-half trait reliability")
save(fig, "trait_reliability.png")

h = e["halves"]["2023_2025"]
names = ["goals", "sot", "corners", "shots", "yellow"]
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(names, [h[n]["share"] for n in names])
ax.axhline(.5, color="grey", ls="--")
ax.set_title("USL League One first-half shares")
save(fig, "halves_constants.png")

fig, ax = plt.subplots(1, 2, figsize=(9, 4))
ax[0].bar(["referee r"], [e["referees"]["r"]])
ax[0].set_ylim(0, 1)
c = e["corners_territorial"]
ax[1].bar(["box touches", "possession"],
          [c["corr_corners_boxtouches"], c["corr_corners_possession"]])
ax[1].set_title("Corners correlations")
save(fig, "referee_and_territory.png")

fig, ax = plt.subplots(figsize=(9, 4))
counts = [len(e["new_teams_by_season"][y]) for y in x]
ax.bar(x, counts)
ax.set_title("New teams by season (churn analogue)")
save(fig, "churn_new_teams.png")
