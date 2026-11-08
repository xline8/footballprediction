"""Build the scores/events-only ES Primera Federacion analysis tables."""
import csv
import json
import re
from collections import defaultdict, deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment' / 'fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
SEASON_COUNTS = {'2021/2022': 767, '2022/2023': 774, '2023/2024': 774,
                 '2024/2025': 774, '2025/2026': 772, '2026/2027': 220}


def score(value):
    m = re.fullmatch(r'\s*(\d+)\s*-\s*(\d+)\s*', value or '')
    assert m, f'unparseable scoreStr: {value!r}'
    return int(m.group(1)), int(m.group(2))


def main():
    indexed = [r for r in csv.DictReader(open(INDEX, newline='')) if r['league_id'] == '8968']
    assert len(indexed) == 4081, len(indexed)
    indexed.sort(key=lambda r: (r['date'], r['match_id']))
    rows = []
    for ir in indexed:
        d = json.load(open(MAIN_REPO / ir['path']))
        gen, status = d.get('general') or {}, (d.get('header') or {}).get('status') or {}
        assert status.get('finished') and not status.get('cancelled'), ir['match_id']
        hg, ag = score(status.get('scoreStr'))
        c = d.get('content') or {}
        evs = ((c.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals = [e for e in evs if e.get('type') == 'Goal']
        periods = ((c.get('stats') or {}).get('Periods') or {})
        shots = ((c.get('shotmap') or {}).get('shots') or [])
        has_stats_all = int(bool(periods.get('All')))
        has_stats_half = int(bool(periods.get('FirstHalf')))
        has_shotmap = int(bool(shots))
        rnd = str(gen.get('matchRound'))
        row = {
            'match_id': ir['match_id'], 'league': 'ES-PrimeraFederacion', 'season': ir['season'],
            'date': ir['date'], 'round': rnd, 'phase': 'playoff' if rnd in ('1/2', 'final') else 'regular',
            'group_home': '', 'group_away': '',
            'home_team_id': str((gen.get('homeTeam') or {}).get('id')), 'home_team': (gen.get('homeTeam') or {}).get('name', ''),
            'away_team_id': str((gen.get('awayTeam') or {}).get('id')), 'away_team': (gen.get('awayTeam') or {}).get('name', ''),
            'coverage_level': gen.get('coverageLevel', ''), 'home_goals': hg, 'away_goals': ag,
            'awarded': int(bool(status.get('awarded'))),
            'extra_time': int(bool((status.get('halfs') or {}).get('firstExtraHalfStarted'))),
            'ht_home_goals': sum(e.get('isHome') is True and e.get('time') is not None and e['time'] <= 45 for e in goals),
            'ht_away_goals': sum(e.get('isHome') is False and e.get('time') is not None and e['time'] <= 45 for e in goals),
            'goal_events_complete': int(len(goals) == hg + ag), 'ht_source': 'events' if evs else 'none',
            'ev_card_total': sum(e.get('type') == 'Card' for e in evs), 'has_stats_all': has_stats_all,
            'has_stats_half': has_stats_half, 'has_shotmap': has_shotmap, 'has_events': int(bool(evs)),
            'referee': ((((c.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}).get('text') or ''),
            'n_events': len(evs),
        }
        for side, home in (('home', True), ('away', False)):
            side_events = [e for e in evs if e.get('type') == 'Card' and e.get('isHome') == home]
            row[f'ev_yellow_{side}'] = sum(e.get('card') == 'Yellow' for e in side_events)
            row[f'ev_yellow_1h_{side}'] = sum(e.get('card') == 'Yellow' and e.get('time') is not None and e['time'] <= 45 for e in side_events)
            row[f'ev_yellowred_{side}'] = sum(e.get('card') == 'YellowRed' for e in side_events)
            row[f'ev_red_{side}'] = sum(e.get('card') == 'Red' for e in side_events)
        rows.append(row)

    # Build the regular-season fixture graph separately for each season.
    groups = {}
    for season in SEASON_COUNTS:
        rs = [r for r in rows if r['season'] == season and r['phase'] == 'regular' and 1 <= int(r['round']) <= 38]
        graph = defaultdict(set); names = {}
        for r in rs:
            a, b = r['home_team_id'], r['away_team_id']
            graph[a].add(b); graph[b].add(a); names[a] = r['home_team']; names[b] = r['away_team']
        comps = []
        unseen = set(graph)
        while unseen:
            start = min(unseen); q, comp = deque([start]), set()
            while q:
                x = q.popleft()
                if x in comp: continue
                comp.add(x); unseen.discard(x); q.extend(graph[x] - comp)
            comps.append(comp)
        assert sorted(map(len, comps)) == [20, 20], (season, list(map(len, comps)))
        comps.sort(key=lambda c: min(names[x] for x in c).casefold())
        groups[season] = {x: i + 1 for i, comp in enumerate(comps) for x in comp}
    for r in rows:
        assert r['home_team_id'] in groups[r['season']] and r['away_team_id'] in groups[r['season']]
        r['group_home'], r['group_away'] = groups[r['season']][r['home_team_id']], groups[r['season']][r['away_team_id']]
    fields = ['match_id','league','season','date','round','phase','group_home','group_away','home_team_id','home_team','away_team_id','away_team','coverage_level','home_goals','away_goals','awarded','extra_time','ht_home_goals','ht_away_goals','goal_events_complete','ht_source','ev_yellow_home','ev_yellow_away','ev_yellow_1h_home','ev_yellow_1h_away','ev_yellowred_home','ev_yellowred_away','ev_red_home','ev_red_away','ev_card_total','has_stats_all','has_stats_half','has_shotmap','has_events','referee','n_events']
    assert len(rows) == 4081 and len({r['match_id'] for r in rows}) == len(rows)
    assert {s: sum(r['season'] == s for r in rows) for s in SEASON_COUNTS} == SEASON_COUNTS
    assert sum(r['has_stats_all'] for r in rows) == sum(r['has_shotmap'] for r in rows) == 0
    with open(OUT / 'espf_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    team_fields = ['match_id','season','date','phase','group','team_id','team','venue','goals_for','goals_against','ht_goals_for','ht_goals_against','yellow_events_for','yellow_events_against']
    team_rows = []
    for r in rows:
        for side, opp in (('home', 'away'), ('away', 'home')):
            team_rows.append({'match_id': r['match_id'], 'season': r['season'], 'date': r['date'], 'phase': r['phase'], 'group': r[f'group_{side}'], 'team_id': r[f'{side}_team_id'], 'team': r[f'{side}_team'], 'venue': side, 'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{opp}_goals'], 'ht_goals_for': r[f'ht_{side}_goals'], 'ht_goals_against': r[f'ht_{opp}_goals'], 'yellow_events_for': r[f'ev_yellow_{side}'], 'yellow_events_against': r[f'ev_yellow_{opp}']})
    with open(OUT / 'espf_team_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=team_fields); w.writeheader(); w.writerows(team_rows)
    print('rows', len(rows), 'per-season', {s: sum(r['season'] == s for r in rows) for s in SEASON_COUNTS}, 'awarded', sum(r['awarded'] for r in rows), 'extra_time', sum(r['extra_time'] for r in rows), 'card_events', sum(r['ev_card_total'] for r in rows), 'goal_events_complete', sum(r['goal_events_complete'] for r in rows))


if __name__ == '__main__': main()
