import json,matplotlib;matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;D=json.load(open(H/'eda_numbers.json'));C=H/'charts';C.mkdir(exist_ok=True);S=list(D['levels'])
fig,ax=plt.subplots(figsize=(10,5))
for k,n in [('goals','Goals'),('sot','SOT'),('corners','Corners'),('total_shots','Total shots'),('yellows','Yellows')]:ax.plot(S,[D['levels'][s][k] for s in S],marker='o',label=n)
ax.legend();ax.tick_params(axis='x',rotation=45);fig.tight_layout();fig.savefig(C/'levels_by_season.png',dpi=120);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4));n=list(D['reliabilities']);ax.barh(n,[D['reliabilities'][k]['r'] for k in n]);ax.set_xlim(-1,1);fig.tight_layout();fig.savefig(C/'trait_reliability.png',dpi=120);plt.close(fig)
fig,ax=plt.subplots(figsize=(5,4));ax.bar(['Goals','Cards'],[D['halves']['goals_1h_share'],D['halves']['yellow_cards_1h_share']]);ax.axhline(.5,color='grey',ls='--');fig.tight_layout();fig.savefig(C/'halves_constants.png',dpi=120);plt.close(fig)
