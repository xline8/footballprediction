"""Phase-1 EDA charts for Egypt Premier League."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader(open(HERE.parent/"data"/"eg_matches.csv")))
data=json.load(open(HERE/"eda_numbers.json"))
out=HERE/"charts"; out.mkdir(exist_ok=True)
seasons=data["seasons"]
def mean(vals): return sum(vals)/len(vals) if vals else 0
def vals(s,k):
    return [float(r[f"{k}_home"])+float(r[f"{k}_away"]) for r in rows if r["season"]==s and r[f"{k}_home"] not in ("","None") and r[f"{k}_away"] not in ("","None")]

fig,axes=plt.subplots(2,3,figsize=(11,6))
for ax,(name,key) in zip(axes.flat,[("goals",None),("SOT","ShotsOnTarget"),("corners","corners"),("yellows","yellow_cards"),("total shots","total_shots"),("xG","expected_goals")]):
    ys=[mean([int(r["home_goals"])+int(r["away_goals"]) for r in rows if r["season"]==s]) if key is None else mean(vals(s,key)) for s in seasons]
    ax.bar(seasons,ys,color="#37474f"); ax.set_title(f"{name} per match by season"); ax.tick_params(labelrotation=30,labelsize=7)
fig.tight_layout(); fig.savefig(out/"levels_by_season.png",dpi=130); plt.close(fig)

traits=data["reliability_2023_2025"]
names=["goals for","SOT for","corners for","yellows for","shots for","touches for","possession","big chance"]
keys=["goals_for","sot_for","corners_for","yellows_for","shots_for","touches_for","possession","big_chance"]
fig,ax=plt.subplots(figsize=(9,5)); items=sorted([(n,traits[k]["r"]) for n,k in zip(names,keys)],key=lambda z:(z[1] if z[1] is not None else -1))
ax.barh([x[0] for x in items],[x[1] or 0 for x in items],color="#2e7d32"); ax.axvline(.3,color="grey",ls="--",lw=1); ax.set_title("Egypt trait split-half reliability (2023/2024–2024/2025)")
fig.tight_layout(); fig.savefig(out/"trait_reliability.png",dpi=130); plt.close(fig)

hs=data["half_shares_complete_dev"]; names=["goals","SOT","corners","total shots","yellow cards"]; shares=[hs[k]["share"] for k in ["goals","sot","corners","shots","yellows"]]
fig,ax=plt.subplots(figsize=(8,3.8)); ax.bar(names,shares,color="#37474f"); ax.axhline(.5,color="grey",ls="--",lw=1); ax.set_ylim(0,.6); ax.set_title("Egypt frozen first-half shares — complete dev splits")
for i,v in enumerate(shares): ax.text(i,v+.015,f"{v:.3f}",ha="center")
fig.tight_layout(); fig.savefig(out/"halves_constants.png",dpi=130); plt.close(fig)
print("charts written",sorted(p.name for p in out.glob("*.png")))
