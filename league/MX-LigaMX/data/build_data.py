"""Build the Liga MX regular-phase modelling tables from the FotMob warehouse."""
import csv, json, math, sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve(); ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'league'))
from jleague_lib import flat_stats, stats_conflicts, shots_of, events_of, ht_from_events
INDEX=ROOT/'data_enrichment/fotmob_world_index.csv'; OUT=HERE.parent
BLOCK_ORDER=["2021/2022 - Apertura","2021/2022 - Clausura","2022/2023 - Apertura","2022/2023 - Clausura","2023/2024 - Apertura","2023/2024 - Clausura","2024/2025 - Apertura","2024/2025 - Clausura","2025/2026 - Apertura","2025/2026 - Clausura"]
INCOMPLETE="2026/2027 - Apertura"
BASE_KEYS=["total_shots","ShotsOnTarget","ShotsOffTarget","blocked_shots","shots_inside_box","shots_outside_box","big_chance","touches_opp_box","corners","yellow_cards","red_cards","fouls","Offsides","keeper_saves","BallPossesion"]
XG_KEYS=["expected_goals","expected_goals_open_play","expected_goals_set_play","expected_goals_non_penalty","expected_goals_on_target"]
HALF_KEYS=["total_shots","ShotsOnTarget","corners","yellow_cards","red_cards","expected_goals","fouls"]
def load(p): return json.loads(Path(p).read_text())
def nan(): return float('nan')
def score(x):
 s=((x.get('header') or {}).get('status') or {}).get('scoreStr')
 if isinstance(s,str):
  try:
   a,b=s.replace('–','-').split('-')[:2]; return int(a.strip()),int(b.strip())
  except ValueError: pass
 t=(x.get('header') or {}).get('teams') or []
 return (int(t[0]['score']),int(t[1]['score'])) if len(t)>=2 and t[0].get('score') is not None and t[1].get('score') is not None else (nan(),nan())
def phase(x):
 r=str((x.get('general') or {}).get('matchRound') or '')
 if r.isdigit() and 1<=int(r)<=17:return 'regular'
 if r:return 'playoff'
 raise ValueError(f'unclassified round label: {r!r}')
def referee_city(c):
 ib=(c.get('matchFacts') or {}).get('infoBox') or {}; rr=ib.get('Referee') or {}; st=ib.get('Stadium') or {}
 return ((rr.get('text') or '').strip() or None,(st.get('city') or '').strip() or None)
def event_yellows(c):
 z=[0,0]
 for e in events_of(c):
  if e.get('type')=='Card' and e.get('card')=='Yellow' and e.get('isHome') is not None:z[0 if e['isHome'] else 1]+=1
 return z
def main():
 with INDEX.open(newline='') as f: idx=[r for r in csv.DictReader(f) if r.get('league_id')=='230']
 canon={}
 for ir in idx:
  x=load(ROOT/ir['path'])
  for t in (x.get('header') or {}).get('teams') or []:
   if t.get('id') is not None and t.get('name') and (t['id'] not in canon or ir['date']>=canon[t['id']][0]):canon[t['id']]=(ir['date'],t['name'])
 regular=[]; playoffs=0; incomplete=0
 for ir in idx:
  x=load(ROOT/ir['path'])
  ph=phase(x)
  if ir['season']==INCOMPLETE: incomplete+=1
  if ph=='regular':regular.append(ir)
  else:playoffs+=1
 rows=[]; team_rows=[]; cards={}; stats_conf=0
 for ir in regular:
  x=load(ROOT/ir['path'])
  h,a=(x.get('header') or {}).get('teams') or [{},{}]; hid,aid=h.get('id'),a.get('id'); hn=canon.get(hid,('',h.get('name')))[1]; an=canon.get(aid,('',a.get('name')))[1]
  c=x.get('content') or {}; st=flat_stats(c); stats_conf+=stats_conflicts(c); ev=events_of(c); sh=[q for q in shots_of(c) if q.get('period')!='PenaltyShootout']; fh=ht_from_events(c); hg,ag=score(x); ref,city=referee_city(c)
  sm={k:[0,0] for k in ('shots','sot','sot_incl_blocked','xg','xgot','xgot_n','xgot_n_on','xgot_n_off')}
  for q in sh:
   if q.get('teamId') not in (hid,aid):continue
   side=0 if q.get('teamId')==hid else 1; sm['shots'][side]+=1
   if q.get('isOnTarget') is True:sm['sot_incl_blocked'][side]+=1
   if q.get('isOnTarget') is True and q.get('isBlocked') is not True:sm['sot'][side]+=1
   if q.get('expectedGoals') is not None:sm['xg'][side]+=float(q['expectedGoals'])
   if q.get('expectedGoalsOnTarget') is not None:
    sm['xgot'][side]+=float(q['expectedGoalsOnTarget']);sm['xgot_n'][side]+=1;sm['xgot_n_on' if q.get('isOnTarget') is True else 'xgot_n_off'][side]+=1
  all_keys={k for p,k in st if p=='All'}; evy=event_yellows(c); red=st.get(('All','red_cards'),(nan(),nan()));
  r={'match_id':ir['match_id'],'league':'MX-LigaMX','season':ir['season'],'block_idx':(BLOCK_ORDER.index(ir['season']) if ir['season'] in BLOCK_ORDER else len(BLOCK_ORDER)),'season_start':int(ir['season'][:4]),'date':ir['date'],'kickoff_utc':((x.get('header') or {}).get('status') or {}).get('utcTime',''),'round':str((x.get('general') or {}).get('matchRound')),'phase':'regular','home_team_id':hid,'home_team':hn,'away_team_id':aid,'away_team':an,'coverage_level':(x.get('general') or {}).get('coverageLevel'),'home_goals':hg,'away_goals':ag,'ht_home_goals':fh[0] if fh else nan(),'ht_away_goals':fh[1] if fh else nan(),'ht_source':'events' if fh is not None else 'none','ev_goals_home':sum(e.get('type')=='Goal' and e.get('isHome') is True for e in ev),'ev_goals_away':sum(e.get('type')=='Goal' and e.get('isHome') is False for e in ev),'referee':ref,'stadium_city':city,'has_events':bool(ev),'has_lineup':bool(c.get('lineup')),'has_player_stats':bool(c.get('playerStats')),'has_stats_all':any(p=='All' for p,k in st),'has_stats_half':any(p in ('FirstHalf','SecondHalf') for p,k in st),'has_shotmap':bool(sh),'n_shootout_shots':len(shots_of(c))-len(sh),'score_events_mismatch':False,'cards_source':'events' if ev else 'none'}
  r['score_events_mismatch']=not math.isnan(hg) and (r['ev_goals_home']!=hg or r['ev_goals_away']!=ag)
  for k in XG_KEYS+BASE_KEYS:
   v=st.get(('All',k),(nan(),nan()));r[k+'_home'],r[k+'_away']=v
  for p,pre in (('FirstHalf','fh'),('SecondHalf','sh')):
   for k in HALF_KEYS:r[f'{pre}_{k}_home'],r[f'{pre}_{k}_away']=st.get((p,k),(nan(),nan()))
  y=st.get(('All','yellow_cards'),(nan(),nan()));r['yellow_home'],r['yellow_away']=evy;r['yellow_cards_home'],r['yellow_cards_away']=y;r['red_home'],r['red_away']=red
  fy=[0,0]
  for e in ev:
   if e.get('type')=='Card' and e.get('card')=='Yellow' and e.get('isHome') is not None and e.get('time') is not None and e['time']<=45:fy[0 if e['isHome'] else 1]+=1
  r['fh_yellow_events_home'],r['fh_yellow_events_away']=fy
  for k,v in sm.items():r[f'sm_{k}_home'],r[f'sm_{k}_away']=v
  rows.append(r)
  for side,tid,nm,oid,onm in (('home',hid,hn,aid,an),('away',aid,an,hid,hn)):
   tr={'match_id':ir['match_id'],'season':ir['season'],'block_idx':r['block_idx'],'date':ir['date'],'team_id':tid,'team':nm,'opponent_id':oid,'opponent':onm,'home_away':side}
   for k,v in r.items():
    if k.endswith('_home'):tr[k[:-5]]=v if side=='home' else r.get(k[:-5]+'_away')
    elif k.endswith('_away') and k[:-5] not in tr:tr[k[:-5]]=v if side=='away' else r.get(k[:-5]+'_home')
   for k in ('ev_goals','expected_goals','total_shots','ShotsOnTarget','corners','yellow','yellow_cards','red','red_cards','fouls','big_chance','touches_opp_box','BallPossesion'):
    tr[k+'_against']=r.get(k+('_away' if side=='home' else '_home'),nan())
   team_rows.append(tr)
  cards.setdefault(ir['season'],[0,0,0,0]);cards[ir['season']][0]+=sum(evy);cards[ir['season']][1]+=sum(v for v in y if v==v);cards[ir['season']][2]+=int(sum(evy)==sum(v for v in y if v==v));cards[ir['season']][3]+=1
 rows.sort(key=lambda z:(z['date'],int(z['match_id'])));team_rows.sort(key=lambda z:(z['date'],int(z['match_id']),z['home_away']))
 def write(p,data):
  keys=[]
  for z in data:
   for k in z:
    if k not in keys:keys.append(k)
  with p.open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(data)
 write(OUT/'mx_matches.csv',rows);write(OUT/'team_matches.csv',team_rows)
 per=dict(Counter(r['season'] for r in rows)); assert all(per.get(s,0)>=153 for s in BLOCK_ORDER);assert len(rows)>=1530 and len(team_rows)==2*len(rows) and len({r['match_id'] for r in rows})==len(rows)
 agreement={s:{'stats_total':v[1],'events_total':v[0],'per_match_agreement_count':v[2],'n_matches':v[3]} for s,v in cards.items() if s in BLOCK_ORDER[:9]}
 print(json.dumps({'index_rows':len(idx),'regular_rows':len(rows),'playoffs_excluded':playoffs,'incomplete_index_rows':incomplete,'team_rows':len(team_rows),'per_tournament_regular':per,'cards_agreement_regular_dev':agreement,'stats_conflicts_checked':stats_conf},indent=2))
if __name__=='__main__':main()
