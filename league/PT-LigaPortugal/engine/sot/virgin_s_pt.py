"""S-PT virgin: only gate_zero passed the dev gate (x4, x6 failed)."""
import csv, json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common
common.SEASONS = common.SEASONS + ('2026/2027',)
from common import *  # noqa
import run_s_pt as R

def main():
    allr = load(R.DATA, {'sh':'shots_home','sa':'shots_away','oh':'sot_home','oa':'sot_away','xh':'xg_home','xa':'xg_away','xh6':'xgot_home','xa6':'xgot_away'}, seasons=common.SEASONS)
    for x in allr: x['y'] = x['oh'] + x['oa']; x['th'] = x['sh']; x['ta'] = x['sa']
    s = '2026/2027'
    tr, L, r, model = R.state(allr, s, 'gate_zero')
    dev = [x for x in allr if x['season'] == s]
    cut = min(x['date'] for x in dev)
    ww = [(weight(cut, x['date'], 270), x['y']) for x in tr]
    base_mu = sum(q * y for q, y in ww) / sum(q for q, y in ww)
    r_base = moment([x['y'] for x in tr])
    nm = naive(allr, s, 'oh', 'oa', base_mu)
    results = {}; rows_out = []
    for kind in ('model', 'league_base_rate', 'naive_trailing_10'):
        pp = []
        for x in dev:
            if kind == 'model':
                m = model(x); p = .5 * nb_over(m, r, 8.5) + .5 * nb_over(nm[x['match_id']], r, 8.5); rr = r
                rows_out.append({**x, 'mu': m, 'r': rr, 'p_over': p})
            else:
                m = base_mu if kind == 'league_base_rate' else nm[x['match_id']]
                p = nb_over(m, r_base, 8.5); rr = r_base
            pp.append((p, int(x['y'] > 8.5)))
        n = len(pp); diffs = [p - y for p, y in pp]
        sd = math.sqrt(sum((d - sum(diffs) / n) ** 2 for d in diffs) / n)
        results[kind] = {'n': n, 'll_8.5': sum(logloss(p, y) for p, y in pp) / n,
                         'mean_p_over': sum(p for p, y in pp) / n, 'actual_over': sum(y for p, y in pp) / n,
                         'calib_pp': 100 * sum(diffs) / n, 'se_pp': 100 * sd / math.sqrt(n)}
    (HERE / 'results_virgin.json').write_text(json.dumps({'protocol': 'S-PT VIRGIN (transitional 2026/2027)', 'arm': 'gate_zero', 'results': results, 'fitted': {'r': r, 'L': L}}, indent=2) + '\n')
    (HERE / 'fitted_params_virgin.json').write_text(json.dumps({'arm': 'gate_zero', 'r': r, 'L_per_team_shots': L}, indent=2) + '\n')
    with open(HERE / 'virgin_predictions_gate_zero.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','mu','r','p_over_8_5'])
        w.writeheader()
        for x in rows_out: w.writerow({'match_id': x['match_id'], 'season': s, 'date': x['date'].isoformat(), 'home_id': x['home_id'], 'away_id': x['away_id'], 'actual_total': x['y'], 'arm': 'gate_zero', 'mu': x['mu'], 'r': x['r'], 'p_over_8_5': x['p_over']})
    print(json.dumps(results, indent=1))
if __name__ == '__main__': main()
