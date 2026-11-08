"""Charts for KR-KLeague2 EDA: levels by season, trait reliability, halves constants."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).parent
eda = json.loads((HERE / 'eda_summary.json').read_text())
out = HERE / 'charts'; out.mkdir(exist_ok=True)
seasons = sorted(eda['levels'])
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, key, title in zip(axes.flat, ['goals', 'sot', 'corners', 'yellows', 'shots', 'reds'],
                          ['Goals', 'SOT', 'Corners', 'Yellows (stats era)', 'Total shots', 'Reds']):
    ax.plot(seasons, [eda['levels'][s][key] for s in seasons], marker='o')
    ax.set_title(f'{title} per match'); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out / 'levels_by_season.png', dpi=110); plt.close(fig)
rel = eda['reliability']; names = [k for k in rel if k.endswith('_for') and isinstance(rel[k], dict)]
vals = [rel[k]['r'] for k in names]
fig, ax = plt.subplots(figsize=(9, 4)); ax.barh(names, vals)
ax.set_xlabel('split-half r (career-pooled)'); ax.set_title('Trait reliability - for traits')
fig.tight_layout(); fig.savefig(out / 'trait_reliability.png', dpi=110); plt.close(fig)
hc = eda['halves_splits_era_2023_2025']
ks = [k for k in hc if 'share_1h' in hc[k]]
fig, ax = plt.subplots(figsize=(7, 4)); ax.bar(ks, [hc[k]['share_1h'] for k in ks])
ax.set_ylabel('1H share'); ax.set_title('Frozen halves constants (splits era 2023-2025)')
fig.tight_layout(); fig.savefig(out / 'halves_constants.png', dpi=110); plt.close(fig)
print("charts done")
