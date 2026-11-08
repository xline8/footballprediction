"""Make the five Phase A EDA charts from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; DATA=json.load(open(HERE/'eda_numbers.json')); OUT=HERE/'charts'; OUT.mkdir(exist_ok=True)
seasons=sorted(DATA['levels'],key=int)
fig,ax=plt.subplots(figsize=(10,5))
for key,label in [('goals','Goals'),('sot','SOT'),('corners','Corners'),('total_shots','Total shots'),('yellows_stats','Stats yellows')]: ax.plot(seasons,[DATA['levels'][s][key] for s in seasons],marker='o',label=label)
ax.set_title('CA-PremierLeague regular levels'); ax.set_xlabel('Season'); ax.legend(); ax.tick_params(axis='x',rotation=45); fig.tight_layout(); fig.savefig(OUT/'levels_by_season.png',dpi=140); plt.close(fig)

z=DATA['reliabilities_by_season_pair']['2023-2024']; names=['goals_for','sot_for','corners_for','shots_for','possession_for','big_chance_for','yellows_for']; labels=['Goals','SOT','Corners','Shots','Possession','Big chance','Yellows']
fig,ax=plt.subplots(figsize=(9,4)); ax.bar(labels,[z[n]['r'] for n in names]); ax.set_ylim(-1,1); ax.set_title('Split-half reliability (2023–2024)'); ax.tick_params(axis='x',rotation=25); fig.tight_layout(); fig.savefig(OUT/'trait_reliability.png',dpi=140); plt.close(fig)

names=['goals','sot','corners','total_shots','yellows']; labels=['Goals','SOT','Corners','Shots','Yellows']; shares=[DATA['halves_2023_2024'][n]['share_1h'] for n in names]; sds=[DATA['halves_2023_2024'][n]['true_sd'] for n in names]
fig,ax=plt.subplots(figsize=(9,4)); x=range(len(names)); ax.bar([i-.18 for i in x],shares,width=.36,label='1H share'); ax.bar([i+.18 for i in x],sds,width=.36,label='true SD'); ax.axhline(.5,color='grey',ls='--'); ax.set_xticks(list(x)); ax.set_xticklabels(labels); ax.set_title('Frozen halves constants and residual SD'); ax.legend(); fig.tight_layout(); fig.savefig(OUT/'halves_constants.png',dpi=140); plt.close(fig)

v=DATA['movers_x2']['vancouver_2023']; fig,ax=plt.subplots(figsize=(6,4)); ax.bar(['GF delta','GA delta'],[v['delta_gf'],v['delta_ga']],color=['#4472c4','#ed7d31']); ax.axhline(0,color='grey'); ax.set_title('Expansion entry: Vancouver 2023'); fig.tight_layout(); fig.savefig(OUT/'churn_new_teams.png',dpi=140); plt.close(fig)

cov=DATA['referee']['coverage_by_season']; fig,ax=plt.subplots(figsize=(8,4)); ax.plot(list(cov),[x['named']/x['n'] for x in cov.values()],marker='o',label='Referee named'); bt=DATA['box_touch_availability']['availability_by_season']; ax.plot(list(bt),[x['nonmissing']/x['matches'] for x in bt.values()],marker='s',label='Box touches present'); ax.set_ylim(0,1); ax.set_title('Referee coverage and box-touch availability'); ax.legend(); ax.tick_params(axis='x',rotation=45); fig.tight_layout(); fig.savefig(OUT/'referee_and_territory.png',dpi=140); plt.close(fig)
print('wrote',', '.join(str(OUT/x) for x in ['levels_by_season.png','trait_reliability.png','halves_constants.png','churn_new_teams.png','referee_and_territory.png']))
