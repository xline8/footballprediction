import csv,json,math
from datetime import date
from pathlib import Path
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'ca_matches.csv'
def load():
    out=[]
    with DATA.open(newline='') as f:
        for r in csv.DictReader(f):
            if r['season'] not in ('2023','2024') or r['phase']!='regular' or r['included']!='1': continue
            y=int(float(r['stats_yellow_home']))+int(float(r['stats_yellow_away'])); d=date.fromisoformat(r['date']); out.append({'match_id':r['match_id'],'season':r['season'],'date':r['date'],'day':d.toordinal(),'kickoff_utc':r['date']+'T00:00:00Z','home_id':int(r['home_team_id']),'away_id':int(r['away_team_id']),'home':r['home_team'],'away':r['away_team'],'yh':int(float(r['stats_yellow_home'])),'ya':int(float(r['stats_yellow_away'])),'y':y,'referee':''})
    assert all(x['season'] in ('2023','2024') for x in out); return sorted(out,key=lambda x:(x['day'],x['match_id']))
def run_dev():
    rows=load(); online=Online(); warm=[]; scored=[]; pred=[]
    for r in rows:
        p=online.prediction(r,'gate_zero'); (warm if r['season']=='2023' else scored).append((r,p)); online.update(r)
    fit=[{'y':r['y'],'model':p['model'],'base':p['base'],'naive':p['naive']} for r,p in warm]; rs={k:estimate_r(fit,k) for k in ('model','base','naive')}; result=[]
    for kind in ('model','base','naive'):
        ps=[nb_over(p[kind],rs[kind],4.5) for r,p in scored]; ys=[int(r['y']>4.5) for r,p in scored]; result.append({'arm':'gate_zero','season':'2024','kind':kind,'n':len(ys),'ll_4.5':sum(-(y*math.log(max(q,1e-12))+(1-y)*math.log(max(1-q,1e-12))) for q,y in zip(ps,ys))/len(ys)})
        for r,p in scored: pred.append({'arm':'gate_zero','season':r['season'],'match_id':r['match_id'],'date':r['date'],'home_team':r['home'],'away_team':r['away'],'actual_total_yellows':r['y'],'p_over_4.5':nb_over(p[kind],rs[kind],4.5) if kind=='model' else ''}) if kind=='model' else None
    for r,p in scored:
        for arm,key in (('baseline_base_rate','base'),('baseline_naive','naive')):
            pred.append({'arm':arm,'season':r['season'],'match_id':r['match_id'],'date':r['date'],'home_team':r['home'],'away_team':r['away'],'actual_total_yellows':r['y'],'p_over_4.5':nb_over(p[key],rs[key],4.5)})
    (HERE/'results_dev.json').write_text(json.dumps({'protocol':{'warmup':'2023','scored':['2024'],'rows_loaded':len(rows),'target':'stats_yellow_home + stats_yellow_away'},'results':result},indent=2)+'\n')
    with (HERE/'results_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=['arm','season','kind','n','ll_4.5']); w.writeheader(); w.writerows(result)
    with (HERE/'predictions_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=sorted(pred[0])); w.writeheader(); w.writerows(pred)
    print(json.dumps(result,indent=2))
if __name__=='__main__': run_dev()
