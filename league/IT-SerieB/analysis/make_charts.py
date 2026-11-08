"""Charts for IT-SerieB EDA, fed from the built CSV and eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
EDA = json.load(open(HERE / 'eda_numbers.json'))
OUT = HERE / 'charts'; OUT.mkdir(exist_ok=True)
SEASONS = sorted(EDA['levels'].keys())
L = EDA['levels']

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, key) in zip(axes.flat, [('goals', 'goals'), ('SOT', 'sot'), ('corners', 'corners'),
                                       ('yellows (events)', 'yellows_events'), ('total shots', 'shots'), ('xG (era seasons only)', 'xg')]):
    xs = [s for s in SEASONS if L[s].get(key) is not None and (key != 'xg' or L[s].get('xg_n', 0) > 50)]
    ys = [L[s][key] for s in xs]
    ax.bar(xs, ys, color='#37474f'); ax.set_title(f'{name} per match by season'); ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / 'levels_by_season.png', dpi=130); plt.close(fig)

traits = {k: v['r'] for k, v in EDA['reliability'].items() if v['r'] is not None}
traits['referee yellows'] = EDA['referee']['split_half_r']
items = sorted(traits.items(), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 5)); ax.barh([k for k, _ in items], [v for _, v in items], color='#2e7d32')
ax.axvline(.3, color='grey', ls='--', lw=1); ax.set_title('IT-SerieB trait split-half reliability (career-pooled)')
fig.tight_layout(); fig.savefig(OUT / 'trait_reliability.png', dpi=130); plt.close(fig)

names = ['goals', 'SOT', 'corners', 'total shots', 'yellow cards']
shares = [0.4501, 0.4598, 0.4734, 0.4650, 0.3733]
fig, ax = plt.subplots(figsize=(8, 3.8)); ax.bar(names, shares, color='#37474f'); ax.axhline(.5, color='grey', ls='--', lw=1); ax.set_ylim(0, .6)
ax.set_title('IT-SerieB first-half shares - frozen constants (complete seasons 2023/2024-2025/2026)')
for i, v in enumerate(shares): ax.text(i, v + .015, f'{v:.3f}', ha='center')
fig.tight_layout(); fig.savefig(OUT / 'halves_constants.png', dpi=130); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
cov = EDA['referee']['coverage_by_season']
axes[0].bar(list(cov.keys()), [100 * cov[s] for s in cov], color='#37474f'); axes[0].set_title('referee coverage % by season'); axes[0].tick_params(labelrotation=30, labelsize=7)
terr = {'possession': EDA['reliability']['possession']['r'], 'big_chance_for': EDA['reliability']['big_chance_for']['r'],
        'box_touches_for': EDA['reliability']['box_touches_for']['r'], 'box_touches_against': EDA['reliability']['box_touches_against']['r']}
axes[1].barh(list(terr.keys()), list(terr.values()), color='#2e7d32'); axes[1].set_title('territorial trait reliability r')
fig.tight_layout(); fig.savefig(OUT / 'referee_and_territory.png', dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 3.8))
srcs = ['serie_a', 'serie_c']; pooled = EDA['movers_pooled_entry_2022_2026']
x = range(len(srcs)); w = 0.35
ax.bar([i - w / 2 for i in x], [pooled[s]['dgf'] for s in srcs], w, label='dGF/match')
ax.bar([i + w / 2 for i in x], [-pooled[s]['dga'] for s in srcs], w, label='-dGA/match (defensive edge)')
ax.set_xticks(list(x)); ax.set_xticklabels(['from Serie A', 'from Serie C']); ax.axhline(0, color='grey', lw=1); ax.legend()
ax.set_title('IT-SerieB mover entry deltas vs league mean (entry seasons 2022/2023-2025/2026)')
fig.tight_layout(); fig.savefig(OUT / 'tier_gap.png', dpi=130); plt.close(fig)
print('charts written', sorted(p.name for p in OUT.glob('*.png')))
