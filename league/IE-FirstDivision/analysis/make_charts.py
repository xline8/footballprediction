"""Write the Phase-A EDA charts from the built data and EDA ledger."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = [r for r in csv.DictReader(open(HERE.parent / "data" / "ie_first_division_matches.csv")) if r["phase"] == "regular"]
EDA = json.load(open(HERE / "eda_numbers.json"))
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
SEASONS = ["2021", "2022", "2023", "2024", "2025"]

def avg_goals(season):
    vals = [int(r["home_goals"]) + int(r["away_goals"]) for r in DATA if r["season"] == season]
    return sum(vals) / len(vals)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].bar(SEASONS, [avg_goals(s) for s in SEASONS], color="#37474f")
axes[0].set_title("Goals per match by season (regular)")
axes[0].tick_params(labelrotation=30, labelsize=8)
axes[1].bar(SEASONS, [EDA["per_season"][s]["over25_pct"] for s in SEASONS], color="#37474f")
axes[1].set_title("Over 2.5 % by season (regular)")
axes[1].tick_params(labelrotation=30, labelsize=8)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

traits = {"goals-for": EDA["reliability"]["goals"]["for"]["r"],
          "goals-against": EDA["reliability"]["goals"]["against"]["r"]}
items = sorted(traits.items(), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.barh([k for k, _ in items], [v for _, v in items], color="#2e7d32")
ax.axvline(0.3, color="grey", ls="--", lw=1)
ax.set_title("IE First Division team-trait split-half reliability (goals)")
ax.set_xlim(0, 1.0)
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

hs = EDA["half_shares_by_season"]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(list(hs), [hs[s]["share"] for s in SEASONS], color="#37474f")
ax.axhline(EDA["halves_constants"]["goals_1h_share"], color="red", ls="--", lw=1, label=f"frozen {EDA['halves_constants']['goals_1h_share']}")
ax.axhline(0.5, color="grey", ls=":", lw=1)
ax.set_ylim(0, 0.6); ax.set_title("First-half share of goals by season (events; presentation only)")
ax.legend()
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
