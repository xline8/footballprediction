"""Build Brazil Serie C analysis tables and payload-content inventories.

The warehouse is intentionally read from the main checkout.  This script is
descriptive only: it does not fit a model and never reads a virgin season for
selection or evaluation.
"""
import csv, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment' / 'fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
ANALYSIS = OUT.parent / 'analysis'
STAT_KEYS = ['expected_goals','ShotsOnTarget','total_shots','corners',
             'yellow_cards','red_cards','touches_opp_box','BallPossesion',
             'fouls','Offsides','keeper_saves']

def flat_stats(content):
    out = {}
    periods = ((content or {}).get('stats') or {}).get('Periods') or {}
    for period, block in periods.items():
        for group in (block or {}).get('stats', []) or []:
            for stat in group.get('stats', []) or []:
                vals = stat.get('stats') or [None, None]
                out[(period, stat.get('key'))] = tuple(vals[:2])
    return {k: v for k, v in out.items() if any(x is not None for x in v)}

def events(content):
    return (((content or {}).get('matchFacts') or {}).get('events') or {}).get('events') or []

def phase(gen):
    name = (gen.get('leagueName') or '').lower()
    rname = str(gen.get('leagueRoundName') or '').lower()
    if 'final' in name or rname == 'final' or 'final' in rname:
        return 'final'
    if '2nd stage' in name or 'promotion round' in name or 'promotion' in rname:
        return 'second'
    return 'first'

def score_pair(s):
    try:
        a, b = [int(x.strip()) for x in str(s).split('-')]
        return a, b
    except Exception:
        return None, None

def main():
    idx = [r for r in csv.DictReader(INDEX.open()) if r['league_id'] == '8971']
    idx.sort(key=lambda r: (r['date'], r['match_id']))
    rows, teams = [], []
    inventory = defaultdict(lambda: {'index_rows':0,'finished':0,'unfinished':0,
        'phase':Counter(),'stats_flag':0,'stats_nonnull':0,'stats_values':0,
        'periods':Counter(),'events':0,'goal_events':0,'card_events':0,
        'shotmap_nonempty':0,'lineup':0,'referee':0,'score_mismatch':0,
        'goal_event_score_matches':0,'goal_event_score_mismatches':0,
        'unlinked_score':0,'teams':set(),'rounds':Counter(),'league_names':Counter()})
    index_flags = Counter(); index_by_season = defaultdict(Counter)
    for ir in idx:
        s = ir['season']; inv = inventory[s]; inv['index_rows'] += 1
        for k in ('has_stats','has_lineup','has_shotmap','has_period_splits'):
            index_flags[k] += ir[k].lower() == 'true'; index_by_season[s][k] += ir[k].lower() == 'true'
        d = json.load((MAIN_REPO / ir['path']).open())
        gen, hdr, content = d.get('general') or {}, d.get('header') or {}, d.get('content') or {}
        status = hdr.get('status') or {}
        st = flat_stats(content); ev = events(content)
        inv['stats_flag'] += ir['has_stats'].lower() == 'true'
        inv['stats_nonnull'] += bool(st); inv['stats_values'] += len(st)
        periods = ((content.get('stats') or {}).get('Periods') or {})
        for p, b in periods.items(): inv['periods'][p] += bool(b)
        inv['events'] += bool(ev); inv['goal_events'] += sum(e.get('type') == 'Goal' for e in ev)
        inv['card_events'] += sum(e.get('type') == 'Card' for e in ev)
        inv['shotmap_nonempty'] += bool(((content.get('shotmap') or {}).get('shots') or []))
        lu = content.get('lineup') or {}
        inv['lineup'] += len((lu.get('homeTeam') or {}).get('starters') or []) == 11 and len((lu.get('awayTeam') or {}).get('starters') or []) == 11
        ref = ((content.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}
        inv['referee'] += bool(ref.get('text'))
        inv['phase'][phase(gen)] += 1; inv['rounds'][str(gen.get('matchRound'))] += 1
        inv['league_names'][gen.get('leagueName')] += 1
        for side in ('homeTeam','awayTeam'):
            t = gen.get(side) or {}; inv['teams'].add(str(t.get('id')))
        if not status.get('finished'):
            inv['unfinished'] += 1; continue
        inv['finished'] += 1
        hg, ag = score_pair(status.get('scoreStr'))
        if hg is None: raise ValueError(f"finished without score {ir['match_id']}")
        if ir.get('score','').replace(' ','') != f'{hg}-{ag}': inv['score_mismatch'] += 1
        goals = [e for e in ev if e.get('type') == 'Goal']
        ge_h = sum(e.get('isHome') is True for e in goals); ge_a = sum(e.get('isHome') is False for e in goals)
        if (ge_h, ge_a) == (hg, ag): inv['goal_event_score_matches'] += 1
        else: inv['goal_event_score_mismatches'] += 1
        ht_h = ht_a = None; ht_known = 0
        if len(goals) == hg + ag and all(e.get('time') is not None and e.get('isHome') is not None for e in goals):
            ht_h = sum(e['time'] <= 45 and e['isHome'] for e in goals); ht_a = sum(e['time'] <= 45 and not e['isHome'] for e in goals); ht_known = 1
        ph = phase(gen); fit = int(ph != 'final')
        row = {'match_id':ir['match_id'],'season':s,'date':ir['date'],'phase':ph,
               'round':str(gen.get('matchRound') or ''),'league_name':gen.get('leagueName'),
               'home_team_id':gen.get('homeTeam',{}).get('id'),'home_team':gen.get('homeTeam',{}).get('name'),
               'away_team_id':gen.get('awayTeam',{}).get('id'),'away_team':gen.get('awayTeam',{}).get('name'),
               'home_goals':hg,'away_goals':ag,'in_fit_set':fit,'ht_home_goals':ht_h,
               'ht_away_goals':ht_a,'ht_known':ht_known,'event_n':len(ev),'goal_event_n':len(goals),
               'card_event_n':sum(e.get('type')=='Card' for e in ev),'stats_present':int(bool(content.get('stats'))),
               'stats_nonnull':int(bool(st)),'stats_value_n':len(st),'shotmap_n':len((content.get('shotmap') or {}).get('shots') or []),
               'referee_present':int(bool(ref.get('text')))}
        rows.append(row)
        for venue, side, other in [('H','home','away'),('A','away','home')]:
            teams.append({'match_id':ir['match_id'],'season':s,'date':ir['date'],'team_id':row[f'{side}_team_id'],
                          'team':row[f'{side}_team'],'opponent_id':row[f'{other}_team_id'],'opponent':row[f'{other}_team'],
                          'venue':venue,'goals_for':row[f'{side}_goals'],'goals_against':row[f'{other}_goals'],
                          'phase':ph,'in_fit_set':fit})
    rows.sort(key=lambda r:(r['date'],r['match_id'])); teams.sort(key=lambda r:(r['date'],r['match_id'],r['venue']))
    for path, data in [(OUT/'brc_matches.csv', rows),(OUT/'brc_team_matches.csv',teams)]:
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    def clean(x):
        if isinstance(x,(Counter,defaultdict)): return {str(k):clean(v) for k,v in x.items()}
        if isinstance(x,set): return sorted(x)
        if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
        return x
    summary={'index_rows':len(idx),'finished_rows':len(rows),'unfinished_rows':len(idx)-len(rows),
             'index_flags':dict(index_flags),'seasons':{s:clean(v) for s,v in inventory.items()},
             'index_flags_by_season':{s:dict(v) for s,v in index_by_season.items()},
             'score_mismatches':sum(v['score_mismatch'] for v in inventory.values()),
             'score_check_n':len(rows)}
    ANALYSIS.mkdir(parents=True,exist_ok=True)
    (ANALYSIS/'inventory_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'index_rows':len(idx),'finished':len(rows),'unfinished':len(idx)-len(rows),'score_mismatches':summary['score_mismatches']},indent=2))

if __name__=='__main__': main()
