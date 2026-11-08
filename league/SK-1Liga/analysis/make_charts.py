import json,matplotlib;matplotlib.use('Agg')
from pathlib import Path
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent;D=json.load(open(H/'eda_numbers.json'));C=H/'charts';C.mkdir(exist_ok=True);S=list(D['levels'])
fig,ax=plt.subplots(figsize=(10,5))
for k,n in [('goals','Goals'),('sot','SOT'),('corners','Corners'),('total_shots','Total shots'),('yellows','Yellows')]:ax.plot(S,[D['levels'][s][k] for s in S],marker='o',label=n)
ax.legend();ax.tick_params(axis='x',rotation=45);fig.tight_layout();fig.savefig(C/'levels_by_season.png',dpi=120);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4));n=list(D['reliabilities']);ax.barh(n,[D['reliabilities'][k]['r'] for k in n]);ax.set_xlim(-1,1);fig.tight_layout();fig.savefig(C/'trait_reliability.png',dpi=120);plt.close(fig)
fig,ax=plt.subplots(figsize=(5,4));ax.bar(['Goals','Cards'],[D['halves']['goals_1h_share'],D['halves']['yellow_cards_1h_share']]);ax.axhline(.5,color='grey',ls='--');fig.tight_layout();fig.savefig(C/'halves_constants.png',dpi=120);plt.close(fig)
mv=D['movers_x2'];labels=[];gf=[];ga=[]
for s in sorted(mv):
 for c in mv[s]['clubs']: labels.append(c['club']+' '+s[:4]);gf.append(c['delta_gf']);ga.append(c['delta_ga'])
fig,ax=plt.subplots(figsize=(9,4));x=range(len(labels));ax.bar([i-.2 for i in x],gf,width=.4,label='delta GF');ax.bar([i+.2 for i in x],ga,width=.4,label='delta GA');ax.axhline(0,color='grey');ax.set_xticks(list(x));ax.set_xticklabels(labels,rotation=30,ha='right',fontsize=7);ax.legend();fig.tight_layout();fig.savefig(C/'movers.png',dpi=120);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4));
rc=D.get('referee',{}).get('coverage_by_season',{}); ax.bar(list(rc),[v['named']/v['n'] for v in rc.values()])
ax.set_ylim(0,1); ax.set_title('Referee coverage'); fig.tight_layout(); fig.savefig(C/'referee_and_territory.png',dpi=120); plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4));
ms=D.get('movers_x2',{}); ss=list(ms); n=[len(ms[s]['clubs']) for s in ss]; ax.bar(ss,n); ax.set_title('Promoted clubs from 2. Liga'); ax.tick_params(axis='x',rotation=45); fig.tight_layout(); fig.savefig(C/'churn_new_teams.png',dpi=120); plt.close(fig)
