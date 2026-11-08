"""Build the IT-SerieB analysis tables from the FotMob warehouse."""
import csv, json
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment' / 'fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion","expected_goals","expected_goals_open_play","expected_goals_set_play",
 "expected_goals_non_penalty","total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots",
 "shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards",
 "red_cards","fouls","Offsides","keeper_saves"]

def _num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        try: return float(v.split(' ')[0].replace('%', ''))
        except ValueError: return None
    return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get('stats') or {}).get('Periods') or {}
    for period, block in periods.items():
        for group in (block or {}).get('stats', []) or []:
            for s in group.get('stats', []) or []:
                vals = s.get('stats') or [None, None]
                h, a = _num(vals[0]), _num(vals[1]) if len(vals) > 1 else None
                if h is not None or a is not None: out[(period, s.get('key'))] = (h, a)
    return out

def main():
    indexed = [r for r in csv.DictReader(open(INDEX)) if r['league_id'] == '86']
    indexed.sort(key=lambda r: (r['date'], r['match_id']))
    out = []
    for ir in indexed:
        d = json.load(open(MAIN_REPO / ir['path']))
        gen, hdr = d.get('general') or {}, d.get('header') or {}
        status = hdr.get('status') or {}
        if not status.get('finished'): continue
        c, fs = d.get('content') or {}, flat_stats(d.get('content') or {})
        def g(period, key): return fs.get((period, key), (None, None))
        phase_name = str(gen.get('leagueName') or '')
        phase = {'Serie B': 'regular', 'Serie B Promotion Playoff': 'promotion_playoff',
                 'Serie B Relegation Playoff': 'relegation_playoff'}.get(phase_name, phase_name)
        # Reggiana id alias: FotMob carried the club as id 959006 ('Reggiana')
        # for Aug-Nov 2023 and as id 6500 ('AC Reggiana 1919') thereafter;
        # the two ids never co-occur and their 2023/2024 sequences are
        # complementary (15 + 23 = 38 matches). Canonical id = 6500.
        ID_ALIAS = {959006: 6500}
        hid = ID_ALIAS.get(gen['homeTeam']['id'], gen['homeTeam']['id'])
        aid = ID_ALIAS.get(gen['awayTeam']['id'], gen['awayTeam']['id'])
        rec = {'match_id': ir['match_id'], 'league': 'IT-SerieB', 'season': ir['season'],
               'date': ir['date'], 'round': str(gen.get('matchRound')), 'phase': phase,
               'home_team_id': hid, 'home_team': gen['homeTeam']['name'],
               'away_team_id': aid, 'away_team': gen['awayTeam']['name'],
               'coverage_level': gen.get('coverageLevel')}
        score = (status.get('scoreStr') or '0 - 0').split('-')
        rec['home_goals'], rec['away_goals'] = int(score[0]), int(score[1])
        evs = ((c.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals = [e for e in evs if e.get('type') == 'Goal']
        rec['ht_home_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and e.get('isHome'))
        rec['ht_away_goals'] = sum(1 for e in goals if e.get('time') is not None and e['time'] <= 45 and not e.get('isHome'))
        rec['ht_source'] = 'events' if evs else 'none'
        for side, home in (('home', True), ('away', False)):
            rec[f'ev_yellow_{side}'] = sum(1 for e in evs if e.get('type') == 'Card' and e.get('card') == 'Yellow' and e.get('isHome') == home)
            rec[f'ev_yellow_1h_{side}'] = sum(1 for e in evs if e.get('type') == 'Card' and e.get('card') == 'Yellow' and e.get('isHome') == home and e.get('time') is not None and e['time'] <= 45)
            rec[f'ev_yellowred_{side}'] = sum(1 for e in evs if e.get('type') == 'Card' and e.get('card') == 'YellowRed' and e.get('isHome') == home)
            rec[f'ev_red_{side}'] = sum(1 for e in evs if e.get('type') == 'Card' and e.get('card') == 'Red' and e.get('isHome') == home)
        for k in STAT_KEYS:
            rec[f'{k}_home'], rec[f'{k}_away'] = g('All', k)
            rec[f'fh_{k}_home'], rec[f'fh_{k}_away'] = g('FirstHalf', k)
            rec[f'sh_{k}_home'], rec[f'sh_{k}_away'] = g('SecondHalf', k)
        # Unified cards target = event feed (EDA cards check: stats feed
        # undercounts events in every dev season, -1.6% to -3.9%, exact
        # agreement only 79.7-89.7%). Stats yellows stay in yellow_cards_*.
        rec['yellow_home'], rec['yellow_away'] = rec['ev_yellow_home'], rec['ev_yellow_away']
        rec['red_home'], rec['red_away'] = rec['red_cards_home'], rec['red_cards_away']
        rec['cards_source'] = 'events'
        rec['referee'] = (((c.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}).get('text') or ''
        periods = list(((c.get('stats') or {}).get('Periods') or {}).keys())
        rec['has_stats_all'] = int(('All', 'corners') in fs)
        rec['has_stats_half'] = int(('FirstHalf', 'corners') in fs)
        rec['has_extra_time'] = int(any('Extra' in p for p in periods))
        shots = ((c.get('shotmap') or {}).get('shots') or [])
        reg = [s for s in shots if s.get('period') != 'PenaltyShootout']
        rec['has_shotmap'], rec['n_shootout_shots'] = int(bool(reg)), len(shots) - len(reg)
        for side, tid in (('home', rec['home_team_id']), ('away', rec['away_team_id'])):
            ss = [s for s in reg if s.get('teamId') == tid]
            rec[f'sm_shots_{side}'] = len(ss)
            rec[f'sm_sot_{side}'] = sum(1 for s in ss if s.get('isOnTarget') and not s.get('isBlocked'))
            rec[f'sm_xg_{side}'] = round(sum(s.get('expectedGoals') or 0 for s in ss), 4)
            xgots = [s.get('expectedGoalsOnTarget') for s in ss if s.get('expectedGoalsOnTarget') is not None]
            rec[f'sm_xgot_{side}'], rec[f'sm_xgot_n_{side}'] = round(sum(xgots), 4), len(xgots)
            rec[f'sm_shots_fh_{side}'] = sum(1 for s in ss if s.get('period') == 'FirstHalf')
        rec['has_events'] = int(bool(evs))
        out.append(rec)
    assert len(out) >= 2059, len(out)
    assert len({r['match_id'] for r in out}) == len(out)
    with open(OUT / 'itserieb_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (('home', 'away'), ('away', 'home')):
            t = {'match_id': r['match_id'], 'season': r['season'], 'date': r['date'], 'phase': r['phase'],
                 'team_id': r[f'{side}_team_id'], 'team': r[f'{side}_team'], 'venue': side,
                 'goals_for': r[f'{side}_goals'], 'goals_against': r[f'{opp}_goals']}
            for k in ['expected_goals','total_shots','ShotsOnTarget','corners','yellow_cards','touches_opp_box','big_chance','BallPossesion']:
                t[f'{k}_for'], t[f'{k}_against'] = r[f'{k}_{side}'], r[f'{k}_{opp}']
            t['yellow_events_for'], t['yellow_events_against'] = r[f'ev_yellow_{side}'], r[f'ev_yellow_{opp}']
            t['sm_xg_for'], t['sm_shots_for'] = r[f'sm_xg_{side}'], r[f'sm_shots_{side}']
            tm.append(t)
    with open(OUT / 'itserieb_team_matches.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0])); w.writeheader(); w.writerows(tm)
    from collections import Counter
    print(f'matches {len(out)} team_rows {len(tm)}')
    print('rows_by_season', dict(sorted(Counter(r['season'] for r in out).items())))
    print('rows_by_phase', dict(sorted(Counter(r['phase'] for r in out).items())))
    print('rows_by_season_phase', {s: dict(sorted(Counter(r['phase'] for r in out if r['season'] == s).items())) for s in sorted({r['season'] for r in out})})

if __name__ == '__main__': main()
