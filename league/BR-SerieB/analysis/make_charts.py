"""Create the frozen Série B EDA charts from brb_matches.csv."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent; rows=list(csv.DictReader(open(HERE.parent/'data'/'brb_matches.csv'))); seasons=['2021','2022','2023','2024','2025','2026']; OUT=HERE/'charts'; OUT.mkdir(exist_ok=True)
def f(r,k): return float(r[k]) if r.get(k) not in ('',None) else None
def mean(x): return sum(x)/len(x) if x else float('nan')
def pair(r,a,b):
    x,y=f(r,a),f(r,b); return x+y if x is not None and y is not None else None
series=[('goals',lambda r:pair(r,'home_goals','away_goals')),('SOT',lambda r:pair(r,'ShotsOnTarget_home','ShotsOnTarget_away')),('corners',lambda r:pair(r,'corners_home','corners_away')),('unified yellows',lambda r:pair(r,'yellow_unified_home','yellow_unified_away')),('total shots',lambda r:pair(r,'total_shots_home','total_shots_away')),('xG (covered)',lambda r:pair(r,'expected_goals_home','expected_goals_away'))]
fig,axes=plt.subplots(2,3,figsize=(11,6))
for ax,(name,fn) in zip(axes.flat,series): ax.bar(seasons,[mean([fn(r) for r in rows if r['season']==s and fn(r) is not None]) for s in seasons],color='#37474f'); ax.set_title(name+' per match'); ax.tick_params(axis='x',rotation=30,labelsize=7)
fig.tight_layout(); fig.savefig(OUT/'levels_by_season.png',dpi=130); plt.close(fig)
traits={'goals-for':.361,'SOT-for':.395,'corners-for':.406,'shots-for':.543,'box touches-for':.586,'cards-for (valid era)':.262,'xG-for (2025+)':.374,'referee yellows':.397}; items=sorted(traits.items(),key=lambda x:x[1]); fig,ax=plt.subplots(figsize=(9,4.5)); ax.barh([x[0] for x in items],[x[1] for x in items],color='#2e7d32'); ax.axvline(.3,color='grey',ls='--'); ax.set_title('BR-SerieB trait split-half reliability (60 splits)'); fig.tight_layout(); fig.savefig(OUT/'trait_reliability.png',dpi=130); plt.close(fig)
shares=[.455,.467,.472,.473,.352]; names=['goals','SOT','corners','total shots','yellows']; fig,ax=plt.subplots(figsize=(8,3.8)); ax.bar(names,shares,color='#37474f'); ax.axhline(.5,color='grey',ls='--'); ax.set_ylim(0,.6); ax.set_title('Frozen first-half shares — complete-splits era 2023–2025'); [ax.text(i,v+.015,f'{v:.3f}',ha='center') for i,v in enumerate(shares)]; fig.tight_layout(); fig.savefig(OUT/'halves_constants.png',dpi=130); plt.close(fig)
print('charts written',sorted(p.name for p in OUT.glob('*.png')))
