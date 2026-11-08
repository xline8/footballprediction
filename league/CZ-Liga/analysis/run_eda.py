import csv,json,math,statistics
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent; M=list(csv.DictReader(open(HERE.parent/'data/cz_matches.csv'))); INC=[r for r in M if r['included']=='1']; DEV=[r for r in INC if r['season'] in {'2021/2022','2022/2023','2023/2024','2024/2025'}]
def f(r,k):
 v=r.get(k); return None if v in (None,'','None') else float(v)
def avg(x): return round(statistics.mean(x),6) if x else None
def cor(x,y):
 if len(x)<2:return None
 a=statistics.mean(x);b=statistics.mean(y); den=math.sqrt(sum((u-a)**2 for u in x)*sum((v-b)**2 for v in y));return round(sum((u-a)*(v-b) for u,v in zip(x,y))/den,6) if den else None
def tot(r,k):
 a,b=f(r,k+'_home'),f(r,k+'_away');return None if a is None or b is None else a+b
def rel(getter):
 d=defaultdict(list)
 for r in DEV:
  for s in ('home','away'): d[(r['season'],r[f'{s}_team_id'])].append(getter(r,s))
 x=[];y=[]
 for z in d.values():
  z=[v for v in z if v is not None]
  if len(z)>=10:x.append(statistics.mean(z[0::2]));y.append(statistics.mean(z[1::2]))
 return {'r':cor(x,y),'n_units':len(x)}
levels={}
for season in sorted(set(r['season'] for r in INC)):
 rs=[r for r in INC if r['season']==season];levels[season]={'n':len(rs),'goals':avg([f(r,'home_goals')+f(r,'away_goals') for r in rs]),'sot':avg([tot(r,'ShotsOnTarget') for r in rs if tot(r,'ShotsOnTarget') is not None]),'corners':avg([tot(r,'corners') for r in rs if tot(r,'corners') is not None]),'total_shots':avg([tot(r,'total_shots') for r in rs if tot(r,'total_shots') is not None]),'yellows':avg([f(r,'yellow_home')+f(r,'yellow_away') for r in rs])}
T={'goals_for':lambda r,s:f(r,s+'_goals'),'goals_against':lambda r,s:f(r,('away' if s=='home' else 'home')+'_goals'),'sot_for':lambda r,s:f(r,'ShotsOnTarget_'+s),'sot_against':lambda r,s:f(r,'ShotsOnTarget_'+('away' if s=='home' else 'home')),'corners_for':lambda r,s:f(r,'corners_'+s),'corners_against':lambda r,s:f(r,'corners_'+('away' if s=='home' else 'home')),'yellows_for':lambda r,s:f(r,'yellow_'+s),'yellows_against':lambda r,s:f(r,'yellow_'+('away' if s=='home' else 'home')),'possession_for':lambda r,s:f(r,'BallPossesion_'+s),'possession_against':lambda r,s:f(r,'BallPossesion_'+('away' if s=='home' else 'home')),'total_shots_for':lambda r,s:f(r,'total_shots_'+s),'total_shots_against':lambda r,s:f(r,'total_shots_'+('away' if s=='home' else 'home'))}
reliabilities={k:rel(v) for k,v in T.items()}
refs=defaultdict(list)
for r in DEV:
 if r['referee']:refs[r['referee']].append(f(r,'yellow_home')+f(r,'yellow_away'))
x=[];y=[]
for z in refs.values():
 if len(z)>=20:x.append(statistics.mean(z[0::2]));y.append(statistics.mean(z[1::2]))
ref={'r':cor(x,y),'n_referees':len(x),'coverage':round(sum(bool(r['referee']) for r in DEV)/len(DEV),6)}
g1=sum(f(r,'ht_home_goals')+f(r,'ht_away_goals') for r in DEV); ga=sum(f(r,'home_goals')+f(r,'away_goals') for r in DEV); c1=sum(f(r,'ht_ev_yellow_home')+f(r,'ht_ev_yellow_away') for r in DEV);ca=sum(f(r,'yellow_home')+f(r,'yellow_away') for r in DEV)
lines={}
for name,key,cands in [('sot','ShotsOnTarget',[7.5,8.5,9.5]),('corners','corners',[8.5,9.5,10.5]),('cards','yellow',[3.5,4.5,5.5])]:
 rates={str(q):round(sum(tot(r,key)>q for r in DEV if tot(r,key)!=None)/sum(tot(r,key)!=None for r in DEV),6) for q in cands};lines[name]={'rates':rates,'primary':min(cands,key=lambda q:abs(rates[str(q)]-.5))}
lines['goals']={'primary':'OU2.5','over_rate':round(sum(f(r,'home_goals')+f(r,'away_goals')>2.5 for r in DEV)/len(DEV),6)}
out={'counts':{'all_matches':len(M),'included':len(INC),'excluded_placement':len(M)-len(INC),'included_by_season':{s:sum(r['season']==s for r in INC) for s in sorted(set(r['season'] for r in INC))},'team_ids':len(set([r['home_team_id'] for r in M]+[r['away_team_id'] for r in M]))},'levels':levels,'reliabilities':reliabilities,'referee_reliability':ref,'halves':{'goals_1h_share':round(g1/ga,6),'yellow_cards_1h_share':round(c1/ca,6),'goals_total':ga,'yellow_total':ca},'primary_lines':lines}
json.dump(out,open(HERE/'eda_numbers.json','w'),indent=2);print(json.dumps(out,indent=2))
