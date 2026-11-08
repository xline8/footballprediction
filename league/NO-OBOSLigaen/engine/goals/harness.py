import csv,json,math
from collections import Counter
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas,transition_offset
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'data/no_obos_matches.csv'; OUT=Path(__file__).resolve().parent
SEASONS=('2021','2022','2023','2024','2025'); SCORED=('2022','2023','2024','2025')
def num(v): return None if v in (None,'') else float(v)
def load(path,allowed):
    assert '2026' not in allowed; out=[]
    with open(path,newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['season'] not in allowed: continue
            out.append({'match_id':r['match_id'],'season':r['season'],'date':date.fromisoformat(r['date']),'hi':int(r['home_team_id']),'ai':int(r['away_team_id']),'home':r['home_team'],'away':r['away_team'],'yh':int(r['home_goals']),'ya':int(r['away_goals']),'xgh':num(r['expected_goals_home']),'xga':num(r['expected_goals_away']),'oph':num(r['expected_goals_open_play_home']),'opa':num(r['expected_goals_open_play_away']),'sph':num(r['expected_goals_set_play_home']),'spa':num(r['expected_goals_set_play_away'])})
    return sorted(out,key=lambda x:(x['date'],x['match_id']))
def score(rows,ps):
    vals=[]
    for r,p in zip(rows,ps):
        over=int(r['yh']+r['ya']>2.5); h=int(r['yh']>r['ya']); d=int(r['yh']==r['ya'])
        vals.append({'ou':-math.log(max(p['over25'] if over else 1-p['over25'],1e-12)),'x12':-math.log(max(p['ph'] if h else p['pd'] if d else p['pa'],1e-12)),'rps':.5*((p['ph']-h)**2+(p['ph']+p['pd']-h-d)**2)})
    n=len(vals); return {'n':n,'ou2.5_ll':sum(x['ou'] for x in vals)/n,'1x2_ll':sum(x['x12'] for x in vals)/n,'rps':sum(x['rps'] for x in vals)/n}
def clim(train):
    n=len(train); return sum(r['yh']>r['ya'] for r in train)/n,sum(r['yh']==r['ya'] for r in train)/n,sum(r['yh']+r['ya']>2.5 for r in train)/n
def metrics(recs):
    out={'pooled':score([r for r,p in recs],[p for r,p in recs]),'seasons':{}}
    for s in SCORED:
        z=[x for x in recs if x[0]['season']==s]; out['seasons'][s]=score([r for r,p in z],[p for r,p in z])
    out['n']=out['pooled']['n']; return out
def load_parent(): return load(Path.home()/'workspace/footballprediction/league/NO-Eliteserien/data/no_matches.csv',set(SEASONS))
def run_dev():
    rows=load(DATA,set(SEASONS)); parent=load_parent(); result={'protocol':'G-NO-OBOS DEV; 2026 excluded','primary_line':2.5,'arms':{},'baselines':{},'x2_offsets':{}}; allarms={}
    for arm in ('GZ','SHR','X2'):
        recs=[]
        for s in SCORED:
            target=[r for r in rows if r['season']==s]; cutoff=min(r['date'] for r in target); train=[r for r in rows if r['date']<cutoff]; model=DC().fit(train,cutoff); counts=Counter(t for r in train for t in (r['hi'],r['ai'])); off=transition_offset(rows,parent,s); result['x2_offsets'][s]={'d_att':off[0],'d_def':off[1],'n_transitions':off[2]}
            for r in target:
                lh,la=adjusted_lambdas(model,r['hi'],r['ai'],arm.lower(),counts,off); p=model.probs(lh,la); p.update({'lam_home':lh,'lam_away':la}); recs.append((r,p))
        allarms[arm]=recs; result['arms'][arm]=metrics(recs)
    result['baselines']['climatology']=baseline(rows); write_outputs(result,allarms,rows); return result
def baseline(rows):
    recs=[]
    for s in SCORED:
        tr=[r for r in rows if int(r['season'])<int(s)]; hw,dr,ou=clim(tr)
        recs += [(r,{'ph':hw,'pd':dr,'pa':1-hw-dr,'over25':ou}) for r in rows if r['season']==s]
    return metrics(recs)
def write_outputs(result,arms,rows):
    (OUT/'results_dev.json').write_text(json.dumps(result,indent=2)+'\n'); fields=['arm','season','match_id','p_over_2_5','lam_home','lam_away','p_home','p_draw','p_away','actual_over_2_5']
    with open(OUT/'results_dev.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for arm,recs in arms.items():
            for r,p in recs: w.writerow({'arm':arm,'season':r['season'],'match_id':r['match_id'],'p_over_2_5':p['over25'],'lam_home':p['lam_home'],'lam_away':p['lam_away'],'p_home':p['ph'],'p_draw':p['pd'],'p_away':p['pa'],'actual_over_2_5':int(r['yh']+r['ya']>2.5)})
        for s in SCORED:
            tr=[r for r in rows if int(r['season'])<int(s)]; hw,dr,ou=clim(tr)
            for r in rows:
                if r['season']==s: w.writerow({'arm':'CLIM','season':s,'match_id':r['match_id'],'p_over_2_5':ou,'p_home':hw,'p_draw':dr,'p_away':1-hw-dr,'actual_over_2_5':int(r['yh']+r['ya']>2.5)})
