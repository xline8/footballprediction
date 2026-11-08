"""Reproducible Cyprus 1. Division inventory and EDA; deliberately no fitting."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROWS=list(csv.DictReader((HERE.parent/'data/cy_matches.csv').open())); WAREHOUSE=Path.home()/'workspace'/'footballprediction'
SEASONS=sorted({r['season'] for r in ROWS}); DEV_STATS={'2022/2023','2023/2024','2024/2025'}; GOALS_DEV={'2021/2022','2022/2023','2023/2024','2024/2025'}
def f(r,k):
    try: return None if r.get(k) in ('',None,'None') else float(r[k])
    except (TypeError,ValueError): return None
def avg(x): return round(st.mean(x),3) if x else None
def pct(n,d): return round(100*n/d,1) if d else None
def corr(x,y):
    if len(x)<5:return None
    mx,my=st.mean(x),st.mean(y); den=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/den,3) if den else None
def total(r,k):
    a,b=f(r,k+'_home'),f(r,k+'_away'); return a+b if a is not None and b is not None else None
def goals(r): return int(r['home_goals'])+int(r['away_goals'])
def over(v,line): return round(sum(x>line for x in v)/len(v),3) if v else None
def levels(rows):
    gs=[goals(r) for r in rows]; out={'matches':len(rows),'goals_per_match':avg(gs),'home_win_rate':round(sum(int(r['home_goals'])>int(r['away_goals']) for r in rows)/len(rows),3),'draw_rate':round(sum(r['home_goals']==r['away_goals'] for r in rows)/len(rows),3),'away_win_rate':round(sum(int(r['home_goals'])<int(r['away_goals']) for r in rows)/len(rows),3),'ou2_5_over_rate':over(gs,2.5),'home_advantage':{'goals':avg([int(r['home_goals'])-int(r['away_goals']) for r in rows])}}
    out['coverage']={'stats_all':pct(sum(r['has_stats_all']=='1' for r in rows),len(rows)),'stats_flag':pct(sum(r['has_stats_flag']=='1' for r in rows),len(rows)),'period_splits':pct(sum(r['has_period_splits_content']=='1' for r in rows),len(rows)),'shotmap':pct(sum(r['has_shotmap']=='1' for r in rows),len(rows)),'events':pct(sum(r['has_events']=='1' for r in rows),len(rows)),'referee':0.0}
    for n,k,ls in (('sot','ShotsOnTarget',[7.5,8.5,9.5]),('corners','corners',[8.5,9.5,10.5]),('cards','yellow',[3.5,4.5,5.5]),('total_shots','total_shots',[17.5,18.5,19.5])):
        v=[total(r,k) for r in rows if total(r,k) is not None]; out[n]={'mean':avg(v),'n':len(v),'over_rates':{str(l):over(v,l) for l in ls},'home_advantage':avg([f(r,k+'_home')-f(r,k+'_away') for r in rows if f(r,k+'_home') is not None and f(r,k+'_away') is not None])}; out['coverage'][n]=pct(len(v),len(rows))
    return out
def reliability(rows):
    specs={'goals_for':(None,False),'goals_against':(None,True),'ShotsOnTarget_for':('ShotsOnTarget',False),'ShotsOnTarget_against':('ShotsOnTarget',True),'corners_for':('corners',False),'corners_against':('corners',True),'total_shots_for':('total_shots',False),'total_shots_against':('total_shots',True),'yellow_for':('yellow',False),'yellow_against':('yellow',True),'BallPossesion_for':('BallPossesion',False),'BallPossesion_against':('BallPossesion',True)}
    out={}
    for name,(key,against) in specs.items():
        d=defaultdict(list)
        for r in rows:
            for side,other in (('home','away'),('away','home')):
                k=(r[side+'_team_id'],r['season']); val=(float(r[other+'_goals']) if key is None and against else float(r[side+'_goals']) if key is None else f(r,key+'_'+(other if against else side)))
                if val is not None:d[k].append(val)
        a=[];b=[]
        for v in d.values():
            if len(v)>=8:a.append(st.mean(v[::2]));b.append(st.mean(v[1::2]))
        out[name]={'r':corr(a,b),'n_team_seasons':len(a)}
    return out
def half(rows, key):
    shares=[]; first=[]; full=[]
    for r in rows:
        a=(f(r,'ht_home_goals')+f(r,'ht_away_goals')) if key=='goals' else (f(r,'ht_yellow_home')+f(r,'ht_yellow_away'))
        b=(float(r['home_goals'])+float(r['away_goals'])) if key=='goals' else total(r,key)
        if a is not None and b is not None and b>0:shares.append(a/b);first.append(a);full.append(b)
    if not shares:return {'n':0,'share_1h':None,'observed_variance':None,'noise_expectation':None,'true_variance':None}
    p=sum(first)/sum(full); noise=st.mean([p*(1-p)/x for x in full]); obs=st.variance(shares) if len(shares)>1 else 0
    return {'n':len(shares),'share_1h':round(p,4),'observed_variance':round(obs,5),'noise_expectation':round(noise,5),'true_variance':round(obs-noise,5),'noise_ratio':round(obs/noise,3) if noise else None,'noise_model':'binomial'}
def season_inventory(rows,s):
    x=[r for r in rows if r['season']==s]; ids={r[k] for r in x for k in ('home_team_id','away_team_id')}; names=defaultdict(set)
    for r in x:names[r['home_team_id']].add(r['home_team']);names[r['away_team_id']].add(r['away_team'])
    return {'matches':len(x),'distinct_team_ids':len(ids),'phase_counts':dict(sorted((p, sum(r['phase']==p for r in x)) for p in {r['phase'] for r in x})),'date_range':[min(r['date'] for r in x),max(r['date'] for r in x)]}
def main():
    per={s:{**levels([r for r in ROWS if r['season']==s]),**season_inventory(ROWS,s)} for s in SEASONS}; names=defaultdict(set)
    for r in ROWS:names[r['home_team_id']].add(r['home_team']);names[r['away_team_id']].add(r['away_team'])
    ev_goal_mismatch=[]; source_event_count=0; source_stats_count=0; source_periods=set(); source_keys=set()
    index_paths={x['match_id']:x['path'].rstrip('\r') for x in csv.DictReader((WAREHOUSE/'data_enrichment/fotmob_world_index.csv').open()) if x['league_id']=='136'}
    for r in ROWS:
        p=json.loads((WAREHOUSE/index_paths[r['match_id']]).read_text())
        c=p.get('content') or {}; ev=(((c.get('matchFacts') or {}).get('events') or {}).get('events') or [])
        source_event_count += bool(ev); score_total=int(r['home_goals'])+int(r['away_goals']); event_goals=sum(e.get('type')=='Goal' and not e.get('isPenaltyShootoutEvent') for e in ev)
        if ev and event_goals != score_total: ev_goal_mismatch.append({'match_id':r['match_id'],'score':f"{r['home_goals']}-{r['away_goals']}",'event_goals':event_goals})
        periods=((c.get('stats') or {}).get('Periods') or {}); source_stats_count += bool(periods.get('All')); source_periods.update(periods)
        for block in periods.values():
            for group in (block or {}).get('stats',[]) or []:
                for stat in group.get('stats',[]) or []: source_keys.add(stat.get('key'))
    dev=[r for r in ROWS if r['season'] in DEV_STATS]; all_pre=[r for r in ROWS if r['season'] in GOALS_DEV]; pre_virgin=[r for r in ROWS if r['season'] in {'2021/2022','2022/2023','2023/2024','2024/2025'}]
    lines={}
    for n,k,ls in (('sot','ShotsOnTarget',[7.5,8.5,9.5]),('corners','corners',[8.5,9.5,10.5]),('cards','yellow',[3.5,4.5,5.5]),('total_shots','total_shots',[17.5,18.5,19.5])):
        v=[total(r,k) for r in dev if total(r,k) is not None]; lines[n]={'candidate_lines':{str(l):{'over_rate':over(v,l),'n':len(v)} for l in ls},'primary_line':min(ls,key=lambda l:abs(over(v,l)-.5)),'n':len(v)}
    lines['goals']={'candidate_lines':{'2.5':{'over_rate':over([goals(r) for r in dev],2.5),'n':len(dev)},'1.5':{'over_rate':over([goals(r) for r in dev],1.5),'n':len(dev)},'3.5':{'over_rate':over([goals(r) for r in dev],3.5),'n':len(dev)}},'primary_line':2.5,'n':len(dev)}
    inventory={'league':'CY-1Division','league_id':'136','rows':len(ROWS),'team_rows':len(ROWS)*2,'seasons':per,'distinct_team_ids':len(names),'multi_name_team_ids':{k:sorted(v) for k,v in names.items() if len(v)>1},'phase_values':sorted({r['phase'] for r in ROWS}),'phase_counts':{s:per[s]['phase_counts'] for s in SEASONS},'cards_source_counts':{'events':sum(r['cards_source']=='events' for r in ROWS)},'stats_flag_vs_payload':{'has_stats_flag':sum(r['has_stats_flag']=='1' for r in ROWS),'has_stats_all':source_stats_count},'events_present':source_event_count,'goal_event_score_mismatch':ev_goal_mismatch,'stats_periods':sorted(source_periods),'stats_keys':sorted(source_keys),'team_id_stability':'21 ids; id 468676 has two names; most recent is Karmiotissa'}
    out={'league':'CY-1Division','league_id':'136','n':len(ROWS),'seasons':SEASONS,'per_season':per,'pooled_levels':levels(ROWS),'pooled_dev_levels':levels(dev),'reliability':reliability(ROWS),'halves':{'goals':half(pre_virgin,'goals'),'yellow_cards':half(pre_virgin,'yellow'),'sot':{'n':0,'reason':'no period splits'},'corners':{'n':0,'reason':'no period splits'},'total_shots':{'n':0,'reason':'no period splits'},'definition':'pooled pre-virgin seasons 2021/2022-2024/2025; event-derived first halves'},'dev_line_tables':lines,'windows':{'goals_dev':sorted(GOALS_DEV),'stats_market_dev':sorted(DEV_STATS),'virgin':'2025/2026','confirmatory':'2026/2027'},'inventory':inventory}
    (HERE/'eda_numbers.json').write_text(json.dumps(out,indent=2)); (HERE/'inventory_summary.json').write_text(json.dumps(inventory,indent=2)); print(json.dumps({'n':len(ROWS),'lines':lines,'halves':out['halves'],'levels':per},indent=2))
if __name__=='__main__':main()
