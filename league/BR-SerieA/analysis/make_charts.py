"""Charts for BR-SerieA EDA (from the built CSV; frozen numbers in EDA.md)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "br_matches.csv")))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021","2022","2023","2024","2025","2026"]

def mean(xs): return sum(xs)/len(xs)
def col(r,k):
    v = r[k]
    return float(v) if v not in ("", None) else None

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, keys) in zip(axes.flat, [
    ("goals", ("home_goals","away_goals")), ("SOT", ("ShotsOnTarget_home","ShotsOnTarget_away")),
    ("corners", ("corners_home","corners_away")), ("unified yellows", ("yellow_unified_home","yellow_unified_away")),
    ("total shots", ("total_shots_home","total_shots_away")), ("xG (covered matches)", ("expected_goals_home","expected_goals_away"))]):
    vals = []
    for s in SEASONS:
        tot = [col(r,keys[0])+col(r,keys[1]) for r in ROWS if r["season"]==s and col(r,keys[0]) is not None and col(r,keys[1]) is not None]
        vals.append(mean(tot))
    ax.bar(SEASONS, vals, color="#37474f"); ax.set_title(f"{name} per match by season")
    ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png", dpi=130); plt.close(fig)

traits = {"shots-for":0.697,"xG-for":0.708,"SOT-for":0.749,"goals-for":0.736,"goals-against":0.659,
          "corners-for":0.597,"yellows-for (stats era-mixed)":0.708,"box-touch for":0.803,"box-touch ag.":0.789,
          "possession":0.928,"big chances":0.785,"set-play share":0.473,"xG/shot":0.571,
          "referee yellows":0.353,"xGOT/shot era 2025+":0.348,"on-target rate":0.264,"finishing":0.110}
fig, ax = plt.subplots(figsize=(9, 5))
items = sorted(traits.items(), key=lambda kv: kv[1])
ax.barh([k for k,_ in items], [v for _,v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1); ax.set_title("BR trait split-half reliability (career-pooled, 60 splits)")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png", dpi=130); plt.close(fig)

names = ["goals","SOT","corners","total shots","yellow cards"]; shares = [0.455,0.462,0.474,0.463,0.366]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("BR frozen first-half shares — the ONLY halves mechanism (EDA F3)\nper-match true variance of the share measured at ~zero")
for i, v in enumerate(shares): ax.text(i, v+0.015, f"{v:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
