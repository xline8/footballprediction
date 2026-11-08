"""Generate the Phase A EDA charts from eda_summary.json."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
H=Path(__file__).parent; S=json.loads((H/"eda_summary.json").read_text()); C=H/"charts"; C.mkdir(exist_ok=True)
seasons=list(S["seasons"]); d=pd.DataFrame(S["seasons"]).T
fig,ax=plt.subplots(figsize=(8,4)); ax.plot(seasons,d.goals_pm_finished,marker="o"); ax.set(title="Finished goals/match by season (2026/2027 in progress)",ylabel="goals/match"); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(C/"levels_by_season.png",dpi=120); plt.close(fig)
r=S["trait_reliability_by_season"]; fig,ax=plt.subplots(figsize=(7,4)); x=range(len(r)); w=.35; ax.bar([v-w/2 for v in x],[r[s]["r_goals_for"] for s in r],w,label="goals for"); ax.bar([v+w/2 for v in x],[r[s]["r_goals_against"] for s in r],w,label="goals against"); ax.set(xticks=list(x),xticklabels=list(r),ylim=(-.3,1),title="Trait split-half r by season"); ax.legend(); ax.grid(axis="y",alpha=.3); fig.tight_layout(); fig.savefig(C/"trait_reliability.png",dpi=120); plt.close(fig)
h=S["halves_dev"]; fig,ax=plt.subplots(figsize=(6,4)); ax.bar(["goals"],[h["share_1h"]]); ax.axhline(.5,color="k",lw=.8); ax.set_ylim(0,.7); ax.set(title="1H goals share, dev Half-event scores"); fig.tight_layout(); fig.savefig(C/"halves_constants.png",dpi=120); plt.close(fig)
print("charts:",sorted(x.name for x in C.glob("*.png")))
