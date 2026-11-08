import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
n=json.loads((HERE/'eda_numbers.json').read_text())
seasons=sorted(n['seasons'])
fig,axes=plt.subplots(1,3,figsize=(12,3.2))
axes[0].plot(seasons,[n['seasons'][s]['goals'] for s in seasons],marker='o'); axes[0].set_title('goals / match (finished regular)'); axes[0].grid(alpha=.3)
axes[1].plot(seasons,[n['seasons'][s]['ou25_rate'] for s in seasons],marker='o'); axes[1].set_title('OU2.5 over-rate'); axes[1].grid(alpha=.3)
axes[2].plot(seasons,[n['seasons'][s]['home_win_rate'] for s in seasons],marker='o'); axes[2].set_title('home win rate'); axes[2].grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE/'charts'/'levels_by_season.png',dpi=110); plt.close(fig)
rel=n['reliability']; labels=[k for k in rel if rel[k]['r'] is not None]; vals=[rel[k]['r'] for k in labels]
fig,ax=plt.subplots(figsize=(9,3.2)); ax.bar(labels,vals); ax.axhline(0,color='k',lw=.8); ax.set_ylabel('split-half r'); ax.set_title('trait reliability (stats traits: no data, not plottable)'); ax.tick_params(axis='x',rotation=40); fig.tight_layout(); fig.savefig(HERE/'charts'/'trait_reliability.png',dpi=110); plt.close(fig)
h=n['halves']['goals_events_dev2022_2024_complete']
fig,ax=plt.subplots(figsize=(7,3.2)); ax.bar(['goals (events, dev 2022-2024)'],[h['pooled_share']]); ax.set_ylabel('pooled 1H share'); ax.set_title('halves constant — goals only (no stats-market source exists)'); fig.tight_layout(); fig.savefig(HERE/'charts'/'halves_constants.png',dpi=110); plt.close(fig)
print('charts done')
