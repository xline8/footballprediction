import json, math
from pathlib import Path
from core import FeatureBuilder, attach_naive, load, model_prediction, baseline_prediction, fit_params, over_prob
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'ve_matches.csv'; BLOCKS=('R1-7','R8-13'); PRIMARY=8.5; LINES=(7.5,8.5,9.5)
def rows(): return attach_naive(FeatureBuilder(load(DATA,{'2025','2026'})).build())
def metric(rs,ps):
    pairs=[(r,p) for r,p in zip(rs,ps) if r['y'] is not None]; rs=[r for r,p in pairs]; ps=[p for r,p in pairs]
    return {'n':len(rs),'ll':sum(-(int(r['y']>PRIMARY)*math.log(max(p[PRIMARY],1e-12))+(1-int(r['y']>PRIMARY))*math.log(max(1-p[PRIMARY],1e-12))) for r,p in pairs)/len(rs),'lines':{str(L):sum(-(int(r['y']>L)*math.log(max(p[L],1e-12))+(1-int(r['y']>L))*math.log(max(1-p[L],1e-12))) for r,p in pairs)/len(rs) for L in LINES},'mean_p':sum(p[PRIMARY] for p in ps)/len(ps),'actual_rate':sum(r['y']>PRIMARY for r in rs)/len(rs)}
def pred(r,kind,params=None):
    if kind=='model': mu,rr=model_prediction(r,params,'gate_zero')
    else: mu,rr=baseline_prediction(r,'league_base_rate' if kind=='base' else 'naive_trailing_10')
    return {L:over_prob(mu,rr,L) for L in LINES}
def run_dev():
    allr=rows(); assert not any(r['season']=='2026' and r['block'] not in BLOCKS for r in allr); result=[]
    for b in BLOCKS:
        target=[r for r in allr if r['block']==b]; cutoff=min(r['date'] for r in target); train=[r for r in allr if r['date']<cutoff]; params=fit_params(train,'gate_zero')
        for k in ('model','base','naive'):
            ps=[pred(r,k,params) for r in target]; x=metric(target,ps); x.update(block=b,kind={'base':'league_base_rate','naive':'naive_trailing_10'}.get(k,k)); result.append(x)
    pooled=[]
    for b in BLOCKS:
        target=[r for r in allr if r['block']==b]; cutoff=min(r['date'] for r in target); train=[r for r in allr if r['date']<cutoff]; params=fit_params(train,'gate_zero'); pooled.extend((r,pred(r,'model',params)) for r in target)
    x=metric([r for r,p in pooled],[p for r,p in pooled]); x.update(block='pooled',kind='model'); result.append(x)
    for k in ('base','naive'):
        z=[]
        for b in BLOCKS:
            target=[r for r in allr if r['block']==b]; cutoff=min(r['date'] for r in target); train=[r for r in allr if r['date']<cutoff]; params=fit_params(train,'gate_zero'); z.extend((r,pred(r,k,params)) for r in target)
        x=metric([r for r,p in z],[p for r,p in z]); x.update(block='pooled',kind={'base':'league_base_rate','naive':'naive_trailing_10'}[k]); result.append(x)
    out={'protocol':{'seed':'2025 Clausura regular','dev_blocks':list(BLOCKS),'virgin_not_loaded':True,'primary_line':PRIMARY},'arm':'gate_zero','big_chance_assert':all(r['bc_h']==0 and r['bc_a']==0 for r in allr),'results':result}
    (HERE/'results_dev.json').write_text(json.dumps(out,indent=2)+'\n'); print('dev')
    for x in result: print('gate_zero',x['block'],x['kind'],x['n'],f"{x['ll']:.6f}")
    return out

def _se(errors):
    m=sum(errors)/len(errors)
    return (sum((x-m)**2 for x in errors)/(len(errors)-1))**.5/(len(errors)**.5)

def run_virgin(dev):
    assert dev['results'] and next(x for x in dev['results'] if x['block']=='pooled' and x['kind']=='model')['ll'] < next(x for x in dev['results'] if x['block']=='pooled' and x['kind']=='league_base_rate')['ll'] and next(x for x in dev['results'] if x['block']=='pooled' and x['kind']=='model')['ll'] < next(x for x in dev['results'] if x['block']=='pooled' and x['kind']=='naive_trailing_10')['ll']
    allr=attach_naive(FeatureBuilder(load(DATA,{'2025','2026'},True)).build()); target=[r for r in allr if r['block']=='2026 Clausura']; train=[r for r in allr if r['date']<min(x['date'] for x in target)]; params=fit_params(train,'gate_zero'); preds=[pred(r,'model',params) for r in target]; m=metric(target,preds); errs=[int(r['y']>PRIMARY)-p[PRIMARY] for r,p in zip(target,preds) if r['y'] is not None]; cal=100*sum(errs)/len(errs); se=100*_se(errs)
    base=metric(target,[pred(r,'base',params) for r in target]); naive=metric(target,[pred(r,'naive',params) for r in target]); status='CLEAN' if abs(cal)<=1 else ('PROVISIONAL' if abs(cal)<=1+se else 'FAIL'); m.update({'block':'2026 Clausura','kind':'model','calibration_actual_minus_predicted_pp':cal,'calibration_se_pp':se,'calibration_status':status,'leg_i':m['ll']<=base['ll'] and m['ll']<=naive['ll'],'leg_ii':status in ('CLEAN','PROVISIONAL'),'params':params})
    out={'protocol':{'virgin_season':'2026 Clausura','transitional':True,'scored_n':m['n'],'unscored_missing_target':len(target)-m['n']},'metrics':{'gate_zero':m,'league_base_rate':base,'naive_trailing_10':naive},'verdict':'PASS' if m['leg_i'] and m['leg_ii'] else 'FAIL','shipped_arm':'gate_zero' if m['leg_i'] and m['leg_ii'] else None,'virgin_read':True}
    (HERE/'results_virgin.json').write_text(json.dumps(out,indent=2)+'\n')
    if out['shipped_arm']:
        PRED=HERE.parents[1]/'predictions'/'c_ve_virgin_predictions.csv'; PRED.parent.mkdir(exist_ok=True); fields=['match_id','date','home_team','away_team','arm','pred_total_ft','pred_total_1h','pred_total_2h','actual_total'];
        with PRED.open('w',newline='',encoding='utf-8') as fh:
            w=__import__('csv').DictWriter(fh,fieldnames=fields); w.writeheader()
            for r,p in zip(target,preds):
                mu,_=model_prediction(r,params,'gate_zero'); w.writerow({'match_id':r['match_id'],'date':r['date'].isoformat(),'home_team':r['home'],'away_team':r['away'],'arm':'gate_zero','pred_total_ft':mu,'pred_total_1h':mu*.4669,'pred_total_2h':mu*(1-.4669),'actual_total':r['y']})
        (HERE/'fitted_params_virgin.json').write_text(json.dumps(params,indent=2)+'\n')
    return out
if __name__=='__main__': run_dev()
