"""Inventory and exploratory diagnostics for the AR Liga Profesional build."""
import csv,json
from pathlib import Path
import numpy as np
def jd(x):
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(np.floating,)):return float(x)
 raise TypeError(type(x).__name__)
HERE=Path(__file__).parent; DATA=HERE.parent/'data'
def rows(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
M=rows(DATA/'ar_matches.csv'); T=rows(DATA/'team_matches.csv')
def f(r,k):
 try:return float(r.get(k,''))
 except (TypeError,ValueError):return np.nan
def mean(a):return float(np.nanmean(a)) if len(a) and np.isfinite(a).any() else None
def ratio(a,b):return float(np.nansum(a)/np.nansum(b)) if np.nansum(b) else None
def corr(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);z=np.isfinite(a)&np.isfinite(b)
 return float(np.corrcoef(a[z],b[z])[0,1]) if z.sum()>2 and np.std(a[z]) and np.std(b[z]) else None
def disp(a):
 a=np.asarray(a,float);a=a[np.isfinite(a)];return float(np.var(a,ddof=1)/np.mean(a)) if len(a)>1 and np.mean(a) else None
def cov(rs,k):return 100*sum(r.get(k)=='True' for r in rs)/len(rs) if rs else None
def split_r(items,fn,seed=90210):
 rng=np.random.default_rng(seed); xs=[];ys=[]
 for _ in range(60):
  x=[];y=[]
  for z in items.values():
   a=np.asarray([fn(q) for q in z],float);a=a[np.isfinite(a)]
   if len(a)<2:continue
   ix=rng.permutation(len(a));n=len(a)//2;x.append(np.mean(a[ix[:n]]));y.append(np.mean(a[ix[n:]]))
  q=corr(x,y)
  if q is not None:xs.append(q)
 x=[];y=[]
 for z in items.values():
  a=np.asarray([fn(q) for q in z],float);a=a[np.isfinite(a)]
  if len(a)>1:x.append(np.mean(a[::2]));y.append(np.mean(a[1::2]))
 return {'r':mean(xs),'n_splits':len(xs),'odd_even_r':corr(x,y)}
def split_r_ratio(items,num,den,seed=90210,min_n=8):
 rng=np.random.default_rng(seed); xs=[]
 for _ in range(60):
  x=[];y=[]
  for z in items.values():
   a=[(f(q,num),f(q,den)) for q in z];a=[(u,v) for u,v in a if np.isfinite(u) and np.isfinite(v) and v>0]
   if len(a)<2*min_n:continue
   ix=rng.permutation(len(a));n=len(a)//2
   x.append(sum(a[i][0] for i in ix[:n])/sum(a[i][1] for i in ix[:n]));y.append(sum(a[i][0] for i in ix[n:])/sum(a[i][1] for i in ix[n:]))
  q=corr(x,y)
  if q is not None:xs.append(q)
 return {'r':mean(xs),'n_splits':len(xs),'method':'ratio_of_sums'}
def levels(rs):
 def v(k):return np.array([f(r,k) for r in rs])
 g=v('home_goals')+v('away_goals');sh=v('total_shots_home')+v('total_shots_away');so=v('ShotsOnTarget_home')+v('ShotsOnTarget_away');co=v('corners_home')+v('corners_away');ye=v('yellow_home')+v('yellow_away');re=v('red_home')+v('red_away');xg=v('expected_goals_home')+v('expected_goals_away')
 return {'n_matches':len(rs),'goals_per_match':mean(g),'home_goals':mean(v('home_goals')),'away_goals':mean(v('away_goals')),'home_draw_away_pct':[100*sum(f(r,'home_goals')>f(r,'away_goals') for r in rs)/len(rs),100*sum(f(r,'home_goals')==f(r,'away_goals') for r in rs)/len(rs),100*sum(f(r,'home_goals')<f(r,'away_goals') for r in rs)/len(rs)],'btts_pct':100*mean((v('home_goals')>0)&(v('away_goals')>0)),'over2_5_pct':100*mean(g>2.5),'total_shots':mean(sh),'sot':mean(so),'corners':mean(co),'yellows':mean(ye),'reds':mean(re),'team_xg':mean(xg),'dispersion_var_mean':{'goals':disp(g),'SOT':disp(so),'corners':disp(co),'cards':disp(ye),'shots':disp(sh)}}
def main():
 seasons=sorted({r['season'] for r in M});inv={};season_levels={}
 for s in seasons:
  rs=[r for r in M if r['season']==s];inv[s]={'n_matches':len(rs),'coverage_pct':{k:cov(rs,k) for k in ('has_stats_all','has_stats_half','has_shotmap','has_events','has_lineup','has_player_stats')},'xg_present_pct':100*sum(np.isfinite(f(r,'expected_goals_home')) for r in rs)/len(rs),'referee_nonnull_pct':100*sum(bool(r['referee']) for r in rs)/len(rs),'touches_opp_box_present_count':sum(np.isfinite(f(r,'touches_opp_box_home')) for r in rs),'score_events_mismatch_count':sum(r['score_events_mismatch']=='True' for r in rs),'distinct_teams':len({r['home_team'] for r in rs}|{r['away_team'] for r in rs}),'date_range':[min(r['date'] for r in rs),max(r['date'] for r in rs)]};season_levels[s]=levels(rs)
  shares={}
  for typ in ('all','on_target','off_target'):
   num=den=0
   for r in rs:
    for side in ('home','away'):
     n=f(r,f'sm_shots_{side}');on=f(r,f'sm_sot_incl_blocked_{side}')
     if typ=='all':den+=n;num+=f(r,f'sm_xgot_n_{side}')
     elif typ=='on_target':den+=on;num+=f(r,f'sm_xgot_n_on_{side}')
     else:den+=n-on;num+=f(r,f'sm_xgot_n_off_{side}')
   shares[typ]={'numerator_xgot_nonnull':num,'denominator_shots':den,'share':num/den if den else None}
  inv[s]['xgot_population_shares']=shares
 groups={}
 for r in T:groups.setdefault(r['team'],[]).append(r)
 groups={k:v for k,v in groups.items() if len(v)>=24};keys={'goals':'ev_goals','shots':'total_shots','SOT':'ShotsOnTarget','corners':'corners','yellows':'yellow_cards','xG':'expected_goals','big_chance':'big_chance','possession':'BallPossesion','box_touches':'touches_opp_box'};rel={}
 for n,k in keys.items():
  rel[n+'_for']=split_r(groups,lambda r,k=k:f(r,k))
  rel[n+'_against']=split_r(groups,lambda r,k=k:f(r,k+'_against'))
 rel.setdefault('ratio_traits',{})['set_play_xg_share']=split_r_ratio(groups,'expected_goals_set_play','expected_goals')
 rel['ratio_traits']['xg_per_shot']=split_r_ratio(groups,'sm_xg','sm_shots')
 rel['ratio_traits']['finishing_goals_minus_xg']=split_r(groups,lambda r:f(r,'ev_goals')-f(r,'expected_goals'))
 rel['ratio_traits']['on_target_rate']=split_r_ratio(groups,'ShotsOnTarget','total_shots')
 rel['ratio_traits']['xgot_per_shot_attacking']=split_r_ratio(groups,'sm_xgot','sm_xgot_n')
 g25={k:[q for q in v if q['date']>='2025-01-01'] for k,v in groups.items()};g25={k:v for k,v in g25.items() if len(v)>=24}
 rel['ratio_traits']['xgot_per_shot_restricted_2025']=split_r_ratio(g25,'sm_xgot','sm_xgot_n')
 halves={};mk={'goals':('ht_home_goals','ht_away_goals','home_goals','away_goals'),'SOT':('fh_ShotsOnTarget_home','fh_ShotsOnTarget_away','ShotsOnTarget_home','ShotsOnTarget_away'),'corners':('fh_corners_home','fh_corners_away','corners_home','corners_away'),'total_shots':('fh_total_shots_home','fh_total_shots_away','total_shots_home','total_shots_away'),'yellows':('fh_yellow_events_home','fh_yellow_events_away','yellow_home','yellow_away')}
 for n,(a,b,c,d) in mk.items():
  if n=='goals':
   z=[r for r in M if np.isfinite(f(r,'fh_corners_home')) and np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
  else:
   z=[r for r in M if np.isfinite(f(r,a)) and np.isfinite(f(r,b)) and f(r,c)+f(r,d)>0]
  p=sum(f(r,a)+f(r,b) for r in z)/sum(f(r,c)+f(r,d) for r in z) if z else None;s=np.array([(f(r,a)+f(r,b))/(f(r,c)+f(r,d)) for r in z]);ns=np.array([f(r,c)+f(r,d) for r in z]);nf=float(np.mean(p*(1-p)/ns)) if z else None
  tmap={}
  for r in z:
   for side,pre in (('home','fh'),('away','fh')):pass
  halves[n]={'n_matches':len(z),'share_1h':p,'observed_variance':float(np.var(s,ddof=1)) if len(s)>1 else None,'noise_floor_permatch':nf,'true_variance':float(np.var(s,ddof=1)-nf) if len(s)>1 else None,'events_all_matches_goals_share':sum(f(r,'ht_home_goals')+f(r,'ht_away_goals') for r in M)/sum(f(r,'home_goals')+f(r,'away_goals') for r in M) if n=='goals' else None}
 for n,(a,b,c,d) in mk.items():
  if n=='goals':zz=[r for r in M if np.isfinite(f(r,'fh_corners_home')) and np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
  else:zz=[r for r in M if np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
  tm={}
  for r in zz:
   sh=(f(r,a)+f(r,b))/(f(r,c)+f(r,d))
   tm.setdefault(r['home_team'],[]).append(sh);tm.setdefault(r['away_team'],[]).append(sh)
  tm={k:v for k,v in tm.items() if len(v)>=16}
  halves[n]['team_share_split_half']=split_r({k:[{'v':x} for x in v] for k,v in tm.items()},lambda q:q['v'])
 refs={}
 for r in M:
  if r['referee']:refs.setdefault(r['referee'],[]).append(r)
 refs={k:v for k,v in refs.items() if len(v)>=20};referee={'coverage_pct':100*sum(bool(r['referee']) for r in M)/len(M),'coverage_by_season':{s:inv[s]['referee_nonnull_pct'] for s in seasons},'eligible_referees':len(refs),'card_rate_split_half':split_r(refs,lambda r:f(r,'yellow_home')+f(r,'yellow_away'))}
 newcomers={};reverse={}
 for i,s in enumerate(seasons[1:],1):
  prev={r['home_team'] for r in M if r['season']==seasons[i-1]}|{r['away_team'] for r in M if r['season']==seasons[i-1]};now={r['home_team'] for r in M if r['season']==s}|{r['away_team'] for r in M if r['season']==s};new=now-prev;gone=prev-now;league=season_levels[s]['goals_per_match']
  def gap(ts):
   z=[r for r in M if r['season']==s and (r['home_team'] in ts or r['away_team'] in ts)];gf=np.mean([(f(r,'home_goals') if r['home_team'] in ts else f(r,'away_goals')) for r in z]) if z else None;ga=np.mean([(f(r,'away_goals') if r['home_team'] in ts else f(r,'home_goals')) for r in z]) if z else None;return {'teams':sorted(ts),'n_teams':len(ts),'gf_per_match':float(gf) if gf is not None else None,'ga_per_match':float(ga) if ga is not None else None,'league_goal_mean_per_match':league,'league_team_goal_mean':league/2,'gf_gap':float(gf-league/2) if gf is not None else None,'ga_gap':float(ga-league/2) if ga is not None else None}
  newcomers[s]=gap(new);reverse[s]={'absent_next_season':sorted(gone),'n_teams':len(gone)}

 DEV_BLOCKS=['2021','2022','2023','2024','2025 - Apertura','2025 - Clausura','2026 - Apertura']
 dev=[r for r in M if r['season'] in DEV_BLOCKS]; virg=[r for r in M if r['season']=='2026 - Clausura']
 def over_rates(rs,total_fn,lines):
  t=np.array([total_fn(r) for r in rs],float);t=t[np.isfinite(t)]
  return {'n':len(rs),'mean':float(np.mean(t)),'median':float(np.median(t)),'over':{str(L):float(100*np.mean(t>L)) for L in lines}}
 line_tables={'dev':{
  'sot':over_rates(dev,lambda r:f(r,'ShotsOnTarget_home')+f(r,'ShotsOnTarget_away'),[6.5,7.5,8.5,9.5]),
  'corners':over_rates(dev,lambda r:f(r,'corners_home')+f(r,'corners_away'),[7.5,8.5,9.5,10.5]),
  'cards':over_rates(dev,lambda r:f(r,'yellow_home')+f(r,'yellow_away'),[3.5,4.5,5.5,6.5]),
  'shots':over_rates(dev,lambda r:f(r,'total_shots_home')+f(r,'total_shots_away'),[22.5,23.5,24.5,25.5,26.5]),
  'goals':over_rates(dev,lambda r:f(r,'home_goals')+f(r,'away_goals'),[1.5,2.5,3.5])},
  'virgin':{
  'sot':over_rates(virg,lambda r:f(r,'ShotsOnTarget_home')+f(r,'ShotsOnTarget_away'),[6.5,7.5,8.5,9.5]),
  'corners':over_rates(virg,lambda r:f(r,'corners_home')+f(r,'corners_away'),[7.5,8.5,9.5,10.5]),
  'cards':over_rates(virg,lambda r:f(r,'yellow_home')+f(r,'yellow_away'),[3.5,4.5,5.5,6.5]),
  'shots':over_rates(virg,lambda r:f(r,'total_shots_home')+f(r,'total_shots_away'),[22.5,23.5,24.5,25.5,26.5]),
  'goals':over_rates(virg,lambda r:f(r,'home_goals')+f(r,'away_goals'),[1.5,2.5,3.5])}}
 cal={s:ratio(np.array([f(r,'home_goals')+f(r,'away_goals') for r in M if r['season']==s]),np.array([f(r,'expected_goals_home')+f(r,'expected_goals_away') for r in M if r['season']==s])) for s in seasons};eda={'seasons':season_levels,'pooled':levels(M),'home_advantage_goals':mean([f(r,'home_goals')-f(r,'away_goals') for r in M]),'reliability':rel,'halves':halves,'referees':referee,'newcomers':newcomers,'reverse_movers':reverse,'xg_calibration_goals_over_xg':cal,'touches_opp_box_key_present':any(inv[s]['touches_opp_box_present_count'] for s in seasons),'star_absence':'Skipped: closed program-wide, as requested.','line_tables':line_tables}
 (HERE/'inventory_summary.json').write_text(json.dumps(inv,indent=2,allow_nan=False,default=jd));(HERE/'eda_summary.json').write_text(json.dumps(eda,indent=2,allow_nan=False,default=jd));print(json.dumps({'matches':len(M),'seasons':seasons,'touches_opp_box_key_present':eda['touches_opp_box_key_present'],'pooled_goals_per_match':eda['pooled']['goals_per_match']},indent=2))
if __name__=='__main__':main()
