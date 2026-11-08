"""Build the FotMob FNL match, team-match, and team identity tables."""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment/fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
STAT_KEYS = ['ShotsOnTarget', 'corners', 'total_shots', 'BallPossesion', 'expected_goals']


def minute(value):
    if isinstance(value, (int, float)):
        return float(value)
    m = re.match(r'^(\d+)', str(value or ''))
    return float(m.group(1)) if m else None


def score(value):
    m = re.search(r'(\d+)\s*[–-]\s*(\d+)', str(value or ''))
    if not m:
        raise ValueError(f'bad score: {value!r}')
    return int(m.group(1)), int(m.group(2))


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    index = [r for r in csv.DictReader(INDEX.open()) if r['league_id'] == '253']
    index.sort(key=lambda r: (r['date'], r['match_id']))
    matches, names = [], defaultdict(lambda: defaultdict(set))
    for ix in index:
        payload = json.loads((MAIN_REPO / ix['path']).read_text())
        general = payload.get('general') or {}
        status = (payload.get('header') or {}).get('status') or {}
        if not status.get('finished'):
            continue
        home, away = general['homeTeam'], general['awayTeam']
        for team in (home, away):
            names[str(team['id'])][ix['season']].add(team['name'])
        content = payload.get('content') or {}
        facts = content.get('matchFacts') or {}
        events = ((facts.get('events') or {}).get('events') or [])
        hg, ag = score(status.get('scoreStr'))
        rec = {
            'match_id': ix['match_id'], 'league': 'CZ-FNL', 'season': ix['season'],
            'date': ix['date'], 'round': str(general.get('matchRound') or ''),
            'sub_league_id': general.get('leagueId'), 'sub_league_name': general.get('leagueName'),
            'phase': 'regular', 'included': 1,
            'home_team_id': home['id'], 'home_team': home['name'],
            'away_team_id': away['id'], 'away_team': away['name'],
            'coverage_level': general.get('coverageLevel'), 'home_goals': hg, 'away_goals': ag,
            'goal_events': sum(e.get('type') == 'Goal' for e in events),
            'goal_events_home': sum(e.get('type') == 'Goal' and bool(e.get('isHome')) for e in events),
            'goal_events_away': sum(e.get('type') == 'Goal' and not bool(e.get('isHome')) for e in events),
            'ht_source': 'events',
            'referee': ((facts.get('infoBox') or {}).get('Referee') or {}).get('text', ''),
            'has_events': int(bool(events)),
            'has_shotmap': int(bool((content.get('shotmap') or {}).get('shots'))),
            'shotmap_shots': len((content.get('shotmap') or {}).get('shots') or []),
            'has_lineups': int(bool(content.get('lineup') or content.get('lineups'))),
            'has_player_stats': int(content.get('playerStats') is not None),
        }
        goals = [e for e in events if e.get('type') == 'Goal']
        for side, is_home in (('home', True), ('away', False)):
            rec[f'ht_{side}_goals'] = sum(bool(e.get('isHome')) == is_home and minute(e.get('time')) is not None and minute(e.get('time')) <= 45 for e in goals)
        for card, tag in (('Yellow', 'yellow'), ('YellowRed', 'yellowred'), ('Red', 'red')):
            for side, is_home in (('home', True), ('away', False)):
                rec[f'ev_{tag}_{side}'] = sum(e.get('type') == 'Card' and e.get('card') == card and bool(e.get('isHome')) == is_home for e in events)
        # These are deliberately schema-stable but empty: FNL has no stats target data.
        for key in STAT_KEYS:
            rec[f'{key}_home'] = None
            rec[f'{key}_away'] = None
        rec['stats_periods_all_present'] = int(((content.get('stats') or {}).get('Periods') or {}).get('All') is not None)
        rec['has_period_splits'] = int(any(k in ((content.get('stats') or {}).get('Periods') or {}) for k in ('FirstHalf', 'SecondHalf')))
        matches.append(rec)
    if len(matches) != 1311:
        raise AssertionError(f'expected 1311 FNL rows, got {len(matches)}')
    if any(r['goal_events'] != r['home_goals'] + r['away_goals'] for r in matches):
        raise AssertionError('goal event/header mismatch found')
    write_csv(OUT / 'fnl_matches.csv', matches)

    team_matches = []
    for r in matches:
        for side, other in (('home', 'away'), ('away', 'home')):
            team_matches.append({
                'match_id': r['match_id'], 'season': r['season'], 'date': r['date'],
                'team_id': r[f'{side}_team_id'], 'team': r[f'{side}_team'], 'venue': side,
                'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{other}_goals'],
            })
    write_csv(OUT / 'fnl_team_matches.csv', team_matches)

    teams = []
    for tid, by_season in sorted(names.items(), key=lambda z: int(z[0])):
        variants = sorted({name for values in by_season.values() for name in values})
        latest_season = max(by_season, key=lambda s: SEASONS.index(s))
        latest_names = sorted(by_season[latest_season])
        teams.append({'team_id': tid, 'canonical_name': latest_names[-1],
                      'name_variants': '|'.join(variants),
                      'seasons_present': '|'.join(sorted(by_season, key=SEASONS.index))})
    write_csv(OUT / 'fnl_teams.csv', teams)
    print(f'matches={len(matches)} included={sum(r["included"] for r in matches)} '
          f'team_rows={len(team_matches)} teams={len(teams)}')


if __name__ == '__main__':
    main()
