"""Build the finished-match and team-match tables for Slovakia 2. Liga.

This league has no usable stats, xG, or shotmap blocks in the warehouse, so
the output intentionally contains only score, event, referee, and identity
fields needed by the EDA.
"""
import csv
import json
import re
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment/fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent


def score(value):
    a, b = re.split(r'\s*[–-]\s*', value or '0-0')[:2]
    return int(float(a)), int(float(b))


def minute(event):
    value = event.get('time')
    if isinstance(value, (int, float)):
        return float(value)
    match = re.match(r'^(\d+)', str(value or ''))
    return float(match.group(1)) if match else None


def main():
    index = [r for r in csv.DictReader(open(INDEX)) if r['league_id'] == '8973']
    index.sort(key=lambda r: (r['date'], r['match_id']))
    rows = []
    for item in index:
        payload = json.load(open(MAIN_REPO / item['path']))
        general = payload.get('general') or {}
        header = payload.get('header') or {}
        status = header.get('status') or {}
        if not status.get('finished'):
            continue
        content = payload.get('content') or {}
        facts = content.get('matchFacts') or {}
        events = (facts.get('events') or {}).get('events') or []
        goals = [e for e in events if e.get('type') == 'Goal']
        home_goals, away_goals = score(status.get('scoreStr'))
        ht_home = sum(1 for e in goals if minute(e) is not None and minute(e) <= 45 and bool(e.get('isHome')))
        ht_away = sum(1 for e in goals if minute(e) is not None and minute(e) <= 45 and not bool(e.get('isHome')))
        event_total_home = sum(1 for e in goals if bool(e.get('isHome')))
        event_total_away = len(goals) - event_total_home
        referee = ((facts.get('infoBox') or {}).get('Referee') or {}).get('text') or ''
        rows.append({
            'match_id': item['match_id'], 'league': 'SK-2Liga', 'season': item['season'],
            'date': item['date'], 'round': str(general.get('matchRound') or ''),
            'sub_league_id': str(general.get('leagueId') or ''),
            'parent_league_id': str(general.get('parentLeagueId') or ''),
            'home_team_id': str(general['homeTeam']['id']), 'home_team': general['homeTeam']['name'],
            'away_team_id': str(general['awayTeam']['id']), 'away_team': general['awayTeam']['name'],
            'coverage_level': general.get('coverageLevel') or '',
            'home_goals': home_goals, 'away_goals': away_goals,
            'ht_home_goals': ht_home, 'ht_away_goals': ht_away, 'ht_source': 'events',
            'has_events': int(bool(events)),
            'events_reconciled': int(bool(events) and event_total_home == home_goals and event_total_away == away_goals),
            'referee': referee,
        })
    if not rows:
        raise RuntimeError('No finished Slovakia 2. Liga matches found')
    assert len({r['match_id'] for r in rows}) == len(rows)
    fields = list(rows[0])
    with open(OUT / 'sk2_matches.csv', 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

    team_rows = []
    for row in rows:
        for side, other in [('home', 'away'), ('away', 'home')]:
            team_rows.append({
                'match_id': row['match_id'], 'season': row['season'], 'date': row['date'],
                'team_id': row[f'{side}_team_id'], 'team': row[f'{side}_team'], 'venue': side,
                'goals_for': row[f'{side}_goals'], 'goals_against': row[f'{other}_goals'],
            })
    with open(OUT / 'sk2_team_matches.csv', 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0]))
        writer.writeheader(); writer.writerows(team_rows)

    latest = {}
    for row in rows:
        for side in ('home', 'away'):
            latest[row[f'{side}_team_id']] = row[f'{side}_team']
    with open(OUT / 'sk2_teams.csv', 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['team_id', 'canonical_name'])
        writer.writeheader()
        writer.writerows({'team_id': k, 'canonical_name': latest[k]} for k in sorted(latest))
    print(f'matches={len(rows)} team_rows={len(team_rows)} teams={len(latest)}')


if __name__ == '__main__':
    main()
