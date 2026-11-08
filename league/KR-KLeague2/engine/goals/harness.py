"""G-KR2 harness: season-blocked walk-forward dev + gated virgin.

Implements PREREG_G_KR2 exactly. Dev gate legs (all required):
Gate Zero pooled 1X2 LL, RPS and OU 2.5 LL all beat expanding
climatology; variants must also beat climatology on all three legs
and pass the per-season sign check (>= 2 of 3 scored seasons with
1X2 LL <= Gate Zero). Virgin gate per arm: 1X2 LL <= Gate Zero and
<= climatology; calibration (home-win and OU 2.5) classified clean
(|diff| <= 1pp) / provisional (<= 1pp + 1 SE) / fail; the worse leg
classifies the arm. Winner = lowest virgin 1X2 LL, ties in arm
order. Halves presentation uses THIS league's frozen goals 1H share
0.396 (config.yaml).
"""
import csv, json, math
from pathlib import Path
from datetime import date
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dc import DC
from arms import adjusted_lambdas, match_counts, mover_offsets

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / 'data' / 'kr2_matches.csv'
SEAS = ['2021', '2022', '2023', '2024']
SCORED = ['2022', '2023', '2024']
ARMS = ['gate_zero', 'shrink', 'x2']
HALF_1H = 0.396


def load(seasons):
    rows = []
    with open(DATA) as f:
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
        rps += 0.5 * ((q[0] - y[0]) ** 2 + (q[0] + q[1] - y[0] - y[1]) ** 2)
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
    tar = [r for r in rows if r['season'] == season]
    cutoff = min(r['date'] for r in tar)
    train = [r for r in rows if r['date'] < cutoff]
    model = DC().fit(train, cutoff)
    counts = match_counts(train)
    movers = mover_offsets(season, train) if arm == 'x2' else {}
    ps = [model.probs(*adjusted_lambdas(model, r['hi'], r['ai'], arm, counts, movers)) for r in tar]
    return tar, train, model, counts, movers, ps


def run_dev():
    rows = load(SEAS)
    out = []
    pred = []
    for arm in ARMS:
        pooled_rows, pooled_ps, pooled_clim = [], [], []
        for s in SCORED:
            tar, train, model, counts, movers, ps = _season_fit(rows, s, arm)
            for r, p in zip(tar, ps):
                lh, la = adjusted_lambdas(model, r['hi'], r['ai'], arm, counts, movers)
                pred.append({'match_id': r['match_id'], 'season': s, 'arm': arm,
                             'lam_h': lh, 'lam_a': la, 'rho': model.rho, **p,
                             'home_goals': r['yh'], 'away_goals': r['ya']})
            z = score(tar, ps); z.update(arm=arm, season=s, kind='model'); out.append(z)
            cp = climatology(train)
            cps = [cp] * len(tar)
            z = score(tar, cps); z.update(arm=arm, season=s, kind='climatology'); out.append(z)
            pooled_rows += tar; pooled_ps += ps; pooled_clim += cps
        z = score(pooled_rows, pooled_ps); z.update(arm=arm, season='pooled', kind='model'); out.append(z)
        z = score(pooled_rows, pooled_clim); z.update(arm=arm, season='pooled', kind='climatology'); out.append(z)
    # dev gate
    def pooled(arm, kind, key):
        return next(x[key] for x in out if x['arm'] == arm and x['season'] == 'pooled' and x['kind'] == kind)
    passing = []
    for arm in ARMS:
        ok = (pooled(arm, 'model', 'll_1x2') < pooled(arm, 'climatology', 'll_1x2')
              and pooled(arm, 'model', 'rps') < pooled(arm, 'climatology', 'rps')
              and pooled(arm, 'model', 'oull_2_5') < pooled(arm, 'climatology', 'oull_2_5'))
        sign = None
        if arm != 'gate_zero':
            wins = sum(1 for s in SCORED
                       if next(x['ll_1x2'] for x in out if x['arm'] == arm and x['season'] == s and x['kind'] == 'model')
                       <= next(x['ll_1x2'] for x in out if x['arm'] == 'gate_zero' and x['season'] == s and x['kind'] == 'model'))
            sign = {'wins': wins, 'of': len(SCORED), 'pass': wins >= 2}
            ok = ok and sign['pass']
        if ok:
            passing.append(arm)
        out.append({'arm': arm, 'season': 'gate', 'kind': 'dev_gate', 'dev_pass': bool(ok), 'sign_check': sign})
    result = {'protocol': {'league': 'KR-KLeague2', 'seasons_loaded': SEAS, 'scored': SCORED,
                           'phase': 'regular'},
              'rows': out, 'dev_passing_arms': passing,
              'gate_zero_dev_pass': 'gate_zero' in passing}
    (HERE / 'results_dev.json').write_text(json.dumps(result, indent=2) + '\n')
    with (HERE / 'results_dev.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['arm', 'season', 'kind', 'n', 'll_1x2', 'rps', 'oull_2_5'])
        w.writeheader()
        w.writerows({k: x.get(k) for k in w.fieldnames} for x in out if x.get('kind') in ('model', 'climatology'))
    with (HERE / 'predictions_dev.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(pred[0])); w.writeheader(); w.writerows(pred)
    print('arm season kind n ll_1x2 rps oull_2_5')
    for x in out:
        if x['season'] == 'pooled':
            print(x['arm'], x['season'], x['kind'], x['n'], f"{x['ll_1x2']:.6f}", f"{x['rps']:.6f}", f"{x['oull_2_5']:.6f}")
    print('dev passing:', passing)
    return result


def _calibration(rows, ps, key, actual_fn):
    diffs = [p[key] - actual_fn(r) for r, p in zip(rows, ps)]
    md = sum(diffs) / len(diffs)
    se = math.sqrt(sum((x - md) ** 2 for x in diffs) / (len(diffs) - 1) / len(diffs))
    return {'diff': md, 'se': se}


def _classify(cal):
    a = abs(cal['diff'])
    return 'clean' if a <= 0.01 else ('provisional' if a <= 0.01 + cal['se'] else 'fail')


def virgin(requested=None):
    dev = json.loads((HERE / 'results_dev.json').read_text())
    if not dev['gate_zero_dev_pass']:
        raise SystemExit('G-KR2: Gate Zero failed dev gate; virgin must NOT be read')
    passing = dev['dev_passing_arms']
    if requested:
        bad = set(requested) - set(passing)
        if bad:
            raise SystemExit(f'G-KR2: virgin refused for non-dev-passing arms: {sorted(bad)}')
        passing = [a for a in passing if a in requested]
    rows = load(SEAS + ['2025'])
    tar = [r for r in rows if r['season'] == '2025']
    train = [r for r in rows if r['season'] != '2025']
    cp = climatology(train)
    clim = score(tar, [cp] * len(tar))
    out = {'arms': {}, 'climatology': clim, 'read_arms': passing}
    packs = {}
    for a in passing:
        model = DC().fit(train, min(r['date'] for r in tar))
        counts = match_counts(train)
        movers = mover_offsets('2025', train) if a == 'x2' else {}
        ps = [model.probs(*adjusted_lambdas(model, r['hi'], r['ai'], a, counts, movers)) for r in tar]
        met = score(tar, ps)
        cal_hw = _calibration(tar, ps, 'ph', lambda r: 1.0 if r['yh'] > r['ya'] else 0.0)
        cal_ou = _calibration(tar, ps, 'over25', lambda r: 1.0 if r['yh'] + r['ya'] > 2.5 else 0.0)
        cls = max((_classify(cal_hw), _classify(cal_ou)),
                  key=lambda c: ('clean', 'provisional', 'fail').index(c))
        met.update({'calibration_home_win': cal_hw, 'calibration_over25': cal_ou,
                    'calibration_class': cls,
                    'virgin_pass': bool(met['ll_1x2'] <= out.get('arms', {}).get('gate_zero', met)['ll_1x2']
                                        and met['ll_1x2'] <= clim['ll_1x2'] and cls != 'fail')})
        out['arms'][a] = met
        packs[a] = (model, ps, counts, movers)
    # gate_zero comparison must use the actual GZ value even if dict order differs
    if 'gate_zero' in out['arms']:
        gz = out['arms']['gate_zero']['ll_1x2']
        for a, met in out['arms'].items():
            met['virgin_pass'] = bool(met['ll_1x2'] <= gz and met['ll_1x2'] <= clim['ll_1x2']
                                      and met['calibration_class'] != 'fail')
    winners = [a for a in passing if out['arms'][a]['virgin_pass']]
    chosen = min(winners, key=lambda a: (out['arms'][a]['ll_1x2'], ARMS.index(a))) if winners else None
    out['shipped_arm'] = chosen
    (HERE / 'results_virgin.json').write_text(json.dumps(out, indent=2) + '\n')
    print('arm n ll_1x2 rps oull clim_ll cal_hw cal_ou class pass')
    for a, met in out['arms'].items():
        print(a, met['n'], f"{met['ll_1x2']:.6f}", f"{met['rps']:.6f}", f"{met['oull_2_5']:.6f}",
              f"{clim['ll_1x2']:.6f}", f"{met['calibration_home_win']['diff']*100:+.2f}pp",
              f"{met['calibration_over25']['diff']*100:+.2f}pp", met['calibration_class'], met['virgin_pass'])
    print('shipped:', chosen)
    if chosen:
        model, ps, counts, movers = packs[chosen]
        dest = HERE.parents[1] / 'predictions'
        dest.mkdir(exist_ok=True)
        fields = ['match_id', 'date', 'home_team', 'away_team', 'home_goals', 'away_goals',
                  'lam_h', 'lam_a', 'rho', 'ph', 'pd', 'pa', 'p_over_1_5', 'p_over_2_5',
                  'p_over_3_5', 'p_btts', 'lam_h_1h', 'lam_a_1h', 'lam_h_2h', 'lam_a_2h', 'arm']
        with (dest / 'g_kr2_virgin_predictions.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r, p in zip(tar, ps):
                lh, la = adjusted_lambdas(model, r['hi'], r['ai'], chosen, counts, movers)
                w.writerow({'match_id': r['match_id'], 'date': r['date'].isoformat(),
                            'home_team': r['home'], 'away_team': r['away'],
                            'home_goals': r['yh'], 'away_goals': r['ya'],
                            'lam_h': lh, 'lam_a': la, 'rho': model.rho,
                            'ph': p['ph'], 'pd': p['pd'], 'pa': p['pa'],
                            'p_over_1_5': p['over15'], 'p_over_2_5': p['over25'],
                            'p_over_3_5': p['over35'], 'p_btts': p['btts'],
                            'lam_h_1h': lh * HALF_1H, 'lam_a_1h': la * HALF_1H,
                            'lam_h_2h': lh * (1 - HALF_1H), 'lam_a_2h': la * (1 - HALF_1H),
                            'arm': chosen})
        params = {'arm': chosen, 'a': {str(k): v for k, v in model.a.items()},
                  'd': {str(k): v for k, v in model.d.items()}, 'h': model.h,
                  'rho': model.rho, 'mu': model.mu,
                  'movers': {str(k): v for k, v in movers.items()},
                  'halves_share_1h': HALF_1H}
        (HERE / 'fitted_params_virgin.json').write_text(json.dumps(params, indent=2) + '\n')
    return out
