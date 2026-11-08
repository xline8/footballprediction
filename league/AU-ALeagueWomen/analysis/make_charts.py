"""Regenerate the three AUW EDA charts; no fitting or virgin inference."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "auw_matches.csv"
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
rows = list(csv.DictReader(DATA.open()))
seasons = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]
regular = [r for r in rows if r["phase"] == "regular" and r["season"] in seasons]
def mean(s, col):
    x = [float(r[f"home_{col}"]) + float(r[f"away_{col}"]) for r in regular if r["season"] == s]
    return sum(x) / len(x)

fig, ax = plt.subplots(figsize=(9, 5))
for col, label in [("goals", "Goals"), ("total_shots", "Total shots"), ("ShotsOnTarget", "SOT"), ("corners", "Corners"), ("yellow_cards", "Yellows")]:
    ax.plot(seasons, [mean(s, col) for s in seasons], marker="o", label=label)
ax.set_ylabel("match total"); ax.set_title("AUW regular-season levels"); ax.legend(ncol=3); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=150); plt.close(fig)

traits = ["goals", "total_shots", "ShotsOnTarget", "corners", "yellow_cards", "touches_opp_box", "big_chance", "BallPossesion"]
reliability = [0.575, 0.729, 0.646, 0.569, 0.546, 0.876, 0.662, 0.923]
fig, ax = plt.subplots(figsize=(9, 4.5)); ax.bar(range(len(traits)), reliability, color="#4472c4"); ax.axhline(.3, color="gray", ls="--"); ax.set_xticks(range(len(traits)), ["Goals", "Shots", "SOT", "Corners", "Yellows", "Box touches", "Big chance", "Possession"], rotation=35, ha="right"); ax.set_ylim(0, 1); ax.set_ylabel("split-half r"); ax.set_title("Development team-trait reliability"); fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=150); plt.close(fig)

names = ["Goals", "SOT", "Corners", "Total shots", "Yellows"]; shares = [0.459, 0.469, 0.480, 0.467, 0.314]
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.bar(names, shares, color="#70ad47"); ax.axhline(.5, color="gray", ls="--"); ax.set_ylim(0, .6); ax.set_ylabel("1H share"); ax.set_title("Frozen half constants (2023/24–2024/25 regular split rows)"); fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=150); plt.close(fig)
print(f"wrote charts to {OUT}")
