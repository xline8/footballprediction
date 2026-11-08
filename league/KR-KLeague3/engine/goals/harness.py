"""G-KR3 season-blocked dev harness and later virgin-mode support."""
import csv
import json
import math
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dc import DC
from arms import adjusted_lambdas, match_counts

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / 'data' / 'kr3_matches.csv'
SEAS = ['2021', '2022', '2023', '2024']
SCORED = ['2022', '2023', '2024']
ARMS = ['gate_zero', 'shrink']
HALF_1H = 0.4273


def load(seasons):
    rows = []
    with DATA.open() as f:
        for x in csv.DictReader(f):
            if x['season'] not in seasons or x['phase'] != 'regular':
                continue
            rows.append({'match_id': x['match_id'], 'season': x['season'],
                         'date': date.fromisoformat(x['date']),
                         'hi': int(x['home_team_id']), 'ai': int(x['away_team_id']),
                         'home': x['home_team'], 'away': x['away_team'],
                         'yh': int(x['home_goals']), 'ya': int(x['away_goals'])})
    assert not any(r['season'] == '2026' for r in rows)
    return sorted(rows, key=lambda r: (r['date'], r['match_id']))


def score(rows, ps):
    ll = rps = ou = 0.0
    for r, p in zip(rows, ps):
        y = [r['yh'] > r['ya'], r['yh'] == r['ya'], r['yh'] < r['ya']]
        q = [p['ph'], p['pd'], p['pa']]
        ll -= math.log(max(q[y.index(True)], 1e-12))
        rps += 0.5 * ((q[0] - y[0]) ** 2 +
                      (q[0] + q[1] - y[0] - y[1]) ** 2)
        over = r['yh'] + r['ya'] > 2.5
        ou -= math.log(max(p['over25'] if over else 1 - p['over25'], 1e-12))
    n = len(rows)
    return {'n': n, 'll_1x2': ll / n, 'rps': rps / n, 'oull_2_5': ou / n}


def climatology(train):
    n = len(train)
    return {'ph': sum(r['yh'] > r['ya'] for r in train) / n,
            'pd': sum(r['yh'] == r['ya'] for r in train) / n,
            'pa': sum(r['yh'] < r['ya'] for r in train) / n,
            'over25': sum(r['yh'] + r['ya'] > 2.5 for r in train) / n}


def _season_fit(rows, season, arm):
    target = [r for r in rows if r['season'] == season]
    cutoff = min(r['date'] for r in target)
    train = [r for r in rows if r['date'] < cutoff]
    model = DC().fit(train, cutoff)
    counts = match_counts(train)
    ps = [model.probs(*adjusted_lambdas(model, r['hi'], r['ai'], arm, counts))
          for r in target]
    return target, train, model, counts, ps


def _prediction(r, p, arm, model, lambdas):
    return {'match_id': r['match_id'], 'season': r['season'],
            'date': r['date'].isoformat(), 'home': r['home'], 'away': r['away'],
            'arm': arm, 'p_home_win': p['ph'], 'p_draw': p['pd'],
            'p_away_win': p['pa'], 'p_over25': p['over25'],
            'actual_outcome': 'H' if r['yh'] > r['ya'] else ('D' if r['yh'] == r['ya'] else 'A'),
            'actual_over25': int(r['yh'] + r['ya'] > 2.5),
            'home_goals': r['yh'], 'away_goals': r['ya'],
            'lambda_home': lambdas[0], 'lambda_away': lambdas[1],
            'rho': model.rho}


def run_dev():
    rows = load(SEAS)
    out = []
    predictions = []
    for arm in ARMS:
        pooled_rows, pooled_ps, pooled_clim = [], [], []
        for season in SCORED:
            target, train, model, counts, ps = _season_fit(rows, season, arm)
            for r, p in zip(target, ps):
                lambdas = adjusted_lambdas(model, r['hi'], r['ai'], arm, counts)
                predictions.append(_prediction(r, p, arm, model, lambdas))
            metrics = score(target, ps)
            metrics.update(arm=arm, season=season, kind='model')
            out.append(metrics)
            cp = climatology(train)
            cps = [cp] * len(target)
            if arm == ARMS[0]:
                metrics = score(target, cps)
                metrics.update(arm='climatology', season=season, kind='climatology')
                out.append(metrics)
            pooled_rows += target; pooled_ps += ps; pooled_clim += cps
        metrics = score(pooled_rows, pooled_ps)
        metrics.update(arm=arm, season='pooled', kind='model')
        out.append(metrics)
        if arm == ARMS[-1]:
            metrics = score(pooled_rows, pooled_clim)
            metrics.update(arm='climatology', season='pooled', kind='climatology')
            out.append(metrics)

    def metric(arm, season, key):
        return next(x[key] for x in out if x['arm'] == arm and x['season'] == season
                    and x['kind'] in ('model', 'climatology'))

    gate = {}
    for arm in ARMS:
        legs = {'ll_1x2': metric(arm, 'pooled', 'll_1x2') < metric('climatology', 'pooled', 'll_1x2'),
                'rps': metric(arm, 'pooled', 'rps') < metric('climatology', 'pooled', 'rps'),
                'oull_2_5': metric(arm, 'pooled', 'oull_2_5') < metric('climatology', 'pooled', 'oull_2_5')}
        sign = None
        if arm != 'gate_zero':
            wins = sum(metric(arm, s, 'll_1x2') <= metric('gate_zero', s, 'll_1x2')
                       for s in SCORED)
            sign = {'wins': wins, 'of': len(SCORED), 'pass': wins >= 2}
            legs['per_season_sign_check'] = sign['pass']
        gate[arm] = {'legs': legs, 'pass': all(legs.values()), 'sign_check': sign}
        out.append({'arm': arm, 'season': 'gate', 'kind': 'dev_gate', **gate[arm]})

    passing = [arm for arm in ARMS if gate[arm]['pass']]
    result = {'protocol': {'league': 'KR-KLeague3', 'seasons_loaded': SEAS,
                           'scored': SCORED, 'phase': 'regular',
                           'virgin_read': False},
              'rows': out, 'dev_passing_arms': passing,
              'gate_zero_dev_pass': gate['gate_zero']['pass'],
              'dev_gate': gate}
    (HERE / 'results_dev.json').write_text(json.dumps(result, indent=2) + '\n')
    fields = ['match_id', 'season', 'date', 'home', 'away', 'arm',
              'p_home_win', 'p_draw', 'p_away_win', 'p_over25',
              'actual_outcome', 'actual_over25', 'home_goals', 'away_goals',
              'lambda_home', 'lambda_away', 'rho']
    with (HERE / 'predictions_dev.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        writer.writerows(predictions)
    print('arm season kind n ll_1x2 rps oull_2_5')
    for x in out:
        if x['season'] == 'pooled' or x['season'] in SCORED and x['kind'] == 'model':
            print(x['arm'], x['season'], x['kind'], x['n'],
                  f"{x['ll_1x2']:.6f}", f"{x['rps']:.6f}", f"{x['oull_2_5']:.6f}")
    print('dev gate:', json.dumps(gate, sort_keys=True))
    return result


def virgin(requested=None):
    """Later-mode virgin evaluation; intentionally not invoked by this brief."""
    dev = json.loads((HERE / 'results_dev.json').read_text())
    if not dev['gate_zero_dev_pass']:
        raise SystemExit('G-KR3: Gate Zero failed dev gate; virgin must NOT be read')
    passing = dev['dev_passing_arms']
    if requested:
        passing = [arm for arm in passing if arm in requested]
    rows = load(SEAS + ['2025'])
    target = [r for r in rows if r['season'] == '2025']
    train = [r for r in rows if r['season'] != '2025']
    clim = score(target, [climatology(train)] * len(target))
    result = {'protocol': {'league': 'KR-KLeague3', 'virgin_read': True},
              'read_arms': passing, 'climatology': clim, 'arms': {}}
    for arm in passing:
        cutoff = min(r['date'] for r in target)
        model = DC().fit(train, cutoff)
        counts = match_counts(train)
        ps = [model.probs(*adjusted_lambdas(model, r['hi'], r['ai'], arm, counts))
              for r in target]
        metrics = score(target, ps)
        metrics['virgin_pass'] = (metrics['ll_1x2'] <= clim['ll_1x2'])
        result['arms'][arm] = metrics
    (HERE / 'results_virgin.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
