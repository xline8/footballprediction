import csv, json, math, statistics as st
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE.parent/'data'/'cla_matches.csv').open()))
def f(v):
    try: return float(v)
    except: return None
# Modelling population: finished + regular only (playoffs and the 62
# never-started 2021 placeholders excluded; see PREPROCESSING).
pop=[r for r in rows if r['finished']=='1' and r['phase']=='regular']
out={}
seasons=sorted(set(r['season'] for r in pop))
out['seasons']={}
for s in seasons:
    sub=[r for r in pop if r['season']==s]
    def mean(key):
        vs=[f(r[key]) for r in sub]; vs=[v for v in vs if v is not None]; return round(sum(vs)/len(vs),4) if vs else None
    def tot(kh,ka):
        vs=[(f(r[kh]),f(r[ka])) for r in sub]; vs=[v for v in vs if v[0] is not None and v[1] is not None]
        return round(sum(a+b for a,b in vs)/len(vs),4) if vs else None
    out['seasons'][s]={
      'n':len(sub),'teams':len(set([r['home_team_id'] for r in sub]+[r['away_team_id'] for r in sub])),
      'goals':tot('home_goals','away_goals'),'home_goals':mean('home_goals'),'away_goals':mean('away_goals'),
      'home_win_rate':round(sum(1 for r in sub if f(r['home_goals'])>f(r['away_goals']))/len(sub),4),
      'ou25_rate':round(sum(1 for r in sub if f(r['home_goals'])+f(r['away_goals'])>2.5)/len(sub),4),
      'sot':tot('ShotsOnTarget_home','ShotsOnTarget_away'),'corners':tot('corners_home','corners_away'),
      'total_shots_stat':tot('total_shots_home','total_shots_away'),
      'yellow_stats':tot('yellow_cards_home','yellow_cards_away'),
      'yellow_events':tot('ev_yellow_home','ev_yellow_away'),
      'stats_cov':round(sum(int(r['has_stats_all']) for r in sub)/len(sub),4),
      'half_cov':round(sum(int(r['has_stats_half']) for r in sub)/len(sub),4),
      'ref_cov':round(sum(1 for r in sub if r['referee'])/len(sub),4),
      'xg_present':sum(1 for r in sub if f(r['expected_goals_home']) is not None),
      'shotmap':sum(int(r['has_shotmap']) for r in sub),
      'events_cov':round(sum(int(r['has_events']) for r in sub)/len(sub),4),
      'goal_events_complete':sum(int(r['goals_events_complete']) for r in sub)}
out['inventory']={}
_idx=list(csv.DictReader(open(Path.home()/'workspace'/'footballprediction'/'data_enrichment'/'fotmob_world_index.csv')))
_flag={}
for r in _idx:
    if r['league_id']=='9126' and r['has_stats']=='True': _flag[r['season']]=_flag.get(r['season'],0)+1
for s in sorted(set(r['season'] for r in rows)):
    sub=[r for r in rows if r['season']==s]
    out['inventory'][s]={'rows':len(sub),'finished':sum(int(r['finished']) for r in sub),
      'finished_regular':sum(1 for r in sub if r['finished']=='1' and r['phase']=='regular'),
      'finished_playoff':sum(1 for r in sub if r['finished']=='1' and r['phase']=='playoff'),
      'unfinished':sum(1 for r in sub if r['finished']=='0'),
      'stats_flag_index':_flag.get(s,0),
      'stats_content_rows':sum(int(r['has_stats_all']) for r in sub),
      'dates':[min(r['date'] for r in sub), max(r['date'] for r in sub)]}
# cards artefact check: stats source does not exist; event plain yellows per season (ALL rows)
out['cards_check']={}
for s in sorted(set(r['season'] for r in rows)):
    sub=[r for r in rows if r['season']==s]
    both=[r for r in sub if f(r['yellow_cards_home']) is not None]
    out['cards_check'][s]={'n_stats_rows':len(both),
      'event_plain_yellows_total':int(sum(f(r['ev_yellow_direct_home'])+f(r['ev_yellow_direct_away']) for r in sub)),
      'event_yellowred_total':int(sum(f(r['ev_yellowred_home'])+f(r['ev_yellowred_away']) for r in sub)),
      'event_red_total':int(sum(f(r['ev_red_home'])+f(r['ev_red_away']) for r in sub)),
      'matches_with_any_event':sum(int(r['has_events']) for r in sub)}
def halves(pairs):
    shares=[a/b for a,b in pairs if b and b>0]
    if not shares: return {'n':0,'pooled_share':None}
    mu=sum(shares)/len(shares)
    samp=sum(mu*(1-mu)/b for a,b in pairs if b and b>0)/len(shares)
    var_obs=st.pvariance(shares)
    return {'n':len(shares),'share_mean_of_ratios':round(mu,4),'pooled_share':round(sum(a for a,b in pairs)/sum(b for a,b in pairs),4),'var_obs':round(var_obs,5),'binom_sampling_var':round(samp,5),'true_var_est':round(max(var_obs-samp,0.0),5)}
out['halves']={}
dev=[r for r in pop if r['season'] in ('2022','2023','2024') and r['goals_events_complete']=='1']
g=[(f(r['ht_home_goals'])+f(r['ht_away_goals']), f(r['home_goals'])+f(r['away_goals'])) for r in dev]
out['halves']['goals_events_dev2022_2024_complete']=halves(g)
dev25=[r for r in pop if r['season'] in ('2022','2023','2024','2025') and r['goals_events_complete']=='1']
g2=[(f(r['ht_home_goals'])+f(r['ht_away_goals']), f(r['home_goals'])+f(r['away_goals'])) for r in dev25]
out['halves']['goals_events_2022_2025_complete_REFERENCE_ONLY']=halves(g2)
out['halves']['stats_markets']='no period splits and no All-period stats exist in any season: no halves source for SOT/corners/cards/total_shots'
tm=[r for r in csv.DictReader((HERE.parent/'data'/'cla_team_matches.csv').open()) if r['finished']=='1' and r['phase']=='regular']
def reliability(forkey, agkey=None):
    by=defaultdict(list)
    for r in tm: by[(r['team_id'],r['season'])].append(r)
    xs,ys=[],[]
    for k,v in by.items():
        v.sort(key=lambda r:(r['date'],r['match_id']))
        if len(v)<10: continue
        h=len(v)//2
        def rate(part):
            a=[f(r[forkey]) for r in part]; a=[x for x in a if x is not None]
            if agkey:
                b=[f(r[agkey]) for r in part]; b=[x for x in b if x is not None]
                return sum(b)/len(b) if b else None
            return sum(a)/len(a) if a else None
        x,y=rate(v[:h]),rate(v[h:])
        if x is not None and y is not None: xs.append(x); ys.append(y)
    if len(xs)<10: return {'n':len(xs),'r':None}
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys)
    cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); vx=sum((a-mx)**2 for a in xs); vy=sum((b-my)**2 for b in ys)
    return {'n':len(xs),'r':round(cov/math.sqrt(vx*vy),3) if vx>0 and vy>0 else None}
out['reliability']={
 'goals_for':reliability('goals_for'),'goals_against':reliability('goals_against'),
 'sot_for':reliability('ShotsOnTarget_for'),'corners_for':reliability('corners_for'),
 'shots_for':reliability('total_shots_for'),'yellows_events':reliability('yellow_events_for'),
 'box_touches_for':reliability('touches_opp_box_for')}
out['referee']={'matches_with_ref':sum(1 for r in rows if r['referee']),
  'by_season':{s:sum(1 for r in rows if r['season']==s and r['referee']) for s in sorted(set(r['season'] for r in rows))}}
ids=defaultdict(set)
for r in rows:
    ids[r['home_team_id']].add(r['home_team_raw']); ids[r['away_team_id']].add(r['away_team_raw'])
out['multi_name_ids']={k:sorted(v) for k,v in ids.items() if len(v)>1}
out['n_team_ids']=len(ids)
print(json.dumps(out,indent=1,ensure_ascii=False))
(HERE/'eda_numbers.json').write_text(json.dumps(out,indent=1,ensure_ascii=False))
(HERE/'inventory_summary.json').write_text(json.dumps(out['inventory'],indent=1,ensure_ascii=False))
