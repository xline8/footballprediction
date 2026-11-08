import csv, json, math, statistics as st
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent
rows=list(csv.DictReader((HERE.parent/'data'/'cl_matches.csv').open()))
def f(v):
    try: return float(v)
    except: return None
out={}
seasons=sorted(set(r['season'] for r in rows))
out['seasons']={}
for s in seasons:
    sub=[r for r in rows if r['season']==s]
    def mean(key): 
        vs=[f(r[key]) for r in sub]; vs=[v for v in vs if v is not None]; return round(sum(vs)/len(vs),4) if vs else None
    def tot(kh,ka):
        vs=[(f(r[kh]),f(r[ka])) for r in sub]; vs=[v for v in vs if v[0] is not None and v[1] is not None]
        return round(sum(a+b for a,b in vs)/len(vs),4) if vs else None
    out['seasons'][s]={
      'n':len(sub),'teams':len(set([r['home_team_id'] for r in sub]+[r['away_team_id'] for r in sub])),
      'goals':tot('home_goals','away_goals'),'home_goals':mean('home_goals'),'away_goals':mean('away_goals'),
      'sot':tot('ShotsOnTarget_home','ShotsOnTarget_away'),'corners':tot('corners_home','corners_away'),
      'total_shots_stat':tot('total_shots_home','total_shots_away'),
      'yellow_stats':tot('yellow_cards_home','yellow_cards_away'),
      'yellow_events':tot('ev_yellow_home','ev_yellow_away'),
      'fouls':tot('fouls_home','fouls_away'),
      'stats_cov':round(sum(int(r['has_stats_all']) for r in sub)/len(sub),4),
      'half_cov':round(sum(int(r['has_stats_half']) for r in sub)/len(sub),4),
      'ref_cov':round(sum(1 for r in sub if r['referee'])/len(sub),4),
      'xg_present':sum(1 for r in sub if f(r['expected_goals_home']) is not None),
      'shotmap':sum(int(r['has_shotmap']) for r in sub)}
# cards artefact: stats vs events agreement per season
out['cards_check']={}
for s in seasons:
    sub=[r for r in rows if r['season']==s]
    both=[r for r in sub if f(r['yellow_cards_home']) is not None]
    exact=sum(1 for r in both if f(r['yellow_cards_home'])==f(r['ev_yellow_home']) and f(r['yellow_cards_away'])==f(r['ev_yellow_away']))
    diffs=[(f(r['yellow_cards_home'])+f(r['yellow_cards_away']))-(f(r['ev_yellow_home'])+f(r['ev_yellow_away'])) for r in both]
    ev_plain=sum(f(r['ev_yellow_direct_home'])+f(r['ev_yellow_direct_away']) for r in sub)
    out['cards_check'][s]={'n_stats':len(both),'exact_agree':exact,'mean_stats_minus_events':round(sum(diffs)/len(diffs),4) if diffs else None,'event_plain_yellows_total':ev_plain}
# total shots identity: total_shots == SOT+off+blocked?
sub=[r for r in rows if f(r['total_shots_home']) is not None and f(r['ShotsOffTarget_home']) is not None]
ok=sum(1 for r in sub if f(r['total_shots_home'])==f(r['ShotsOnTarget_home'])+f(r['ShotsOffTarget_home'])+f(r['blocked_shots_home']) and f(r['total_shots_away'])==f(r['ShotsOnTarget_away'])+f(r['ShotsOffTarget_away'])+f(r['blocked_shots_away']))
sot_off=sum(1 for r in sub if f(r['total_shots_home'])==f(r['ShotsOnTarget_home'])+f(r['ShotsOffTarget_home']))
out['total_shots_identity']={'n':len(sub),'eq_sot_off_blocked':ok,'eq_sot_off_only':sot_off}
# halves shares + noise: per market, 1H share of total using fh_ splits (2023+), and goals via ht events (all seasons)
def halves(pairs):
    # pairs: list of (h1,total)
    shares=[a/b for a,b in pairs if b and b>0]
    mu=sum(shares)/len(shares)
    # true variance: var_obs - mean sampling var under binomial p=mu
    samp=sum(mu*(1-mu)/b for a,b in pairs if b and b>0)/len(shares)
    var_obs=st.pvariance(shares)
    return {'n':len(shares),'share_mean_of_ratios':round(mu,4),'pooled_share':round(sum(a for a,b in pairs)/sum(b for a,b in pairs),4),'var_obs':round(var_obs,5),'binom_sampling_var':round(samp,5),'true_var_est':round(max(var_obs-samp,0.0),5)}
out['halves']={}
g=[(f(r['ht_home_goals'])+f(r['ht_away_goals']), f(r['home_goals'])+f(r['away_goals'])) for r in rows]
out['halves']['goals_events_all']=halves(g)
for mk,fh,tt in [('sot','fh_ShotsOnTarget_home','ShotsOnTarget_home'),('corners','fh_corners_home','corners_home'),('total_shots','fh_total_shots_home','total_shots_home'),('cards','fh_yellow_cards_home','yellow_cards_home')]:
    pr=[]
    for r in rows:
        if f(r[fh]) is not None:
            h1=f(r[fh])+f(r[fh.replace('_home','_away')]); tot=f(r[tt])+f(r[tt.replace('_home','_away')]); pr.append((h1,tot))
    out['halves'][mk]=halves(pr)
# split-half reliability: per team-season, chron halves, corr of trait rates
tm=list(csv.DictReader((HERE.parent/'data'/'cl_team_matches.csv').open()))
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
            b=[f(r[agkey]) for r in part] if agkey else None
            if agkey: 
                bb=[x for x in b if x is not None]; return sum(bb)/len(bb) if bb else None
            return sum(a)/len(a) if a else None
        x,y=rate(v[:h]),rate(v[h:])
        if x is not None and y is not None: xs.append(x); ys.append(y)
    if len(xs)<10: return {'n':len(xs),'r':None}
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys)
    cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); vx=sum((a-mx)**2 for a in xs); vy=sum((b-my)**2 for b in ys)
    return {'n':len(xs),'r':round(cov/math.sqrt(vx*vy),3) if vx>0 and vy>0 else None}
out['reliability']={
 'goals_for':reliability('goals_for'),'goals_against':reliability('goals_against'),
 'sot_for':reliability('ShotsOnTarget_for'),'sot_against':reliability('ShotsOnTarget_against'),
 'corners_for':reliability('corners_for'),'corners_against':reliability('corners_against'),
 'shots_for':reliability('total_shots_for'),'shots_against':reliability('total_shots_against'),
 'yellows_for_stats':reliability('yellow_cards_for'),'yellows_events':reliability('yellow_events_for'),
 'box_touches_for':reliability('touches_opp_box_for')}
# referee strictness reliability: per referee-season halves by match count of total yellows (stats)
by=defaultdict(list)
for r in rows:
    if r['referee']: by[r['referee']].append(r)
xs,ys=[],[]
for k,v in by.items():
    if len(v)<10: continue
    v.sort(key=lambda r:(r['date'],r['match_id'])); h=len(v)//2
    def m(part): 
        a=[f(r['yellow_cards_home'])+f(r['yellow_cards_away']) for r in part if f(r['yellow_cards_home']) is not None]; return sum(a)/len(a)
    xs.append(m(v[:h])); ys.append(m(v[h:]))
if len(xs)>=5:
    mx,my=sum(xs)/len(xs),sum(ys)/len(ys); cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys)); vx=sum((a-mx)**2 for a in xs); vy=sum((b-my)**2 for b in ys)
    out['referee']={'n_refs_split':len(xs),'r':round(cov/math.sqrt(vx*vy),3),'n_refs_total':len(by),'matches_with_ref':sum(len(v) for v in by.values())}
# team name/id stability
ids=defaultdict(set)
for r in rows:
    ids[r['home_team_id']].add(r['home_team_raw'] if 'home_team_raw' in r else r['home_team']); ids[r['away_team_id']].add(r['away_team_raw'] if 'away_team_raw' in r else r['away_team'])
out['multi_name_ids']={k:sorted(v) for k,v in ids.items() if len(v)>1}
out['n_team_ids']=len(ids)
print(json.dumps(out,indent=1,ensure_ascii=False))
(HERE/'eda_numbers.json').write_text(json.dumps(out,indent=1,ensure_ascii=False))
