import csv,json,math
from pathlib import Path
import numpy as np
from model import Online,estimate_r,nb_over
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'qasd_matches.csv'; PRED=HERE.parents[1]/'predictions'/'k_qasd_virgin_predictions.csv'; DEV='2025/2026'; VIRGIN='2026/2027'; LINES=(4.5,5.5,6.5)
def load(seasons):
    z=[]
    with DATA.open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['season'] not in seasons or r['phase']!='regular' or r.get('awarded','0')!='0': continue
            dt=r['date']; z.append({'match_id':r['match_id'],'season':r['season'],'round':int(r['round']),'date':dt,'key':(dt,r['match_id']),'day':__import__('datetime').date.fromisoformat(dt).toordinal(),'home_id':int(r['home_team_id']),'away_id':int(r['away_team_id']),'home':r['home_team'],'away':r['away_team'],'yh':int(float(r['yellow_home'])),'ya':int(float(r['yellow_away'])),'y':int(float(r['yellow_home']))+int(float(r['yellow_away']))})
    return sorted(z,key=lambda x:x['key'])
def walk(rows,online,keep=False):
    out=[]
    for d in sorted({x['date'] for x in rows}):
        z=[x for x in rows if x['date']==d]; ps=[(x,online.prediction(x)) for x in z]
        if keep: out+=ps
        for x,_ in ps: online.update(x)
    return out
def scored(rows,rs):
    o={}
    for method in ('model','base','naive'):
        o[method]={}
        for L in LINES:
            p=[nb_over(x[method],rs[method],L) for x in rows]; y=[int(x['y']>L) for x in rows]; o[method][str(L)]={'n':len(rows),'ll':sum(-(b*math.log(max(q,1e-12))+(1-b)*math.log(max(1-q,1e-12))) for q,b in zip(p,y))/len(rows),'mean_p':sum(p)/len(p),'actual_rate':sum(y)/len(y)}
    return o
def rmap(rows): return {m:estimate_r(rows,m) for m in ('model','base','naive')}
def dev():
    rows=load({'2024/2025',DEV}); assert sum(x['season']=='2024/2025' for x in rows)==56; assert sum(x['season']==DEV for x in rows)==56; warm=[x for x in rows if x['season']==DEV and 1<=x['round']<=7]; target=[x for x in rows if x['season']==DEV and 8<=x['round']<=14]; assert len(warm)==28 and len(target)==28; on=Online(); allp=walk(rows,on,True); fit=[{'y':x['y'],'model':p['model'],'base':p['base'],'naive':p['naive']} for x,p in allp if not (x['season']==DEV and 8<=x['round']<=14)]; rr=[{'y':x['y'],'model':p['model'],'base':p['base'],'naive':p['naive']} for x,p in allp if x['season']==DEV and 8<=x['round']<=14]; rm=rmap(fit); s=scored(rr,rm); out={'protocol':{'loaded_seasons':['2024/2025',DEV],'history_2024_2025':56,'warmup_n':28,'scored_n':28,'date_grouped':True},'arms':{'gate_zero':{'r':rm,'pooled':s,'dev_gate_pass':s['model']['5.5']['ll']<s['base']['5.5']['ll'] and s['model']['5.5']['ll']<s['naive']['5.5']['ll']}},'baselines':{'league_base_rate':s['base'],'naive':s['naive']}}; (HERE/'results_dev.json').write_text(json.dumps(out,indent=2)+'\n'); (HERE/'results_dev.csv').write_text('scope,name,ll_4.5,ll_5.5,ll_6.5,n\n'+'\n'.join('pooled,'+n+','+','.join(str(s[k]["ll"]) for k in ('4.5','5.5','6.5'))+',28' for n,s in [('gate_zero',s['model']),('league_base_rate',s['base']),('naive',s['naive'])])+'\n');
    with (HERE/'predictions_dev.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['arm','match_id','date','home_team','away_team','actual_total_yellows','p_over_4.5','p_over_5.5','p_over_6.5','baseline_league_p','baseline_naive_p']); w.writeheader()
        for x,p in allp:
            if x['season']==DEV and 8<=x['round']<=14:
                w.writerow({'arm':'gate_zero','match_id':x['match_id'],'date':x['date'],'home_team':x['home'],'away_team':x['away'],'actual_total_yellows':x['y'],**{f'p_over_{L}':nb_over(p['model'],rm['model'],L) for L in LINES},'baseline_league_p':nb_over(p['base'],rm['base'],5.5),'baseline_naive_p':nb_over(p['naive'],rm['naive'],5.5)})
    return out
def virgin(predict=False):
    d=json.loads((HERE/'results_dev.json').read_text());
    if not d['arms']['gate_zero']['dev_gate_pass']: return fail()
    rows=load({'2024/2025',DEV,VIRGIN}); assert len([x for x in rows if x['season']==VIRGIN])==29; on=Online(); allp=walk(rows,on,True); fit=[{'y':x['y'],'model':p['model'],'base':p['base'],'naive':p['naive']} for x,p in allp if x['season']!=VIRGIN]; vr=[(x,p) for x,p in allp if x['season']==VIRGIN]; rm=rmap(fit); vals=[nb_over(p['model'],rm['model'],5.5) for x,p in vr]; ys=[int(x['y']>5.5) for x,p in vr]; dif=np.array(vals)-ys; out={'protocol':{'virgin_read':True,'virgin_season':VIRGIN,'transitional':True,'n':29},'arms':{'gate_zero':{'metrics':scored([{'y':x['y'],'model':p['model'],'base':p['base'],'naive':p['naive']} for x,p in vr],rm),'calibration':{'diff_5_5':float(dif.mean()),'se_5_5':float(dif.std(ddof=1)/math.sqrt(29))}}},'shipped_arm':None}; best=min(out['arms']['gate_zero']['metrics'][k]['5.5']['ll'] for k in ('base','naive')); v=out['arms']['gate_zero']; out['gate_legs']={'ll_le_gz':True,'ll_le_best_baseline':v['metrics']['model']['5.5']['ll']<=best,'calibration_pass_or_provisional':abs(v['calibration']['diff_5_5'])<=.01+v['calibration']['se_5_5']}; out['shipped_arm']='gate_zero' if all(out['gate_legs'].values()) else None; (HERE/'results_virgin.json').write_text(json.dumps(out,indent=2)+'\n'); (HERE/'fitted_params_virgin.json').write_text(json.dumps({'arm':'gate_zero','r':rm},indent=2)+'\n');
    if out['shipped_arm'] and predict: write_predictions(vr,rm); return out
    return out
def fail():
    o={'virgin_read':False,'reason':'Gate Zero failed dev gate'}; (HERE/'results_virgin.json').write_text(json.dumps(o,indent=2)+'\n'); (HERE/'fitted_params_virgin.json').write_text(json.dumps({'arm':'gate_zero','training_rows':0,'params':{}},indent=2)+'\n'); return o
def write_predictions(rows,rm):
    PRED.parent.mkdir(exist_ok=True); fs=['arm','match_id','date','home_team','away_team','actual_total_yellows','expected_home','expected_away','expected_total']+[f'ft_p_over_{L}' for L in LINES]+[f'1h_p_over_{L}' for L in (1.5,2.5,3.5)]+[f'2h_p_over_{L}' for L in (2.5,3.5,4.5)]
    with PRED.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fs); w.writeheader()
        for x,p in rows:
            t=p['model']; q={'arm':'gate_zero','match_id':x['match_id'],'date':x['date'],'home_team':x['home'],'away_team':x['away'],'actual_total_yellows':x['y'],'expected_home':p['eh'],'expected_away':p['ea'],'expected_total':t}; q.update({f'ft_p_over_{L}':nb_over(t,rm['model'],L) for L in LINES}); q.update({f'1h_p_over_{L}':nb_over(.3151*t,rm['model'],L) for L in (1.5,2.5,3.5)}); q.update({f'2h_p_over_{L}':nb_over(.6849*t,rm['model'],L) for L in (2.5,3.5,4.5)}); w.writerow(q)
