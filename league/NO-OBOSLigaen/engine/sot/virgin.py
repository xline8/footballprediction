"""S-NO-OBOS virgin read: season 2026, ONCE, dev-passing arms only.

Walk-forward continuing from the dev end state (the harness replays
2021-2025 to rebuild state, exactly as the dev run consumed them, then
scores 2026). Written by the coordinator after the dev results were
frozen and verified; the dev harness itself never loads 2026.
Outputs results_virgin.json + virgin_rows.csv (per-match, for
independent recomputation) in this directory. Predictions export is a
separate step (write_predictions) run only after the gate legs are
applied.
"""
import csv, json, math, os
from model import Engine, load_matches
from harness import DATA, OUT, ll, actual

VIRGIN = '2026'
ALL = ('2021', '2022', '2023', '2024', '2025', '2026')
PRIMARY = 9.5
ARMS = ('GZ', 'RS')  # both passed the dev gate (results_dev.json)


def arm_metrics(rows):
    n = len(rows)
    ps = [p['probs'][PRIMARY] for _, p in rows]
    ys = [actual(m) for m, _ in rows]
    diff = sum(ps) / n - sum(ys) / n
    se = math.sqrt(sum((p - y - diff) ** 2 for p, y in zip(ps, ys)) / (n - 1)) / math.sqrt(n)
    return {'n': n, 'll_9.5': sum(ll(p, y) for p, y in zip(ps, ys)) / n,
            'mean_predicted_over_rate': sum(ps) / n, 'actual_over_rate': sum(ys) / n,
            'calibration_diff': diff, 'calibration_se': se}


def main():
    dev = json.load(open(os.path.join(OUT, 'results_dev.json')))
    for arm in ARMS:
        a = dev['arms'][arm]
        assert a['pooled_dev_ll_9.5'] < dev['baselines']['base_rate']['pooled_dev_ll_9.5']
        assert a['pooled_dev_ll_9.5'] < dev['baselines']['naive_trailing_10']['pooled_dev_ll_9.5']
    ms = load_matches(DATA, set(ALL))
    out = {'protocol': 'S-NO-OBOS VIRGIN; season 2026 read once; arms GZ+RS (dev-passing)',
           'primary_line': PRIMARY, 'arms': {}, 'baselines': {}}
    allrows = {}
    for arm in ARMS:
        eng = Engine(ms, arm)
        rows = []
        for m in ms:
            if m['season'] == VIRGIN:
                rows.append((m, eng.predict(m)))
            eng.update(m)
        allrows[arm] = rows
        out['arms'][arm] = arm_metrics(rows)
    pre = [m for m in ms if m['season'] != VIRGIN]
    base_rate = sum(actual(m) for m in pre) / len(pre)
    grows = allrows['GZ']
    n = len(grows)
    ys = [actual(m) for m, _ in grows]
    for name, fn in (('base_rate', lambda m, p: base_rate),
                     ('naive_trailing_10', lambda m, p: p['naive_probs'][PRIMARY])):
        ps = [fn(m, p) for m, p in grows]
        diff = sum(ps) / n - sum(ys) / n
        se = math.sqrt(sum((p - y - diff) ** 2 for p, y in zip(ps, ys)) / (n - 1)) / math.sqrt(n)
        out['baselines'][name] = {'n': n, 'll_9.5': sum(ll(p, y) for p, y in zip(ps, ys)) / n,
                                  'mean_predicted_over_rate': sum(ps) / n,
                                  'actual_over_rate': sum(ys) / n,
                                  'calibration_diff': diff, 'calibration_se': se}
    out['base_rate_value'] = base_rate
    with open(os.path.join(OUT, 'results_virgin.json'), 'w') as f:
        json.dump(out, f, indent=2)
    fields = ['kind', 'arm_or_baseline', 'season', 'match_id', 'p_over_9_5', 'actual_over_9_5', 'exp_sot_total']
    with open(os.path.join(OUT, 'virgin_rows.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm, rows in allrows.items():
            for m, p in rows:
                w.writerow({'kind': 'arm', 'arm_or_baseline': arm, 'season': m['season'],
                            'match_id': m['match_id'], 'p_over_9_5': p['probs'][PRIMARY],
                            'actual_over_9_5': actual(m), 'exp_sot_total': p['exp_h'] + p['exp_a']})
        for m, p in grows:
            w.writerow({'kind': 'baseline', 'arm_or_baseline': 'naive_trailing_10', 'season': m['season'],
                        'match_id': m['match_id'], 'p_over_9_5': p['naive_probs'][PRIMARY],
                        'actual_over_9_5': actual(m), 'exp_sot_total': p['exp_h'] + p['exp_a']})
    print(json.dumps(out, indent=2))
    return out


if __name__ == '__main__':
    main()
