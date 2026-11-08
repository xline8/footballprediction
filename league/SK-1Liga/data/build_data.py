"""Build Slovak 1. Liga match and team-match analysis tables from FotMob warehouse."""
import csv, json, re
from pathlib import Path

MAIN_REPO = Path('/home/hatch/workspace/footballprediction')
INDEX = MAIN_REPO / 'data_enrichment/fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent
STAT_KEYS = ['BallPossesion','expected_goals','expected_goals_open_play','expected_goals_set_play',
 'expected_goals_non_penalty','total_shots','ShotsOnTarget','ShotsOffTarget','blocked_shots',
 'shots_inside_box','shots_outside_box','big_chance','touches_opp_box','corners','yellow_cards',
 'red_cards','fouls','Offsides','keeper_saves']

def num(v):
    if v is None: return None
    if isinstance(v,(int,float)): return float(v)
    try: return float(str(v).split(' ')[0].replace('%',''))
    except (ValueError, TypeError): return None

def flat_stats(content):
    out={}
    for period, block in (((content or {}).get('stats') or {}).get('Periods') or {}).items():
        for group in (block or {}).get('stats',[]) or []:
            for s in group.get('stats',[]) or []:
                vals=s.get('stats') or [None,None]
                out[(period,s.get('key'))]=(num(vals[0]), num(vals[1]) if len(vals)>1 else None)
    return out

def minute(e):
    v=e.get('time')
    if isinstance(v,(int,float)): return float(v)
    m=re.match(r'^(\d+)', str(v or ''))
    return float(m.group(1)) if m else None

def phase(name):
    n=name or ''
    if 'Championship' in n: return 'championship'
    if 'Relegation' in n: return 'relegation'
    if 'ECL Playoff' in n: return 'playoff'
    return 'regular'

def score(s):
    p=re.split(r'\s*[–-]\s*', s or '0-0')
    return int(float(p[0])), int(float(p[1]))

def main():
    rows=[r for r in csv.DictReader(open(INDEX)) if r['league_id']=='176']
    rows.sort(key=lambda r:(r['date'],r['match_id']))
    out=[]
    for idx in rows:
        d=json.load(open(MAIN_REPO/idx['path']))
        gen=d.get('general') or {}; hdr=d.get('header') or {}; status=hdr.get('status') or {}
        if not status.get('finished'): continue
        content=d.get('content') or {}; fs=flat_stats(content)
        def g(period,key): return fs.get((period,key),(None,None))
        ph=phase(gen.get('leagueName'))
        rec={'match_id':idx['match_id'],'league':'SK-1Liga','season':idx['season'],'date':idx['date'],
             'round':str(gen.get('matchRound')),'sub_league_id':gen.get('leagueId'),'sub_league_name':gen.get('leagueName'),
             'phase':ph,'included':int(ph!='playoff'),'home_team_id':gen['homeTeam']['id'],
             'home_team':gen['homeTeam']['name'],'away_team_id':gen['awayTeam']['id'],
             'away_team':gen['awayTeam']['name'],'coverage_level':gen.get('coverageLevel')}
        rec['home_goals'],rec['away_goals']=score(status.get('scoreStr'))
        evs=((content.get('matchFacts') or {}).get('events') or {}).get('events') or []
        goals=[e for e in evs if e.get('type')=='Goal']
        for side, flag in [('home',True),('away',False)]:
            rec[f'ht_{side}_goals']=sum(1 for e in goals if minute(e) is not None and minute(e)<=45 and bool(e.get('isHome'))==flag)
        rec['ht_source']='events'
        for card,tag in [('Yellow','yellow'),('YellowRed','yellowred'),('Red','red')]:
            for side,flag in [('home',True),('away',False)]:
                rec[f'ev_{tag}_{side}']=sum(1 for e in evs if e.get('type')=='Card' and e.get('card')==card and bool(e.get('isHome'))==flag)
                rec[f'ht_ev_{tag}_{side}']=sum(1 for e in evs if e.get('type')=='Card' and e.get('card')==card and bool(e.get('isHome'))==flag and minute(e) is not None and minute(e)<=45)
        for side in ('home','away'):
            rec[f'yellow_{side}']=float(rec[f'ev_yellow_{side}'])
            rec[f'yellowred_{side}']=float(rec[f'ev_yellowred_{side}'])
            rec[f'red_{side}']=float(rec[f'ev_red_{side}']+rec[f'ev_yellowred_{side}'])
        for k in STAT_KEYS:
            for period, prefix in [('All',''),('FirstHalf','fh_'),('SecondHalf','sh_')]:
                h,a=g(period,k); rec[f'{prefix}{k}_home']=h; rec[f'{prefix}{k}_away']=a
        rec['stats_yellow_home']=rec['yellow_cards_home']; rec['stats_yellow_away']=rec['yellow_cards_away']
        rec['stats_red_home']=rec['red_cards_home']; rec['stats_red_away']=rec['red_cards_away']
        ref=(((content.get('matchFacts') or {}).get('infoBox') or {}).get('Referee') or {}).get('text')
        rec['referee']=ref
        periods=((content.get('stats') or {}).get('Periods') or {})
        rec['has_stats_all']=int(('All','corners') in fs); rec['has_stats_half']=int(('FirstHalf','corners') in fs)
        rec['has_shotmap']=int(bool((content.get('shotmap') or {}).get('shots'))); rec['n_shotmap_shots']=len((content.get('shotmap') or {}).get('shots') or [])
        rec['has_events']=int(bool(evs)); rec['has_xg']=int(any(rec.get(f'{k}_home') is not None for k in ('expected_goals','expected_goals_open_play')))
        rec['xg_home']=None; rec['xg_away']=None; rec['sm_shots_home']=0; rec['sm_shots_away']=0
        out.append(rec)
    if not out: raise RuntimeError('No Slovak matches found')
    assert len(set(r['match_id'] for r in out))==len(out)
    fields=list(out[0]);
    with open(OUT/'sk_matches.csv','w',newline='') as f: csv.DictWriter(f,fieldnames=fields).writeheader(); csv.DictWriter(f,fieldnames=fields).writerows(out)
    tm=[]
    for r in out:
        for side,opp in [('home','away'),('away','home')]:
            t={'match_id':r['match_id'],'season':r['season'],'date':r['date'],'phase':r['phase'],'included':r['included'],
               'team_id':r[f'{side}_team_id'],'team':r[f'{side}_team'],'venue':side,
               'goals_for':r[f'{side}_goals'],'goals_against':r[f'{opp}_goals']}
            for k in ['total_shots','ShotsOnTarget','corners','BallPossesion','touches_opp_box','big_chance']:
                t[f'{k}_for']=r.get(f'{k}_{side}'); t[f'{k}_against']=r.get(f'{k}_{opp}')
            for k in ['yellow','yellowred','red']: t[f'{k}_for']=r[f'{k}_{side}']; t[f'{k}_against']=r[f'{k}_{opp}']
            t['referee']=r['referee']; tm.append(t)
    tf=list(tm[0])
    with open(OUT/'sk_team_matches.csv','w',newline='') as f: csv.DictWriter(f,fieldnames=tf).writeheader(); csv.DictWriter(f,fieldnames=tf).writerows(tm)
    latest={}
    for r in out:
        for side in ('home','away'): latest[r[f'{side}_team_id']]=r[f'{side}_team']
    with open(OUT/'sk_teams.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['team_id','canonical_name']); w.writeheader(); w.writerows({'team_id':k,'canonical_name':v} for k,v in sorted(latest.items()))
    print(f'matches={len(out)} included={sum(r["included"] for r in out)} team_rows={len(tm)} teams={len(latest)}')

if __name__=='__main__': main()
