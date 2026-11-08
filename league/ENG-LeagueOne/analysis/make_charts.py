"""Charts for ENG-LeagueOne EDA (from the built CSV; frozen numbers in EDA.md)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "engl1_matches.csv")))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026","2026/2027"]

def mean(xs): return sum(xs)/len(xs)
def col(r,k):
    v=r.get(k)
    return float(v) if v not in (None,"") else 0.0

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, keys) in zip(axes.flat, [
    ("goals", ("home_goals","away_goals")), ("SOT", ("ShotsOnTarget_home","ShotsOnTarget_away")),
    ("corners", ("corners_home","corners_away")), ("yellows", ("yellow_home","yellow_away")),
    ("total shots", ("total_shots_home","total_shots_away")), ("xG", ("expected_goals_home","expected_goals_away"))]):
    vals = [mean([col(r,keys[0])+col(r,keys[1]) for r in ROWS if r["season"]==s and r.get(keys[0]) not in (None,"")]) if any(r["season"]==s and r.get(keys[0]) not in (None,"") for r in ROWS) else 0.0 for s in SEASONS]
    ax.bar(SEASONS, vals, color="#37474f"); ax.set_title(f"{name} per match by season")
    ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png", dpi=130); plt.close(fig)

traits = {"shots-for":0.886,"xG-for":0.913,"SOT-for":0.799,"goals-for":0.605,
          "corners-for":0.615,"yellows-for":0.309,"box-touch for":0.870,"big-chance for":0.791,
          "possession":0.962,"set-play share":0.456,"referee yellows":0.305,"xG/shot":0.457,
          "xGOT/shot era": -0.094}
fig, ax = plt.subplots(figsize=(9, 5))
items = sorted(traits.items(), key=lambda kv: kv[1])
ax.barh([k for k,_ in items], [v for _,v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1); ax.set_title("ENG-LeagueOne trait split-half reliability (career-pooled)")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png", dpi=130); plt.close(fig)

names = ["goals","SOT","corners","total shots","yellow cards"]; shares = [0.4425,0.4414,0.4672,0.4551,0.3277]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("ENG-LeagueOne frozen first-half shares — the ONLY halves mechanism (EDA F3)\nper-match true variance of the share measured at ~zero")
for i, v in enumerate(shares): ax.text(i, v+0.015, f"{v:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
