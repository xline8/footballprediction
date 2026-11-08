"""Build France Ligue 2 tables from the main FotMob warehouse."""
import csv, json
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment/fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "expected_goals_non_penalty",
             "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance",
             "touches_opp_box", "corners", "yellow_cards", "red_cards",
             "fouls", "Offsides", "keeper_saves"]

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split()[0].replace('%', ''))
    except (ValueError, IndexError): return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get('stats') or {}).get('Periods') or {}
    for period, block in periods.items():
        for group in (block or {}).get('stats', []) or []:
            for stat in group.get('stats', []) or []:
                vals = stat.get('stats') or []
                out[(period, stat.get('key'))] = (num(vals[0]) if vals else None,
                                                  num(vals[1]) if len(vals) > 1 else None)
    return out

def main():
    indexed = [r for r in csv.DictReader(open(INDEX, newline='')) if r['league_id'] == '110']
    indexed.sort(key=lambda r: (r['date'], r['match_id']))
    rows = []
    for ir in indexed:
        d = json.load(open(MAIN_REPO / ir['path']))
        gen, header = d.get('general') or {}, d.get('header') or {}
        status = header.get('status') or {}
        if not status.get('finished'): continue
        content = d.get('content') or {}; fs = flat_stats(content)
        def stat(period, key): return fs.get((period, key), (None, None))
        home, away = gen['homeTeam'], gen['awayTeam']
        rec = {'match_id': ir['match_id'], 'league': 'FR-Ligue2', 'league_id': '110',
               'country': 'France', 'season': ir['season'], 'date': ir['date'],
               'round': str(gen.get('matchRound') or gen.get('leagueRoundName') or ''),
               'round_name': str(gen.get('leagueRoundName') or ''),
               'home_team_id': home['id'], 'home_team': home['name'],
               'away_team_id': away['id'], 'away_team': away['name'],
               'coverage_level': gen.get('coverageLevel')}
        # The feed's observed rounds are numeric regular rounds (1..38); retain
        # the data-derived label so future playoff/playout rounds are visible.
        round_value = rec['round']
        rec['phase'] = 'regular' if round_value.isdigit() and 1 <= int(round_value) <= 38 else 'non_regular'
        score = str(status.get('scoreStr') or '0 - 0').split('-')
        rec['home_goals'], rec['away_goals'] = int(score[0]), int(score[1])
        events = ((content.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals = [e for e in events if e.get('type') == 'Goal']
        rec['ht_home_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and e.get('isHome'))
        rec['ht_away_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and not e.get('isHome'))
        rec['ht_source'] = 'events' if events else 'none'
        for side, is_home in [('home', True), ('away', False)]:
            rec[f'ev_yellow_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'Yellow' and e.get('isHome') == is_home)
            rec[f'ev_yellow_1h_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'Yellow' and e.get('isHome') == is_home and e.get('time') is not None and e['time'] <= 45)
            rec[f'ev_yellowred_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'YellowRed' and e.get('isHome') == is_home)
            rec[f'ev_red_{side}'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'Red' and e.get('isHome') == is_home)
        for key in STAT_KEYS:
            rec[f'{key}_home'], rec[f'{key}_away'] = stat('All', key)
            rec[f'fh_{key}_home'], rec[f'fh_{key}_away'] = stat('FirstHalf', key)
            rec[f'sh_{key}_home'], rec[f'sh_{key}_away'] = stat('SecondHalf', key)
        rec['referee'] = (((content.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}).get('text') or ''
        periods = list(((content.get('stats') or {}).get('Periods') or {}).keys())
        rec['has_stats_all'] = int(('All', 'corners') in fs)
        rec['has_stats_half'] = int(('FirstHalf', 'corners') in fs)
        rec['has_events'] = int(bool(events))
        shots = ((content.get('shotmap') or {}).get('shots') or [])
        reg = [s for s in shots if s.get('period') != 'PenaltyShootout']
        rec['has_shotmap'], rec['n_shootout_shots'] = int(bool(reg)), len(shots) - len(reg)
        for side, tid in [('home', home['id']), ('away', away['id'])]:
            ss = [s for s in reg if s.get('teamId') == tid]
            rec[f'sm_shots_{side}'] = len(ss)
            rec[f'sm_sot_{side}'] = sum(1 for s in ss if s.get('isOnTarget') and not s.get('isBlocked'))
            rec[f'sm_xg_{side}'] = round(sum(s.get('expectedGoals') or 0 for s in ss), 4)
            xgot = [s.get('expectedGoalsOnTarget') for s in ss if s.get('expectedGoalsOnTarget') is not None]
            rec[f'sm_xgot_{side}'], rec[f'sm_xgot_n_{side}'] = round(sum(xgot), 4), len(xgot)
            rec[f'sm_shots_fh_{side}'] = sum(1 for s in ss if s.get('period') == 'FirstHalf')
        rows.append(rec)
    assert len(rows) >= 1851, len(rows)
    assert len({r['match_id'] for r in rows}) == len(rows)
    with open(OUT / 'fr_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, opp in [('home', 'away'), ('away', 'home')]:
            t = {'match_id': r['match_id'], 'season': r['season'], 'date': r['date'], 'phase': r['phase'],
                 'team_id': r[f'{side}_team_id'], 'team': r[f'{side}_team'], 'venue': side,
                 'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{opp}_goals']}
            for key in ['expected_goals','total_shots','ShotsOnTarget','corners','yellow_cards','touches_opp_box','big_chance','BallPossesion']:
                t[f'{key}_for'], t[f'{key}_against'] = r[f'{key}_{side}'], r[f'{key}_{opp}']
            for key in ['ev_yellow','ev_yellow_1h','sm_xg','sm_shots']:
                t[f'{key}_for'], t[f'{key}_against'] = r[f'{key}_{side}'], r[f'{key}_{opp}']
            team_rows.append(t)
    with open(OUT / 'fr_team_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print(f'matches {len(rows)} team_rows {len(team_rows)}')

if __name__ == '__main__': main()
