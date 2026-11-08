import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
n=json.loads((HERE/'eda_numbers.json').read_text())
seasons=sorted(n['seasons'])
fig,axes=plt.subplots(1,3,figsize=(12,3.2))
for ax,key,title in [(axes[0],'goals','goals'),(axes[1],'sot','SOT'),(axes[2],'corners','corners')]:
    ax.plot(seasons,[n['seasons'][s][key] for s in seasons],marker='o'); ax.set_title(title); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(HERE/'charts'/'levels_by_season.png',dpi=110); plt.close(fig)
rel=n['reliability']; labels=list(rel); vals=[rel[k]['r'] for k in labels]
fig,ax=plt.subplots(figsize=(9,3.2)); ax.bar(labels,vals); ax.axhline(0,color='k',lw=.8); ax.set_ylabel('split-half r'); ax.tick_params(axis='x',rotation=40); fig.tight_layout(); fig.savefig(HERE/'charts'/'trait_reliability.png',dpi=110); plt.close(fig)
h=n['halves']; keys=['goals_events_all','sot','corners','total_shots','cards']
fig,ax=plt.subplots(figsize=(7,3.2)); ax.bar(keys,[h[k]['pooled_share'] for k in keys]); ax.set_ylabel('pooled 1H share'); fig.tight_layout(); fig.savefig(HERE/'charts'/'halves_constants.png',dpi=110); plt.close(fig)
print('charts done')
