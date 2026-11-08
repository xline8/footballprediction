import csv,json,math
from pathlib import Path
from core import load,FeatureBuilder,attach_naive,fit_params,model_prediction,baseline_prediction,over_prob
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/'data'/'ca_matches.csv'; SEAS=('2021','2022','2023','2024'); SCORED=('2022','2023','2024')
def run_dev():
    rows=attach_naive(FeatureBuilder(load(str(DATA),set(SEAS))).build()); assert all(r['season'] in SEAS for r in rows)
    result=[]; pred=[]
    for s in SCORED:
        target=[r for r in rows if r['season']==s]; train=[r for r in rows if r['season']<s]
        p=fit_params(train,'gate_zero')
        for kind in ('model','league_base_rate','naive_trailing_10'):
            ps=[]
            for r in target:
                mu,rr=model_prediction(r,p,'gate_zero') if kind=='model' else baseline_prediction(r,'league_base_rate' if kind=='league_base_rate' else 'naive_trailing_10'); q=over_prob(mu,rr,9.5); ps.append(q)
                pred.append({'arm':'gate_zero' if kind=='model' else ('baseline_league_rate' if kind=='league_base_rate' else 'baseline_naive'),'season':s,'match_id':r['match_id'],'date':r['date'].isoformat(),'home_team':r['home'],'away_team':r['away'],'actual_corners_total':r['y'],'p_over_9.5':q,'p_over_8.5':over_prob(mu,rr,8.5),'p_over_10.5':over_prob(mu,rr,10.5)})
            ys=[int(r['y']>9.5) for r in target]; result.append({'arm':'gate_zero','season':s,'kind':kind,'n':len(ys),'ll_9.5':sum(-(y*math.log(max(q,1e-12))+(1-y)*math.log(max(1-q,1e-12))) for q,y in zip(ps,ys))/len(ys)})
    for kind,armname in (('model','gate_zero'),('league_base_rate','baseline_league_rate'),('naive_trailing_10','baseline_naive')):
        sel=[x for x in pred if x['arm']==armname]; ys=[int(x['actual_corners_total']>9.5) for x in sel]
        result.append({'arm':'gate_zero','season':'pooled','kind':kind,'n':len(ys),'ll_9.5':sum(-(y*math.log(max(x['p_over_9.5'],1e-12))+(1-y)*math.log(max(1-x['p_over_9.5'],1e-12))) for x,y in zip(sel,ys))/len(ys)})
    (HERE/'results_dev.json').write_text(json.dumps({'protocol':{'warmup':'2021','scored':list(SCORED),'rows_loaded':len(rows),'covariates':['BallPossesion','big_chance']},'results':result},indent=2)+'\n')
    with (HERE/'results_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=['arm','season','kind','n','ll_9.5']); w.writeheader(); w.writerows(result)
    with (HERE/'predictions_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=sorted(pred[0])); w.writeheader(); w.writerows(pred)
    print(json.dumps(result,indent=2))
if __name__=='__main__': run_dev()
