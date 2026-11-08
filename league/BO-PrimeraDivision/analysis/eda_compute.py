"""Compute descriptive EDA; no models are fit."""
import json
from pathlib import Path
import numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'league/BO-PrimeraDivision/analysis'; D=ROOT/'league/BO-PrimeraDivision/data'
d=pd.read_csv(D/'bo_matches.csv'); d.date=pd.to_datetime(d.date); d['round_num']=pd.to_numeric(d['round'],errors='coerce'); d['goals_total']=d.home_goals+d.away_goals
r=d[d.phase=='regular'].copy()
def total(x,k):
    if f'{k}_home' in x: return x[f'{k}_home']+x[f'{k}_away']
    if f'{k}_home_1h' in x: return x[f'{k}_home_1h']+x[f'{k}_away_1h']
    raise KeyError(k)

levels={}
for s,g in d.groupby('season'):
    z={'n':len(g),'regular_n':int((g.phase=='regular').sum()),'playoff_n':int((g.phase=='playoff').sum()),'teams':len(set(g.home_team_id)|set(g.away_team_id)),'rounds':sorted(g['round'].astype(str).unique())}
    for k in ['goals_total','ShotsOnTarget','corners','event_yellow_unified','total_shots']:
        y=g[k] if k=='goals_total' else total(g,k); z[k]={'n':int(y.notna().sum()),'mean':float(y.mean()) if y.notna().any() else None,'sd':float(y.std()) if y.notna().sum()>1 else None}
    levels[str(s)]=z

tm=pd.read_csv(D/'bo_team_matches.csv'); tm.date=pd.to_datetime(tm.date); tm=tm[tm.phase=='regular'].sort_values(['season','team_id','date','match_id'])
trait_cols=['goals_for','goals_against','sot_for','sot_against','corners_for','corners_against','yellow_for','yellow_against','total_shots_for','box_touches_for','box_touches_against','possession_for','big_chances_for']
reliability={}
for s,g in tm.groupby('season'):
    reliability[str(s)]={}
    for col in trait_cols:
        pairs=[]
        for _,tg in g.groupby('team_id'):
            if len(tg)<6: continue
            a=tg.iloc[::2][col].dropna(); b=tg.iloc[1::2][col].dropna(); n=min(len(a),len(b))
            if n>=3: pairs.append((a.iloc[:n].mean(),b.iloc[:n].mean()))
        arr=np.array(pairs); rr=np.corrcoef(arr.T)[0,1] if len(arr)>=3 and arr[:,0].std()>0 and arr[:,1].std()>0 else None
        reliability[str(s)][col]={'n_teams':len(pairs),'r':float(rr) if rr is not None else None}

def ratio(x,num,den):
    if num and f'{num}_home_1h' in x: a=x[f'{num}_home_1h']+x[f'{num}_away_1h']
    else: a=(total(x,num) if num else x.ht_home_goals+x.ht_away_goals)
    b=(total(x,den) if den else x.goals_total); ok=a.notna()&b.notna()&(b>0)
    return float(a[ok].sum()/b[ok].sum()),int(ok.sum()),float((a[ok]/b[ok]).var()) if ok.sum()>1 else None
half={}; seed=r[r.season.isin([2021,2022,2023,2024])]; q=ratio(seed,None,None); half['goals']={'share':q[0],'n':q[1],'match_share_variance':q[2]}
g25=r[r.season==2025]
for k in ['ShotsOnTarget','corners','total_shots']:
    q=ratio(g25,k,k); half[k]={'share':q[0],'n':q[1],'match_share_variance':q[2]}
q=ratio(g25,'event_yellow_unified','event_yellow_unified'); st1=g25.yellow_cards_home_1h+g25.yellow_cards_away_1h; st=total(g25,'yellow_cards'); ok=st.notna()&(st>0)
half['cards']={'share':q[0],'n':q[1],'match_share_variance':q[2],'crosscheck_stats':float(st1[ok].sum()/st[ok].sum()),'crosscheck_n':int(ok.sum())}

dev=r[(r.season==2025)&r.round_num.between(11,30)]; lines={}
for market,k in [('S-BO','ShotsOnTarget'),('C-BO','corners'),('K-BO','event_yellow_unified'),('T-BO','total_shots')]:
    y=total(dev,k); line=float(np.floor(y.mean())+0.5); lines[market]={'n':len(y),'mean':float(y.mean()),'line':line,'over_rate':float((y>line).mean())}
stat_y=total(g25,'yellow_cards'); ev_y=total(g25,'event_yellow_unified')
plain_y=total(g25,'event_yellow')
art={'stats_yellow_total':float(stat_y.sum()),'event_plain_yellow_total':float(plain_y.sum()),'event_unified_yellow_total':float(ev_y.sum()),'match_agreement_n':int((stat_y==ev_y).sum()),'n':len(g25),'events_incomplete_2025_26':int(((d.season.isin([2025,2026]))&(d.events_complete==0)).sum())}
g25=g25.copy(); g25['month']=g25.date.dt.month; g25['round_block']=((g25.round_num-1)//5+1)*5
spike={'month':g25.groupby('month').goals_total.agg(['count','mean']).round(4).to_dict('index'),'round_block':g25.groupby('round_block').goals_total.agg(['count','mean']).round(4).to_dict('index'),'home_mean':float(g25.home_goals.mean()),'away_mean':float(g25.away_goals.mean())}
out={'levels':levels,'reliability':reliability,'halves':half,'dev_lines':lines,'artifacts':art,'goals_spike_2025':spike}
(A/'eda_numbers.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
