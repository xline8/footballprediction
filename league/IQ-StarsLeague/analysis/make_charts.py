"""Generate the scores-only Phase A chart set from dev-era EDA constants."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
seasons = ["2021/22", "2022/23", "2023/24", "2024/25"]
goals = [1.981, 2.180, 2.301, 2.263]
ou = [0.343, 0.400, 0.404, 0.392]

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(seasons, goals, marker="o", label="goals / match")
ax.plot(seasons, ou, marker="s", label="OU2.5 over-rate")
ax.set_ylim(0, 2.6); ax.set_title("IQ-StarsLeague dev levels by season")
ax.legend(); save(fig, "levels_by_season.png")

fig, ax = plt.subplots(figsize=(7, 4))
labels = ["goals-for", "goals-against"]
vals = [0.769, 0.772]
ax.bar(labels, vals, color=["#2e7d32", "#1565c0"])
ax.axhline(0, color="black", lw=.8); ax.set_ylim(0, .9)
ax.set_title("Dev team-goal trait split-half reliability")
save(fig, "trait_reliability.png")

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["goals"], [0.4323308271], color="#37474f")
ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6); ax.set_title("Frozen first-half constant (presentation only)")
ax.text(0, .45, "0.4323", ha="center"); save(fig, "halves_constants.png")
