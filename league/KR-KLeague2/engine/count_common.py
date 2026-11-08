"""Shared count-market mechanics for KR-KLeague2 (SOT / corners / cards / total shots).

Gate Zero = production count pattern: Poisson team attack/defence
ratings fitted by damped iterative proportional fitting (IPF), then
CENTRED on the training league means so a team with no history is
predicted at the league level (the production cards model's fallback
behaviour). Solver note: the goals-scale IPF step (0.7 x 14) oscillates
on count-scale targets (train totals swing 234 -> 3 -> 174 -> ...);
the frozen family is unchanged, only the solver damping differs
(step 0.25, 100 iterations, verified to converge on every
market/season training window in this league).

All features for a target season use only matches before that season.
"""
import csv, math
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'kr2_matches.csv'
HL_DAYS = 270.0
IPF_STEP = 0.25
IPF_ITERS = 100
PRIOR = 0.25


def load(seasons, target):
    out = []
    with DATA.open() as f:
        for x in csv.DictReader(f):
            if x['season'] not in seasons or x['phase'] != 'regular':
                continue
            if x.get(target[0], '') == '' or x.get(target[1], '') == '':
                continue
            out.append({'match_id': x['match_id'], 'season': x['season'],
                        'date': date.fromisoformat(x['date']),
                        'hi': int(x['home_team_id']), 'ai': int(x['away_team_id']),
                        'home': x['home_team'], 'away': x['away_team'],
                        'yh': float(x[target[0]]), 'ya': float(x[target[1]]),
                        'touch_h': float(x['touches_opp_box_home']) if x['touches_opp_box_home'] else None,
                        'touch_a': float(x['touches_opp_box_away']) if x['touches_opp_box_away'] else None})
    assert not any(r['season'] == '2026' for r in out)
    return sorted(out, key=lambda r: (r['date'], r['match_id']))


def fit_ratings(train, cutoff):
    """Damped IPF on decayed counts; returns centred rating dict.

    Raw fixed point: lam_h = exp(a[h] + d[a] + h), lam_a = exp(a[a] +
    d[h]). Centring subtracts the plain means abar/dbar from a/d and
    folds them into level_h/level_a, leaving known-team lambdas
    unchanged and making unseen teams predict the league level.
    """
    a = defaultdict(float); d = defaultdict(float); h = 0.0
    obs = [(r, 0.5 ** ((cutoff - r['date']).days / HL_DAYS)) for r in train]
    wg_h = wg_a = wm = 0.0
    for r, w in obs:
        wg_h += w * r['yh']; wg_a += w * r['ya']; wm += w
    mu_h, mu_a = wg_h / wm, wg_a / wm
    for _ in range(IPF_ITERS):
        of = defaultdict(float); ef = defaultdict(float)
        od = defaultdict(float); ed = defaultdict(float); so = se = 0.0
        for r, w in obs:
            lh = math.exp(a[r['hi']] + d[r['ai']] + h)
            la = math.exp(a[r['ai']] + d[r['hi']])
            of[r['hi']] += w * r['yh']; ef[r['hi']] += w * lh
            of[r['ai']] += w * r['ya']; ef[r['ai']] += w * la
            od[r['ai']] += w * r['yh']; ed[r['ai']] += w * lh
            od[r['hi']] += w * r['ya']; ed[r['hi']] += w * la
            so += w * r['yh']; se += w * lh
        for t in set(of) | set(ef):
            a[t] += IPF_STEP * math.log((of[t] + PRIOR) / (ef[t] + PRIOR))
        for t in set(od) | set(ed):
            d[t] += IPF_STEP * math.log((od[t] + PRIOR) / (ed[t] + PRIOR))
        h += IPF_STEP * math.log((so + PRIOR) / (se + PRIOR))
    teams = set(a) | set(d)
    abar = sum(a[t] for t in teams) / len(teams)
    dbar = sum(d[t] for t in teams) / len(teams)
    return {'att': {t: a[t] - abar for t in teams},
            'def': {t: d[t] - dbar for t in teams},
            'level_h': math.exp(abar + dbar + h),
            'level_a': math.exp(abar + dbar),
            'mu_h': mu_h, 'mu_a': mu_a}


def lambdas(fit, hid, aid):
    lh = fit['level_h'] * math.exp(fit['att'].get(hid, 0.0) + fit['def'].get(aid, 0.0))
    la = fit['level_a'] * math.exp(fit['att'].get(aid, 0.0) + fit['def'].get(hid, 0.0))
    return lh, la


def moment_r(train, predict_total, last_n=None):
    """Frozen moment estimator: r = sum(mu^2) / sum((y-mu)^2 - mu)."""
    z = train[-last_n:] if last_n else train
    num = den = 0.0
    for r in z:
        mu = predict_total(r); y = r['yh'] + r['ya']
        num += mu * mu; den += (y - mu) ** 2 - mu
    return 500.0 if den <= 0 else min(500.0, max(2.0, num / den))


def nb_over(mu, r, line):
    """P(X > line) for Negative Binomial with mean mu and size r."""
    p = r / (r + mu); q = 1.0 - p; cdf = 0.0; term = p ** r
    for k in range(0, int(math.floor(line)) + 1):
        cdf += term
        term *= q * (r + k) / (k + 1)
    return min(1.0, max(0.0, 1.0 - cdf))


def box_touch_index(train):
    per = defaultdict(list); allv = []
    for r in train:
        if r['touch_h'] is not None and r['touch_a'] is not None:
            per[r['hi']].append((r['touch_h'], r['touch_a']))
            per[r['ai']].append((r['touch_a'], r['touch_h']))
            allv += [r['touch_h'], r['touch_a']]
    league = sum(allv) / len(allv) if allv else 1.0
    idx = {}
    for t, z in per.items():
        idx[t] = {'att': (sum(x for x, _ in z) / len(z)) / league,
                  'def': (sum(y for _, y in z) / len(z)) / league,
                  'active': len(z) >= 8}
    return idx


def x7_multiplier(idx, hid, aid):
    if hid not in idx or aid not in idx or not idx[hid]['active'] or not idx[aid]['active']:
        return 1.0, 1.0
    mh = math.sqrt(idx[hid]['att'] * idx[aid]['def'])
    ma = math.sqrt(idx[aid]['att'] * idx[hid]['def'])
    return min(2.0, max(0.5, mh)), min(2.0, max(0.5, ma))


def naive_mu(train, hid, aid):
    """Trailing-10 naive, frozen construction: per side,
    (team's last-10 for + opponent's last-10 against) / 2, using only
    pre-season matches; league side means as the no-history fallback."""
    def last10(t):
        return [r for r in train if r['hi'] == t or r['ai'] == t][-10:]
    def for_mean(t):
        z = last10(t)
        if not z: return None
        return sum(r['yh'] if r['hi'] == t else r['ya'] for r in z) / len(z)
    def against_mean(t):
        z = last10(t)
        if not z: return None
        return sum(r['ya'] if r['hi'] == t else r['yh'] for r in z) / len(z)
    mu_h = sum(r['yh'] for r in train) / len(train)
    mu_a = sum(r['ya'] for r in train) / len(train)
    fh, aa = for_mean(hid), against_mean(aid)
    fa, ah = for_mean(aid), against_mean(hid)
    lh = ((fh if fh is not None else mu_h) + (aa if aa is not None else mu_a)) / 2
    la = ((fa if fa is not None else mu_a) + (ah if ah is not None else mu_h)) / 2
    return lh + la
