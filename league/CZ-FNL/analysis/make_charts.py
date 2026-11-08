"""Make the goals-only FNL chart set from eda_numbers.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / 'charts'; OUT.mkdir(exist_ok=True)
D = json.loads((HERE/'eda_numbers.json').read_text())
S = list(D['levels'])

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT/name, dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(S, [D['levels'][s]['goals'] for s in S], marker='o', label='Goals')
ax.set_title('CZ FNL goals per match by season'); ax.set_ylabel('goals / match'); ax.tick_params(axis='x', rotation=35); ax.legend(); save(fig, 'levels_by_season.png')

rel = D['reliabilities']; labels = ['goals for', 'goals against']; vals = [rel[k]['r'] for k in ('goals_for','goals_against')]
fig, ax = plt.subplots(figsize=(7, 3.5)); ax.barh(labels, vals, color=['#2e7d32','#ef6c00']); ax.set_xlim(-1,1); ax.axvline(0, color='grey', lw=1); ax.set_title('FNL goals trait reliability, split-half r')
for i,v in enumerate(vals): ax.text(v + (0.02 if v >= 0 else -0.12), i, f'{v:.3f}', va='center')
save(fig, 'trait_reliability.png')

h = D['halves']['goals_1h_share']
fig, ax = plt.subplots(figsize=(5, 3.5)); ax.bar(['Goals'], [h], color='#37474f'); ax.axhline(.5, color='grey', ls='--'); ax.set_ylim(0,.6); ax.set_title('FNL frozen first-half constant (dev)'); ax.text(0, h+.02, f'{h:.4f}', ha='center'); save(fig, 'halves_constants.png')
print('charts written to', OUT)
