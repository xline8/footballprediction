"""Create the three Phase A descriptive charts."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; S=json.load(open(HERE/"eda_summary.json")); CH=HERE/"charts"; CH.mkdir(exist_ok=True)
seasons=["2021","2022","2023","2024","2025","2026"]; lev=S["levels"]
fig,ax=plt.subplots(figsize=(10,5));
for k,label in [("goals","Goals"),("sot","SOT"),("corners","Corners"),("shots","Total shots")]: ax.plot(seasons,[lev[s][k] for s in seasons],marker="o",label=label)
ax.set_title("IS-BestaDeildin levels by season"); ax.set_xlabel("Calendar season"); ax.set_ylabel("Per match"); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(CH/"levels_by_season.png",dpi=120); plt.close(fig)
tr=S["traits"]; names=[k for k,v in tr.items() if v["r"] is not None]
fig,ax=plt.subplots(figsize=(9,6)); ax.barh(names,[tr[k]["r"] for k in names]); ax.axvline(.5,color="r",ls="--"); ax.set_xlim(-.1,1); ax.set_title("Split-half trait reliability (stats era; career pooled)"); fig.tight_layout(); fig.savefig(CH/"trait_reliabilities.png",dpi=120); plt.close(fig)
keys=[("Goals",S["halves_constants"]["goals"]),("SOT",S["halves_constants"]["ShotsOnTarget"]),("Corners",S["halves_constants"]["corners"]),("Shots",S["halves_constants"]["total_shots"]),("Yellows",S["halves_constants"]["yellow_cards"])]
fig,ax=plt.subplots(figsize=(9,4.5)); ax.bar([x for x,_ in keys],[y for _,y in keys]); ax.axhline(.5,color="r",ls="--"); ax.set_ylim(0,.6); ax.set_ylabel("Frozen 1H share"); ax.set_title("Frozen first-half constants"); fig.tight_layout(); fig.savefig(CH/"halves_constants.png",dpi=120); plt.close(fig)
print("charts written")
