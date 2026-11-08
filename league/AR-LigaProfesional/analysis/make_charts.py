"""Plot only values already frozen in eda_summary.json."""
import json
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).parent;OUT=HERE/'charts';OUT.mkdir(exist_ok=True)
E=json.loads((HERE/'eda_summary.json').read_text())
def save(fig,n):fig.tight_layout();fig.savefig(OUT/n,dpi=130);plt.close(fig);print('wrote',n)
s=E['seasons'];xs=list(s)
fig,ax=plt.subplots(figsize=(8,4.2))
for k,l in [('goals_per_match','goals'),('sot','SOT'),('corners','corners'),('yellows','cards')]:ax.plot(xs,[s[x][k] for x in xs],marker='o',label=l)
ax.set_title('AR Liga Profesional levels by block');ax.legend();save(fig,'levels_by_season.png')
r=E['reliability']; items=[(k,v['r']) for k,v in r.items() if isinstance(v,dict) and 'r' in v]+[(k,v['r']) for k,v in r.get('ratio_traits',{}).items()]
items=[x for x in items if x[1] is not None];items.sort(key=lambda x:x[1]);fig,ax=plt.subplots(figsize=(8,5));ax.barh([x[0] for x in items],[x[1] for x in items],color='#2e7d32');ax.axvline(.3,color='grey',ls='--');ax.set_xlim(0,1);ax.set_title('Team-trait split-half reliability');save(fig,'trait_reliability.png')
h=E['halves'];names=list(h);fig,ax=plt.subplots(figsize=(8,4));v=[h[x]['share_1h'] for x in names];ax.bar(names,v,color='#37474f');ax.axhline(.5,color='grey',ls='--');ax.set_ylim(0,.6);ax.set_title('First-half shares (noise floor in JSON)');
for i,x in enumerate(v):ax.text(i,x+.01,f'{x:.3f}',ha='center')
save(fig,'halves_constants.png')
fig,ax=plt.subplots(figsize=(8,4));vals=[E['referees']['card_rate_split_half']['r'] or 0,r.get('possession_for',{}).get('r') or 0,r.get('big_chance_for',{}).get('r') or 0];ax.bar(['referee cards','possession','big chance'],vals,color=['#2e7d32','#90a4ae','#90a4ae']);ax.set_ylim(0,1);ax.set_title('Referee and territory reliability');save(fig,'referee_and_territory.png')
