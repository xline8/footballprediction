"""Build CA-PremierLeague match and team-match tables from the FotMob warehouse."""
import csv, json, re
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment/fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
STAT_KEYS = ['BallPossesion','expected_goals','total_shots','ShotsOnTarget','ShotsOffTarget',
             'blocked_shots','shots_inside_box','shots_outside_box','big_chance',
             'touches_opp_box','corners','yellow_cards','red_cards','fouls','Offsides',
             'keeper_saves']

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split(' ')[0].replace('%', ''))
    except (ValueError, TypeError): return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get('stats') or {}).get('Periods') or {}
    for period, block in periods.items():
        for group in (block or {}).get('stats', []) or []:
            for stat in group.get('stats', []) or []:
                vals = stat.get('stats') or [None, None]
                key = stat.get('key')
                # Keep the first occurrence; the feed repeats some keys in groups.
                if (period, key) not in out:
                    out[(period, key)] = (num(vals[0]), num(vals[1]) if len(vals) > 1 else None)
    return out

def event_minute(event):
    # FotMob stores stoppage-time first-half events as time=45 with
    # overloadTime set (e.g. 45+2).  The study convention is time <= 45.
    value = event.get('time')
    if isinstance(value, (int, float)): return float(value)
    match = re.match(r'^\s*(\d+)', str(value or ''))
    return float(match.group(1)) if match else None

def ht_goal_count(events, is_home):
    """Count credited first-half goals; time=45 includes 45+overloadTime."""
    total = 0
    for event in events:
        if event.get('type') != 'Goal' or event.get('isHome') is None:
            continue
        minute = event_minute(event)
        if minute is not None and minute <= 45 and bool(event.get('isHome')) == is_home:
            total += 1
    return total

def phase(match_round):
    # The league's regular rounds are numeric strings. Every other round is a playoff.
    return 'regular' if re.fullmatch(r'\d+', str(match_round or '')) else 'playoff'

def score(score_str):
    parts = re.split(r'\s*[–-]\s*', score_str or '0-0')
    return int(float(parts[0])), int(float(parts[1]))

def main():
    index = [r for r in csv.DictReader(open(INDEX)) if r['league_id'] == '9986']
    index.sort(key=lambda r: (r['date'], r['match_id']))
    rows = []
    for item in index:
        payload = json.load(open(MAIN_REPO / item['path']))
        general = payload.get('general') or {}
        status = (payload.get('header') or {}).get('status') or {}
        if not status.get('finished'):
            continue
        content = payload.get('content') or {}
        fs = flat_stats(content)
        get = lambda period, key: fs.get((period, key), (None, None))
        match_round = str(general.get('matchRound') or '')
        ph = phase(match_round)
        home = general['homeTeam']; away = general['awayTeam']
        rec = {'match_id': item['match_id'], 'league': 'CA-PremierLeague', 'season': item['season'],
               'date': item['date'], 'round': match_round, 'sub_league_id': general.get('leagueId'),
               'sub_league_name': general.get('leagueName'), 'phase': ph, 'included': int(ph == 'regular'),
               'home_team_id': home['id'], 'home_team': home['name'], 'away_team_id': away['id'],
               'away_team': away['name'], 'coverage_level': general.get('coverageLevel')}
        rec['home_goals'], rec['away_goals'] = score(status.get('scoreStr'))
        events = ((content.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals = [e for e in events if e.get('type') == 'Goal']
        for side, is_home in [('home', True), ('away', False)]:
            rec[f'ht_{side}_goals'] = ht_goal_count(events, is_home)
        rec['ht_source'] = 'events'
        rec['ev_goals_home'] = sum(1 for e in goals if bool(e.get('isHome')) is True)
        rec['ev_goals_away'] = sum(1 for e in goals if bool(e.get('isHome')) is False)
        rec['score_events_mismatch'] = int((rec['ev_goals_home'], rec['ev_goals_away']) != (rec['home_goals'], rec['away_goals']))
        for card, tag in [('Yellow', 'yellow'), ('YellowRed', 'yellowred'), ('Red', 'red')]:
            for side, is_home in [('home', True), ('away', False)]:
                rec[f'ev_{tag}_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == card and bool(e.get('isHome')) == is_home)
                rec[f'ht_ev_{tag}_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == card and bool(e.get('isHome')) == is_home and event_minute(e) is not None and event_minute(e) <= 45)
        for side in ('home', 'away'):
            rec[f'yellow_{side}'] = float(rec[f'ev_yellow_{side}'])
            rec[f'yellowred_{side}'] = float(rec[f'ev_yellowred_{side}'])
            rec[f'red_{side}'] = float(rec[f'ev_red_{side}'] + rec[f'ev_yellowred_{side}'])
        for key in STAT_KEYS:
            for period, prefix in [('All', ''), ('FirstHalf', 'fh_'), ('SecondHalf', 'sh_')]:
                h, a = get(period, key)
                rec[f'{prefix}{key}_home'] = h; rec[f'{prefix}{key}_away'] = a
        rec['stats_yellow_home'] = rec['yellow_cards_home']; rec['stats_yellow_away'] = rec['yellow_cards_away']
        rec['stats_red_home'] = rec['red_cards_home']; rec['stats_red_away'] = rec['red_cards_away']
        info = (content.get('matchFacts') or {}).get('infoBox') or {}
        rec['referee'] = ((info.get('Referee') or {}).get('text') or '').strip()
        shots = (content.get('shotmap') or {}).get('shots') or []
        rec['has_stats_all'] = int(('All', 'corners') in fs)
        rec['has_stats_half'] = int(('FirstHalf', 'corners') in fs)
        rec['has_shotmap'] = int(bool(shots)); rec['n_shotmap_shots'] = len(shots)
        rec['has_events'] = int(bool(events)); rec['has_xg'] = int(rec['expected_goals_home'] is not None or rec['expected_goals_away'] is not None)
        rows.append(rec)
    if not rows: raise RuntimeError('No CA-PremierLeague matches found')
    fields = list(rows[0])
    with open(OUT / 'ca_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, opp in [('home', 'away'), ('away', 'home')]:
            t = {'match_id': r['match_id'], 'season': r['season'], 'date': r['date'], 'phase': r['phase'],
                 'included': r['included'], 'team_id': r[f'{side}_team_id'], 'team': r[f'{side}_team'],
                 'venue': side, 'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{opp}_goals']}
            for key in ['total_shots','ShotsOnTarget','corners','BallPossesion','touches_opp_box','big_chance']:
                t[f'{key}_for'] = r.get(f'{key}_{side}'); t[f'{key}_against'] = r.get(f'{key}_{opp}')
            for key in ['yellow','yellowred','red']:
                t[f'{key}_for'] = r[f'{key}_{side}']; t[f'{key}_against'] = r[f'{key}_{opp}']
            for key in ['stats_yellow','stats_red']:
                t[f'{key}_for'] = r[f'{key}_{side}']; t[f'{key}_against'] = r[f'{key}_{opp}']
            t['referee'] = r['referee']; team_rows.append(t)
    with open(OUT / 'ca_team_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    latest = {}
    for r in rows:
        for side in ('home', 'away'): latest[str(r[f'{side}_team_id'])] = r[f'{side}_team']
    with open(OUT / 'ca_teams.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['team_id', 'canonical_name']); w.writeheader()
        w.writerows({'team_id': k, 'canonical_name': v} for k, v in sorted(latest.items()))
    print(f'matches={len(rows)} included={sum(r["included"] for r in rows)} playoffs={sum(not r["included"] for r in rows)} team_rows={len(team_rows)} teams={len(latest)}')

if __name__ == '__main__': main()
