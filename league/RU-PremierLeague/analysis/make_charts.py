import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/"eda_numbers.json").read_text())
OUT=HERE/"charts"; OUT.mkdir(exist_ok=True); seasons=D["seasons"]

fig,axes=plt.subplots(2,3,figsize=(11,6))
for ax,(key,label) in zip(axes.flat,[("goals","goals"),("sot","SOT"),("corners","corners"),("cards_stats","stats cards"),("total_shots","total shots"),("xg","stats xG")]):
    ax.bar(seasons,[D["per_season"][s][key] or 0 for s in seasons],color="#37474f")
    ax.set_title(label+" per match"); ax.tick_params(axis="x",rotation=30,labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png",dpi=130); plt.close(fig)

items=sorted((k,v) for k,v in D["reliability"].items() if v is not None)
fig,ax=plt.subplots(figsize=(9,6)); ax.barh([x[0] for x in items],[x[1] for x in items],color="#2e7d32")
ax.axvline(.3,color="grey",ls="--"); ax.set_title("RU Premier League trait split-half reliability")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=130); plt.close(fig)

keys=["goals","ShotsOnTarget","corners","total_shots","yellow_cards"]; names=["goals","SOT","corners","total shots","yellow cards"]
vals=[D["half_shares"][k].get("share_ratio_of_sums",0) for k in keys]
fig,ax=plt.subplots(figsize=(8,3.8)); ax.bar(names,vals,color="#37474f"); ax.axhline(.5,color="grey",ls="--"); ax.set_ylim(0,.6)
ax.set_title("Frozen first-half shares — complete split era")
for i,v in enumerate(vals): ax.text(i,v+.015,f"{v:.3f}",ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=130); plt.close(fig)
print("charts written")

