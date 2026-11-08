"""Make Phase A EDA charts; no fitting."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; OUT=HERE/'charts'; OUT.mkdir(exist_ok=True)
D=json.loads((HERE/'eda_numbers.json').read_text()); seasons=D['seasons']; per=D['per_season']
fig,ax=plt.subplots(figsize=(9,5));
for k,label in [('goals_per_match','Goals'),('sot.mean','SOT'),('corners.mean','Corners'),('cards.mean','Cards'),('total_shots.mean','Total shots')]:
    vals=[]
    for s in seasons:
        x=per[s]; v=x
        for p in k.split('.'):v=v[p]
        vals.append(v)
    ax.plot(seasons,vals,marker='o',label=label)
ax.set_title('Cyprus 1. Division levels by season'); ax.tick_params(axis='x',rotation=35); ax.legend(); fig.tight_layout(); fig.savefig(OUT/'levels_by_season.png',dpi=140); plt.close(fig)
R=D['reliability']; names=list(R); vals=[R[n]['r'] for n in names]; fig,ax=plt.subplots(figsize=(9,5)); ax.bar(range(len(names)),[v or 0 for v in vals]); ax.set_xticks(range(len(names)),names,rotation=70,ha='right'); ax.set_ylim(-1,1); ax.set_title('Split-half trait reliability'); fig.tight_layout(); fig.savefig(OUT/'trait_reliability.png',dpi=140); plt.close(fig)
H=D['halves']; fig,ax=plt.subplots(figsize=(6,4)); names=['Goals','Cards']; vals=[H['goals']['share_1h'],H['yellow_cards']['share_1h']]; ax.bar(names,vals); ax.set_ylim(0,1); ax.set_title('First-half event shares'); fig.tight_layout(); fig.savefig(OUT/'halves_constants.png',dpi=140); plt.close(fig)
