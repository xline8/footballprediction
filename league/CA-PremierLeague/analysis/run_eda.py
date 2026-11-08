"""Phase A descriptive EDA for CA-PremierLeague; never fits a model."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / 'data' / 'ca_matches.csv')))
REG = [r for r in ROWS if r['included'] == '1']
PRE2026 = [r for r in REG if r['season'] != '2026']
DEV = [r for r in REG if r['season'] in {'2021','2022','2023','2024'}]
K_DEV = [r for r in REG if r['season'] in {'2023','2024'}]
VIRGIN = [r for r in REG if r['season'] == '2025']

def val(r,k):
    x=r.get(k); return None if x in (None,'','None') else float(x)
def mean(xs): return round(statistics.mean(xs),6) if xs else None
def corr(x,y):
    if len(x)<2: return None
    mx,my=statistics.mean(x),statistics.mean(y); den=math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/den,6) if den else None
def total(r,k):
    a,b=val(r,k+'_home'),val(r,k+'_away'); return a+b if a is not None and b is not None else None
def other(s): return 'away' if s=='home' else 'home'
def unit_key(r,s): return (r['season'],r[s+'_team_id'])

# Levels. 2026 is inventory-only; it is never passed to trait or halves code.
levels={}
for season in sorted({r['season'] for r in REG},key=int):
    rs=[r for r in REG if r['season']==season]
    def vals(k): return [x for x in (total(r,k) for r in rs) if x is not None]
    levels[season]={'n_regular':len(rs),'status':'in_progress_inventory_only' if season=='2026' else 'complete',
        'goals':mean([float(r['home_goals'])+float(r['away_goals']) for r in rs]),
        'home_goal_diff':mean([float(r['home_goals'])-float(r['away_goals']) for r in rs]),
        'sot':mean(vals('ShotsOnTarget')),'corners':mean(vals('corners')),'total_shots':mean(vals('total_shots')),
        'yellows_stats':mean(vals('stats_yellow')),'stats_n':sum(r['has_stats_all']=='1' for r in rs)}

TRAITS={
 'goals_for':lambda r,s:val(r,s+'_goals'),'goals_against':lambda r,s:val(r,other(s)+'_goals'),
 'sot_for':lambda r,s:val(r,'ShotsOnTarget_'+s),'sot_against':lambda r,s:val(r,'ShotsOnTarget_'+other(s)),
 'corners_for':lambda r,s:val(r,'corners_'+s),'corners_against':lambda r,s:val(r,'corners_'+other(s)),
 'shots_for':lambda r,s:val(r,'total_shots_'+s),'shots_against':lambda r,s:val(r,'total_shots_'+other(s)),
 'possession_for':lambda r,s:val(r,'BallPossesion_'+s),'possession_against':lambda r,s:val(r,'BallPossesion_'+other(s)),
 'big_chance_for':lambda r,s:val(r,'big_chance_'+s),'big_chance_against':lambda r,s:val(r,'big_chance_'+other(s)),
 'yellows_for':lambda r,s:val(r,'stats_yellow_'+s),'yellows_against':lambda r,s:val(r,'stats_yellow_'+other(s))}
def reliability(rows,getter):
    d=defaultdict(list)
    for r in rows:
        for s in ('home','away'):
            x=getter(r,s)
            if x is not None:d[unit_key(r,s)].append(x)
    x=[];y=[]
    for z in d.values():
        if len(z)>=8:x.append(mean(z[0::2]));y.append(mean(z[1::2]))
    return {'r':corr(x,y),'n_units':len(x),'min_matches':8}
pairs={}
for a,b in [('2021','2022'),('2022','2023'),('2023','2024'),('2024','2025')]:
    rs=[r for r in PRE2026 if r['season'] in {a,b}]
    pairs[a+'-'+b]={k:reliability(rs,v) for k,v in TRAITS.items() if not k.startswith('yellows_') or a>='2023'}
yellow_reliability={p:{k:v for k,v in z.items() if k.startswith('yellows_')} for p,z in pairs.items() if p in {'2023-2024','2024-2025'}}

def half_stats(rows,total_fn,first_fn,label):
    use=[r for r in rows if total_fn(r) is not None and first_fn(r) is not None and total_fn(r)>0]
    shares=[first_fn(r)/total_fn(r) for r in use]; p=sum(first_fn(r) for r in use)/sum(total_fn(r) for r in use)
    observed=statistics.pvariance(shares) if shares else 0; noise=mean([p*(1-p)/total_fn(r) for r in use]) or 0; true=max(0,observed-noise)
    return {'label':label,'n_matches':len(use),'share_1h':round(p,6),'observed_variance':round(observed,6),'binomial_poisson_noise_variance':noise,'true_variance':round(true,6),'true_sd':round(math.sqrt(true),6)}
HALF_ROWS=[r for r in REG if r['season'] in {'2023','2024'}]
halves={}
for label,key,first in [('goals','goals',lambda r:val(r,'ht_home_goals')+val(r,'ht_away_goals')),('sot','ShotsOnTarget',lambda r:total(r,'fh_ShotsOnTarget')),('corners','corners',lambda r:total(r,'fh_corners')),('total_shots','total_shots',lambda r:total(r,'fh_total_shots')),('yellows','stats_yellow',lambda r:total(r,'fh_yellow_cards'))]:
    total_fn=(lambda r:float(r['home_goals'])+float(r['away_goals'])) if key=='goals' else (lambda r,k=key:total(r,k))
    halves[label]=half_stats(HALF_ROWS,total_fn,first,label)

# Referee strictness: first/second chronological halves of each named referee.
ref_groups=defaultdict(list)
for r in PRE2026:
    if r['referee']:ref_groups[r['referee']].append(r)
rx=[];ry=[]
for rs in ref_groups.values():
    rs.sort(key=lambda r:(r['date'],r['match_id']))
    if len(rs)>=8:
        mid=len(rs)//2; rx.append(mean([total(r,'stats_yellow') for r in rs[:mid] if total(r,'stats_yellow') is not None])); ry.append(mean([total(r,'stats_yellow') for r in rs[mid:] if total(r,'stats_yellow') is not None]))
ref_cov={s:{'named':sum(bool(r['referee']) for r in ROWS if r['season']==s),'n':sum(r['season']==s for r in ROWS)} for s in sorted({r['season'] for r in ROWS},key=int)}
referee={'coverage_by_season':ref_cov,'split_half_strictness':{'r':corr(rx,ry),'n_referees':len(rx),'min_matches':8}}

# Expansion entry is descriptive: there is no tier corpus in scope.
vancouver='1436202'; rs=[r for r in REG if r['season']=='2023']; league_team_mean=sum(float(r['home_goals'])+float(r['away_goals']) for r in rs)/(2*len(rs)); vr=[r for r in rs if r['home_team_id']==vancouver or r['away_team_id']==vancouver]
vgf=sum(float(r['home_goals'] if r['home_team_id']==vancouver else r['away_goals']) for r in vr)/len(vr); vga=sum(float(r['away_goals'] if r['home_team_id']==vancouver else r['home_goals']) for r in vr)/len(vr)
movers={'class':'expansion_entry_only_no_tier_corpus','vancouver_2023':{'team_id':vancouver,'matches':len(vr),'gf_per_match':round(vgf,6),'ga_per_match':round(vga,6),'league_team_mean':round(league_team_mean,6),'delta_gf':round(vgf-league_team_mean,6),'delta_ga':round(vga-league_team_mean,6)}}

box={'availability_by_season':{s:{'matches':sum(r['season']==s for r in ROWS),'nonmissing':sum(val(r,'touches_opp_box_home') is not None and val(r,'touches_opp_box_away') is not None for r in ROWS if r['season']==s)} for s in sorted({r['season'] for r in ROWS},key=int)},'trailing_min8_dev_seasons':{s:sum(val(r,'touches_opp_box_home') is not None and val(r,'touches_opp_box_away') is not None for r in REG if r['season']==s) for s in ['2021','2022','2023','2024']}}

def line(values,candidates):
    rates={str(q):round(sum(v>q for v in values)/len(values),6) for q in candidates}; q=min(candidates,key=lambda z:abs(rates[str(z)]-.5)); return {'n':len(values),'over_rates':rates,'primary':q}
primary_lines={'G-CA':line([float(r['home_goals'])+float(r['away_goals']) for r in DEV],[1.5,2.5,3.5]),'S-CA':line([total(r,'ShotsOnTarget') for r in DEV if total(r,'ShotsOnTarget') is not None],[7.5,8.5,9.5]),'C-CA':line([total(r,'corners') for r in DEV if total(r,'corners') is not None],[8.5,9.5,10.5]),'K-CA':line([total(r,'stats_yellow') for r in K_DEV if total(r,'stats_yellow') is not None],[3.5,4.5,5.5]),'T-CA':line([total(r,'total_shots') for r in DEV if total(r,'total_shots') is not None],[21.5,22.5,23.5])}
cards_2025=[(total(r,'stats_yellow'),total(r,'ev_yellow')) for r in VIRGIN if total(r,'stats_yellow') is not None]
out={'counts':{'all_matches':len(ROWS),'regular_included':len(REG),'playoffs_excluded':len(ROWS)-len(REG),'regular_by_season':{s:sum(r['season']==s for r in REG) for s in sorted({r['season'] for r in REG},key=int)},'teams':len({r[f'{x}_team_id'] for r in ROWS for x in ('home','away')})},'levels':levels,'reliabilities_by_season_pair':pairs,'yellow_reliabilities_credible':yellow_reliability,'halves_2023_2024':halves,'referee':referee,'movers_x2':movers,'box_touch_availability':box,'possession_big_chance_reliability':{k:v for k,v in pairs['2023-2024'].items() if k.startswith(('possession','big_chance'))},'cards_audit_2025':{'n':len(cards_2025),'exact_total_agreement':sum(a==b for a,b in cards_2025),'stats_mean':mean([a for a,b in cards_2025]),'event_yellow_mean':mean([b for a,b in cards_2025])},'primary_lines':primary_lines,'contradictions':[]}
json.dump(out,open(HERE/'eda_numbers.json','w'),indent=2); print(json.dumps(out,indent=2))
