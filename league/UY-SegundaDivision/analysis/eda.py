"""UY Segunda inventory and dev-only scores EDA.  2026 is inventory/levels only."""
import csv,json
from collections import Counter
from pathlib import Path
import numpy as np,pandas as pd
HERE=Path(__file__).parent; ROOT=HERE.parents[2]
IDX=ROOT/'data_enrichment/fotmob_world_index_uy.csv'; RAW=ROOT/'data_enrichment/fotmob_world/Uruguay/Segunda Division'
M=pd.read_csv(HERE.parent/'data'/'uy_segunda_matches.csv'); M.season=M.season.astype(str); M['tot_goals']=M.home_goals+M.away_goals
TM=pd.read_csv(HERE.parent/'data'/'uy_segunda_team_matches.csv'); TM.season=TM.season.astype(str)
idx=[r for r in csv.DictReader(open(IDX)) if r['league_id']=='9122']
def payload(r):
 d=json.load(open(ROOT/r['path'])); c=d.get('content') or {}; st=(d.get('header') or {}).get('status') or {}; ev=(((c.get('matchFacts') or {}).get('events') or {}).get('events') or []); cards=Counter(e.get('card') for e in ev if e.get('type')=='Card'); per=((c.get('stats') or {}).get('Periods') or {}); info=((c.get('matchFacts') or {}).get('infoBox') or {}); ref=((info.get('Referee') or {}).get('text') or '').strip(); lu=c.get('lineup') or {}
 return {'season':str(r['season']),'finished':bool(st.get('finished')),'score':bool(st.get('scoreStr')),'score_zero':r.get('score')=='0-0','stats':bool(per),'shotmap':bool((c.get('shotmap') or {}).get('shots')),'splits':any(x in ('FirstHalf','SecondHalf') for x in per),'events':bool(ev),'referee':bool(ref),'lineup':any(len((lu.get(x) or {}).get('starters') or [])==11 for x in ('homeTeam','awayTeam')),'et':Counter(e.get('type') for e in ev),'cards':cards,'card_n':sum(cards.values())}
raw=[payload(r) for r in idx]
inv={'total_payloads':len(raw),'total_matches':len(M),'finished_only_rule':'header.status.finished == true; 53 unfinished 2021 0-0 placeholders dropped','seasons':{}}
for s in sorted({x['season'] for x in raw}):
 q=[x for x in raw if x['season']==s]; d=M[M.season==s]; et=Counter(); cards=Counter()
 for x in q: et.update(x['et']); cards.update(x['cards'])
 inv['seasons'][s]={'payloads':len(q),'finished':sum(x['finished'] for x in q),'unfinished':sum(not x['finished'] for x in q),'unfinished_score_0_0':sum((not x['finished']) and x['score_zero'] for x in q),'score_present':sum(x['score'] for x in q),'stats':sum(x['stats'] for x in q),'shotmap':sum(x['shotmap'] for x in q),'period_splits':sum(x['splits'] for x in q),'events':sum(x['events'] for x in q),'referee':sum(x['referee'] for x in q),'lineup':sum(x['lineup'] for x in q),'event_type_counts':dict(et),'card_type_counts':dict(cards),'card_match_distribution':dict(Counter(x['card_n'] for x in q)),'teams_finished':int(len(set(d.home_team_id)|set(d.away_team_id))),'goals_finished':int(d.tot_goals.sum()),'goals_per_match_finished':float(d.tot_goals.mean())}
inv['name_variants']={'7808':['Fenix','Fénix'],'4660':['Paysandu','Paysandú']}; (HERE/'inventory_summary.json').write_text(json.dumps(inv,indent=1))
OUT={'seasons':{}}
for s,d in inv['seasons'].items():
 x=M[M.season==s]; OUT['seasons'][s]={**{k:d[k] for k in ('payloads','finished','unfinished','stats','shotmap','period_splits','events','referee','lineup','teams_finished')},'goals_pm_finished':d['goals_per_match_finished'],'home_win_rate':float((x.home_goals>x.away_goals).mean()),'draw_rate':float((x.home_goals==x.away_goals).mean()),'away_win_rate':float((x.home_goals<x.away_goals).mean()),'ou25_over_rate':float((x.tot_goals>2.5).mean())}
dev=M[M.season.isin(['2021','2022','2023','2024','2025'])]; scored=M[M.season.isin(['2022','2023','2024','2025'])]
OUT['pooled_eval']={'n':len(scored),'home_win_rate':float((scored.home_goals>scored.away_goals).mean()),'draw_rate':float((scored.home_goals==scored.away_goals).mean()),'away_win_rate':float((scored.home_goals<scored.away_goals).mean()),'ou25_over_rate':float((scored.tot_goals>2.5).mean()),'goals_pm':float(scored.tot_goals.mean())}
def rel(col):
 if col not in TM.columns: return None,0
 d=TM[TM.season.isin(['2021','2022','2023','2024','2025'])].sort_values(['team_id','date','match_id']); d=d[d[col].notna()].copy(); d['i']=d.groupby('team_id').cumcount(); a=d[d.i%2==0].groupby('team_id')[col].mean(); b=d[d.i%2==1].groupby('team_id')[col].mean(); j=pd.concat([a,b],axis=1).dropna(); return (float(j.iloc[:,0].corr(j.iloc[:,1])) if len(j)>=3 else None),len(j)
OUT['trait_reliability_dev']={}
for n,c in [('goals_for','goals_for'),('goals_against','goals_against'),('sot','sot_for'),('corners','corners_for'),('shots','shots_for'),('yellows','yellow_for')]:
 r,nj=rel(c); OUT['trait_reliability_dev'][n]={'split_half_r':r,'n_teams':nj,'note':None if nj else 'target absent; n=0'}
OUT['season_to_season_dev']={}
for n,c in [('goals_for','goals_for'),('goals_against','goals_against')]:
 p=TM[TM.season.isin(['2021','2022','2023','2024','2025'])].groupby(['season','team_id'])[c].mean().unstack(0); z=[]
 for a,b in zip(sorted(p.columns),sorted(p.columns)[1:]):
  j=p[[a,b]].dropna(); z.append({'seasons':f'{a}-{b}','r':float(j[a].corr(j[b])) if len(j)>=3 else None,'n_teams':len(j)})
 OUT['season_to_season_dev'][n]=z
g=dev[dev.has_events & ~dev.score_events_mismatch]; hs={'rule':'event minute <=45 is first half; added-time field unavailable','share_1h':float(g.goals_1h_total.sum()/g.tot_goals.sum()),'n_goals':int(g.tot_goals.sum()),'n_matches':len(g),'by_season':{s:{'share_1h':float(x.goals_1h_total.sum()/x.tot_goals.sum()),'n_goals':int(x.tot_goals.sum())} for s,x in g.groupby('season')}}; z=g[g.tot_goals>0]; hs['per_match_share_variance']=float((z.goals_1h_total/z.tot_goals).var());
q=TM[TM.season.isin(['2021','2022','2023','2024','2025'])].copy(); q=q[q.goals_for>0]; q['share']=q.ht_goals_for/q.goals_for; q=q.dropna(subset=['share']); q['i']=q.sort_values(['team_id','date','match_id']).groupby('team_id').cumcount(); a=q[q.i%2==0].groupby('team_id').share.mean(); b=q[q.i%2==1].groupby('team_id').share.mean(); j=pd.concat([a,b],axis=1).dropna(); hs['team_share_split_half_r']=float(j.iloc[:,0].corr(j.iloc[:,1])) if len(j)>=3 else None; hs['team_share_n']=len(j); hs['team_share_between_variance']=float(q.groupby('team_id').share.mean().var()); hs['team_share_within_variance']=float(q.assign(center=q.groupby('team_id').share.transform('mean')).eval('(share-center)**2').mean())
# De-confounded check: the naive career r above mixes seasons whose league-wide
# 1H shares differ (0.380-0.518), inflating any team-level correlation.
# Within team-season odd/even split-half removes the season mix.
q2=q.sort_values(['team_id','season','date','match_id']).copy(); q2['i2']=q2.groupby(['team_id','season']).cumcount(); a2=q2[q2.i2%2==0].groupby(['team_id','season']).share.mean(); b2=q2[q2.i2%2==1].groupby(['team_id','season']).share.mean(); j2=pd.concat([a2,b2],axis=1).dropna(); hs['team_share_split_half_within_season_r']=float(j2.iloc[:,0].corr(j2.iloc[:,1])) if len(j2)>=3 else None; hs['team_share_within_season_n']=len(j2)
q3=q.copy(); q3['share_dm']=q3['share']-q3.groupby('season')['share'].transform('mean'); q3=q3.sort_values(['team_id','date','match_id']); q3['i3']=q3.groupby('team_id').cumcount(); a3=q3[q3.i3%2==0].groupby('team_id').share_dm.mean(); b3=q3[q3.i3%2==1].groupby('team_id').share_dm.mean(); j3=pd.concat([a3,b3],axis=1).dropna(); hs['team_share_split_half_season_demeaned_r']=float(j3.iloc[:,0].corr(j3.iloc[:,1])) if len(j3)>=3 else None; hs['team_share_season_demeaned_n']=len(j3); OUT['halves_dev']=hs
AUF={'2022':{1835,1838,188312},'2023':{924934,2220,2221},'2024':{395613,1319664,4669},'2025':{7808,4421,1833},'2026':{4424,6381,4669}}; trans=[]; tier3={}; prev=set()
for s in sorted(M.season.unique()):
 cur=set(M[M.season==s].home_team_id)|set(M[M.season==s].away_team_id); ents=cur-prev if prev else set(); tier3[s]=len(ents-AUF.get(s,set()))
 if s in AUF and s <= '2025':
  for tid in AUF[s]:
   x=TM[(TM.season==s)&(TM.team_id==tid)]
   if len(x): trans.append({'season':s,'team_id':int(tid),'team':str(x.team.iloc[0]),'gf_diff':float(x.goals_for.mean()-TM[TM.season==s].goals_for.mean()),'ga_diff':float(x.goals_against.mean()-TM[TM.season==s].goals_against.mean())})
 prev=cur
gf=[x['gf_diff'] for x in trans]; ga=[x['ga_diff'] for x in trans]; mu=float((scored.home_goals.sum()+scored.away_goals.sum())/(2*len(scored)))
offsets={}
for target in ['2022','2023','2024','2025']:
 prior=[x for x in trans if x['season']<target]; mg=np.mean([x['gf_diff'] for x in prior]) if prior else 0.; ma=np.mean([x['ga_diff'] for x in prior]) if prior else 0.; offsets[target]={'mean_gf_diff_prior':float(mg),'mean_ga_diff_prior':float(ma),'log_gf':float(np.log((mu+mg)/mu)),'log_ga':float(np.log((mu+ma)/mu)),'n_prior':len(prior)}
OUT['movers_dev']={'transitions':trans,'n':len(trans),'mean_gf_diff':float(np.mean(gf)),'mean_ga_diff':float(np.mean(ga)),'gf_negative':sum(x<0 for x in gf),'gf_positive':sum(x>0 for x in gf),'ga_negative':sum(x<0 for x in ga),'ga_positive':sum(x>0 for x in ga),'tier3_entrants_by_season':tier3,'baseline':'same-season finished Segunda team-match mean','frozen_log_offsets_by_target':offsets}
def pick(v):
 r={str(x):float((v>x).mean()) for x in (1.5,2.5,3.5)}; return {'over_rates':r,'primary':min(r,key=lambda k:abs(r[k]-.5)),'n':len(v)}
OUT['lines']={'goals_ou':pick(scored.tot_goals),'stats_markets':None}; OUT['dev_windows']={'warm_up':['2021'],'evaluation':['2022','2023','2024','2025'],'n_evaluation':len(scored)}; OUT['card_events_dev']={k:int(sum(inv['seasons'][s]['card_type_counts'].get(k,0) for s in ['2021','2022','2023','2024','2025'])) for k in ('Yellow','Red','YellowRed')}; OUT['dev_levels_note']='Fitting-relevant numbers use finished 2021-2025 only; 2026 inventory/levels display only.'
(HERE/'eda_summary.json').write_text(json.dumps(OUT,indent=1,allow_nan=False)); print(json.dumps({'reliability':OUT['trait_reliability_dev'],'halves':OUT['halves_dev'],'movers':OUT['movers_dev'],'lines':OUT['lines']},indent=1))
