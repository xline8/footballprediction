"""G-PT virgin run: fit on 2021/2022-2025/2026, score 2026/2027 once.
Arms gate_zero and shrink both passed the dev gate (shrink is a
documented clone). Writes results_virgin.json, fitted_params_virgin.json
and the shipped arm's predictions (tie -> gate_zero)."""
import csv, json, math, sys
from datetime import date
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_g_pt import DC, ll, pois, tau  # noqa: E402

DATA = HERE.parents[1] / "data/pt_matches.csv"
SEASONS = ["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026"]
VIRGIN = "2026/2027"

def load(seasons):
    out = []
    with open(DATA, newline='', encoding='utf-8') as f:
        for x in csv.DictReader(f):
            if x['season'] not in seasons: continue
            out.append({'id': x['match_id'], 'season': x['season'],
                        'date': date.fromisoformat(x['date']), 'hi': x['home_id'], 'ai': x['away_id'],
                        'home': x['home_team'], 'away': x['away_team'],
                        'yh': float(x['home_goals']), 'ya': float(x['away_goals']),
                        'xgh': float(x['xg_home']), 'xga': float(x['xg_away'])})
    return sorted(out, key=lambda z: (z['date'], z['id']))

def main():
    dev = json.loads((HERE / 'results_dev.json').read_text())
    pooled = {(r['arm'], r['kind']): r for r in dev['results'] if r['season'] == 'pooled'}
    clim = pooled[('gate_zero', 'climatology')]
    passing = [a for a in ('gate_zero', 'shrink')
               if pooled[(a, 'model')]['ll_1x2'] < clim['ll_1x2'] and pooled[(a, 'model')]['rps'] < clim['rps']
               and pooled[(a, 'model')]['ll_ou2_5'] < clim['ll_ou2_5']]
    assert passing, "no arm passed the dev gate; virgin must not be read"
    rows = load(SEASONS + [VIRGIN])
    tr = [r for r in rows if r['season'] in SEASONS]
    te = [r for r in rows if r['season'] == VIRGIN]
    cut = min(r['date'] for r in te)
    hw = sum(r['yh'] > r['ya'] for r in tr) / len(tr)
    dw = sum(r['yh'] == r['ya'] for r in tr) / len(tr)
    po_c = sum(r['yh'] + r['ya'] > 2.5 for r in tr) / len(tr)
    results, fits, preds_by_arm = {}, {}, {}
    for arm in passing:
        dc = DC(arm == 'shrink'); dc.fit(tr, cut); dc.apply_shrink()
        fits[arm] = {'rho': dc.rho, 'h': dc.h, 'a': dict(dc.a), 'd': dict(dc.d),
                     'team_counts': dict(dc.count)}
        ps = []
        for g in te:
            ph, pd, pa, po = dc.probs(g)
            ps.append((g, ph, pd, pa, po))
        n = len(ps)
        ll1 = sum(-math.log(max(ph if g['yh'] > g['ya'] else (pd if g['yh'] == g['ya'] else pa), 1e-12)) for g, ph, pd, pa, po in ps) / n
        ou = sum(ll(po, int(g['yh'] + g['ya'] > 2.5)) for g, ph, pd, pa, po in ps) / n
        dh = [ph - int(g['yh'] > g['ya']) for g, ph, pd, pa, po in ps]
        do = [po - int(g['yh'] + g['ya'] > 2.5) for g, ph, pd, pa, po in ps]
        def sd(v):
            m = sum(v) / len(v); return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))
        results[arm] = {'n': n, 'll_1x2': ll1, 'll_ou2_5': ou,
                        'calib_home_win_pp': 100 * sum(dh) / n, 'se_home_win_pp': 100 * sd(dh) / math.sqrt(n),
                        'calib_ou25_pp': 100 * sum(do) / n, 'se_ou25_pp': 100 * sd(do) / math.sqrt(n),
                        'mean_ph': sum(ph for _, ph, *_ in ps) / n, 'actual_hw': sum(g['yh'] > g['ya'] for g, *_ in ps) / n,
                        'mean_p_over25': sum(po for *_, po in ps) / n, 'actual_over25': sum(g['yh'] + g['ya'] > 2.5 for g, *_ in ps) / n}
        preds_by_arm[arm] = (dc, ps)
    cl_ll = sum(-math.log(max(hw if g['yh'] > g['ya'] else (dw if g['yh'] == g['ya'] else 1 - hw - dw), 1e-12)) for g in te) / len(te)
    results['climatology'] = {'n': len(te), 'll_1x2': cl_ll, 'll_ou2_5': sum(ll(po_c, int(g['yh'] + g['ya'] > 2.5)) for g in te) / len(te)}
    (HERE / 'results_virgin.json').write_text(json.dumps({'protocol': 'G-PT VIRGIN (transitional 2026/2027)', 'passing_arms': passing, 'results': results}, indent=2) + '\n')
    (HERE / 'fitted_params_virgin.json').write_text(json.dumps(fits, indent=2) + '\n')
    # shipped arm decided by the verdict's gate arithmetic; write gate_zero
    # predictions (the tie rule ships gate_zero when arms are identical).
    dc, ps = preds_by_arm['gate_zero']
    out = HERE.parents[1] / 'predictions' / 'g_pt_virgin_predictions.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['match_id','date','home','away','home_goals','away_goals','arm','lam_home','lam_away','p_home','p_draw','p_away','p_over15','p_over25','p_over35','p_btts','p_over05_1h','p_over15_1h','p_over25_1h','p_over15_2h','p_over25_2h','p_over35_2h'])
        for g, ph, pd, pa, po in ps:
            lh, la = dc.lam(g['hi'], g['ai'])
            mm = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, dc.rho) for y in range(11)] for x in range(11)]
            zz = sum(map(sum, mm))
            btts = (1 - sum(mm[0][y] for y in range(11)) / zz - sum(mm[x][0] for x in range(11)) / zz + mm[0][0] / zz)
            def over_scaled(scale, line):
                a1, a2 = lh * scale, la * scale
                mm = [[pois(x, a1) * pois(y, a2) * tau(x, y, a1, a2, dc.rho) for y in range(11)] for x in range(11)]
                zz = sum(map(sum, mm))
                return sum(mm[x][y] for x in range(11) for y in range(11) if x + y > line) / zz
            o = lambda _m, line: over_scaled(0.443, line)
            m1 = None
            o2 = lambda line: over_scaled(0.557, line)
            w.writerow([g['id'], g['date'].isoformat(), g['home'], g['away'], int(g['yh']), int(g['ya']), 'gate_zero',
                        round(lh,4), round(la,4), round(ph,6), round(pd,6), round(pa,6),
                        round(dc.over(lh, la, 1.5),6), round(po,6), round(dc.over(lh, la, 3.5),6), round(btts,6),
                        round(o(m1,0.5),6), round(o(m1,1.5),6), round(o(m1,2.5),6),
                        round(o2(1.5),6), round(o2(2.5),6), round(o2(3.5),6)])
    print(json.dumps(results, indent=1))
if __name__ == '__main__': main()
