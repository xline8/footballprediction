"""Charts for ES-LaLiga2 EDA, fed from the built CSV and eda_numbers.json."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / 'data' / 'es_matches.csv')))
EDA = json.load(open(HERE / 'eda_numbers.json'))
OUT = HERE / 'charts'; OUT.mkdir(exist_ok=True)
SEASONS = EDA['seasons']

def val(r, k): return float(r[k])
def level(keys, season): return sum(val(r, keys[0]) + val(r, keys[1]) for r in ROWS if r['season'] == season) / sum(r['season'] == season for r in ROWS)

fig, axes = plt.subplots(2, 3, figsize=(11, 6))
for ax, (name, keys) in zip(axes.flat, [('goals', ('home_goals','away_goals')), ('SOT', ('ShotsOnTarget_home','ShotsOnTarget_away')), ('corners', ('corners_home','corners_away')), ('yellows (events)', ('ev_yellow_home','ev_yellow_away')), ('total shots', ('total_shots_home','total_shots_away')), ('xG', ('expected_goals_home','expected_goals_away'))]):
    xs = [s for s in SEASONS if all(r[keys[0]] not in ('', 'None') and r[keys[1]] not in ('', 'None') for r in ROWS if r['season'] == s)]
    ys = [level(keys, s) for s in xs]
    ax.bar(xs, ys, color='#37474f'); ax.set_title(f'{name} per match by season'); ax.tick_params(labelrotation=30, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / 'levels_by_season.png', dpi=130); plt.close(fig)

traits = {k: v['r'] for k, v in EDA['reliability'].items() if v['r'] is not None}
traits['referee yellows'] = EDA['referee_reliability']['complete_2021_2026']['r']
items = sorted(traits.items(), key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 5)); ax.barh([k for k,_ in items], [v for _,v in items], color='#2e7d32'); ax.axvline(.3, color='grey', ls='--', lw=1)
ax.set_title('ES-LaLiga2 trait split-half reliability (career-pooled)'); fig.tight_layout(); fig.savefig(OUT / 'trait_reliability.png', dpi=130); plt.close(fig)

hs = EDA['half_shares_2023_2026']; names = ['goals', 'SOT', 'corners', 'total shots', 'yellow cards']
keys = ['goals_events', 'sot', 'corners', 'total_shots', 'yellows_events']; shares = [hs[k]['share'] for k in keys]
fig, ax = plt.subplots(figsize=(8, 3.8)); ax.bar(names, shares, color='#37474f'); ax.axhline(.5, color='grey', ls='--', lw=1); ax.set_ylim(0, .6)
ax.set_title('ES-LaLiga2 first-half shares — complete-splits era (EDA)')
for i, v in enumerate(shares): ax.text(i, v + .015, f'{v:.3f}', ha='center')
fig.tight_layout(); fig.savefig(OUT / 'halves_constants.png', dpi=130); plt.close(fig)
print('charts written', sorted(p.name for p in OUT.glob('*.png')))
