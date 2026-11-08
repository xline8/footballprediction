"""K-PT virgin: only arm x8 passed the dev gate (gate_zero failed vs
the base rate). Fit on 2021/2022-2025/2026, score 2026/2027 once."""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common
common.SEASONS = common.SEASONS + ('2026/2027',)
from common import *  # noqa
import run_k_pt as R

def main():
    allr = load(R.DATA, {'yh':'yellow_home','ya':'yellow_away'}, seasons=common.SEASONS)
    for x in allr: x['y'] = x['yh'] + x['ya']
    s = '2026/2027'
    tr, mu, r, model = R.state(allr, s)
    dev = [x for x in allr if x['season'] == s]
    refs = defaultdict(lambda: [0., 0.])
    for x in tr:
        refs[x['referee']][0] += x['y']; refs[x['referee']][1] += 1
    cut = min(x['date'] for x in dev)
    ww = [(weight(cut, x['date'], 270), x['y']) for x in tr]
    base_mu = sum(q * y for q, y in ww) / sum(q for q, y in ww)
    r_base = moment([x['y'] for x in tr])
    nm = naive(allr, s, 'yh', 'ya', base_mu)
    share = 0; results = {}; rows_out = []
    for kind in ('model', 'league_base_rate', 'naive_trailing_10'):
        pp = []
        for x in dev:
            m = model(x) if kind == 'model' else (base_mu if kind == 'league_base_rate' else nm[x['match_id']])
            rr = r if kind == 'model' else r_base
            if kind == 'model' and x['referee'] and refs[x['referee']][1] > 0:
                mult = clamp((refs[x['referee']][0] + 8 * mu) / (refs[x['referee']][1] + 8) / mu, .75, 1.33)
                if mult != 1.0: share += 1
                m *= mult
            p = nb_over(m, rr, 4.5)
            pp.append((p, int(x['y'] > 4.5)))
            if kind == 'model':
                rows_out.append({**x, 'mu': m, 'r': rr, 'p_over': p, 'mult': mult if x['referee'] else 1.0})
        n = len(pp); diffs = [p - y for p, y in pp]
        sd = math.sqrt(sum((d - sum(diffs) / n) ** 2 for d in diffs) / n)
        results[kind] = {'n': n, 'll_4.5': sum(logloss(p, y) for p, y in pp) / n,
                         'mean_p_over': sum(p for p, y in pp) / n, 'actual_over': sum(y for p, y in pp) / n,
                         'calib_pp': 100 * sum(diffs) / n, 'se_pp': 100 * sd / math.sqrt(n)}
    results['x8_multiplier_non1_share'] = share / len(dev)
    (HERE / 'results_virgin.json').write_text(json.dumps({'protocol': 'K-PT VIRGIN (transitional 2026/2027)', 'arm': 'x8', 'results': results, 'fitted': {'r': r, 'mu_per_match': mu}}, indent=2) + '\n')
    (HERE / 'fitted_params_virgin.json').write_text(json.dumps({'arm': 'x8', 'r': r, 'mu_per_match': mu, 'referee_rates': {k: v for k, v in refs.items() if k}}, indent=2) + '\n')
    with open(HERE / 'virgin_predictions_x8.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','mu','r','p_over_4_5','mult'])
        w.writeheader()
        for x in rows_out: w.writerow({'match_id': x['match_id'], 'season': s, 'date': x['date'].isoformat(), 'home_id': x['home_id'], 'away_id': x['away_id'], 'actual_total': x['y'], 'arm': 'x8', 'mu': x['mu'], 'r': x['r'], 'p_over_4_5': x['p_over'], 'mult': x['mult']})
    print(json.dumps(results, indent=1))
if __name__ == '__main__': main()
