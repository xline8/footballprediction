import csv,json,math,os
from pathlib import Path
import numpy as np
from model import Engine,load_matches,LINES,NB_R,nb_over

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'safd_matches.csv'; PRED=HERE.parents[1]/'predictions'/'s_safd_virgin_predictions.csv'; DEV_SEASON='2025/2026'; VIRGIN_SEASON='2026/2027'; ARMS=('GZ','RS')
def ll(p,y): p=min(max(p,1e-12),1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m,L): return float(m['sot_h']+m['sot_a']>L)
def groups(ms):
    out=[]
    for d in sorted({m['date'] for m in ms}): out.append((d,[m for m in ms if m['date']==d]))
    return out
def walk(ms,eng,score_season=None):
    rows=[]
    for _,z in groups(ms):
        ps=[(m,eng.predict(m)) for m in z]
        if score_season is None or z[0]['season']==score_season: rows.extend(ps)
        for m,_ in ps: eng.update(m)
    return rows,eng
def metrics(rows):
    out={'pooled':{},'seasons':{},'n':len(rows)}
    for L in LINES:
        out['pooled'][f'll_{L}']=sum(ll(p['probs'][L],actual(m,L)) for m,p in rows)/len(rows)
        for s in sorted({m['season'] for m,_ in rows}):
            z=[(m,p) for m,p in rows if m['season']==s]; out['seasons'].setdefault(s,{})[f'll_{L}']=sum(ll(p['probs'][L],actual(m,L)) for m,p in z)/len(z); out['seasons'][s]['n']=len(z)
    return out
def baseline(rows,all_ms):
    out={}
    for kind in ('league_base_rate','naive'):
        vals=[]
        for m,p in rows:
            prior=[x for x in all_ms if x['date']<m['date']]; rate=sum(actual(x,8.5) for x in prior)/len(prior) if prior else .5; vals.append((m,p,rate if kind=='league_base_rate' else p['naive_probs'][8.5]))
        q={'pooled':{},'seasons':{},'n':len(vals)}
        for L in LINES:
            q['pooled'][f'll_{L}']=sum(ll((v if kind=='league_base_rate' else p['naive_probs'][L]),actual(m,L)) for m,p,v in vals)/len(vals)
            for s in sorted({m['season'] for m,_,_ in vals}):
                z=[(m,p,v) for m,p,v in vals if m['season']==s]; q['seasons'].setdefault(s,{})[f'll_{L}']=sum(ll((v if kind=='league_base_rate' else p['naive_probs'][L]),actual(m,L)) for m,p,v in z)/len(z); q['seasons'][s]['n']=len(z)
        out[kind]=q
    return out
def dev():
    ms=load_matches(DATA,{DEV_SEASON}); assert len(ms)==304; scored=ms[90:]; assert len(scored)==214
    out={'protocol':{'warmup_n':90,'scored_n':214,'date_grouped':True},'arms':{},'baselines':{}}
    stored={}
    for a in ARMS: stored[a]=walk(ms,Engine(ms,a),DEV_SEASON)[0][90:]; out['arms'][a]=metrics(stored[a])
    out['baselines']=baseline(stored['GZ'],ms); out['dev_gate']={a:out['arms'][a]['pooled']['ll_8.5']<out['baselines']['league_base_rate']['pooled']['ll_8.5'] and out['arms'][a]['pooled']['ll_8.5']<out['baselines']['naive']['pooled']['ll_8.5'] for a in ARMS}
    (HERE/'results_dev.json').write_text(json.dumps(out,indent=2)+'\n'); write_dev_csv(out); return out
def write_dev_csv(o):
    with (HERE/'results_dev.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['scope','name','ll_7.5','ll_8.5','ll_9.5','n'])
        for k,b in [('arm',o['arms']),('baseline',o['baselines'])]:
            for n,v in b.items(): w.writerow(['pooled',k+':'+n,*[v['pooled'][f'll_{L}'] for L in LINES],v['n']])
def calibration(rows):
    dif=[p['probs'][8.5]-actual(m,8.5) for m,p in rows]; return {'diff':sum(dif)/len(dif),'se':float(np.std(dif,ddof=1)/math.sqrt(len(dif))),'n':len(rows),'ll_8.5':sum(ll(p['probs'][8.5],actual(m,8.5)) for m,p in rows)/len(rows)}
def virgin(make_predictions=False):
    d=json.loads((HERE/'results_dev.json').read_text()); passing=[a for a in ARMS if d['dev_gate'][a]]
    if not passing: return fail_virgin()
    ms=load_matches(DATA,{DEV_SEASON,VIRGIN_SEASON}); assert len([m for m in ms if m['season']==VIRGIN_SEASON])==94
    out={'protocol':{'virgin_read':True,'virgin_season':'2026/2027','transitional':True,'n':94},'arms':{},'baselines':{},'read_arms':passing}
    allrows={}
    for a in passing:
        rows,eng=walk(ms,Engine(ms,a),VIRGIN_SEASON); vr=[x for x in rows if x[0]['season']==VIRGIN_SEASON]; allrows[a]=(vr,eng); out['arms'][a]=calibration(vr)
    rows,eng=walk(ms,Engine(ms,'GZ'),VIRGIN_SEASON); vr=[x for x in rows if x[0]['season']==VIRGIN_SEASON]; base=sum(actual(m,8.5) for m in ms if m['date']<vr[0][0]['date'])/len([m for m in ms if m['date']<vr[0][0]['date']]); out['baselines']={'league_base_rate':{'ll_8.5':sum(ll(base,actual(m,8.5)) for m,p in vr)/94,'calibration_diff':sum(base-actual(m,8.5) for m,p in vr)/94},'naive':{'ll_8.5':sum(ll(p['naive_probs'][8.5],actual(m,8.5)) for m,p in vr)/94,'calibration_diff':sum(p['naive_probs'][8.5]-actual(m,8.5) for m,p in vr)/94}}
    best=min(v['ll_8.5'] for v in out['baselines'].values()); eligible=[a for a in passing if out['arms'][a]['ll_8.5']<=out['arms']['GZ']['ll_8.5'] and out['arms'][a]['ll_8.5']<=best and abs(out['arms'][a]['diff'])<=.01+out['arms'][a]['se'] and (a=='GZ' or sum(d['arms'][a]['seasons'][s]['ll_8.5']<=d['arms']['GZ']['seasons'][s]['ll_8.5'] for s in [DEV_SEASON])>=1)]
    chosen=min(eligible,key=lambda a:(out['arms'][a]['ll_8.5'],ARMS.index(a))) if eligible else None; out['shipped_arm']=chosen; out['gate_legs']={a:{'ll_le_gz':bool(out['arms'][a]['ll_8.5']<=out['arms']['GZ']['ll_8.5']),'ll_le_best_baseline':bool(out['arms'][a]['ll_8.5']<=best),'calibration_pass_or_provisional':bool(abs(out['arms'][a]['diff'])<=.01+out['arms'][a]['se']),'dev_sign_check':a=='GZ'} for a in passing}
    (HERE/'results_virgin.json').write_text(json.dumps(out,indent=2)+'\n'); write_fitted(allrows[chosen][1] if chosen else eng,chosen or 'GZ',chosen is None)
    if chosen and make_predictions: write_predictions(allrows[chosen][0],chosen)
    return out
def fail_virgin():
    o={'virgin_read':False,'reason':'Gate Zero failed dev gate'}; (HERE/'results_virgin.json').write_text(json.dumps(o,indent=2)+'\n'); (HERE/'fitted_params_virgin.json').write_text(json.dumps({'arm':'GZ','training_rows':0,'params':{}},indent=2)+'\n'); return o
def write_fitted(eng,arm,none):
    if none: x={'arm':'GZ','training_rows':0,'params':{}}
    else: x={'arm':arm,'nb_r':NB_R,'regression':{d:{'teams':v['teams'],'theta':v['theta'].tolist()} for d,v in eng.reg.d.items()}}
    (HERE/'fitted_params_virgin.json').write_text(json.dumps(x,indent=2)+'\n')
def write_predictions(rows,arm):
    PRED.parent.mkdir(exist_ok=True); fields=['arm','match_id','date','home_team','away_team','actual_total_sot','exp_sot_home','exp_sot_away','exp_sot_total']+[f'ft_p_over_{L}' for L in LINES]+[f'1h_p_over_{L}' for L in (3.5,4.5,5.5)]+[f'2h_p_over_{L}' for L in (4.5,5.5,6.5)]
    with PRED.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for m,p in rows:
            t=p['exp_h']+p['exp_a']; q={'arm':arm,'match_id':m['match_id'],'date':m['date'],'home_team':m['home'],'away_team':m['away'],'actual_total_sot':m['sot_h']+m['sot_a'],'exp_sot_home':p['exp_h'],'exp_sot_away':p['exp_a'],'exp_sot_total':t}; q.update({f'ft_p_over_{L}':p['probs'][L] for L in LINES}); q.update({f'1h_p_over_{L}':nb_over(.4540*t,NB_R,L) for L in (3.5,4.5,5.5)}); q.update({f'2h_p_over_{L}':nb_over(.5460*t,NB_R,L) for L in (4.5,5.5,6.5)}); w.writerow(q)
