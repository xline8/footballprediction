"""Reproducible content-based inventory for FotMob league 249."""
import csv, json
from collections import Counter, defaultdict
from pathlib import Path
BASE = Path(__file__).resolve().parents[3]
WAREHOUSE = Path(__import__('sys').argv[1]).resolve() if len(__import__('sys').argv) > 1 else BASE
INDEX = BASE / 'data_enrichment' / 'fotmob_world_index.csv'
OUT = Path(__file__).resolve().parent / 'inventory_summary.json'
SEASONS = ['2021/2022','2022/2023','2023/2024','2024/2025','2025/2026','2026/2027']

def has_xg(stats):
    if not isinstance(stats, dict): return False
    blob = json.dumps(stats).lower()
    return 'expected_goals' in blob or 'xg' in blob

def main():
    irs = [r for r in csv.DictReader((BASE/'data_enrichment/fotmob_world_index.csv').open()) if r['league_id']=='249']
    seasons = defaultdict(list); names=defaultdict(set); teams=defaultdict(set); league_names=Counter(); parent=Counter(); phases=Counter()
    awarded=[]; rows=[]
    for ir in irs:
        d=json.loads((WAREHOUSE/ir['path']).read_text()); g,h,c=d['general'],d['header'],d['content']; mf=c.get('matchFacts') or {}
        ev=((mf.get('events') or {}).get('events') or []); cards=[e for e in ev if e.get('type')=='Card']
        shot=c.get('shotmap') or {}; stats=c.get('stats'); lineup=c.get('lineup')
        ref=(mf.get('infoBox') or {}).get('Referee') or {}
        row={'match_id':ir['match_id'],'season':ir['season'],'date':ir['date'],'score':True,
             'stats':stats is not None,'shotmap':bool(shot.get('shots')),'xg':has_xg(stats) or has_xg(shot),
             'lineup':lineup is not None,'referee':bool(ref.get('text')),'events':bool(ev),
             'half':sum(e.get('type')=='Half' for e in ev)>0,'cards':bool(cards),'yellow':sum(e.get('card')=='Yellow' for e in cards),
             'red':sum(e.get('card')=='Red' for e in cards),'yellowred':sum(e.get('card')=='YellowRed' for e in cards),
             'goals':sum(e.get('type')=='Goal' for e in ev),'teams':[h['id'] for h in h['teams']],
             'team_names':[h['name'] for h in h['teams']], 'league_name':g['leagueName'], 'parent':g['parentLeagueId'],
             'round':g.get('leagueRoundName') or '', 'awarded':bool(h['status'].get('awarded'))}
        rows.append(row); seasons[ir['season']].append(row); league_names[g['leagueName']]+=1; parent[str(g['parentLeagueId'])]+=1; phases['regular']+=1
        for i,n in zip(row['teams'],row['team_names']): teams[ir['season']].add(i); names[i].add(n)
        if row['awarded']: awarded.append(ir['match_id'])
    entrants={}; prior=set()
    for s in SEASONS:
        ids=teams[s]; entrants[s]=sorted(ids-prior, key=int); prior |= ids
    out={'league':'MK-PrvaLiga','fotmob_id':249,'index_rows':len(irs),'payloads_present':len(rows),
         'parentLeagueId_distribution':dict(parent),'leagueName_distribution':dict(league_names),
         'phase_distribution':dict(phases),'league_scope_note':'single table, all rounds, regular phase',
         'team_count_total':len(set().union(*(teams[s] for s in SEASONS))),
         'team_counts_by_season':{s:len(teams[s]) for s in SEASONS},
         'team_ids_by_season':{s:sorted(teams[s],key=int) for s in SEASONS},
         'team_name_variants':{str(k):sorted(v) for k,v in names.items() if len(v)>1},
         'entrants_by_team_id':{s:sorted(entrants[s],key=int) for s in SEASONS},
         'awarded_match_ids':sorted(awarded,key=int),'date_ranges':{s:[min(r['date'] for r in seasons[s]),max(r['date'] for r in seasons[s])] for s in SEASONS},
         'rounds_by_season':{s:sorted({r['round'] for r in seasons[s]},key=lambda x:int(x) if str(x).isdigit() else str(x)) for s in SEASONS}, 'seasons':{}}
    for s in SEASONS:
        rs=seasons[s]; out['seasons'][s]={'n':len(rs),'teams':len(teams[s]),'round_count':len({r['round'] for r in rs}),
          'date_range':out['date_ranges'][s], 'model_rows':sum(not r['awarded'] for r in rs),'awarded':sum(r['awarded'] for r in rs),
          'coverage':{k:sum(r[k] for r in rs) for k in ['score','stats','shotmap','xg','lineup','referee','events','half','cards']},
          'eventless':sum(not r['events'] for r in rs),'card_event_rows':sum(r['cards'] for r in rs),
          'card_events':sum(r['red']+r['yellowred']+r['yellow'] for r in rs), 'red_events':sum(r['red'] for r in rs),
          'yellowred_events':sum(r['yellowred'] for r in rs),'yellow_events':sum(r['yellow'] for r in rs),
          'goal_events':sum(r['goals'] for r in rs),'lineup_nonnull':sum(r['lineup'] for r in rs)}
    out['events_total']={k:sum(r[k] for r in rows) for k in ['goals','half','cards','yellow','red','yellowred']}
    out['content_absence_zero_counts_by_season']={s:{k:len(seasons[s])-sum(r[k] for r in seasons[s]) for k in ['stats','shotmap','xg','lineup','referee','yellow']} for s in SEASONS}
    # The sibling-league check is performed against the complete index, not only payload rows.
    allidx=list(csv.DictReader(INDEX.open())); nm=sorted({r['league_id'] for r in allidx if r['country']=='North Macedonia'})
    out['north_macedonia_league_ids_in_index']=nm; out['only_north_macedonia_league_is_249']=(nm==['249'])
    out['has_playoff_distribution']=dict(Counter(str(json.loads((WAREHOUSE/r['path']).read_text())['content'].get('hasPlayoff')) for r in irs))
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
