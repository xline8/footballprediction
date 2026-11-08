"""Charts for SA-ProLeague EDA (from the built CSV; frozen numbers in EDA.md)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "sa_matches.csv")))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026","2026/2027"]

def mean(xs): return sum(xs)/len(xs)
def col(r,k): return float(r[k])

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, keys) in zip(axes.flat, [
    ("goals", ("home_goals","away_goals")), ("SOT", ("ShotsOnTarget_home","ShotsOnTarget_away")),
    ("corners", ("corners_home","corners_away")), ("yellows", ("yellow_home","yellow_away")),
    ("total shots", ("total_shots_home","total_shots_away")), ("xG", ("expected_goals_home","expected_goals_away"))]):
    vals = [mean([col(r,keys[0])+col(r,keys[1]) for r in ROWS if r["season"]==s and r[keys[0]] not in ("", "None")]) for s in SEASONS]
    ax.bar(SEASONS, vals, color="#37474f"); ax.set_title(f"{name} per match by season")
    ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png", dpi=130); plt.close(fig)

traits = {"shots-for":0.929,"xG-for":0.900,"SOT-for":0.887,"goals-for":0.806,
          "corners-for":0.910,"yellows-for (events)":0.264,"box-touch for":0.953,"big-chance for":0.878,
          "possession":0.962,"set-play share":0.514,"referee yellows":-0.279,"xG/shot":0.654,
          "xGOT/shot 24/25+":0.545}
fig, ax = plt.subplots(figsize=(9, 5))
items = sorted(traits.items(), key=lambda kv: kv[1])
ax.barh([k for k,_ in items], [v for _,v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1); ax.set_title("SA trait split-half reliability (post-break era 2023/2024+)")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png", dpi=130); plt.close(fig)

names = ["goals","SOT","corners","total shots","yellow cards"]; shares = [0.4251,0.4469,0.4740,0.4559,0.3509]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("SA frozen first-half shares — the ONLY halves mechanism (EDA F3)\nper-match true variance of the share measured at ~zero")
for i, v in enumerate(shares): ax.text(i, v+0.015, f"{v:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
