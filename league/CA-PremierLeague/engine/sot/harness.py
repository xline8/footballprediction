import csv,json,math
from pathlib import Path
from model import Engine,load_matches,LINES,NB_R,nb_over
HERE=Path(__file__).resolve().parent
DATA=HERE.parents[1]/'data'/'ca_matches.csv'
SCORED=('2022','2023','2024'); ALLOWED=('2021','2022','2023','2024')
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def run_dev():
    rows=load_matches(str(DATA),set(ALLOWED)); assert all(x['season'] in ALLOWED for x in rows)
    out=[]; pred=[]; by={}
    for arm in ('GZ','RS'):
        e=Engine(rows,arm); by[arm]={s:[] for s in SCORED}
        for m in rows:
            p=e.predict(m)
            if m['season'] in SCORED:
                by[arm][m['season']].append((m,p)); pred.append({'arm':arm,'season':m['season'],'match_id':m['match_id'],'date':m['date'].isoformat(),'home_team':m['home'],'away_team':m['away'],'actual_total_sot':m['sot_h']+m['sot_a'],**{f'p_over_{str(L)}':p['probs'][L] for L in LINES}})
                if arm=='GZ': pred.append({'arm':'baseline_naive','season':m['season'],'match_id':m['match_id'],'date':m['date'].isoformat(),'home_team':m['home'],'away_team':m['away'],'actual_total_sot':m['sot_h']+m['sot_a'],**{f'p_over_{str(L)}':p['naive_probs'][L] for L in LINES}})
            e.update(m)
    for s in SCORED:
        target=[m for m in rows if m['season']==s]; prior=[m for m in rows if m['season']<s]; rate=sum(m['sot_h']+m['sot_a']>7.5 for m in prior)/len(prior)
        for arm in ('GZ','RS'):
            for kind in ('model','base','naive'):
                pairs=by[arm][s]; ps=[p['probs'][7.5] if kind=='model' else (p['naive_probs'][7.5] if kind=='naive' else rate) for m,p in pairs]; ys=[int(m['sot_h']+m['sot_a']>7.5) for m,p in pairs]
                out.append({'arm':arm,'season':s,'kind':kind,'n':len(ys),'ll_7.5':sum(ll(p,y) for p,y in zip(ps,ys))/len(ys)})
    for arm in ('GZ','RS'):
        pairs=sum((by[arm][s] for s in SCORED),[]); ys=[int(m['sot_h']+m['sot_a']>7.5) for m,p in pairs]
        out.append({'arm':arm,'season':'pooled','kind':'model','n':len(ys),'ll_7.5':sum(ll(p['probs'][7.5],y) for (m,p),y in zip(pairs,ys))/len(ys)})
    pairs=sum((by['GZ'][s] for s in SCORED),[]); ys=[int(m['sot_h']+m['sot_a']>7.5) for m,p in pairs]
    out.append({'arm':'GZ','season':'pooled','kind':'naive','n':len(ys),'ll_7.5':sum(ll(p['naive_probs'][7.5],y) for (m,p),y in zip(pairs,ys))/len(ys)})
    base_ps=[]
    for s in SCORED:
        prior=[m for m in rows if m['season']<s]; base_ps += [sum(m['sot_h']+m['sot_a']>7.5 for m in prior)/len(prior)]*len(by['GZ'][s])
    out.append({'arm':'GZ','season':'pooled','kind':'base','n':len(ys),'ll_7.5':sum(ll(p,y) for p,y in zip(base_ps,ys))/len(ys)})
    (HERE/'results_dev.json').write_text(json.dumps({'protocol':{'warmup':'2021','scored':list(SCORED),'rows_loaded':len(rows)},'results':out},indent=2)+'\n')
    with (HERE/'results_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=['arm','season','kind','n','ll_7.5']); w.writeheader(); w.writerows(out)
    with (HERE/'predictions_dev.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=sorted(pred[0])); w.writeheader(); w.writerows(pred)
    print(json.dumps(out,indent=2))
if __name__=='__main__': run_dev()
