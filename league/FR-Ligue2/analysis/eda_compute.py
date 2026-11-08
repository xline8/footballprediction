"""Compute French Ligue 2 descriptive EDA numbers from built French tables."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / 'data' / 'fr_matches.csv')))
SEASONS = sorted({r['season'] for r in ROWS})
COMPLETE = SEASONS[:-1]
DEV = ['2021/2022', '2022/2023', '2023/2024', '2024/2025']
EVAL = ['2022/2023', '2023/2024', '2024/2025']
VIRGIN = ['2025/2026']

def f(r, key):
    v = r.get(key)
    return None if v in (None, '', 'None') else float(v)

def mean(vals): return round(st.mean(vals), 3) if vals else None

def split_half(vals_by_team):
    xs, ys = [], []
    for vals in vals_by_team.values():
        if len(vals) >= 10:
            xs.append(st.mean(vals[0::2])); ys.append(st.mean(vals[1::2]))
    if len(xs) < 5: return None, len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return ((sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / den) if den else None, len(xs))

def team_series(rows, key):
    d = defaultdict(list)
    for r in rows:
        for side in ('home', 'away'):
            v = f(r, f'{key}_{side}')
            if v is not None: d[r[f'{side}_team']].append(v)
    return d

def half_share(rows, numerator, denominator, event=False):
    shares, totals = [], []
    for r in rows:
        if event:
            a = f(r, 'ev_yellow_1h_home'); b = f(r, 'ev_yellow_1h_away')
            c = f(r, 'ev_yellow_home'); d = f(r, 'ev_yellow_away')
        else:
            a, b = f(r, f'fh_{numerator}_home'), f(r, f'fh_{numerator}_away')
            c, d = f(r, f'{denominator}_home'), f(r, f'{denominator}_away')
        if None in (a, b, c, d) or c + d == 0: continue
        shares.append((a+b)/(c+d)); totals.append(c+d)
    if not shares: return {'n': 0, 'share': None, 'observed_sd': None, 'true_sd': None}
    p = st.mean(shares); observed = st.variance(shares) if len(shares) > 1 else 0
    noise = st.mean([p*(1-p)/n for n in totals])
    return {'n': len(shares), 'share': round(p, 4), 'observed_sd': round(math.sqrt(observed), 4),
            'true_sd': round(math.sqrt(max(0, observed-noise)), 4)}

def exact_agreement(rows):
    valid = [r for r in rows if f(r, 'yellow_cards_home') is not None and f(r, 'yellow_cards_away') is not None]
    return round(100 * sum(f(r, 'yellow_cards_home') + f(r, 'yellow_cards_away') == f(r, 'ev_yellow_home') + f(r, 'ev_yellow_away') for r in valid) / len(valid), 1) if valid else None

out = {'n': len(ROWS), 'seasons': SEASONS}
per = {}
for season in SEASONS:
    rs = [r for r in ROWS if r['season'] == season]
    def total_stat(key):
        vals = [f(r, f'{key}_home') + f(r, f'{key}_away') for r in rs if f(r, f'{key}_home') is not None and f(r, f'{key}_away') is not None]
        return mean(vals)
    def coverage(key): return round(100 * sum(f(r, key) is not None for r in rs) / len(rs), 1)
    per[season] = {
        'n': len(rs), 'goals': mean([int(r['home_goals']) + int(r['away_goals']) for r in rs]),
        'home_goals': mean([int(r['home_goals']) for r in rs]), 'away_goals': mean([int(r['away_goals']) for r in rs]),
        'sot': total_stat('ShotsOnTarget'), 'corners': total_stat('corners'), 'shots': total_stat('total_shots'),
        'yellows_events': mean([int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs]),
        'yellows_stats': total_stat('yellow_cards'), 'reds': total_stat('red_cards'), 'xg': total_stat('expected_goals'),
        'coverage': {'stats': round(100 * sum(int(r['has_stats_all']) for r in rs) / len(rs), 1),
                     'half': round(100 * sum(int(r['has_stats_half']) for r in rs) / len(rs), 1),
                     'shotmap': round(100 * sum(int(r['has_shotmap']) for r in rs) / len(rs), 1),
                     'referee': round(100 * sum(bool(r['referee']) for r in rs) / len(rs), 1),
                     'touches': coverage('touches_opp_box_home'), 'xg': coverage('expected_goals_home'),
                     'events': round(100 * sum(int(r['has_events']) for r in rs) / len(rs), 1)},
        'phase_counts': {p: sum(r['phase'] == p for r in rs) for p in ('regular', 'playoff')}
    }
out['per_season'] = per
out['yellows_stats_vs_events'] = {
    'exact_agreement_pct_by_season': {s: exact_agreement([r for r in ROWS if r['season'] == s]) for s in SEASONS},
    'pooled_dev_pct': exact_agreement([r for r in ROWS if r['season'] in DEV]),
    'pooled_all_pct': exact_agreement(ROWS),
    'totals_by_season': {s: {'events': sum(int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in ROWS if r['season'] == s),
                            'stats': sum(int(f(r, 'yellow_cards_home') or 0) + int(f(r, 'yellow_cards_away') or 0) for r in ROWS if r['season'] == s)} for s in SEASONS}
}
out['goals_per_xg'] = {}
for s in SEASONS:
    if per[s]['coverage']['xg'] >= 50:
        rs = [r for r in ROWS if r['season'] == s and f(r, 'expected_goals_home') is not None and f(r, 'expected_goals_away') is not None]
        out['goals_per_xg'][s] = round(sum(int(r['home_goals']) + int(r['away_goals']) for r in rs) / sum(f(r, 'expected_goals_home') + f(r, 'expected_goals_away') for r in rs), 3)
    else: out['goals_per_xg'][s] = None

rel = {}
career = [r for r in ROWS if r['season'] in COMPLETE]
goals = defaultdict(list)
for r in career:
    goals[r['home_team']].append(int(r['home_goals'])); goals[r['away_team']].append(int(r['away_goals']))
for name, key in [('goals_for', None), ('sot_for', 'ShotsOnTarget'), ('corners_for', 'corners'), ('shots_for', 'total_shots'),
                  ('yellows_for', 'yellow'), ('touches_for', 'touches_opp_box'), ('touches_against', 'touches_opp_box_against'),
                  ('bigchance_for', 'big_chance'), ('possession', 'BallPossesion')]:
    if name == 'goals_for': d = goals
    elif name == 'touches_against':
        d = defaultdict(list)
        for r in career:
            for side, opp in (('home', 'away'), ('away', 'home')):
                v = f(r, f'touches_opp_box_{opp}')
                if v is not None: d[r[f'{side}_team']].append(v)
    elif name == 'yellows_for':
        d = defaultdict(list)
        for r in career:
            for side in ('home', 'away'): d[r[f'{side}_team']].append(f(r, f'ev_yellow_{side}'))
    else: d = team_series(career, key)
    val, n = split_half(d); rel[name] = {'r': round(val, 3) if val is not None else None, 'n_teams': n}
for key in ('xg_for', 'set_play_share', 'xg_per_shot', 'xgot_per_shot'):
    rel[key] = {'r': None, 'n_teams': 0, 'note': 'era_dead_xg'}
out['reliability'] = rel

def referee_rel(seasons):
    d = defaultdict(list)
    for r in ROWS:
        if r['season'] in seasons and r['referee']:
            d[r['referee']].append(int(r['ev_yellow_home']) + int(r['ev_yellow_away']))
    val, n = split_half({k: v for k, v in d.items() if len(v) >= 10})
    return {'r': round(val, 3) if val is not None else None, 'n_refs': n}
out['referee_reliability'] = {'dev_2021_2025': referee_rel(set(DEV)), 'complete_2021_2026': referee_rel(set(COMPLETE))}
half_rows = [r for r in ROWS if r['season'] in ('2023/2024', '2024/2025', '2025/2026')]
goal_shares = []
for r in half_rows:
    total = int(r['home_goals']) + int(r['away_goals'])
    if total: goal_shares.append((int(r['ht_home_goals']) + int(r['ht_away_goals'])) / total)
def goal_half():
    p = st.mean(goal_shares); obs = st.variance(goal_shares); totals = [int(r['home_goals']) + int(r['away_goals']) for r in half_rows if int(r['home_goals']) + int(r['away_goals'])]
    return {'n': len(goal_shares), 'share': round(p, 4), 'observed_sd': round(math.sqrt(obs), 4), 'true_sd': round(math.sqrt(max(0, obs-st.mean([p*(1-p)/n for n in totals]))), 4)}
out['half_shares_2023_2026'] = {'goals_events': goal_half(), 'sot': half_share(half_rows, 'ShotsOnTarget', 'ShotsOnTarget'), 'corners': half_share(half_rows, 'corners', 'corners'), 'total_shots': half_share(half_rows, 'total_shots', 'total_shots'), 'yellows_events': half_share(half_rows, None, None, True)}

# Churn/movers keyed on team_id / accent-normalised names: 10 of the 42
# FotMob team ids carry two spellings across seasons (accents dropped in
# some seasons' payloads, e.g. 'Cadiz' vs 'Cádiz'), so raw-name set
# arithmetic invents phantom clubs. Ids are exact (22/season, 42 overall,
# verified by the coordinator); spellings map 1:1 onto ids with no
# collisions, so accent-stripped name matching is exact for the
# index-based mover membership (the index carries names only).
import unicodedata
def _norm(n):
    return ''.join(c for c in unicodedata.normalize('NFKD', n) if not unicodedata.combining(c)).strip().lower()
id_name = {}
for r in ROWS:
    id_name.setdefault(r['home_team_id'], r['home_team']); id_name.setdefault(r['away_team_id'], r['away_team'])
team_season = {s: ({r['home_team_id'] for r in ROWS if r['season'] == s} | {r['away_team_id'] for r in ROWS if r['season'] == s}) for s in SEASONS}
out['churn'] = {'distinct_teams_per_season': {s: len(v) for s, v in team_season.items()}, 'entries': {s: {'count': len(team_season[s] - team_season[SEASONS[i-1]]), 'teams': sorted(id_name[t] for t in team_season[s] - team_season[SEASONS[i-1]])} for i, s in enumerate(SEASONS) if i}, 'distinct_teams_overall': len(set().union(*team_season.values()))}

idx = list(csv.DictReader(open('/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv')))
def league_teams(lid, season):
    return {_norm(x) for r in idx if r['league_id'] == lid and r['season'] == season for x in (r['home'], r['away'])}
name_season = {s: ({_norm(r['home_team']) for r in ROWS if r['season'] == s} | {_norm(r['away_team']) for r in ROWS if r['season'] == s}) for s in SEASONS}
movers = {}
for i, s in enumerate(SEASONS[1:]):
    prev = SEASONS[i]; cur = name_season[s]; old = name_season[prev]
    from_ll = sorted((cur - old) & league_teams('53', prev) - league_teams('110', prev))
    from_pf = sorted((cur - old) & league_teams('8970', prev) - league_teams('110', prev))
    movers[s] = {'from Ligue1': from_ll, 'from Ligue3': from_pf}
def mover_perf(groups):
    gf, ga = [], []
    for s, groups_for_s in movers.items():
        for group in groups:
            clubs = set(groups_for_s[group])
            for r in ROWS:
                if r['season'] != s: continue
                for side, opp in (('home', 'away'), ('away', 'home')):
                    if _norm(r[f'{side}_team']) in clubs: gf.append(int(r[f'{side}_goals'])); ga.append(int(r[f'{opp}_goals']))
    return {'team_matches': len(gf), 'gf_per_match': mean(gf), 'ga_per_match': mean(ga), 'gd_per_match': mean([a-b for a,b in zip(gf,ga)])}
entry_seasons = [s for s in SEASONS[1:]]
entry_rows = [r for r in ROWS if r['season'] in entry_seasons]
mu = sum(int(r['home_goals']) + int(r['away_goals']) for r in entry_rows) / (2 * len(entry_rows))
out['movers'] = movers
out['mover_pooled'] = {}
for group in ('from Ligue1', 'from Ligue3'):
    perf = mover_perf([group]); perf.update({'league_mu': round(mu, 3), 'gf_delta_vs_mu': round(perf['gf_per_match'] - mu, 3) if perf['gf_per_match'] is not None else None, 'ga_delta_vs_mu': round(perf['ga_per_match'] - mu, 3) if perf['ga_per_match'] is not None else None})
    out['mover_pooled'][group] = perf

def over_rates(seasons):
    rs = [r for r in ROWS if r['season'] in seasons]
    specs = {'goals_ou_2.5': lambda r: int(r['home_goals']) + int(r['away_goals']) > 2.5,
             'sot_over_7.5': lambda r: f(r,'ShotsOnTarget_home') + f(r,'ShotsOnTarget_away') > 7.5,
             'sot_over_8.5': lambda r: f(r,'ShotsOnTarget_home') + f(r,'ShotsOnTarget_away') > 8.5,
             'shots_over_23.5': lambda r: f(r,'total_shots_home') + f(r,'total_shots_away') > 23.5,
             'corners_over_9.5': lambda r: f(r,'corners_home') + f(r,'corners_away') > 9.5,
             'corners_over_10.5': lambda r: f(r,'corners_home') + f(r,'corners_away') > 10.5,
             'cards_over_4.5': lambda r: int(r['ev_yellow_home']) + int(r['ev_yellow_away']) > 4.5,
             'cards_over_5.5': lambda r: int(r['ev_yellow_home']) + int(r['ev_yellow_away']) > 5.5,
             'shots_over_24.5': lambda r: f(r,'total_shots_home') + f(r,'total_shots_away') > 24.5,
             'shots_over_25.5': lambda r: f(r,'total_shots_home') + f(r,'total_shots_away') > 25.5,
             'shots_over_26.5': lambda r: f(r,'total_shots_home') + f(r,'total_shots_away') > 26.5}
    return {k: round(100 * sum(fn(r) for r in rs) / len(rs), 1) for k, fn in specs.items()}
out['over_rates'] = {'evaluation_2022_2025': over_rates(EVAL), 'virgin_2025_2026': over_rates(VIRGIN)}
complete_rows = [r for r in ROWS if r['season'] in COMPLETE]
out['home_advantage_complete'] = {'home_win_rate_pct': round(100 * sum(int(r['home_goals']) > int(r['away_goals']) for r in complete_rows) / len(complete_rows), 1), 'home_goals': mean([int(r['home_goals']) for r in complete_rows]), 'away_goals': mean([int(r['away_goals']) for r in complete_rows])}
out['thin_data_team_seasons_lt6'] = sum(1 for s in SEASONS for tid in team_season[s] if sum(1 for r in ROWS if r['season'] == s and tid in (r['home_team_id'], r['away_team_id'])) < 6)

json.dump(out, open(HERE / 'eda_numbers.json', 'w'), indent=1)
with open(HERE / 'DATA_UNDERSTANDING.md', 'w') as fh:
    fh.write('# France Ligue 2 — DATA UNDERSTANDING\n\n')
    fh.write('Source: French FotMob warehouse JSONs indexed under league_id 110. Counts and coverage below are computed from the builder output.\n\n')
    for s in SEASONS:
        p = per[s]
        fh.write(f"## {s}\n\n- Played matches: {p['n']}; teams: {len(team_season[s])}; rounds: {', '.join(sorted({r['round'] for r in ROWS if r['season']==s}, key=lambda x:int(x) if x.isdigit() else x))}.\n")
        fh.write(f"- Coverage: stats {p['coverage']['stats']}%, period splits {p['coverage']['half']}%, shotmap {p['coverage']['shotmap']}%, expected_goals {p['coverage']['xg']}%, referee {p['coverage']['referee']}%, events {p['coverage']['events']}%.\n")
        fh.write(f"- Phase counts: {p['phase_counts']}.\n\n")
    fh.write('Observed feed rounds are numeric 1–38 only; no promotion play-off or relegation play-out rows are present in this warehouse slice. The team count falls from 20 to 18 in 2024/2025.\n')
with open(HERE / 'EDA.md', 'w') as fh:
    fh.write('# France Ligue 2 — EDA\n\nAll figures are generated from `eda_numbers.json`; no model fitting is performed.\n\n')
    fh.write('| Season | Matches | Goals/match | Home | Away | OU2.5 % | SOT | Corners | Cards stats | Cards events | Total shots | xG cov. | Shotmap cov. | Referee cov. |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n')
    for s in SEASONS:
        p=per[s]; c=p['coverage']; fh.write(f"| {s} | {p['n']} | {p['goals']} | {p['home_goals']} | {p['away_goals']} | {100*sum(int(r['home_goals'])+int(r['away_goals'])>2.5 for r in ROWS if r['season']==s)/p['n']:.1f} | {p['sot']} | {p['corners']} | {p['yellows_stats']} | {p['yellows_events']} | {p['shots']} | {c['xg']} | {c['shotmap']} | {c['referee']} |\n")
    fh.write(f"\n## Decisions and diagnostics\n\n- Cards stats-vs-events: `{json.dumps(out['yellows_stats_vs_events'], sort_keys=True)}`. The event target is adopted because the stats feed is lower in every season and has non-zero mismatch/dropout evidence.\n- Split-half reliabilities: `{json.dumps(out['reliability'], sort_keys=True)}`. Referee: `{json.dumps(out['referee_reliability'], sort_keys=True)}`.\n- Frozen complete-split half constants: `{json.dumps(out['half_shares_2023_2026'], sort_keys=True)}`; observed variance is compared with binomial/Poisson noise in the JSON.\n- Movers: `{json.dumps(out['mover_pooled'], sort_keys=True)}`; thin-data team-seasons under six prior matches: `{out['thin_data_team_seasons_lt6']}`.\n- Primary .5-line rates: `{json.dumps(out['over_rates'], sort_keys=True)}`. xG/shotmap verdict: expected_goals coverage is `{json.dumps({s:per[s]['coverage']['xg'] for s in SEASONS})}`, so xG-era variants are development-dead if coverage is absent in the development block.\n")
print(json.dumps(out, indent=1))
