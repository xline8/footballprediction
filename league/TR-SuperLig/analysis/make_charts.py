"""Charts for TR-SuperLig EDA (numbers read from the built CSV/EDA JSON)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "tr_matches.csv")))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026","2026/2027"]

def mean(xs):
    xs=[x for x in xs if x==x]; return sum(xs)/len(xs)
def col(r,k):
    v=r[k]; return float(v) if v not in (None,"") else float("nan")

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, keys) in zip(axes.flat, [
    ("goals", ("home_goals","away_goals")), ("SOT", ("ShotsOnTarget_home","ShotsOnTarget_away")),
    ("corners", ("corners_home","corners_away")), ("yellows", ("yellow_home","yellow_away")),
    ("total shots", ("total_shots_home","total_shots_away")), ("xG", ("expected_goals_home","expected_goals_away"))]):
    vals = [mean([col(r,keys[0])+col(r,keys[1]) for r in ROWS if r["season"]==s]) for s in SEASONS]
    ax.bar(SEASONS, vals, color="#37474f"); ax.set_title(f"{name} per match by season")
    ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png", dpi=130); plt.close(fig)

import json
numbers = json.load(open(HERE / "eda_numbers.json"))
rel = numbers["reliability"]
traits = {"possession": rel["possession"], "box-touch for": rel["touches_for"],
          "box-touch ag.": rel["touches_against"], "shots-for": rel["shots_for"],
          "xG-for": rel["xg_for"], "SOT-for": rel["sot_for"], "big chances": rel["bigchance_for"],
          "goals-for": rel["goals_for"], "goals-against": rel["goals_against"], "corners-for": rel["corners_for"],
          "set-play share": numbers["sp_share_rel"][0], "xG/shot": numbers["xg_per_shot_rel"][0],
          "on-target rate": numbers["on_target_rate_rel"][0], "yellows-for": rel["yellows_for"],
          "referee yellows": numbers["ref_rel"][0], "xGOT/shot era": numbers["xgot_rel_era"][0]}
fig, ax = plt.subplots(figsize=(9, 5))
items = sorted(traits.items(), key=lambda kv: kv[1])
ax.barh([k for k,_ in items], [v for _,v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1); ax.set_title("BE trait split-half reliability (career-pooled, 60 splits)")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png", dpi=130); plt.close(fig)

names = ["goals","SOT","corners","total shots","yellow cards"]
shares = [numbers["half_shares"]["goals_half_era"]["share_ratio_of_sums"],
          numbers["half_shares"]["sot"]["share_ratio_of_sums"],
          numbers["half_shares"]["corners"]["share_ratio_of_sums"],
          numbers["half_shares"]["shots"]["share_ratio_of_sums"],
          numbers["half_shares"]["yellows"]["share_ratio_of_sums"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("BE frozen first-half shares — the ONLY halves mechanism (EDA F3)\nper-match true variance of the share measured at ~zero")
for i, v in enumerate(shares): ax.text(i, v+0.015, f"{v:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
