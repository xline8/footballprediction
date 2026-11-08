"""Deterministic EDA numbers for Slovakia 2. Liga.

Only the finished-match CSV drives league levels, reliability, and halves.
The warehouse is consulted for the cross-tier inventory and mover audit.
"""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('/home/hatch/workspace/footballprediction')
M = list(csv.DictReader(open(HERE.parent / 'data' / 'sk2_matches.csv')))
TEAM = list(csv.DictReader(open(HERE.parent / 'data' / 'sk2_teams.csv')))
INDEX = list(csv.DictReader(open(MAIN / 'data_enrichment/fotmob_world_index.csv')))
DEV = {'2021/2022', '2022/2023', '2023/2024', '2024/2025'}


def f(row, key):
    value = row.get(key)
    return None if value in (None, '', 'None') else float(value)


def avg(values):
    return round(statistics.mean(values), 6) if values else None


def cor(x, y):
    if len(x) < 2: return None
    mx, my = statistics.mean(x), statistics.mean(y)
    den = math.sqrt(sum((a-mx)**2 for a in x) * sum((b-my)**2 for b in y))
    return round(sum((a-mx)*(b-my) for a, b in zip(x, y)) / den, 6) if den else None


def team_ids(rows):
    return {str(r[f'{s}_team_id']) for r in rows for s in ('home', 'away')}


def payload_rows(league_id, season=None, exclude_playoff=False):
    result = []
    for item in INDEX:
        if item['league_id'] != league_id or (season and item['season'] != season): continue
        payload = json.load(open(MAIN / item['path']))
        general = payload.get('general') or {}; status = (payload.get('header') or {}).get('status') or {}
        if not status.get('finished'): continue
        if exclude_playoff and 'ECL Playoff' in (general.get('leagueName') or ''): continue
        result.append((item, payload))
    return result


def rel(getter):
    groups = defaultdict(list)
    for r in M:
        if r['season'] not in DEV: continue
        for side in ('home', 'away'):
            groups[(r['season'], r[f'{side}_team_id'])].append(getter(r, side))
    x, y = [], []
    for values in groups.values():
        if len(values) >= 10:
            x.append(statistics.mean(values[0::2])); y.append(statistics.mean(values[1::2]))
    return {'r': cor(x, y), 'n_units': len(x)}


def share_reliability():
    groups = defaultdict(list)
    for r in M:
        if r['season'] not in {'2023/2024', '2024/2025'} or r['events_reconciled'] != '1': continue
        for side in ('home', 'away'):
            total = f(r, f'{side}_goals')
            first = f(r, f'ht_{side}_goals')
            groups[(r['season'], r[f'{side}_team_id'])].append((first, total))
    x, y = [], []
    for values in groups.values():
        halves = []
        for part in (values[0::2], values[1::2]):
            first, total = sum(a for a, _ in part), sum(b for _, b in part)
            halves.append(first / total if first is not None and total >= 5 else None)
        if halves[0] is not None and halves[1] is not None: x.append(halves[0]); y.append(halves[1])
    return {'r': cor(x, y), 'n_units': len(x)}


def event_half_stats(rows):
    totals = [sum(f(r, k) for k in ('home_goals', 'away_goals')) for r in rows]
    firsts = [sum(f(r, k) for k in ('ht_home_goals', 'ht_away_goals')) for r in rows]
    total, first = sum(totals), sum(firsts); p = first / total
    with_goals = [firsts[i] / totals[i] for i in range(len(rows)) if totals[i] > 0]
    noise = statistics.mean(p * (1-p) / totals[i] for i in range(len(rows)) if totals[i] > 0)
    observed = statistics.pvariance(with_goals)
    return {'first_half_goals': first, 'total_goals': total, 'match_count': len(rows),
            'share': round(p, 6), 'observed_variance': round(observed, 6),
            'binomial_noise': round(noise, 6), 'true_variance': round(observed-noise, 6),
            'matches_with_goals': len(with_goals)}


def main():
    seasons = sorted({r['season'] for r in M})
    levels = {}
    for season in seasons:
        rows = [r for r in M if r['season'] == season]
        goals = [f(r, 'home_goals') + f(r, 'away_goals') for r in rows]
        outcomes = [1 if f(r,'home_goals') > f(r,'away_goals') else 0 if f(r,'home_goals') == f(r,'away_goals') else -1 for r in rows]
        levels[season] = {'n': len(rows), 'goals': avg(goals), 'home_goals': avg([f(r,'home_goals') for r in rows]),
            'home_win_rate': round(outcomes.count(1)/len(rows), 6), 'draw_rate': round(outcomes.count(0)/len(rows), 6),
            'away_win_rate': round(outcomes.count(-1)/len(rows), 6),
            'ou1.5_rate': round(sum(g > 1.5 for g in goals)/len(rows), 6),
            'ou2.5_rate': round(sum(g > 2.5 for g in goals)/len(rows), 6),
            'ou3.5_rate': round(sum(g > 3.5 for g in goals)/len(rows), 6),
            'btts_rate': round(sum(f(r,'home_goals') > 0 and f(r,'away_goals') > 0 for r in rows)/len(rows), 6),
            'events_present': sum(r['has_events'] == '1' for r in rows),
            'referee_named': sum(bool(r['referee']) for r in rows)}
    dev_rows = [r for r in M if r['season'] in DEV]
    dev_goals = [f(r,'home_goals') + f(r,'away_goals') for r in dev_rows]
    reliabilities = {
        'goals_for': rel(lambda r,s: f(r, f'{s}_goals')),
        'goals_against': rel(lambda r,s: f(r, f'{"away" if s == "home" else "home"}_goals')),
    }
    event_rows = [r for r in M if r['events_reconciled'] == '1']
    halves = {'dev_era': event_half_stats([r for r in event_rows if r['season'] in {'2023/2024','2024/2025'}]),
              'by_season': {s: event_half_stats([r for r in event_rows if r['season'] == s]) for s in seasons if any(r['season']==s for r in event_rows)},
              'all_events': event_half_stats(event_rows), 'team_split_half_reliability': share_reliability()}

    names = {r['team_id']: r['canonical_name'] for r in TEAM}
    tier2_finished = {s: team_ids([{'home_team_id': (p.get('general') or {}).get('homeTeam',{}).get('id'), 'away_team_id': (p.get('general') or {}).get('awayTeam',{}).get('id')} for _,p in payload_rows('8973', s)]) for s in seasons}
    tier1_finished = {}
    for s in seasons:
        tier1_finished[s] = set()
        for _, p in payload_rows('176', s, exclude_playoff=True):
            g = p.get('general') or {}
            tier1_finished[s] |= {str(g['homeTeam']['id']), str(g['awayTeam']['id'])}
    movers = {}
    completed = []
    newcomers = {}
    promoted = {}
    for season in [f'{y}/{y+1}' for y in range(2022, 2027)]:
        y = int(season[:4]); prior = f'{y-1}/{y}'
        current_rows = [r for r in M if r['season'] == season]
        current_ids = team_ids(current_rows)
        league_mean = sum(f(r,'home_goals')+f(r,'away_goals') for r in current_rows)/(2*len(current_rows)) if current_rows else None
        arrivals = []
        for club in sorted((tier1_finished.get(prior,set()) & current_ids) - tier1_finished.get(season,set())):
            cr = [r for r in current_rows if club in (r['home_team_id'], r['away_team_id'])]
            gf = sum(f(r, 'home_goals' if r['home_team_id']==club else 'away_goals') for r in cr)/len(cr)
            ga = sum(f(r, 'away_goals' if r['home_team_id']==club else 'home_goals') for r in cr)/len(cr)
            row = {'club': names.get(club, next((r[f'{s}_team'] for r in cr for s in ('home','away') if r[f'{s}_team_id']==club), club)), 'team_id': club,
                   'n_matches': len(cr), 'gf_per_match': round(gf,6), 'ga_per_match': round(ga,6),
                   'league_mu': round(league_mean,6), 'delta_gf': round(gf-league_mean,6), 'delta_ga': round(ga-league_mean,6)}
            arrivals.append(row)
        newcomers[season] = {'count': len(current_ids - tier2_finished.get(prior,set()) - tier1_finished.get(prior,set())),
                             'names': sorted(names.get(c,c) for c in current_ids - tier2_finished.get(prior,set()) - tier1_finished.get(prior,set()))}
        promoted[season] = sorted(names.get(c,c) for c in (tier1_finished.get(season,set()) & tier2_finished.get(prior,set())) - tier1_finished.get(prior,set()))
        movers[season] = {'clubs': arrivals, 'cumulative_prior': {'delta_gf': avg([r['delta_gf'] for r in completed]), 'delta_ga': avg([r['delta_ga'] for r in completed]), 'n_transitions': len(completed)}}
        completed.extend(arrivals)

    inv = {'index_rows_by_season': {s: sum(i['season']==s and i['league_id']=='8973' for i in INDEX) for s in seasons},
           'finished_by_season': {s: len([r for r in M if r['season']==s]) for s in seasons},
           'unfinished_by_season': {s: sum(i['season']==s and i['league_id']=='8973' for i in INDEX)-len([r for r in M if r['season']==s]) for s in seasons},
           'sub_league_ids_by_season': {s: sorted({str(r['sub_league_id']) for r in M if r['season']==s}) for s in seasons},
           'format_note': {'2021/2022':'16 teams / 30 rounds','2022/2023':'16 teams / 30 rounds','2023/2024':'16 teams / 30 rounds','2024/2025':'14 teams / 26 rounds','2025/2026':'16 teams / 30 rounds','2026/2027':'16 teams / 30 rounds, in progress'}}
    audit = {'events_present': sum(r['has_events']=='1' for r in M), 'events_reconciled': len(event_rows),
             'defects': [{'match_id':'4553752','reason':'score 3-0 but event block lists 2 away goals'}, {'match_id':'4838232','reason':'Arevalo 67\' goal is duplicated (6 events for 5 goals)'}]}
    out = {'inventory': inv, 'levels': levels, 'dev_pooled': {'n':len(dev_rows), 'ou2.5_over_rate': round(sum(g>2.5 for g in dev_goals)/len(dev_goals),6)},
           'reliabilities': reliabilities, 'halves': halves, 'movers_x2': {'by_season': movers, 'newcomers': newcomers, 'promoted_2_to_1': promoted},
           'referee': {'coverage_by_season': {s:{'named':sum(bool(r['referee']) for r in M if r['season']==s),'total':sum(r['season']==s for r in M)} for s in seasons}},
           'events_audit': audit, 'primary_line': {'metric':'goals OU2.5 dev over-rate','n':len(dev_rows),'over_rate':round(sum(g>2.5 for g in dev_goals)/len(dev_goals),6)}}
    json.dump(out, open(HERE/'eda_numbers.json','w'), indent=2)
    print(json.dumps(out, indent=2))


if __name__ == '__main__': main()
