"""Create the three requested scores-only EDA charts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
EDA = json.load(open(HERE / 'eda_numbers.json'))
OUT = HERE / 'charts'; OUT.mkdir(exist_ok=True)
S = EDA['seasons']; p = EDA['per_season']
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, key, title in zip(axes, ('goals_per_match','OU2.5_over_rate','H_rate'), ('Goals per match','OU2.5 over-rate','Home-win rate')):
    ax.bar(S, [p[s][key] for s in S], color='#37474f'); ax.set_title(title); ax.tick_params(axis='x', labelrotation=35, labelsize=8)
fig.tight_layout(); fig.savefig(OUT / 'levels_by_season.png', dpi=130); plt.close(fig)
rel = EDA['reliability']; labels = ['GF chronological', 'GA chronological', 'GF rounds', 'GA rounds']; vals = [rel['chronological_halves']['gf_r'], rel['chronological_halves']['ga_r'], rel['rounds_1_19_vs_20_38_regular']['gf_r'], rel['rounds_1_19_vs_20_38_regular']['ga_r']]
fig, ax = plt.subplots(figsize=(8, 3.8)); ax.barh(labels, vals, color='#2e7d32'); ax.axvline(0, color='grey', lw=1); ax.set_xlim(-1, 1); ax.set_title('ES Primera Federacion split-half reliability'); fig.tight_layout(); fig.savefig(OUT / 'trait_reliability.png', dpi=130); plt.close(fig)
shares = [EDA['half_shares_goals_events']['per_season'][s]['share'] for s in S]
fig, ax = plt.subplots(figsize=(9, 4)); ax.bar(S, shares, color='#37474f'); ax.axhline(.4301, color='#c62828', ls='--', label='DEV frozen 0.4301'); ax.set_ylim(0, .6); ax.set_title('First-half goal share (complete goal events)'); ax.tick_params(axis='x', labelrotation=35, labelsize=8); ax.legend(); fig.tight_layout(); fig.savefig(OUT / 'halves_constants.png', dpi=130); plt.close(fig)
print('charts written', sorted(x.name for x in OUT.glob('*.png')))
