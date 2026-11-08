"""EDA for SK-1Liga (Slovakia 1. liga, FotMob id 176).

Reads data/sk_matches.csv (built by data/build_data.py) plus the
warehouse index/payloads for the tier-2 (2. Liga, id 8973) mover
check. Writes analysis/eda_numbers.json. Dev era = 2021/2022 seed +
2022/2023-2024/2025 evaluation; virgin = 2025/2026 (levels and the
cards artefact audit only); 2026/2027 is inventory only.
"""
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('/home/hatch/workspace/footballprediction')
M = list(csv.DictReader(open(HERE.parent / 'data' / 'sk_matches.csv')))
INC = [r for r in M if r['included'] == '1']
DEV_SEASONS = {'2021/2022', '2022/2023', '2023/2024', '2024/2025'}
DEV = [r for r in INC if r['season'] in DEV_SEASONS]
VIRGIN = [r for r in INC if r['season'] == '2025/2026']


def f(r, k):
    v = r.get(k)
    return None if v in (None, '', 'None') else float(v)


def avg(x):
    return round(statistics.mean(x), 6) if x else None


def cor(x, y):
    if len(x) < 2:
        return None
    a, b = statistics.mean(x), statistics.mean(y)
    den = math.sqrt(sum((u - a) ** 2 for u in x) * sum((v - b) ** 2 for v in y))
    return round(sum((u - a) * (v - b) for u, v in zip(x, y)) / den, 6) if den else None


def tot(r, k):
    a, b = f(r, k + '_home'), f(r, k + '_away')
    return None if a is None or b is None else a + b


def opp(s):
    return 'away' if s == 'home' else 'home'


# ---- F1: levels per season (included rows) ----
levels = {}
for season in sorted({r['season'] for r in INC}):
    rs = [r for r in INC if r['season'] == season]
    levels[season] = {
        'n': len(rs),
        'goals': avg([f(r, 'home_goals') + f(r, 'away_goals') for r in rs]),
        'home_goals': avg([f(r, 'home_goals') for r in rs]),
        'away_goals': avg([f(r, 'away_goals') for r in rs]),
        'sot': avg([tot(r, 'ShotsOnTarget') for r in rs if tot(r, 'ShotsOnTarget') is not None]),
        'corners': avg([tot(r, 'corners') for r in rs if tot(r, 'corners') is not None]),
        'total_shots': avg([tot(r, 'total_shots') for r in rs if tot(r, 'total_shots') is not None]),
        'yellows': avg([f(r, 'yellow_home') + f(r, 'yellow_away') for r in rs]),
        'stats_n': sum(r['has_stats_all'] == '1' for r in rs),
    }

# ---- F2: trait reliabilities (split-half odd/even team matches, per team-season) ----
TRAITS = {
    'goals_for': lambda r, s: f(r, s + '_goals'),
    'goals_against': lambda r, s: f(r, opp(s) + '_goals'),
    'sot_for': lambda r, s: f(r, 'ShotsOnTarget_' + s),
    'sot_against': lambda r, s: f(r, 'ShotsOnTarget_' + opp(s)),
    'corners_for': lambda r, s: f(r, 'corners_' + s),
    'corners_against': lambda r, s: f(r, 'corners_' + opp(s)),
    'yellows_for': lambda r, s: f(r, 'yellow_' + s),
    'yellows_against': lambda r, s: f(r, 'yellow_' + opp(s)),
    'possession_for': lambda r, s: f(r, 'BallPossesion_' + s),
    'possession_against': lambda r, s: f(r, 'BallPossesion_' + opp(s)),
    'total_shots_for': lambda r, s: f(r, 'total_shots_' + s),
    'total_shots_against': lambda r, s: f(r, 'total_shots_' + opp(s)),
}


def rel(getter):
    d = defaultdict(list)
    for r in DEV:
        for s in ('home', 'away'):
            d[(r['season'], r[f'{s}_team_id'])].append(getter(r, s))
    x, y = [], []
    for z in d.values():
        z = [v for v in z if v is not None]
        if len(z) >= 10:
            x.append(statistics.mean(z[0::2]))
            y.append(statistics.mean(z[1::2]))
    return {'r': cor(x, y), 'n_units': len(x)}


reliabilities = {k: rel(v) for k, v in TRAITS.items()}

# ---- F3: halves from event times (dev era) ----
g1 = sum(f(r, 'ht_home_goals') + f(r, 'ht_away_goals') for r in DEV)
ga = sum(f(r, 'home_goals') + f(r, 'away_goals') for r in DEV)
c1 = sum(f(r, 'ht_ev_yellow_home') + f(r, 'ht_ev_yellow_away') for r in DEV)
ca = sum(f(r, 'yellow_home') + f(r, 'yellow_away') for r in DEV)
g_share, y_share = g1 / ga, c1 / ca


def half_variance(total_fn, first_fn, p):
    rows = [r for r in DEV if total_fn(r) > 0]
    shares = [first_fn(r) / total_fn(r) for r in rows]
    observed = statistics.pvariance(shares)
    noise = statistics.mean([p * (1 - p) / total_fn(r) for r in rows])
    return {'observed_variance': round(observed, 6), 'noise_floor': round(noise, 6),
            'true_variance': round(observed - noise, 6), 'n_matches': len(rows)}


def share_split_half_r(total_fn, first_fn):
    d = defaultdict(list)
    for r in DEV:
        for s in ('home', 'away'):
            d[(r['season'], r[f'{s}_team_id'])].append((first_fn(r, s), total_fn(r, s)))
    x, y = [], []
    for z in d.values():
        halves = []
        for part in (z[0::2], z[1::2]):
            num = sum(a for a, b in part)
            den = sum(b for a, b in part)
            halves.append(num / den if den >= 3 else None)
        if halves[0] is not None and halves[1] is not None:
            x.append(halves[0])
            y.append(halves[1])
    return {'r': cor(x, y), 'n_units': len(x)}


halves = {
    'goals_1h_share': round(g_share, 6),
    'yellow_cards_1h_share': round(y_share, 6),
    'goals_total': ga,
    'yellow_total': ca,
    'goals_variance': half_variance(lambda r: f(r, 'home_goals') + f(r, 'away_goals'),
                                    lambda r: f(r, 'ht_home_goals') + f(r, 'ht_away_goals'), g_share),
    'yellows_variance': half_variance(lambda r: f(r, 'yellow_home') + f(r, 'yellow_away'),
                                      lambda r: f(r, 'ht_ev_yellow_home') + f(r, 'ht_ev_yellow_away'), y_share),
    'goals_share_team_r': share_split_half_r(
        lambda r, s: f(r, s + '_goals'),
        lambda r, s: f(r, 'ht_' + s + '_goals')),
    'yellows_share_team_r': share_split_half_r(
        lambda r, s: f(r, 'yellow_' + s),
        lambda r, s: f(r, 'ht_ev_yellow_' + s)),
    'sot_1h_share': None,
    'corners_1h_share': None,
    'total_shots_1h_share': None,
}

# ---- F4: movers (X2) — promoted clubs from 2. Liga (id 8973) ----
index = list(csv.DictReader(open(MAIN / 'data_enrichment/fotmob_world_index.csv')))
tier2_ids = defaultdict(set)
for z in index:
    if z['league_id'] != '8973':
        continue
    d = json.load(open(MAIN / z['path']))
    g = d.get('general') or {}
    for side in ('homeTeam', 'awayTeam'):
        tid = (g.get(side) or {}).get('id')
        if tid is not None:
            tier2_ids[z['season']].add(str(tid))

names = {}
for r in M:
    for s in ('home', 'away'):
        names[r[f'{s}_team_id']] = r[f'{s}_team']

movers = {}
completed = []
for season in ['2022/2023', '2023/2024', '2024/2025', '2025/2026']:
    y = int(season[:4])
    prior_label = f'{y - 1}/{y}'
    rs = [r for r in INC if r['season'] == season]
    prior_top = {r[f'{s}_team_id'] for r in INC if r['season'] == prior_label for s in ('home', 'away')}
    league_mean = sum(f(r, 'home_goals') + f(r, 'away_goals') for r in rs) / (2 * len(rs))
    rows = []
    for club in sorted(tier2_ids.get(prior_label, set()) - prior_top):
        if club not in {r[f'{s}_team_id'] for r in rs for s in ('home', 'away')}:
            continue
        cr = [r for r in rs if r['home_team_id'] == club or r['away_team_id'] == club]
        gf = sum(f(r, 'home_goals' if r['home_team_id'] == club else 'away_goals') for r in cr) / len(cr)
        gc = sum(f(r, 'away_goals' if r['home_team_id'] == club else 'home_goals') for r in cr) / len(cr)
        rows.append({'club': names.get(club, club), 'team_id': club, 'matches': len(cr),
                     'gf_per_match': round(gf, 6), 'ga_per_match': round(gc, 6),
                     'delta_gf': round(gf - league_mean, 6), 'delta_ga': round(gc - league_mean, 6)})
    movers[season] = {
        'league_mean_per_team_match': round(league_mean, 6),
        'clubs': rows,
        'cumulative_prior': {
            'delta_gf': avg([x['delta_gf'] for x in completed]),
            'delta_ga': avg([x['delta_ga'] for x in completed]),
            'n_transitions': len(completed),
        },
    }
    completed.extend(rows)

# ---- F5: referee coverage ----
ref_cov = {}
for season in sorted({r['season'] for r in M}):
    rs = [r for r in M if r['season'] == season]
    ref_cov[season] = {'named': sum(bool(r['referee']) for r in rs), 'n': len(rs)}
referee = {'coverage_by_season': ref_cov,
           'dev_coverage': round(sum(bool(r['referee']) for r in DEV) / len(DEV), 6),
           'reliability': None}

# ---- F6: cards artefact audit (virgin era, stats vs events) ----
both = [(tot(r, 'yellow_cards'), f(r, 'yellow_home') + f(r, 'yellow_away'))
        for r in VIRGIN if tot(r, 'yellow_cards') is not None]
cards_audit = {
    'virgin_n': len(VIRGIN),
    'stats_yellows_present': len(both),
    'exact_total_agreement': sum(1 for a, b in both if a == b),
    'stats_mean': avg([a for a, b in both]),
    'event_mean_on_same_rows': avg([b for a, b in both]),
    'dev_stats_key_matches': sum(1 for r in DEV if tot(r, 'yellow_cards') is not None),
    'target': 'event yellows (card == Yellow); YellowRed/Red excluded',
}

# ---- primary lines (dev pooled, included rows) ----
lines = {}
for name, key, cands in [('sot', 'ShotsOnTarget', [7.5, 8.5, 9.5]),
                         ('corners', 'corners', [9.5, 10.5, 11.5]),
                         ('cards', 'yellow', [3.5, 4.5, 5.5])]:
    vals = [tot(r, key) for r in DEV if tot(r, key) is not None]
    rates = {str(q): round(sum(v > q for v in vals) / len(vals), 6) for q in cands}
    lines[name] = {'n': len(vals), 'rates': rates,
                   'primary': min(cands, key=lambda q: abs(rates[str(q)] - 0.5))}
lines['goals'] = {'primary': 'OU2.5',
                  'over_rate': round(sum(f(r, 'home_goals') + f(r, 'away_goals') > 2.5 for r in DEV) / len(DEV), 6)}

out = {
    'counts': {
        'all_matches': len(M),
        'included': len(INC),
        'excluded_playoff': len(M) - len(INC),
        'included_by_season': {s: sum(r['season'] == s for r in INC)
                               for s in sorted({r['season'] for r in INC})},
        'team_ids': len({r[f'{s}_team_id'] for r in M for s in ('home', 'away')}),
    },
    'levels': levels,
    'reliabilities': reliabilities,
    'referee': referee,
    'halves': halves,
    'movers_x2': movers,
    'cards_audit': cards_audit,
    'primary_lines': lines,
}
json.dump(out, open(HERE / 'eda_numbers.json', 'w'), indent=2)
print(json.dumps(out, indent=2))
