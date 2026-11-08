"""Vietnam V-League inventory and dev-only scores EDA.

2025/2026 (virgin) and 2026/2027 (in progress) appear in inventory/levels
only — no fitting, no trait or halves numbers are computed on them.
The frozen goals 1H constant is dev-only (2021-2024/2025).
"""
import csv, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
IDX = ROOT / 'data_enrichment/fotmob_world_index.csv'
WH = ROOT if (ROOT / 'data_enrichment/fotmob_world/Vietnam').exists() else Path.home() / 'workspace/footballprediction'
M = pd.read_csv(HERE.parent / 'data' / 'vn_vleague_matches.csv')
M.season = M.season.astype(str)
M['tot_goals'] = M.home_goals + M.away_goals
TM = pd.read_csv(HERE.parent / 'data' / 'vn_vleague_team_matches.csv')
TM.season = TM.season.astype(str)

idx = [r for r in csv.DictReader(open(IDX)) if r['league_id'] == '9088']

def season_start_key(v):
    return (int(str(v).split('/')[0]), str(v))

def payload(r):
    d = json.load(open(WH / r['path']))
    c = d.get('content') or {}
    st = (d.get('header') or {}).get('status') or {}
    ev = (((c.get('matchFacts') or {}).get('events') or {}).get('events') or [])
    cards = Counter(e.get('card') for e in ev if e.get('type') == 'Card')
    per = ((c.get('stats') or {}).get('Periods') or {})
    info = ((c.get('matchFacts') or {}).get('infoBox') or {})
    ref = ((info.get('Referee') or {}).get('text') or '').strip()
    lu = c.get('lineup') or {}
    ht = [e for e in ev if e.get('type') == 'Half' and e.get('halfStrShort') == 'HT']
    ge = [e for e in ev if e.get('type') == 'Goal' and not e.get('isPenaltyShootoutEvent')]
    ht_agree = None
    if ge and ht:
        h1 = sum(1 for e in ge if isinstance(e.get('time'), (int, float)) and e['time'] <= 45 and e.get('isHome'))
        a1 = sum(1 for e in ge if isinstance(e.get('time'), (int, float)) and e['time'] <= 45 and not e.get('isHome'))
        ht_agree = (h1, a1) == (ht[0].get('homeScore'), ht[0].get('awayScore'))
    return {'season': str(r['season']), 'finished': bool(st.get('finished')),
            'ht_agree': ht_agree, 'score': bool(st.get('scoreStr')),
            'stats': bool(per), 'shotmap': bool((c.get('shotmap') or {}).get('shots')),
            'splits': any(x in ('FirstHalf', 'SecondHalf') for x in per),
            'events': bool(ev), 'referee': bool(ref),
            'lineup': any(len((lu.get(x) or {}).get('starters') or []) == 11 for x in ('homeTeam', 'awayTeam')),
            'et': Counter(e.get('type') for e in ev), 'cards': cards,
            'card_n': sum(cards.values())}

raw = [payload(r) for r in idx]
inv = {'total_payloads': len(raw), 'total_matches': len(M),
       'finished_only_rule': 'header.status.finished == true; all 969 payloads finished, drops nothing',
       'seasons': {}}
for s in sorted({x['season'] for x in raw}):
    q = [x for x in raw if x['season'] == s]
    d = M[M.season == s]
    et = Counter(); cards = Counter()
    for x in q:
        et.update(x['et']); cards.update(x['cards'])
    inv['seasons'][s] = {'payloads': len(q), 'finished': sum(x['finished'] for x in q),
        'unfinished': sum(not x['finished'] for x in q),
        'score_present': sum(x['score'] for x in q),
        'stats': sum(x['stats'] for x in q), 'shotmap': sum(x['shotmap'] for x in q),
        'period_splits': sum(x['splits'] for x in q), 'events': sum(x['events'] for x in q),
        'referee': sum(x['referee'] for x in q), 'lineup': sum(x['lineup'] for x in q),
        'event_type_counts': dict(et), 'card_type_counts': dict(cards),
        'card_match_distribution': dict(Counter(x['card_n'] for x in q)),
        'teams_finished': int(len(set(d.home_team_id) | set(d.away_team_id))),
        'goals_finished': int(d.tot_goals.sum()),
        'goals_per_match_finished': float(d.tot_goals.mean()),
        'ht_crosscheck_agree': sum(x.get('ht_agree') is True for x in q),
        'ht_crosscheck_checked': sum(x.get('ht_agree') is not None for x in q)}
inv['name_variants'] = {str(k): sorted(v) for k, v in
    ((109375, ['Nam Dinh', 'Nam Định']), (179219, ['Ha Noi FC', 'Ha Nội FC']),
     (109374, ['Binh Duong', 'HCM City']), (179226, ['FLC Thanh Hoa', 'Thanh Hoa FC', 'Thanh Hòa FC']),
     (1151181, ['Binh Dinh', 'Bình Định']), (179222, ['Hai Phong', 'Hải Phòng']),
     (179220, ['Da Nang', 'Da Nẵng']), (179228, ['Ho Chi Minh City FC', 'Cong An Ho Chi Minh City', 'Cong An Ho Chí Minh City']),
     (179227, ['Hoang Anh Gia Lai', 'Hoàng Anh Gia Lai']), (614354, ['Cong An Ha Noi', 'Công An Hà Nội']),
     (1235223, ['Ninh Binh Club', 'Ninh Bình Club']))}
inv['score_events_mismatch_ids'] = [int(x) for x in M[M.score_events_mismatch].match_id]
(HERE / 'inventory_summary.json').write_text(json.dumps(inv, indent=1))

OUT = {'seasons': {}}
for s, d in inv['seasons'].items():
    x = M[M.season == s]
    OUT['seasons'][s] = {**{k: d[k] for k in ('payloads', 'finished', 'unfinished', 'stats', 'shotmap',
        'period_splits', 'events', 'referee', 'lineup', 'teams_finished',
        'ht_crosscheck_agree', 'ht_crosscheck_checked')},
        'goals_pm_finished': d['goals_per_match_finished'],
        'home_win_rate': float((x.home_goals > x.away_goals).mean()),
        'draw_rate': float((x.home_goals == x.away_goals).mean()),
        'away_win_rate': float((x.home_goals < x.away_goals).mean()),
        'ou15_over_rate': float((x.tot_goals > 1.5).mean()),
        'ou25_over_rate': float((x.tot_goals > 2.5).mean()),
        'ou35_over_rate': float((x.tot_goals > 3.5).mean()),
        'btts_rate': float(((x.home_goals > 0) & (x.away_goals > 0)).mean())}
DEV = ['2021', '2022', '2023', '2023/2024', '2024/2025']
scored = M[M.season.isin(['2022', '2023', '2023/2024', '2024/2025'])]
OUT['pooled_eval'] = {'n': len(scored),
    'home_win_rate': float((scored.home_goals > scored.away_goals).mean()),
    'draw_rate': float((scored.home_goals == scored.away_goals).mean()),
    'away_win_rate': float((scored.home_goals < scored.away_goals).mean()),
    'ou15_over_rate': float((scored.tot_goals > 1.5).mean()),
    'ou25_over_rate': float((scored.tot_goals > 2.5).mean()),
    'ou35_over_rate': float((scored.tot_goals > 3.5).mean()),
    'goals_pm': float(scored.tot_goals.mean())}

def corr(xs, ys):
    xs = list(xs); ys = list(ys)
    if len(xs) < 3: return None
    return float(np.corrcoef(xs, ys)[0, 1])

# F2 trait reliability: per-season chronological split-half (first half of
# the season's fixtures vs second half), teams with >=5 matches each half.
OUT['trait_reliability_by_season'] = {}
for s in DEV:
    rs = M[M.season == s].sort_values(['date', 'match_id'])
    half = len(rs) // 2
    def traits(sub):
        gf = Counter(); ga = Counter(); gp = Counter()
        for _, x in sub.iterrows():
            gf[x.home_team_id] += x.home_goals; ga[x.home_team_id] += x.away_goals; gp[x.home_team_id] += 1
            gf[x.away_team_id] += x.away_goals; ga[x.away_team_id] += x.home_goals; gp[x.away_team_id] += 1
        return {t: (gf[t] / gp[t], ga[t] / gp[t]) for t in gp if gp[t] >= 5}
    a, b = traits(rs.iloc[:half]), traits(rs.iloc[half:])
    common = sorted(set(a) & set(b))
    OUT['trait_reliability_by_season'][s] = {
        'n_teams': len(common),
        'r_goals_for': corr([a[t][0] for t in common], [b[t][0] for t in common]),
        'r_goals_against': corr([a[t][1] for t in common], [b[t][1] for t in common])}

# F3 halves: Half-event HT scores; per-match 1H share vs binomial noise.
g = M[M.ht_source == 'half_event'].copy()
g = g[g.season.isin(DEV)]
hs = {'rule': 'Half-event HT score (homeScore/awayScore at HT); cross-checked vs goal-event times <=45',
      'share_1h': float(g.goals_1h_total.sum() / g.tot_goals.sum()),
      'n_goals': int(g.tot_goals.sum()), 'n_matches': len(g),
      'by_season': {s: {'share_1h': float(x.goals_1h_total.sum() / x.tot_goals.sum()),
                         'n_goals': int(x.tot_goals.sum()), 'n_matches': len(x)}
                    for s, x in g.groupby('season')}}
z = g[g.tot_goals > 0]
shares = z.goals_1h_total / z.tot_goals
hs['per_match_share_mean'] = float(shares.mean())
hs['per_match_share_variance'] = float(shares.var(ddof=0))
p = hs['share_1h']
hs['binomial_expected_variance'] = float(np.mean([p * (1 - p) / t for t in z.tot_goals]))
hs['excess_variance'] = hs['per_match_share_variance'] - hs['binomial_expected_variance']
# team-level 1H share split-half (odd/even career split, dev seasons only)
q = TM[TM.season.isin(DEV)].copy()
q = q[q.goals_for > 0]; q['share'] = q.ht_goals_for / q.goals_for
q = q.dropna(subset=['share'])
q['i'] = q.sort_values(['team_id', 'date', 'match_id']).groupby('team_id').cumcount()
a = q[q.i % 2 == 0].groupby('team_id').share.mean()
b = q[q.i % 2 == 1].groupby('team_id').share.mean()
j = pd.concat([a, b], axis=1).dropna()
hs['team_share_split_half_r'] = float(j.iloc[:, 0].corr(j.iloc[:, 1])) if len(j) >= 3 else None
hs['team_share_n'] = len(j)
hs['team_share_between_variance'] = float(q.groupby('team_id').share.mean().var())
hs['team_share_within_variance'] = float(((q.share - q.groupby('team_id').share.transform('mean')) ** 2).mean())
OUT['halves_dev'] = hs

# F4 entrants: first-appearance teams per season, GF/GA vs season mean.
seen = set(); trans = []
for s in sorted(M.season.unique(), key=lambda v: (season_start_key(v), v)):
    rs = M[M.season == s]
    teams = set(rs.home_team_id) | set(rs.away_team_id)
    new = teams - seen
    gf = Counter(); ga = Counter(); gp = Counter()
    for _, x in rs.iterrows():
        gf[x.home_team_id] += x.home_goals; ga[x.home_team_id] += x.away_goals; gp[x.home_team_id] += 1
        gf[x.away_team_id] += x.away_goals; ga[x.away_team_id] += x.home_goals; gp[x.away_team_id] += 1
    lg = sum(gf.values()) / sum(gp.values())
    for t in sorted(new):
        trans.append({'season': s, 'team_id': int(t), 'gp': int(gp[t]),
                      'gf': round(gf[t] / gp[t], 3), 'ga': round(ga[t] / gp[t], 3),
                      'gf_diff': round(gf[t] / gp[t] - lg, 3), 'ga_diff': round(ga[t] / gp[t] - lg, 3)})
    seen |= teams
OUT['entrants_dev'] = {'transitions': [t for t in trans if t['season'] in DEV]}

# F13 SHRINK bite: prior in-league match counts at each target-season start.
seen_matches = Counter(); bands = {}
for s in sorted(M.season.unique(), key=lambda v: (season_start_key(v), v)):
    rs = M[M.season == s]
    teams = set(rs.home_team_id) | set(rs.away_team_id)
    b = Counter()
    for t in teams:
        n = seen_matches[t]
        b['0' if n == 0 else '1-5' if n <= 5 else '6-23' if n <= 23 else '24+'] += 1
    bands[s] = dict(b)
    for _, x in rs.iterrows():
        seen_matches[x.home_team_id] += 1; seen_matches[x.away_team_id] += 1
OUT['prior_match_bands'] = bands
(HERE / 'eda_summary.json').write_text(json.dumps(OUT, indent=1))
print('seasons:', {s: OUT['seasons'][s]['goals_pm_finished'] for s in OUT['seasons']})
print('pooled_eval:', OUT['pooled_eval'])
print('halves:', {k: hs[k] for k in ('share_1h', 'n_goals', 'n_matches', 'per_match_share_variance', 'binomial_expected_variance', 'excess_variance', 'team_share_split_half_r')})
print('traits:', OUT['trait_reliability_by_season'])
print('bands:', bands)
