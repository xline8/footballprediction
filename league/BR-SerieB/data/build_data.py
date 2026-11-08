"""Build the Brazil Serie B analysis tables from the FotMob warehouse."""
import csv, json
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "expected_goals_non_penalty", "total_shots",
             "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box",
             "shots_outside_box", "big_chance", "touches_opp_box", "corners",
             "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves"]

def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split()[0].replace('%', ''))
    except (TypeError, ValueError): return None

def flat_stats(content):
    out = {}
    for period, block in (((content or {}).get('stats') or {}).get('Periods') or {}).items():
        for group in (block or {}).get('stats', []) or []:
            for stat in group.get('stats', []) or []:
                vals = stat.get('stats') or [None, None]
                h, a = num(vals[0]), num(vals[1] if len(vals) > 1 else None)
                if h is not None or a is not None: out[(period, stat.get('key'))] = (h, a)
    return out

def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r['league_id'] == '8814']
    rows.sort(key=lambda r: (r['date'], r['match_id']))
    out = []
    for ir in rows:
        d = json.load(open(MAIN_REPO / ir['path']))
        gen, status = d.get('general') or {}, (d.get('header') or {}).get('status') or {}
        if not status.get('finished'): continue
        content, fs = d.get('content') or {}, flat_stats(d.get('content') or {})
        def get(period, key): return fs.get((period, key), (None, None))
        rec = {'match_id': ir['match_id'], 'league': 'BR-SerieB', 'season': ir['season'],
               'date': ir['date'], 'round': str(gen.get('matchRound')),
               'home_team_id': gen['homeTeam']['id'], 'home_team': gen['homeTeam']['name'],
               'away_team_id': gen['awayTeam']['id'], 'away_team': gen['awayTeam']['name'],
               'coverage_level': gen.get('coverageLevel')}
        score = (status.get('scoreStr') or '0 - 0').split('-')
        rec['home_goals'], rec['away_goals'] = int(score[0]), int(score[1])
        events = ((content.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals = [e for e in events if e.get('type') == 'Goal']
        rec['ht_home_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and e.get('isHome'))
        rec['ht_away_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and not e.get('isHome'))
        rec['ht_source'] = 'events'
        rec['ev_yellow_home'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'Yellow' and e.get('isHome'))
        rec['ev_yellow_away'] = sum(1 for e in events if e.get('type') == 'Card' and e.get('card') == 'Yellow' and not e.get('isHome'))
        for key in STAT_KEYS:
            h, a = get('All', key); rec[f'{key}_home'], rec[f'{key}_away'] = h, a
            h, a = get('FirstHalf', key); rec[f'fh_{key}_home'], rec[f'fh_{key}_away'] = h, a
            h, a = get('SecondHalf', key); rec[f'sh_{key}_home'], rec[f'sh_{key}_away'] = h, a
        rec['yellow_home'], rec['yellow_away'] = rec['yellow_cards_home'], rec['yellow_cards_away']
        rec['red_home'], rec['red_away'] = rec['red_cards_home'], rec['red_cards_away']
        rec['cards_source'] = 'stats' if rec['yellow_home'] is not None else 'none'
        # 2021-2022 event cards contain no ordinary Yellow records; their stats
        # values are not a recoverable target. The unified target starts in 2023.
        if ir['season'] >= '2023':
            rec['yellow_unified_home'], rec['yellow_unified_away'] = rec['yellow_home'], rec['yellow_away']
            rec['yellow_unified_source'] = 'stats' if rec['yellow_home'] is not None else 'none'
        else:
            rec['yellow_unified_home'] = rec['yellow_unified_away'] = None
            rec['yellow_unified_source'] = 'unusable_pre2023'
        ref = (((content.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}).get('text')
        rec['referee'] = ref or None
        periods = ((content.get('stats') or {}).get('Periods') or {})
        rec['has_stats_all'] = int(('All', 'corners') in fs)
        rec['has_stats_half'] = int(('FirstHalf', 'corners') in fs and ('SecondHalf', 'corners') in fs)
        rec['has_extra_time'] = int(any('Extra' in p for p in periods))
        shots = ((content.get('shotmap') or {}).get('shots') or [])
        regulation = [s for s in shots if s.get('period') != 'PenaltyShootout']
        rec['has_shotmap'], rec['n_shootout_shots'] = int(bool(regulation)), len(shots) - len(regulation)
        for side, tid in [('home', rec['home_team_id']), ('away', rec['away_team_id'])]:
            ss = [s for s in regulation if s.get('teamId') == tid]
            rec[f'sm_shots_{side}'] = len(ss)
            rec[f'sm_sot_{side}'] = sum(1 for s in ss if s.get('isOnTarget') and not s.get('isBlocked'))
            rec[f'sm_xg_{side}'] = round(sum(s.get('expectedGoals') or 0 for s in ss), 4) if ss else None
            xgot = [s.get('expectedGoalsOnTarget') for s in ss if s.get('expectedGoalsOnTarget') is not None]
            rec[f'sm_xgot_{side}'] = round(sum(xgot), 4) if xgot else None
            rec[f'sm_xgot_n_{side}'] = len(xgot)
            rec[f'sm_shots_fh_{side}'] = sum(1 for s in ss if s.get('period') == 'FirstHalf')
        rec['has_events'] = int(bool(events)); out.append(rec)
    # Floor, not equality: the live index can also list unplayed fixtures,
    # which the loop above skips; 2270 is the frozen build-time count.
    assert len(out) >= 2270, len(out)
    ids = [r['match_id'] for r in out]; assert len(set(ids)) == len(ids)
    with open(OUT / 'brb_matches.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    team = []
    for r in out:
        for side, opp in [('home', 'away'), ('away', 'home')]:
            t = {'match_id': r['match_id'], 'season': r['season'], 'date': r['date'], 'team_id': r[f'{side}_team_id'],
                 'team': r[f'{side}_team'], 'venue': side,
                 'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{opp}_goals']}
            for k in ['expected_goals', 'total_shots', 'ShotsOnTarget', 'corners', 'yellow_cards', 'touches_opp_box', 'big_chance', 'BallPossesion']:
                t[f'{k}_for'], t[f'{k}_against'] = r.get(f'{k}_{side}'), r.get(f'{k}_{opp}')
            t['yellow_unified_for'], t['yellow_unified_against'] = r[f'yellow_unified_{side}'], r[f'yellow_unified_{opp}']
            t['sm_xg_for'], t['sm_shots_for'] = r[f'sm_xg_{side}'], r[f'sm_shots_{side}']; team.append(t)
    with open(OUT / 'brb_team_matches.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(team[0])); w.writeheader(); w.writerows(team)
    print(f'matches {len(out)} team_rows {len(team)}')

if __name__ == '__main__': main()
