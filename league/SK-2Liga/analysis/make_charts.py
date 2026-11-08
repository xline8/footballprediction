"""Make the deterministic SK-2Liga EDA charts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = json.load(open(HERE / 'eda_numbers.json'))
CHARTS = HERE / 'charts'
CHARTS.mkdir(exist_ok=True)
SEASONS = list(DATA['levels'])

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(SEASONS, [DATA['levels'][s]['goals'] for s in SEASONS], marker='o')
ax.set_title('Goals per match by season'); ax.tick_params(axis='x', rotation=45)
fig.tight_layout(); fig.savefig(CHARTS / 'levels_by_season.png', dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(5, 4))
labels = ['GF', 'GA']; vals = [DATA['reliabilities']['goals_for']['r'], DATA['reliabilities']['goals_against']['r']]
ax.bar(labels, vals); ax.set_ylim(-1, 1); ax.set_title('Split-half reliability')
fig.tight_layout(); fig.savefig(CHARTS / 'trait_reliability.png', dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(['Dev era'], [DATA['halves']['dev_era']['share']]); ax.axhline(.5, color='grey', ls='--')
ax.set_ylim(0, 1); ax.set_title('First-half goal share')
fig.tight_layout(); fig.savefig(CHARTS / 'halves_constants.png', dpi=120); plt.close(fig)

labels, gf, ga = [], [], []
for season, item in DATA['movers_x2']['by_season'].items():
    for club in item['clubs']:
        labels.append(f"{club['club']} {season[:4]}"); gf.append(club['delta_gf']); ga.append(club['delta_ga'])
fig, ax = plt.subplots(figsize=(9, 4)); x = list(range(len(labels)))
ax.bar([i-.2 for i in x], gf, .4, label='delta GF'); ax.bar([i+.2 for i in x], ga, .4, label='delta GA'); ax.axhline(0, color='grey')
ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=7); ax.legend(); fig.tight_layout()
fig.savefig(CHARTS / 'movers.png', dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(SEASONS, [DATA['movers_x2']['newcomers'].get(s, {'count': 0})['count'] for s in SEASONS])
ax.set_title('New teams by season'); ax.tick_params(axis='x', rotation=45)
fig.tight_layout(); fig.savefig(CHARTS / 'churn_new_teams.png', dpi=120); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4))
coverage = DATA['referee']['coverage_by_season']
ax.bar(SEASONS, [0 for _ in SEASONS]); ax.set_ylim(0, 1); ax.set_title('Referee coverage (none named)')
ax.tick_params(axis='x', rotation=45); fig.tight_layout(); fig.savefig(CHARTS / 'referee_and_territory.png', dpi=120); plt.close(fig)
