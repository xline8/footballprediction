"""Charts for FI-Veikkausliiga EDA (levels by season, trait reliability, halves constants)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
S=json.load(open(HERE/"eda_summary.json")); CH=HERE/"charts"; CH.mkdir(exist_ok=True)
seasons=S["seasons"]
fig,ax=plt.subplots(figsize=(8,4))
for k,lab in [("goals","goals"),("sot","SOT"),("corners","corners"),("shots","total shots"),("yellows","yellows")]:
    ax.plot(seasons,[S["levels"][s][k] for s in seasons],marker="o",label=lab)
ax.legend(); ax.set_title("FI-Veikkausliiga levels per match by season"); fig.tight_layout(); fig.savefig(CH/"levels_by_season.png",dpi=110)
fig,ax=plt.subplots(figsize=(8,4))
tr=S["traits"]; ax.bar([k for k in tr],[tr[k]["r"] for k in tr]); ax.axhline(0,color="k",lw=0.8)
ax.set_title("Split-half trait reliability (r)"); fig.tight_layout(); fig.savefig(CH/"trait_reliability.png",dpi=110)
fig,ax=plt.subplots(figsize=(6,4))
ax.bar(["goals 1H (events)","yellows 1H (events)","SOT 1H (2025 splits)","corners 1H (2025 splits)"],
 [S["halves_goals_dev"]["share"],S["halves_yellows_dev"]["share"],S["halves_splits_2025"]["ShotsOnTarget"]["share"],S["halves_splits_2025"]["corners"]["share"]])
ax.set_title("Frozen halves constants (dev era)"); fig.tight_layout(); fig.savefig(CH/"halves_constants.png",dpi=110)
print("charts done")
