"""Make the three frozen DZ Ligue 1 EDA chart families."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "eda_numbers.json").read_text())
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
SEASONS = [s for s in D["by_season"] if s not in ("pooled_completed", "pooled_incl_partial")]
SHORT = {s: s.replace("20", "", 1).replace("/20", "/") for s in SEASONS}
labels = [SHORT[s] + ("*" if s == "2026/2027" else "") for s in SEASONS]
B = D["by_season"]

fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for a, key, title in zip((ax[0], ax[2]), ("mean_goals_per_match", "over_2_5_rate"),
                         ("goals per match", "over 2.5 rate")):
    a.bar(labels, [B[s][key] for s in SEASONS], color="#37474f")
    a.set_title(title); a.tick_params(axis="x", rotation=35, labelsize=7)
ax[1].bar([i - .18 for i in range(len(SEASONS))], [B[s]["home_goals_per_match"] for s in SEASONS],
          width=.36, label="home goals", color="#37474f")
ax[1].bar([i + .18 for i in range(len(SEASONS))], [B[s]["away_goals_per_match"] for s in SEASONS],
          width=.36, label="away goals", color="#c62828")
ax[1].set_xticks(range(len(SEASONS)), labels, rotation=35); ax[1].set_title("home/away goals per match")
ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

T = D["trait_reliability"]
fig, ax = plt.subplots(figsize=(8, 4)); x = range(len(SEASONS) + 1)
ax.plot(list(x), [T["by_season"][s]["r_attack"] for s in SEASONS] + [T["pooled_completed"]["r_attack"]], "o-", label="attack (goals for)")
ax.plot(list(x), [T["by_season"][s]["r_defence"] for s in SEASONS] + [T["pooled_completed"]["r_defence"]], "o-", label="defence (goals against)")
ax.set_xticks(list(x), labels + ["pooled"], rotation=35)
ax.axhline(0, color="grey", lw=.8); ax.legend(); ax.set_title("Trait split-half reliability (regular phase)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

frozen = D["halves"]["frozen_goals_1h_share"]
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(labels + ["pooled"], [D["halves"]["by_season"][s]["share"] for s in SEASONS] + [frozen], color="#37474f")
ax.axhline(frozen, color="#c62828", ls="--", label=f"frozen pooled {frozen:.4f}")
ax.legend(); ax.set_ylim(0, .6); ax.set_title("First-half goal share (regular phase)"); ax.tick_params(axis="x", rotation=35)
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written")
