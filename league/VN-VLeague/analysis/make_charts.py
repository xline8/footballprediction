"""Generate EDA charts from eda_summary.json and the built CSV only."""
import json
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
H = Path(__file__).parent
S = json.loads((H / 'eda_summary.json').read_text())
C = H / 'charts'; C.mkdir(exist_ok=True)
seasons = sorted(S['seasons'])
d = pd.DataFrame(S['seasons']).T
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seasons, d.goals_pm_finished, marker='o')
ax.set(title='Finished goals/match by season (2026/2027 in progress, inventory only)', ylabel='goals/match')
ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(C / 'levels_by_season.png', dpi=120); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(seasons)); w = .18
for i, (c, l) in enumerate([('stats', 'stats'), ('events', 'events'), ('lineup', 'lineup'), ('referee', 'referee')]):
    ax.bar([v + (i - 1.5) * w for v in x], d[c] / d.payloads, width=w, label=l)
ax.set(xticks=list(x), xticklabels=seasons, ylim=(0, 1.05), title='Payload coverage by season')
ax.legend(); ax.grid(axis='y', alpha=.3); fig.tight_layout(); fig.savefig(C / 'coverage_by_season.png', dpi=120); plt.close(fig)
r = S['trait_reliability_by_season']
fig, ax = plt.subplots(figsize=(7, 4))
xs = range(len(r)); w = .35
ax.bar([v - w / 2 for v in xs], [r[s]['r_goals_for'] for s in r], width=w, label='goals for')
ax.bar([v + w / 2 for v in xs], [r[s]['r_goals_against'] for s in r], width=w, label='goals against')
ax.set(xticks=list(xs), xticklabels=list(r), ylim=(-0.3, 1.0), title='Trait split-half r by season (chronological halves)')
ax.legend(); ax.grid(axis='y', alpha=.3); fig.tight_layout(); fig.savefig(C / 'trait_reliability.png', dpi=120); plt.close(fig)
h = S['halves_dev']
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(['goals'], [h['share_1h']]); ax.axhline(.5, color='k', lw=.8)
ax.set_ylim(0, .7); ax.set(title='1H goals share, dev Half-event scores (0.4468)')
fig.tight_layout(); fig.savefig(C / 'halves_constants.png', dpi=120); plt.close(fig)
m = pd.DataFrame(S['entrants_dev']['transitions'])
m = m[m.season != '2021']  # 2021 is the warehouse seed, not real entrants
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(m.gf_diff, m.ga_diff)
ax.axvline(0, color='k', lw=.5); ax.axhline(0, color='k', lw=.5)
ax.set(xlabel='GF diff vs season mean', ylabel='GA diff vs season mean',
       title='Entrants (no prior-season record), dev transitions excl. 2021 seed')
fig.tight_layout(); fig.savefig(C / 'entrants.png', dpi=120); plt.close(fig)
print('charts:', sorted(x.name for x in C.glob('*.png')))
