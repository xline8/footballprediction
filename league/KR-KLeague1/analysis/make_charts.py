"""Charts for SE-Allsvenskan EDA: levels by season, trait reliability, halves constants."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).parent
eda=json.loads((HERE/'eda_summary.json').read_text())
out=HERE/'charts'; out.mkdir(exist_ok=True)
seasons=[s for s in sorted(eda['levels']) ]
fig,axes=plt.subplots(2,3,figsize=(12,6))
for ax,key,title in zip(axes.flat,['goals','sot','corners','yellows','shots','xg'],['Goals','SOT','Corners','Yellows','Total shots','xG']):
    ax.plot(seasons,[eda['levels'][s][key] for s in seasons],marker='o'); ax.set_title(f'{title} per match'); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out/'levels_by_season.png',dpi=110); plt.close(fig)
rel=eda['reliability']; names=[k for k in rel if k.endswith('_for')]; vals=[rel[k]['r'] for k in names]
fig,ax=plt.subplots(figsize=(9,4)); ax.barh(names,vals); ax.set_xlabel('split-half r (career-pooled)'); ax.set_title('Trait reliability — for traits'); fig.tight_layout(); fig.savefig(out/'trait_reliability.png',dpi=110); plt.close(fig)
hc=eda['halves_complete_2024_2025']
fig,ax=plt.subplots(figsize=(7,4)); ks=list(hc); ax.bar(ks,[hc[k]['share_1h'] for k in ks]); ax.set_ylabel('1H share'); ax.set_title('Frozen halves constants (complete era; yellows 2024-2025)'); fig.tight_layout(); fig.savefig(out/'halves_constants.png',dpi=110); plt.close(fig)
print("charts done")
