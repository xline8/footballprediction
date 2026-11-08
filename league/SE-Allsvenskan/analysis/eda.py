"""Inventory + EDA for SE-Allsvenskan. Outputs inventory_summary.json + eda_summary.json."""
import csv, json
from pathlib import Path
import numpy as np
HERE=Path(__file__).parent; DATA=HERE.parent/'data'
def rows(p):
    with open(p,newline='') as f: return list(csv.DictReader(f))
M=rows(DATA/'se_matches.csv'); T=rows(DATA/'se_team_matches.csv')
def f(r,k):
    try: return float(r.get(k,''))
    except (TypeError,ValueError): return np.nan
def mean(a):
    a=np.asarray(a,float); a=a[np.isfinite(a)]
    return float(np.mean(a)) if len(a) else None
def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float); z=np.isfinite(a)&np.isfinite(b)
    return float(np.corrcoef(a[z],b[z])[0,1]) if z.sum()>2 and np.std(a[z]) and np.std(b[z]) else None
def split_r(items,fn,seed=90210,min_matches=24):
    rng=np.random.default_rng(seed); xs=[]
    for _ in range(60):
        x=[];y=[]
        for z in items.values():
            a=np.asarray([fn(q) for q in z],float); a=a[np.isfinite(a)]
            if len(a)<min_matches: continue
            ix=rng.permutation(len(a)); n=len(a)//2; x.append(np.mean(a[ix[:n]])); y.append(np.mean(a[ix[n:]]))
        q=corr(x,y)
        if q is not None: xs.append(q)
    return {'r': float(np.mean(xs)) if xs else None, 'n_splits': len(xs)}
def split_r_ratio(items,num,den,seed=90210,min_n=8):
    rng=np.random.default_rng(seed); xs=[]
    for _ in range(60):
        x=[];y=[]
        for z in items.values():
            a=[(f(q,num),f(q,den)) for q in z]; a=[(u,v) for u,v in a if np.isfinite(u) and np.isfinite(v) and v>0]
            if len(a)<2*min_n: continue
            ix=rng.permutation(len(a)); n=len(a)//2
            x.append(sum(a[i][0] for i in ix[:n])/sum(a[i][1] for i in ix[:n])); y.append(sum(a[i][0] for i in ix[n:])/sum(a[i][1] for i in ix[n:]))
        q=corr(x,y)
        if q is not None: xs.append(q)
    return {'r': float(np.mean(xs)) if xs else None, 'n_splits': len(xs), 'method':'ratio_of_sums'}
def levels(rs):
    def v(k): return np.array([f(r,k) for r in rs])
    g=v('home_goals')+v('away_goals'); sh=v('total_shots_home')+v('total_shots_away'); so=v('ShotsOnTarget_home')+v('ShotsOnTarget_away'); co=v('corners_home')+v('corners_away'); ye=v('yellow_home')+v('yellow_away'); xg=v('expected_goals_home')+v('expected_goals_away')
    def disp(a): return float(np.nanvar(a,ddof=1)/np.nanmean(a)) if len(a)>1 else None
    return {'n':len(rs),'goals':mean(g),'home_goals':mean(v('home_goals')),'away_goals':mean(v('away_goals')),
      'hw_pct':100*float(np.mean(v('home_goals')>v('away_goals'))),'draw_pct':100*float(np.mean(v('home_goals')==v('away_goals'))),'aw_pct':100*float(np.mean(v('home_goals')<v('away_goals'))),
      'btts_pct':100*float(np.mean((v('home_goals')>0)&(v('away_goals')>0))),'over25_pct':100*float(np.mean(g>2.5)),
      'shots':mean(sh),'sot':mean(so),'corners':mean(co),'yellows':mean(ye),'reds':mean(v('red_home')+v('red_away')),'xg':mean(xg),
      'dispersion':{'goals':disp(g),'sot':disp(so),'corners':disp(co),'yellows':disp(ye),'shots':disp(sh)},
      'over_rates':{str(L): float(np.mean(g>L)) for L in (1.5,2.5,3.5)}}
def main():
    seasons=sorted({r['season'] for r in M})
    inv={}; lev={}
    for s in seasons:
        rs=[r for r in M if r['season']==s]
        inv[s]={'n':len(rs),'date_range':[min(r['date'] for r in rs),max(r['date'] for r in rs)],'teams':len({r['home_team'] for r in rs}|{r['away_team'] for r in rs}),
          'has_stats_all_pct':100*mean([f(r,'has_stats_all') for r in rs]),'has_stats_half_pct':100*mean([f(r,'has_stats_half') for r in rs]),
          'has_shotmap_pct':100*mean([f(r,'has_shotmap') for r in rs]),'has_events_pct':100*mean([f(r,'has_events') for r in rs]),
          'referee_pct':100*sum(bool(r['referee']) for r in rs)/len(rs),
          'xg_pct':100*sum(np.isfinite(f(r,'expected_goals_home')) for r in rs)/len(rs),
          'touches_pct':100*sum(np.isfinite(f(r,'touches_opp_box_home')) for r in rs)/len(rs),
          'yellow_stats_pct':100*sum(np.isfinite(f(r,'yellow_home')) for r in rs)/len(rs)}
        # xgot shares
        for typ in ('all','on','off'):
            num=den=0
            for r in rs:
                for side in ('home','away'):
                    n=f(r,f'sm_shots_{side}'); sot=f(r,f'sm_sot_{side}'); gn=f(r,f'sm_xgot_n_{side}')
                    if typ=='all': den+=n; num+=gn
                    elif typ=='on': den+=sot; num+=0  # approx: xgot_n_on not stored; use overall below
                    else: den+=n-sot
            inv[s].setdefault('xgot_share_all', num/den if den else None)
        lev[s]=levels(rs)
    # team groups from team_matches (columns: *_for / *_against with original key names)
    groups={}
    for r in T: groups.setdefault(r['team'],[]).append(r)
    groups={k:v for k,v in groups.items() if len(v)>=24}
    rel={}
    # team_matches columns use keys like expected_goals_for, total_shots_for, ShotsOnTarget_for, corners_for, yellow_cards_for
    for name,k in {'goals':'goals','shots':'total_shots','SOT':'ShotsOnTarget','corners':'corners','yellows':'yellow_cards','xG':'expected_goals','big_chance':'big_chance','possession':'BallPossesion','box_touches':'touches_opp_box'}.items():
        fk = 'goals_for' if k=='goals' else f'{k}_for'
        ak = 'goals_against' if k=='goals' else f'{k}_against'
        rel[name+'_for']=split_r(groups, lambda r,k=fk: f(r,k))
        rel[name+'_against']=split_r(groups, lambda r,k=ak: f(r,k))
    rel['ratio_traits']={}
    rel['ratio_traits']['set_play_xg_share']=split_r_ratio(groups,'expected_goals_set_play_for' if 'expected_goals_set_play_for' in T[0] else 'expected_goals_for','expected_goals_for')
    # team_matches only carries subset; set-play / sm aggregates may be limited - compute ratio traits from matches directly per team
    # Build per-team match-level records from M for ratio traits
    tm={}
    for r in M:
        for side,opp in (('home','away'),('away','home')):
            tm.setdefault(r[f'{side}_team'],[]).append({
              'sp': f(r,f'expected_goals_set_play_{side}'), 'xg': f(r,f'expected_goals_{side}'),
              'sm_xg': f(r,f'sm_xg_{side}'), 'sm_shots': f(r,f'sm_shots_{side}'),
              'goals': f(r,f'{side}_goals'), 'sot': f(r,f'ShotsOnTarget_{side}'), 'shots': f(r,f'total_shots_{side}'),
              'xgot': f(r,f'sm_xgot_{side}'), 'xgot_n': f(r,f'sm_xgot_n_{side}'), 'date': r['date'], 'season': r['season']})
    def ratio_trait(key_num,key_den, filt=None):
        items={}
        for t,recs in tm.items():
            rr=[x for x in recs if (filt is None or filt(x))]
            items[t]=rr
        # emulate split_r_ratio on dict records
        rng=np.random.default_rng(90210); xs=[]
        for _ in range(60):
            x=[];y=[]
            for z in items.values():
                a=[(q[key_num],q[key_den]) for q in z]; a=[(u,v) for u,v in a if np.isfinite(u) and np.isfinite(v) and v>0]
                if len(a)<16: continue
                ix=rng.permutation(len(a)); n=len(a)//2
                x.append(sum(a[i][0] for i in ix[:n])/sum(a[i][1] for i in ix[:n])); y.append(sum(a[i][0] for i in ix[n:])/sum(a[i][1] for i in ix[n:]))
            q=corr(x,y)
            if q is not None: xs.append(q)
        return {'r': float(np.mean(xs)) if xs else None}
    rel['ratio_traits']['set_play_xg_share']=ratio_trait('sp','xg')
    rel['ratio_traits']['xg_per_shot']=ratio_trait('sm_xg','sm_shots')
    rel['ratio_traits']['on_target_rate']=ratio_trait('sot','shots')
    rel['ratio_traits']['xgot_per_shot_all']=ratio_trait('xgot','xgot_n')
    rel['ratio_traits']['xgot_per_shot_2025plus']=ratio_trait('xgot','xgot_n', filt=lambda x: x['season']>='2025')
    rel['ratio_traits']['xgot_per_shot_2024plus']=ratio_trait('xgot','xgot_n', filt=lambda x: x['season']>='2024')
    # finishing: goals - xg per team-match
    rel['finishing']=split_r({t:[{'v':x['goals']-x['xg']} for x in recs] for t,recs in tm.items()}, lambda r: r['v'])
    # halves: use complete-splits era only (seasons where has_stats_half high) - determined dynamically: seasons >=2024 checked in inv
    halves={}
    mk={'goals':('ht_home_goals','ht_away_goals','home_goals','away_goals','events'),
        'SOT':('fh_ShotsOnTarget_home','fh_ShotsOnTarget_away','ShotsOnTarget_home','ShotsOnTarget_away','splits'),
        'corners':('fh_corners_home','fh_corners_away','corners_home','corners_away','splits'),
        'total_shots':('fh_total_shots_home','fh_total_shots_away','total_shots_home','total_shots_away','splits'),
        'yellows':('fh_yellow_cards_home','fh_yellow_cards_away','yellow_home','yellow_away','splits')}
    for name,(a,b,c,d,src) in mk.items():
        if src=='events':
            z=[r for r in M if np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
        else:
            z=[r for r in M if f(r,'has_stats_half')==1 and np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
        if not z: halves[name]={'n':0}; continue
        p=sum(f(r,a)+f(r,b) for r in z)/sum(f(r,c)+f(r,d) for r in z)
        s=np.array([(f(r,a)+f(r,b))/(f(r,c)+f(r,d)) for r in z]); ns=np.array([f(r,c)+f(r,d) for r in z])
        halves[name]={'n':len(z),'share_1h':float(p),'observed_var':float(np.var(s,ddof=1)),'noise_floor':float(np.mean(p*(1-p)/ns)),'true_var':float(np.var(s,ddof=1)-np.mean(p*(1-p)/ns)),'seasons':sorted({r['season'] for r in z})}
    # halves on complete era 2024-2025 only
    halves_complete={}
    for name,(a,b,c,d,src) in mk.items():
        if src=='events':
            z=[r for r in M if r['season'] in ('2024','2025') and np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
        else:
            z=[r for r in M if r['season'] in ('2024','2025') and f(r,'has_stats_half')==1 and np.isfinite(f(r,a)) and f(r,c)+f(r,d)>0]
        if not z: halves_complete[name]={'n':0}; continue
        p=sum(f(r,a)+f(r,b) for r in z)/sum(f(r,c)+f(r,d) for r in z)
        s=np.array([(f(r,a)+f(r,b))/(f(r,c)+f(r,d)) for r in z]); ns=np.array([f(r,c)+f(r,d) for r in z])
        halves_complete[name]={'n':len(z),'share_1h':float(p),'true_var':float(np.var(s,ddof=1)-np.mean(p*(1-p)/ns))}
    # referee split-half (only referees with >=20 matches; yellows per match)
    refs={}
    for r in M:
        if r['referee']: refs.setdefault(r['referee'],[]).append(f(r,'yellow_home')+f(r,'yellow_away'))
    refs={k:v for k,v in refs.items() if len(v)>=20}
    ref_rel=split_r({k:[{'v':x} for x in v] for k,v in refs.items()}, lambda r: r['v'], min_matches=20) if len(refs)>=3 else {'r':None,'n_refs':len(refs)}
    ref_rel['n_refs']=len(refs)
    # movers: teams in season S not in S-1
    by_season={s:{r['home_team'] for r in M if r['season']==s}|{r['away_team'] for r in M if r['season']==s} for s in seasons}
    movers={}
    for i,s in enumerate(seasons):
        if i==0: continue
        new=by_season[s]-by_season[seasons[i-1]]
        movers[s]=sorted(new)
    # mover performance: first-season GF/GA per match vs league
    mover_perf=[]
    for s,news in movers.items():
        for t in news:
            recs=[x for x in tm.get(t,[]) if x['season']==s]
            if recs: mover_perf.append({'season':s,'team':t,'n':len(recs),'gf':float(np.mean([x['goals'] for x in recs]))})
    # primary lines dev (2021-2024)
    dev=[r for r in M if r['season'] in ('2021','2022','2023','2024')]
    def over(rs,k1,k2,line): return float(np.mean([f(r,k1)+f(r,k2)>line for r in rs]))
    lines={'sot':{str(L):over(dev,'ShotsOnTarget_home','ShotsOnTarget_away',L) for L in (7.5,8.5,9.5,10.5)},
           'corners':{str(L):over(dev,'corners_home','corners_away',L) for L in (8.5,9.5,10.5)},
           'cards':{str(L):over(dev,'yellow_home','yellow_away',L) for L in (2.5,3.5,4.5)},
           'shots':{str(L):over(dev,'total_shots_home','total_shots_away',L) for L in (23.5,24.5,25.5,26.5)},
           'goals_over25': float(np.mean([f(r,'home_goals')+f(r,'away_goals')>2.5 for r in dev]))}
    out={'inventory':inv,'levels':lev,'levels_pooled':levels(M),'reliability':rel,'halves_all':halves,'halves_complete_2024_2025':halves_complete,'referee':ref_rel,'movers':movers,'mover_perf_sample':mover_perf,'dev_primary_lines':lines,
         'goals_xg_ratio':{s: (lev[s]['goals']/lev[s]['xg'] if lev[s]['xg'] else None) for s in seasons}}
    (HERE/'inventory_summary.json').write_text(json.dumps(inv,indent=2,default=str)+'\n')
    (HERE/'eda_summary.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
    print(json.dumps(out,indent=2,default=str))
if __name__=='__main__': main()
