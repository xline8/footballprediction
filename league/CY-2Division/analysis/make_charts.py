"""Make Phase A EDA charts; no fitting."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / 'charts'
OUT.mkdir(exist_ok=True)
D = json.loads((HERE / 'eda_numbers.json').read_text())
seasons = D['seasons']
per = D['per_season']

fig, ax = plt.subplots(figsize=(9, 5))
vals = [per[s]['goals_per_match'] for s in seasons]
ax.plot(seasons, vals, marker='o', label='Goals per match')
ax.set_title('Cyprus 2. Division levels by season')
ax.tick_params(axis='x', rotation=35)
ax.legend()
fig.tight_layout()
fig.savefig(OUT / 'levels_by_season.png', dpi=140)
plt.close(fig)

R = D['reliability']
names = list(R)
vals = [R[n]['r'] for n in names]
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(range(len(names)), [v or 0 for v in vals])
ax.set_xticks(range(len(names)), names, rotation=30, ha='right')
ax.set_ylim(-1, 1)
ax.set_title('Split-half trait reliability (goals)')
fig.tight_layout()
fig.savefig(OUT / 'trait_reliability.png', dpi=140)
plt.close(fig)

H = D['halves']
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(['Goals'], [H['goals']['share_1h']])
ax.set_ylim(0, 1)
ax.set_title('First-half event share (goals)')
fig.tight_layout()
fig.savefig(OUT / 'halves_constants.png', dpi=140)
plt.close(fig)
print('charts written')
