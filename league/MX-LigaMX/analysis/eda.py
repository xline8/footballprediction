"""Phase A descriptive inventory for Liga MX; no model fitting."""
import csv,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).parent; DATA=HERE.parent/'data'
M=list(csv.DictReader((DATA/'mx_matches.csv').open(newline=''))); T=list(csv.DictReader((DATA/'team_matches.csv').open(newline='')))
S=["2021/2022 - Apertura","2021/2022 - Clausura","2022/2023 - Apertura","2022/2023 - Clausura","2023/2024 - Apertura","2023/2024 - Clausura","2024/2025 - Apertura","2024/2025 - Clausura","2025/2026 - Apertura","2025/2026 - Clausura"]; DEV=S[:9]; VIRGIN=S[-1]
ALT={"Ciudad de México (D.F.)":2240,"Ciudad de México":2240,"Toluca de Lerdo":2600,"Pachuca de Soto":2432,"Puebla":2135,"Morelia":1920,"Aguascalientes":1888,"San Luis Potosí":1860,"Santiago de Querétaro":1820,"León de los Aldamas":1815,"Zapopan":1566,"Guadalajara":1566,"Ciudad Juárez":1140,"Torreón":1120,"San Nicolás de los Garza":512,"Guadalupe":512,"Monterrey":512,"Tijuana":31,"Mazatlán":10}
def f(r,k):
 try:return float(r.get(k,''))
 except:return np.nan
def a(rs,fn):return np.array([fn(r) for r in rs],float)
def avg(x):x=np.asarray(x,float);return float(np.nanmean(x)) if np.isfinite(x).any() else None
def ratio(x,y):
 x,y=np.asarray(x,float),np.asarray(y,float);z=np.isfinite(x)&np.isfinite(y)
 return float(x[z].sum()/y[z].sum()) if z.any() and y[z].sum() else None
def corr(x,y):
 x,y=np.asarray(x,float),np.asarray(y,float);z=np.isfinite(x)&np.isfinite(y)
 return float(np.corrcoef(x[z],y[z])[0,1]) if z.sum()>2 and x[z].std() and y[z].std() else None
def split(groups,fn,ratio_mode=False):
 rng=np.random.default_rng(90210); out=[]
 for _ in range(60):
  x=[];y=[]
  for rs in groups.values():
   q=a(rs,fn);q=q[np.isfinite(q)]
   if len(q)<2:continue
   ix=rng.permutation(len(q));n=len(q)//2;x.append(q[ix[:n]].mean());y.append(q[ix[n:]].mean())
  z=corr(x,y)
  if z is not None:out.append(z)
 return {'r':avg(out),'n_splits':len(out),'odd_even_r':None}
def split_ratio(groups,num,den):
 rng=np.random.default_rng(90210);out=[]
 for _ in range(60):
  x=[];y=[]
  for rs in groups.values():
   q=[(f(r,num),f(r,den)) for r in rs if np.isfinite(f(r,num)) and np.isfinite(f(r,den)) and f(r,den)>0]
   if len(q)<16:continue
   ix=rng.permutation(len(q));n=len(q)//2;x.append(sum(q[i][0] for i in ix[:n])/sum(q[i][1] for i in ix[:n]));y.append(sum(q[i][0] for i in ix[n:])/sum(q[i][1] for i in ix[n:]))
  z=corr(x,y)
  if z is not None:out.append(z)
 return {'r':avg(out),'n_splits':len(out),'method':'ratio_of_sums'}
def cov(rs,k):return 100*sum(r[k]=='True' for r in rs)/len(rs)
def levels(rs):
 g=a(rs,lambda r:f(r,'home_goals')+f(r,'away_goals')); sh=a(rs,lambda r:f(r,'total_shots_home')+f(r,'total_shots_away')); so=a(rs,lambda r:f(r,'ShotsOnTarget_home')+f(r,'ShotsOnTarget_away')); co=a(rs,lambda r:f(r,'corners_home')+f(r,'corners_away')); ye=a(rs,lambda r:f(r,'yellow_home')+f(r,'yellow_away'))
 return {'n_matches':len(rs),'goals_per_match':avg(g),'home_goals':avg(a(rs,lambda r:f(r,'home_goals'))),'away_goals':avg(a(rs,lambda r:f(r,'away_goals'))),'home_draw_away_pct':[100*avg(a(rs,lambda r:f(r,'home_goals')>f(r,'away_goals'))),100*avg(a(rs,lambda r:f(r,'home_goals')==f(r,'away_goals'))),100*avg(a(rs,lambda r:f(r,'home_goals')<f(r,'away_goals')))],'btts_pct':100*avg((a(rs,lambda r:f(r,'home_goals'))>0)&(a(rs,lambda r:f(r,'away_goals'))>0)),'over2_5_pct':100*avg(g>2.5),'total_shots':avg(sh),'sot':avg(so),'corners':avg(co),'yellows':avg(ye),'team_xg':avg(a(rs,lambda r:f(r,'expected_goals_home')+f(r,'expected_goals_away'))),'dispersion_var_mean':{k:float(np.nanvar(v,ddof=1)/np.nanmean(v)) for k,v in [('goals',g),('SOT',so),('corners',co),('cards',ye),('shots',sh)]}}
def line(rs,fn,ls):
 x=a(rs,fn);x=x[np.isfinite(x)];return {'n':len(x),'mean':float(x.mean()),'median':float(np.median(x)),'over':{str(q):float(100*np.mean(x>q)) for q in ls}}
def main():
 inv={}; lev={}
 for s in S:
  rs=[r for r in M if r['season']==s];inv[s]={'n_matches':len(rs),'coverage_pct':{k:cov(rs,k) for k in ['has_stats_all','has_stats_half','has_shotmap','has_events','has_lineup','has_player_stats']},'xg_present_pct':100*sum(np.isfinite(f(r,'expected_goals_home')) for r in rs)/len(rs),'referee_nonnull_pct':100*sum(bool(r['referee']) for r in rs)/len(rs),'touches_opp_box_present_count':sum(np.isfinite(f(r,'touches_opp_box_home')) for r in rs),'distinct_teams':len({r['home_team'] for r in rs}|{r['away_team'] for r in rs}),'date_range':[min(r['date'] for r in rs),max(r['date'] for r in rs)]};lev[s]=levels(rs)
  ag={'stats_total':sum(f(r,'yellow_cards_home')+f(r,'yellow_cards_away') for r in rs),'events_total':sum(f(r,'yellow_home')+f(r,'yellow_away') for r in rs),'per_match_agreement_count':sum(f(r,'yellow_cards_home')+f(r,'yellow_cards_away')==f(r,'yellow_home')+f(r,'yellow_away') for r in rs),'n_matches':len(rs)};inv[s]['cards_agreement']=ag;sh={}
  for typ in ['all','on_target','off_target']:
   den=num=0
   for r in rs:
    for z in ['home','away']:
     shots=f(r,'sm_shots_'+z);on=f(r,'sm_sot_incl_blocked_'+z);den+=shots if typ=='all' else on if typ=='on_target' else shots-on;num+=f(r,'sm_xgot_n_'+z) if typ=='all' else f(r,'sm_xgot_n_on_'+z) if typ=='on_target' else f(r,'sm_xgot_n_off_'+z)
   sh[typ]={'numerator_xgot_nonnull':num,'denominator_shots':den,'share':num/den if den else None}
  inv[s]['xgot_population_shares']=sh
 groups={};
 for r in T:groups.setdefault(r['team'],[]).append(r)
 groups={k:v for k,v in groups.items() if len(v)>=24};rel={}; keys={'goals':'ev_goals','shots':'total_shots','SOT':'ShotsOnTarget','corners':'corners','yellows':'yellow','xG':'expected_goals','big_chance':'big_chance','possession':'BallPossesion','box_touches':'touches_opp_box'}
 for n,k in keys.items():rel[n+'_for']=split(groups,lambda r,k=k:f(r,k));rel[n+'_against']=split(groups,lambda r,k=k:f(r,k+'_against'))
 rel['ratio_traits']={'set_play_xg_share':split_ratio(groups,'expected_goals_set_play','expected_goals'),'xg_per_shot':split_ratio(groups,'sm_xg','sm_shots'),'on_target_rate':split_ratio(groups,'ShotsOnTarget','total_shots'),'xgot_per_shot_attacking':split_ratio(groups,'sm_xgot','sm_xgot_n'),'finishing_goals_minus_xg':split(groups,lambda r:f(r,'ev_goals')-f(r,'expected_goals'))}
 g25={k:[r for r in v if r['date']>='2025-01-01'] for k,v in groups.items()};rel['ratio_traits']['xgot_per_shot_restricted_2025']=split_ratio({k:v for k,v in g25.items() if len(v)>=24},'sm_xgot','sm_xgot_n')
 halves={}; specs={'goals':('ht_home_goals','ht_away_goals','home_goals','away_goals'),'SOT':('fh_ShotsOnTarget_home','fh_ShotsOnTarget_away','ShotsOnTarget_home','ShotsOnTarget_away'),'corners':('fh_corners_home','fh_corners_away','corners_home','corners_away'),'total_shots':('fh_total_shots_home','fh_total_shots_away','total_shots_home','total_shots_away'),'yellows':('fh_yellow_events_home','fh_yellow_events_away','yellow_home','yellow_away')}
 for n,(aa,bb,cc,dd) in specs.items():
  rs=[r for r in M if np.isfinite(f(r,aa)) and np.isfinite(f(r,bb)) and f(r,cc)+f(r,dd)>0];sh=a(rs,lambda r:(f(r,aa)+f(r,bb))/(f(r,cc)+f(r,dd)));p=ratio([f(r,aa)+f(r,bb) for r in rs],[f(r,cc)+f(r,dd) for r in rs]);halves[n]={'n_matches':len(rs),'share_1h':p,'observed_variance':float(np.var(sh,ddof=1)) if len(sh)>1 else None,'noise_floor_permatch':float(np.mean(p*(1-p)/a(rs,lambda r:f(r,cc)+f(r,dd)))) if rs else None,'true_variance':float(np.var(sh,ddof=1)-np.mean(p*(1-p)/a(rs,lambda r:f(r,cc)+f(r,dd)))) if len(sh)>1 else None}
 refs={};
 for r in M:
  if r['referee']:refs.setdefault(r['referee'],[]).append(r)
 refs={k:v for k,v in refs.items() if len(v)>=20};ref={'coverage_pct':100*sum(bool(r['referee']) for r in M)/len(M),'coverage_by_season':{s:inv[s]['referee_nonnull_pct'] for s in S},'eligible_referees':len(refs),'card_rate_split_half':split(refs,lambda r:f(r,'yellow_home')+f(r,'yellow_away'))}
 sets={s:{r['home_team'] for r in M if r['season']==s}|{r['away_team'] for r in M if r['season']==s} for s in S};stable={'teams_overall':sorted(set().union(*sets.values())),'n_teams_overall':len(set().union(*sets.values())),'by_season':{s:len(v) for s,v in sets.items()},'transitions':{S[i]+' -> '+S[i+1]:{'new':sorted(sets[S[i+1]]-sets[S[i]]),'departed':sorted(sets[S[i]]-sets[S[i+1]])} for i in range(9)}}
 city={};
 for r in M:
  if r['stadium_city']:city.setdefault(r['home_team'],[]).append(r['stadium_city'])
 ta={t:ALT.get(max(set(v),key=v.count)) for t,v in city.items()};az=[];missing=0
 for r in M:
  h=ta.get(r['home_team']);a0=ta.get(r['away_team'])
  if h is None or a0 is None:missing+=1
  else:az.append((r,h,a0))
 def azsum(z):return {'n':len(z),'home_goal_edge':avg([f(r,'home_goals')-f(r,'away_goals') for r,_,_ in z]),'home_win_rate':100*avg([f(r,'home_goals')>f(r,'away_goals') for r,_,_ in z])}
 alt={'mapping':ALT,'known_matches':len(az),'unknown_matches':missing,'pooled_high_altitude':azsum([z for z in az if z[1]>=2000]),'pooled_rest':azsum([z for z in az if z[1]<2000]),'away_under_1000_high_home':azsum([z for z in az if z[1]>=2000 and z[2]<1000]),'away_under_1000_rest_home':azsum([z for z in az if z[1]<2000 and z[2]<1000]),'verdict':'DESCRIPTIVE / NOT ADOPTED: static home altitude is collinear with stable team identity and absorbed by team/venue ratings.'}
 fns={'sot':(lambda r:f(r,'ShotsOnTarget_home')+f(r,'ShotsOnTarget_away'),[6.5,7.5,8.5,9.5]),'corners':(lambda r:f(r,'corners_home')+f(r,'corners_away'),[7.5,8.5,9.5,10.5]),'cards':(lambda r:f(r,'yellow_home')+f(r,'yellow_away'),[3.5,4.5,5.5,6.5]),'shots':(lambda r:f(r,'total_shots_home')+f(r,'total_shots_away'),[22.5,23.5,24.5,25.5,26.5]),'goals':(lambda r:f(r,'home_goals')+f(r,'away_goals'),[1.5,2.5,3.5])};line_tables={'dev':{},'virgin':{}}
 for k,(fn,ls) in fns.items():line_tables['dev'][k]=line([r for r in M if r['season'] in DEV],fn,ls);line_tables['virgin'][k]=line([r for r in M if r['season']==VIRGIN],fn,ls)
 cal={s:ratio([f(r,'home_goals')+f(r,'away_goals') for r in M if r['season']==s],[f(r,'expected_goals_home')+f(r,'expected_goals_away') for r in M if r['season']==s]) for s in S};eda={'seasons':lev,'pooled':levels(M),'home_advantage_goals':avg([f(r,'home_goals')-f(r,'away_goals') for r in M]),'reliability':rel,'halves':halves,'referees':ref,'team_stability':stable,'xg_calibration_goals_over_xg':cal,'line_tables':line_tables,'cards_agreement':{s:inv[s]['cards_agreement'] for s in DEV},'altitude':alt,'xgot_era_guard':'2025-01-01+'}
 def jd(x):
  if isinstance(x,(np.integer,)):return int(x)
  if isinstance(x,(np.floating,)):return float(x)
  raise TypeError(type(x).__name__)
 (HERE/'inventory_summary.json').write_text(json.dumps(inv,indent=2,allow_nan=False,default=jd));(HERE/'eda_summary.json').write_text(json.dumps(eda,indent=2,allow_nan=False,default=jd));print(json.dumps({'matches':len(M),'pooled':eda['pooled'],'halves':halves,'team_stability':stable,'altitude':alt},indent=2,default=jd))
if __name__=='__main__':main()
