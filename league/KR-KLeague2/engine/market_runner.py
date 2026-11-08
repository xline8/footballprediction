"""Dev + virgin runner for the KR-KLeague2 count markets.

Implements the frozen prereg gates exactly:
- dev pass (arm): pooled LL at the primary line beats BOTH baselines;
  variants also need the per-season sign check (variant LL <= Gate
  Zero LL in at least half of the scored dev seasons).
- virgin: read once, only for dev-passing arms; an arm passes iff
  LL <= Gate Zero virgin LL, LL <= best virgin baseline LL, and
  calibration |diff| <= 1pp (clean) or <= 1pp + 1 SE (provisional).
- winner: lowest virgin LL among passing arms; ties by arm order.
Predictions/params are written only when an arm passes the virgin
gate. If Gate Zero fails dev, virgin refuses to run at all.
"""
import csv, json, math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_common import (load, fit_ratings, lambdas, moment_r, nb_over,
                          box_touch_index, x7_multiplier, naive_mu)

CFG = {
    'sot':         dict(target=('ShotsOnTarget_home', 'ShotsOnTarget_away'), line=8.5,
                        secondary=(7.5, 9.5), arms=('gate_zero', 'x7'), half=0.415,
                        seed='2022', scored=('2023', '2024'), prefix='s'),
    'corners':     dict(target=('corners_home', 'corners_away'), line=8.5,
                        secondary=(9.5, 10.5), arms=('gate_zero', 'x7'), half=0.425,
                        seed='2022', scored=('2023', '2024'), prefix='c'),
    'cards':       dict(target=('yellow_home', 'yellow_away'), line=2.5,
                        secondary=(3.5, 4.5), arms=('gate_zero',), half=0.330,
                        seed='2023', scored=('2024',), prefix='k'),
    'total_shots': dict(target=('total_shots_home', 'total_shots_away'), line=24.5,
                        secondary=(23.5, 25.5), arms=('gate_zero', 'x7', 'e9'), half=0.421,
                        seed='2022', scored=('2023', '2024'), prefix='t'),
}


def ll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def predict_rows(rows, target_seasons, arms, cfg):
    """Season-blocked predictions for arms + baselines.

    Returns {name: [(row, mu_total, p_primary, {line: p})]} including
    'base_rate' and 'naive'. Baselines use each season's Gate Zero r
    (frozen in the prereg for naive; base rate is a constant prob)."""
    line = cfg['line']; lines = (line,) + cfg['secondary']
    out = {a: [] for a in list(arms) + ['base_rate', 'naive']}
    fits = {}
    for s in target_seasons:
        tar = [r for r in rows if r['season'] == s]
        cutoff = min(r['date'] for r in tar)
        train = [r for r in rows if r['date'] < cutoff]
        fit = fit_ratings(train, cutoff)
        idx = box_touch_index(train)
        r_full = moment_r(train, lambda z: sum(lambdas(fit, z['hi'], z['ai'])))
        r_e9 = moment_r(train, lambda z: sum(lambdas(fit, z['hi'], z['ai'])), last_n=200)
        rate = {L: sum(r['yh'] + r['ya'] > L for r in train) / len(train) for L in lines}
        fits[s] = (fit, r_full, r_e9)
        for z in tar:
            lh, la = lambdas(fit, z['hi'], z['ai'])
            for arm in arms:
                rr = r_e9 if arm == 'e9' else r_full
                ah, aa = lh, la
                if arm == 'x7':
                    mh, ma = x7_multiplier(idx, z['hi'], z['ai'])
                    ah, aa = lh * mh, la * ma
                mu = ah + aa
                out[arm].append((z, mu, {L: nb_over(mu, rr, L) for L in lines}, rr))
            out['base_rate'].append((z, None, {L: rate[L] for L in lines}, None))
            nmu = naive_mu(train, z['hi'], z['ai'])
            out['naive'].append((z, nmu, {L: nb_over(nmu, r_full, L) for L in lines}, r_full))
    return out, fits


def summarise(preds, line):
    """preds: [(row, mu, {line:p}, r)] -> pooled + per-season LL etc."""
    def block(pairs):
        if not pairs: return None
        ys = [1.0 if (r['yh'] + r['ya']) > line else 0.0 for r, _, _, _ in pairs]
        ps = [p[line] for _, _, p, _ in pairs]
        diffs = [p - y for p, y in zip(ps, ys)]
        md = sum(diffs) / len(diffs)
        se = (math.sqrt(sum((x - md) ** 2 for x in diffs) / (len(diffs) - 1) / len(diffs))
              if len(diffs) > 1 else 0.0)
        return {'n': len(pairs), 'll_primary': sum(ll(p, y) for p, y in zip(ps, ys)) / len(pairs),
                'mean_p': sum(ps) / len(ps), 'actual_rate': sum(ys) / len(ys),
                'calibration_diff': md, 'calibration_se': se}
    res = {'pooled': block(preds), 'seasons': {}}
    for s in sorted({r['season'] for r, _, _, _ in preds}):
        res['seasons'][s] = block([x for x in preds if x[0]['season'] == s])
    return res


def run_dev(kind):
    cfg = CFG[kind]
    seasons = [cfg['seed']] + list(cfg['scored'])
    rows = load(seasons, cfg['target'])
    if kind == 'cards':
        assert all(r['season'] in ('2023', '2024') for r in rows)
    preds, _ = predict_rows(rows, list(cfg['scored']), cfg['arms'], cfg)
    out = {'protocol': {'market': kind, 'primary_line': cfg['line'], 'seed': cfg['seed'],
                        'scored': list(cfg['scored'])},
           'arms': {}, 'baselines': {}}
    for a in cfg['arms']:
        out['arms'][a] = summarise(preds[a], cfg['line'])
    for b in ('base_rate', 'naive'):
        out['baselines'][b] = summarise(preds[b], cfg['line'])
    gz = out['arms']['gate_zero']['pooled']['ll_primary']
    bb = min(out['baselines'][b]['pooled']['ll_primary'] for b in ('base_rate', 'naive'))
    passing = []
    for a in cfg['arms']:
        v = out['arms'][a]
        ok = v['pooled']['ll_primary'] < out['baselines']['base_rate']['pooled']['ll_primary'] and \
             v['pooled']['ll_primary'] < out['baselines']['naive']['pooled']['ll_primary']
        sign = None
        if a != 'gate_zero':
            wins = sum(1 for s in cfg['scored']
                       if v['seasons'][s]['ll_primary'] <= out['arms']['gate_zero']['seasons'][s]['ll_primary'])
            sign = {'wins': wins, 'of': len(cfg['scored']), 'pass': wins * 2 >= len(cfg['scored'])}
            ok = ok and sign['pass']
        v['sign_check'] = sign
        v['dev_pass'] = bool(ok)
        if ok: passing.append(a)
    out['dev_passing_arms'] = passing
    out['gate_zero_dev_pass'] = 'gate_zero' in passing
    here = Path(__file__).resolve().parent / kind
    here.mkdir(exist_ok=True)
    (here / 'results_dev.json').write_text(json.dumps(out, indent=2) + '\n')
    with (here / 'results_dev.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['name', 'kind', 'scope', 'n', 'll_primary', 'mean_p', 'actual_rate', 'calibration_diff'])
        for kind2, block in (('arm', out['arms']), ('baseline', out['baselines'])):
            for name, v in block.items():
                w.writerow([name, kind2, 'pooled', v['pooled']['n'], v['pooled']['ll_primary'],
                            v['pooled']['mean_p'], v['pooled']['actual_rate'], v['pooled']['calibration_diff']])
                for s, sv in v['seasons'].items():
                    w.writerow([name, kind2, s, sv['n'], sv['ll_primary'], sv['mean_p'], sv['actual_rate'], sv['calibration_diff']])
    with (here / 'predictions_dev.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['match_id', 'season', 'arm', 'mu', 'r', 'p_over_primary', 'actual_total'])
        w.writeheader()
        for name in list(cfg['arms']) + ['base_rate', 'naive']:
            for r, mu, ps, rr in preds[name]:
                w.writerow({'match_id': r['match_id'], 'season': r['season'], 'arm': name,
                            'mu': '' if mu is None else mu, 'r': '' if rr is None else rr,
                            'p_over_primary': ps[cfg['line']], 'actual_total': r['yh'] + r['ya']})
    print(f"== {kind} DEV (primary {cfg['line']}) ==")
    for a in cfg['arms']:
        v = out['arms'][a]['pooled']
        print(f"{a:10s} n={v['n']} LL={v['ll_primary']:.6f} mean_p={v['mean_p']:.4f} actual={v['actual_rate']:.4f} dev_pass={out['arms'][a]['dev_pass']}")
    for b in ('base_rate', 'naive'):
        v = out['baselines'][b]['pooled']
        print(f"{b:10s} n={v['n']} LL={v['ll_primary']:.6f}")
    return out


def run_virgin(kind, requested=None):
    cfg = CFG[kind]
    here = Path(__file__).resolve().parent / kind
    dev = json.loads((here / 'results_dev.json').read_text())
    if not dev['gate_zero_dev_pass']:
        raise SystemExit(f'{kind}: Gate Zero failed dev gate; virgin must NOT be read')
    passing = dev['dev_passing_arms']
    if requested:
        bad = set(requested) - set(passing)
        if bad: raise SystemExit(f'{kind}: virgin refused for non-dev-passing arms: {sorted(bad)}')
        passing = [a for a in passing if a in requested]
    seasons = [cfg['seed']] + list(cfg['scored']) + ['2025']
    rows = load(seasons, cfg['target'])
    preds, fits = predict_rows(rows, ['2025'], [a for a in cfg['arms'] if a in passing], cfg)
    # baselines on the virgin window
    allrows = rows
    tar = [r for r in allrows if r['season'] == '2025']
    train = [r for r in allrows if r['date'] < min(r['date'] for r in tar)]
    fit = fit_ratings(train, min(r['date'] for r in tar))
    r_full = moment_r(train, lambda z: sum(lambdas(fit, z['hi'], z['ai'])))
    line = cfg['line']
    base = {'base_rate': [(z, None, {line: sum(r['yh'] + r['ya'] > line for r in train) / len(train)}, None) for z in tar],
            'naive': [(z, naive_mu(train, z['hi'], z['ai']),
                       {line: nb_over(naive_mu(train, z['hi'], z['ai']), r_full, line)}, r_full) for z in tar]}
    out = {'protocol': {'market': kind, 'primary_line': line, 'virgin_season': '2025'},
           'arms': {}, 'baselines': {}, 'read_arms': passing}
    for b in ('base_rate', 'naive'):
        out['baselines'][b] = summarise(base[b], line)['pooled']
    best_base = min(out['baselines'][b]['ll_primary'] for b in ('base_rate', 'naive'))
    gz_ll = None
    for a in passing:
        out['arms'][a] = summarise(preds[a], line)['pooled']
        if a == 'gate_zero': gz_ll = out['arms'][a]['ll_primary']
    winners = []
    for a in passing:
        v = out['arms'][a]
        cal = abs(v['calibration_diff'])
        v['calibration_class'] = ('clean' if cal <= 0.01 else
                                  'provisional' if cal <= 0.01 + v['calibration_se'] else 'fail')
        v['virgin_pass'] = bool(v['ll_primary'] <= gz_ll and v['ll_primary'] <= best_base
                                and v['calibration_class'] != 'fail')
        if v['virgin_pass']: winners.append(a)
    chosen = min(winners, key=lambda a: (out['arms'][a]['ll_primary'], cfg['arms'].index(a))) if winners else None
    out['shipped_arm'] = chosen
    (here / 'results_virgin.json').write_text(json.dumps(out, indent=2) + '\n')
    print(f"== {kind} VIRGIN 2025 (primary {line}) ==")
    for a in passing:
        v = out['arms'][a]
        print(f"{a:10s} n={v['n']} LL={v['ll_primary']:.6f} calib={v['calibration_diff']*100:+.2f}pp SE={v['calibration_se']*100:.2f}pp class={v['calibration_class']} pass={v['virgin_pass']}")
    for b in ('base_rate', 'naive'):
        print(f"{b:10s} LL={out['baselines'][b]['ll_primary']:.6f}")
    print('shipped:', chosen)
    if chosen:
        fit, r_full, r_e9 = fits['2025']
        rr = r_e9 if chosen == 'e9' else r_full
        idx = box_touch_index(train)
        dest = here.parents[1] / 'predictions'
        dest.mkdir(exist_ok=True)
        with (dest / f"{cfg['prefix']}_kr2_virgin_predictions.csv").open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['match_id', 'date', 'home_team', 'away_team', 'arm',
                                              'expected_home', 'expected_away', 'expected_total', 'r',
                                              'p_over_primary', 'mean_1h', 'mean_2h', 'actual_total'])
            w.writeheader()
            for z, mu, ps, _ in preds[chosen]:
                lh, la = lambdas(fit, z['hi'], z['ai'])
                if chosen == 'x7':
                    mh, ma = x7_multiplier(idx, z['hi'], z['ai']); lh, la = lh * mh, la * ma
                w.writerow({'match_id': z['match_id'], 'date': z['date'].isoformat(),
                            'home_team': z['home'], 'away_team': z['away'], 'arm': chosen,
                            'expected_home': lh, 'expected_away': la, 'expected_total': lh + la,
                            'r': rr, 'p_over_primary': ps[line],
                            'mean_1h': (lh + la) * cfg['half'], 'mean_2h': (lh + la) * (1 - cfg['half']),
                            'actual_total': z['yh'] + z['ya']})
        params = {'arm': chosen, 'r': rr, 'level_h': fit['level_h'], 'level_a': fit['level_a'],
                  'att': {str(k): v for k, v in fit['att'].items()},
                  'def': {str(k): v for k, v in fit['def'].items()},
                  'halves_share_1h': cfg['half'], 'primary_line': line}
        (here / 'fitted_params_virgin.json').write_text(json.dumps(params, indent=2) + '\n')
    return out


def main(kind, mode, requested=None):
    if mode == 'dev': return run_dev(kind)
    if mode == 'virgin': return run_virgin(kind, requested)
    raise SystemExit('mode must be dev or virgin')
