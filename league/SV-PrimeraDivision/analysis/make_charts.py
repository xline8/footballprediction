"""Make the three frozen SV EDA chart families from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "eda_numbers.json").read_text())
I = json.loads((HERE / "inventory_summary.json").read_text())["by_tournament"]
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)

TOURNAMENTS = [s for s in D["by_tournament"]
               if s not in ("pooled_regular", "pooled_regular_incl_partial", "playoffs")]
SHORT = {"2021/2022 - Apertura": "21/22 Ap", "2021/2022 - Clausura": "21/22 Cl",
         "2022/2023 - Apertura": "22/23 Ap", "2022/2023 - Clausura": "22/23 Cl",
         "2023/2024 - Apertura": "23/24 Ap", "2023/2024 - Clausura": "23/24 Cl",
         "2024/2025 - Apertura": "24/25 Ap", "2024/2025 - Clausura": "24/25 Cl",
         "2025/2026 - Apertura": "25/26 Ap", "2025/2026 - Clausura": "25/26 Cl",
         "2026/2027 - Apertura": "26/27 Ap*"}
labels = [SHORT[s] for s in TOURNAMENTS]
B = D["by_tournament"]
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
for a, key, title in zip(ax, ("mean_goals_per_match", "home_win_rate", "over_2_5_rate"),
                         ("goals per match", "home-win rate", "over 2.5 rate")):
    a.bar(labels, [B[s][key] for s in TOURNAMENTS], color="#37474f")
    a.set_title(title); a.tick_params(axis="x", rotation=35, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)
T = D["trait_reliability"]
seasons = list(T["by_tournament"])
fig, ax = plt.subplots(figsize=(8, 4)); x = range(len(seasons) + 1)
ax.plot(list(x), [T["by_tournament"][s]["r_attack"] for s in seasons] + [T["pooled"]["r_attack"]], "o-", label="attack (goals for)")
ax.plot(list(x), [T["by_tournament"][s]["r_defence"] for s in seasons] + [T["pooled"]["r_defence"]], "o-", label="defence (goals against)")
ax.set_xticks(list(x), [SHORT[s] for s in seasons] + ["pooled"], rotation=35)
ax.axhline(0, color="grey", lw=.8); ax.legend(); ax.set_title("Trait split-half reliability (regular phase)")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)
frozen = D["halves"]["frozen_goals_1h_share"]
fig, ax = plt.subplots(figsize=(8, 4))
vals = [D["halves"]["by_tournament"][s]["share"] for s in TOURNAMENTS] + [frozen]
ax.bar(labels + ["pooled"], vals, color="#37474f")
ax.axhline(frozen, color="#c62828", ls="--", label=f"frozen pooled {frozen:.4f}")
ax.legend(); ax.set_ylim(0, .6); ax.set_title("First-half goal share (regular phase)")
ax.tick_params(axis="x", rotation=35)
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written")
