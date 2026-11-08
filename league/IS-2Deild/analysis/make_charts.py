"""Plot only frozen numbers from eda_summary.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
EDA = json.loads((HERE / "eda_summary.json").read_text())
SEASONS = list(EDA["seasons"])

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(SEASONS, [EDA["seasons"][s]["goals"] for s in SEASONS], marker="o", label="goals/match")
ax.plot(SEASONS, [EDA["seasons"][s]["home_win"] for s in SEASONS], marker="s", label="home win")
ax.plot(SEASONS, [EDA["seasons"][s]["over25"] for s in SEASONS], marker="^", label="OU2.5 over")
ax.set_title("IS-2Deild levels by season"); ax.legend(); save(fig, "levels_by_season.png")

fig, ax = plt.subplots(figsize=(6, 4))
labels = ["goals for", "goals against"]; values = [EDA["reliability"]["goals_for_r"], EDA["reliability"]["goals_against_r"]]
ax.bar(labels, values, color="#455a64"); ax.set_ylim(0, 1); ax.set_ylabel("split-half r"); ax.set_title("Trait reliability")
for i, v in enumerate(values): ax.text(i, v + .02, f"{v:.3f}", ha="center")
save(fig, "trait_reliability.png")

fig, ax = plt.subplots(figsize=(8, 4))
shares = [EDA["seasons"][s]["goals_1h"] / EDA["seasons"][s]["total_goals"] for s in SEASONS]
ax.plot(SEASONS, shares, marker="o", label="season 1H share")
ax.axhline(EDA["pooled"]["goals_1h_share"], color="black", ls="--", label="pooled frozen constant")
ax.set_ylim(0, .6); ax.set_ylabel("share"); ax.set_title("First-half goal share"); ax.legend()
save(fig, "halves_constants.png")
