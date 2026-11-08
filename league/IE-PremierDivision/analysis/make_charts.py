"""Write the three Phase-A EDA charts from the built data and EDA ledger."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = list(csv.DictReader(open(HERE.parent / "data" / "ie_matches.csv")))
EDA = json.load(open(HERE / "eda_numbers.json"))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021", "2022", "2023", "2024", "2025"]

def avg_total(season, key):
    vals = []
    for r in DATA:
        if r["season"] != season: continue
        if key == "goals": vals.append(int(r["home_goals"])+int(r["away_goals"]))
        elif r.get(f"{key}_home") not in (None, "") and r.get(f"{key}_away") not in (None, ""):
            vals.append(float(r[f"{key}_home"])+float(r[f"{key}_away"]))
    return sum(vals)/len(vals) if vals else 0

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, key) in zip(axes.flat, [("goals", "goals"), ("SOT", "ShotsOnTarget"), ("corners", "corners"), ("yellows", "yellow"), ("total shots", "total_shots"), ("xG", "expected_goals")]):
    vals = [avg_total(s, key) for s in SEASONS]
    ax.bar(SEASONS, vals, color="#37474f"); ax.set_title(f"{name} per match by season")
    ax.tick_params(labelrotation=30, labelsize=8)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

traits = {}
for market in EDA["reliability"]:
    traits[f"{market}-for"] = EDA["reliability"][market]["for"]["r"]
for name, value in [("touches-against", EDA["reliability"]["touches"]["against"]["r"]), ("big-chance-against", EDA["reliability"]["big_chance"]["against"]["r"]), ("referee yellows", EDA["referee_reliability_events"]["r"])]: traits[name] = value
items = sorted([(k, v) for k, v in traits.items() if v is not None], key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 5)); ax.barh([k for k, _ in items], [v for _, v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1); ax.set_title("IE Premier Division event/stat trait split-half reliability")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

hs = EDA["halves_constants"]
names = ["goals", "SOT", "corners", "total shots", "yellow cards"]
shares = [hs["goals_1h_share"], hs["sot_1h_share"], hs["corners_1h_share"], hs["total_shots_1h_share"], hs["yellow_cards_1h_share"]]
fig, ax = plt.subplots(figsize=(8, 3.8)); ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("IE frozen first-half shares — presentation only")
for i, v in enumerate(shares): ax.text(i, v+0.015, f"{v:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
