import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'ca_matches.csv'
SEASONS=('2021','2022','2023','2024'); SCORED=('2022','2023','2024'); ARMS=('gate_zero','shrink')
def load():
    out=[]
    with DATA.open(newline='') as f:
        for r in csv.DictReader(f):
            if r['season'] not in SEASONS or r['phase']!='regular' or r['included']!='1': continue
            out.append({'match_id':r['match_id'],'season':r['season'],'date':date.fromisoformat(r['date']),'hi':int(r['home_team_id']),'ai':int(r['away_team_id']),'home':r['home_team'],'away':r['away_team'],'yh':int(float(r['home_goals'])),'ya':int(float(r['away_goals']))})
    assert not any(str(x['date'].year) in {'2025','2026'} for x in out)
    return sorted(out,key=lambda x:(x['date'],x['match_id']))
def ll(p,y): return -math.log(max(p[y],1e-12))
def score(rows,ps):
    a={'n':len(rows),'ll_1x2':0.,'rps':0.,'oull_2_5':0.}
    for r,p in zip(rows,ps):
        y=0 if r['yh']>r['ya'] else 1 if r['yh']==r['ya'] else 2; q=[p['ph'],p['pd'],p['pa']]
        a['ll_1x2']+=ll(q,y); yy=[int(y==i) for i in range(3)]; a['rps']+=.5*((q[0]-yy[0])**2+(q[0]+q[1]-yy[0]-yy[1])**2); o=int(r['yh']+r['ya']>2.5); a['oull_2_5']+=-math.log(max(p['over25'] if o else 1-p['over25'],1e-12))
    for k in ('ll_1x2','rps','oull_2_5'): a[k]/=len(rows)
    return a
def run_dev():
    rows=load(); result=[]; pred=[]
    for s in SCORED:
        target=[r for r in rows if r['season']==s]; train=[r for r in rows if r['date']<min(x['date'] for x in target)]
        cp=[sum(x['yh']>x['ya'] for x in train)/len(train),sum(x['yh']==x['ya'] for x in train)/len(train)]; cp.append(1-sum(cp)); co=sum(x['yh']+x['ya']>2.5 for x in train)/len(train)
        for arm in ARMS:
            m=DC().fit(train,min(x['date'] for x in target)); counts=match_counts(train); ps=[]
            for r in target:
                lh,la=adjusted_lambdas(m,r['hi'],r['ai'],arm,set(),(0,0),counts,m.mu); p=m.probs(lh,la); ps.append(p)
                pred.append({'arm':arm,'season':s,'match_id':r['match_id'],'date':r['date'].isoformat(),'home_team':r['home'],'away_team':r['away'],'actual_home_goals':r['yh'],'actual_away_goals':r['ya'],'p_home':p['ph'],'p_draw':p['pd'],'p_away':p['pa'],'p_over_2.5':p['over25']})
            z=score(target,ps); z.update(arm=arm,season=s,kind='model'); result.append(z)
        for r in target: pred.append({'arm':'baseline_climatology','season':s,'match_id':r['match_id'],'date':r['date'].isoformat(),'home_team':r['home'],'away_team':r['away'],'actual_home_goals':r['yh'],'actual_away_goals':r['ya'],'p_home':cp[0],'p_draw':cp[1],'p_away':cp[2],'p_over_2.5':co})
        cpred=[{'ph':cp[0],'pd':cp[1],'pa':cp[2],'over25':co} for _ in target]; z=score(target,cpred); z.update(arm='baseline_climatology',season=s,kind='baseline'); result.append(z)
    pooled_rows=[r for r in rows if r['season'] in SCORED]
    for arm in ARMS: result.append({**score(pooled_rows,[{'ph':x['p_home'],'pd':x['p_draw'],'pa':x['p_away'],'over25':x['p_over_2.5']} for x in pred if x['arm']==arm]),'arm':arm,'season':'pooled','kind':'model'})
    result.append({**score(pooled_rows,[{'ph':x['p_home'],'pd':x['p_draw'],'pa':x['p_away'],'over25':x['p_over_2.5']} for x in pred if False]),'arm':'baseline_climatology','season':'pooled','kind':'baseline'} if False else {})
    # Recompute pooled baseline from the per-season prior-only rates.
    bp=[]
    for s in SCORED:
        t=[r for r in rows if r['season']==s]; tr=[r for r in rows if r['date']<min(x['date'] for x in t)]; q=[sum(x['yh']>x['ya'] for x in tr)/len(tr),sum(x['yh']==x['ya'] for x in tr)/len(tr)]; q.append(1-sum(q)); o=sum(x['yh']+x['ya']>2.5 for x in tr)/len(tr); bp += [{'ph':q[0],'pd':q[1],'pa':q[2],'over25':o} for _ in t]
    result=[x for x in result if x]
    result.append({**score(pooled_rows,bp),'arm':'baseline_climatology','season':'pooled','kind':'baseline'})
    fields=['arm','season','kind','match_id','date','home_team','away_team','actual_home_goals','actual_away_goals','p_home','p_draw','p_away','p_over_2.5']
    with (HERE/'predictions_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(pred)
    (HERE/'results_dev.json').write_text(json.dumps({'protocol':{'warmup':'2021','scored':list(SCORED),'rows_loaded':len(rows)},'results':result},indent=2)+'\n')
    with (HERE/'results_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=['arm','season','kind','n','ll_1x2','rps','oull_2_5']); w.writeheader(); w.writerows({k:x.get(k) for k in w.fieldnames} for x in result)
    print(json.dumps(result,indent=2))
if __name__=='__main__': run_dev()
