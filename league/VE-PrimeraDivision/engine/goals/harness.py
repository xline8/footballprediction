import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas, match_counts

HERE = Path(__file__).resolve().parent; DATA = HERE.parents[1] / 'data' / 've_matches.csv'
SEED=('2021','2022'); DEV=('2023','2024'); VIRGIN='2025'; PRIMARY=2.5; HALF=0.4478

def load():
    out=[]
    with DATA.open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['season'] not in set(SEED+DEV) or r['phase']!='regular': continue
            out.append({'match_id':r['match_id'],'season':r['season'],'date':date.fromisoformat(r['date']),'hi':r['home_team_id'],'ai':r['away_team_id'],'home':r['home_team'],'away':r['away_team'],'yh':int(float(r['home_goals'])),'ya':int(float(r['away_goals'])),'xgh':None,'xga':None})
    return sorted(out,key=lambda x:(x['date'],x['match_id']))

def score(rows,ps):
    ll=rps=ou=0.0
    for r,p in zip(rows,ps):
        y=(1,0,0) if r['yh']>r['ya'] else ((0,1,0) if r['yh']==r['ya'] else (0,0,1)); q=[p['ph'],p['pd'],p['pa']]
        ll-=math.log(max(q[y.index(1)],1e-12)); rps+=.5*((q[0]-y[0])**2+(q[0]+q[1]-y[0]-y[1])**2)
        z=r['yh']+r['ya']>PRIMARY; ou-=math.log(max(p['over25'] if z else 1-p['over25'],1e-12))
    return {'n':len(rows),'ll_1x2':ll/len(rows),'rps':rps/len(rows),'oull_2_5':ou/len(rows)}

def clim(train):
    n=len(train); h=sum(r['yh']>r['ya'] for r in train)/n; d=sum(r['yh']==r['ya'] for r in train)/n; return [h,d,1-h-d],sum(r['yh']+r['ya']>PRIMARY for r in train)/n

def run_dev():
    rows=load(); assert not any(r['season'] in ('2025','2026') for r in rows)
    result=[]; pooled={a:[] for a in ('gate_zero','shrink')}; cpooled=[]
    for s in DEV:
        target=[r for r in rows if r['season']==s]; cutoff=min(r['date'] for r in target); train=[r for r in rows if r['date']<cutoff]
        base,o=clim(train)
        for arm in ('gate_zero','shrink'):
            m=DC().fit(train,cutoff); counts=match_counts(train); ps=[m.probs(*adjusted_lambdas(m,r['hi'],r['ai'],arm,counts)) for r in target]
            x=score(target,ps); x.update(arm=arm,season=s,kind='model'); result.append(x); pooled[arm].extend(zip(target,ps))
            cp=[{'ph':base[0],'pd':base[1],'pa':base[2],'over25':o} for _ in target]
            x=score(target,cp); x.update(arm=arm,season=s,kind='climatology'); result.append(x)
            if arm=='gate_zero': cpooled.extend(zip(target,cp))
    for arm in ('gate_zero','shrink'):
        x=score([r for r,p in pooled[arm]],[p for r,p in pooled[arm]]); x.update(arm=arm,season='pooled',kind='model'); result.append(x)
        x=score([r for r,p in cpooled],[p for r,p in cpooled]); x.update(arm=arm,season='pooled',kind='climatology'); result.append(x)
    (HERE/'results_dev.json').write_text(json.dumps(result,indent=2)+'\n'); print('dev'); print('arm season kind n ll_1x2 rps oull_2_5')
    for x in result: print(x['arm'],x['season'],x['kind'],x['n'],f"{x['ll_1x2']:.6f}",f"{x['rps']:.6f}",f"{x['oull_2_5']:.6f}")
    return result

def _se(values):
    m=sum(values)/len(values)
    return (sum((x-m)**2 for x in values)/(len(values)-1))**.5/(len(values)**.5)

def run_virgin(dev_result):
    dev_model={(x['arm'],x['season']):x for x in dev_result if x['kind']=='model'}
    dev_base=next(x for x in dev_result if x['arm']=='gate_zero' and x['season']=='pooled' and x['kind']=='climatology')
    dev_pass={a: (next(x for x in dev_result if x['arm']==a and x['season']=='pooled' and x['kind']=='model')['ll_1x2'] < dev_base['ll_1x2'] and next(x for x in dev_result if x['arm']==a and x['season']=='pooled' and x['kind']=='model')['rps'] < dev_base['rps'] and next(x for x in dev_result if x['arm']==a and x['season']=='pooled' and x['kind']=='model')['oull_2_5'] < dev_base['oull_2_5']) for a in ('gate_zero','shrink')}
    if not dev_pass['gate_zero']:
        out={'verdict':'FAIL','virgin_read':False,'reason':'Gate Zero failed the dev gate; 2025 virgin NOT read','read_arms':[],'dev_pass':dev_pass}
        (HERE/'results_virgin.json').write_text(json.dumps(out,indent=2)+'\n')
        return out
    rows=load(); target=[r for r in csv.DictReader(DATA.open(newline='',encoding='utf-8')) if r['season']==VIRGIN and r['phase']=='regular']
    # Reuse the same typed loader shape while keeping the virgin read explicit.
    target=[{'match_id':r['match_id'],'season':r['season'],'date':date.fromisoformat(r['date']),'hi':r['home_team_id'],'ai':r['away_team_id'],'home':r['home_team'],'away':r['away_team'],'yh':int(float(r['home_goals'])),'ya':int(float(r['away_goals'])),'xgh':None,'xga':None} for r in target]
    train=[r for r in rows if r['date'] < min(x['date'] for x in target)]
    base,o=clim(train); results={}; eligible=[]
    for arm in ('gate_zero','shrink'):
        if not dev_pass[arm]: continue
        m=DC().fit(train,min(x['date'] for x in target)); counts=match_counts(train); ps=[m.probs(*adjusted_lambdas(m,r['hi'],r['ai'],arm,counts)) for r in target]
        x=score(target,ps); home=[p['ph']-(r['yh']>r['ya']) for r,p in zip(target,ps)]; over=[p['over25']-(r['yh']+r['ya']>2.5) for r,p in zip(target,ps)]
        cal={'home_win_actual_minus_predicted_pp':-100*sum(home)/len(home),'home_win_se_pp':100*_se(home),'ou25_actual_minus_predicted_pp':-100*sum(over)/len(over),'ou25_se_pp':100*_se(over)}
        def status(v,se): return 'CLEAN' if abs(v)<=1 else ('PROVISIONAL' if abs(v)<=1+se else 'FAIL')
        cal['home_win_status']=status(cal['home_win_actual_minus_predicted_pp'],cal['home_win_se_pp']); cal['ou25_status']=status(cal['ou25_actual_minus_predicted_pp'],cal['ou25_se_pp'])
        x.update(arm=arm,climatology=score(target,[{'ph':base[0],'pd':base[1],'pa':base[2],'over25':o} for _ in target]),calibration=cal,params={'arm':arm,'h':m.h,'rho':m.rho,'mu':m.mu,'a':dict(m.a),'d':dict(m.d),'match_counts':dict(counts)})
        x['leg_i']=x['ll_1x2']<=next(v for a,v in results.items() if a=='gate_zero')['ll_1x2'] if results else True
        x['leg_ii']=cal['home_win_status'] in ('CLEAN','PROVISIONAL') and cal['ou25_status'] in ('CLEAN','PROVISIONAL')
        x['leg_iii']=arm=='gate_zero' or sum(dev_model[(arm,s)]['ll_1x2']<=dev_model[('gate_zero',s)]['ll_1x2'] for s in DEV)>=len(DEV)/2
        results[arm]=x
    # Gate Zero is the reference even when encountered first; add its climatology comparison.
    for arm,x in results.items(): x['leg_i']=x['ll_1x2']<=results['gate_zero']['ll_1x2'] and x['ll_1x2']<=x['climatology']['ll_1x2']
    eligible=[a for a,x in results.items() if dev_pass[a] and x['leg_i'] and x['leg_ii'] and x['leg_iii']]
    ship=min(eligible,key=lambda a:(results[a]['ll_1x2'],0 if a=='gate_zero' else 1)) if eligible else None
    out={'protocol':{'virgin_season':VIRGIN,'n':len(target),'transitional':False},'virgin_read':True,'read_arms':list(results),'metrics':results,'dev_pass':dev_pass,'shipped_arm':ship,'verdict':'PASS' if ship else 'FAIL'}
    (HERE/'results_virgin.json').write_text(json.dumps(out,indent=2)+'\n')
    if ship:
        m=DC().fit(train,min(x['date'] for x in target)); counts=match_counts(train)
        with (HERE.parents[1]/'predictions'/'g_ve_virgin_predictions.csv').open('w',newline='',encoding='utf-8') as fh:
            fields=['match_id','date','home_team','away_team','arm','lam_h','lam_a','ph','pd','pa','p_over_1_5','p_over_2_5','p_over_3_5','pred_total_ft','pred_total_1h','pred_total_2h','actual_home_goals','actual_away_goals']; w=csv.DictWriter(fh,fieldnames=fields); w.writeheader()
            for r in target:
                p=m.probs(*adjusted_lambdas(m,r['hi'],r['ai'],ship,counts)); ft=p['ph']*0 # placeholder overwritten below
                lh,la=adjusted_lambdas(m,r['hi'],r['ai'],ship,counts); ft=lh+la
                w.writerow({'match_id':r['match_id'],'date':r['date'].isoformat(),'home_team':r['home'],'away_team':r['away'],'arm':ship,'lam_h':lh,'lam_a':la,'ph':p['ph'],'pd':p['pd'],'pa':p['pa'],'p_over_1_5':p['over15'],'p_over_2_5':p['over25'],'p_over_3_5':p['over35'],'pred_total_ft':ft,'pred_total_1h':ft*HALF,'pred_total_2h':ft*(1-HALF),'actual_home_goals':r['yh'],'actual_away_goals':r['ya']})
        (HERE/'fitted_params_virgin.json').write_text(json.dumps(results[ship]['params'],indent=2)+'\n')
    return out
