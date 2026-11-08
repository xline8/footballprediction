import csv,json,math,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from gate_lib import assert_no_sealed_rows,derive_level_prior,log_loss
import model_l1
from model_l1 import ShotsRegressionStore,NaiveTracker,BaseRateTracker,TrailingR,LevelLayer,nb_over

DATA=HERE.parents[1]/'data'/'ca_matches.csv'; SEAS=('2021','2022','2023','2024'); SCORED=('2022','2023','2024'); LINES=(21.5,22.5,23.5); LAM=100.0

def load():
    out=[]; raw_dev=[]
    with DATA.open(newline='') as f:
        for r in csv.DictReader(f):
            if r['season'] not in SEAS or r['phase']!='regular' or r['included']!='1': continue
            raw_dev.append(r)
            out.append({'match_id':r['match_id'],'season':r['season'],'date':r['date'],'day':__import__('datetime').date.fromisoformat(r['date']).toordinal(),'home_id':int(r['home_team_id']),'away_id':int(r['away_team_id']),'home':r['home_team'],'away':r['away_team'],'shots_h':float(r['total_shots_home']),'shots_a':float(r['total_shots_away'])})
    assert_no_sealed_rows(raw_dev,{'2025','2026'})
    assert all(x['season'] in SEAS for x in out)
    assert_no_sealed_rows(out,{'2025','2026'})
    return sorted(out,key=lambda x:(x['day'],x['match_id']))

def run_dev():
    rows=load(); mbar=derive_level_prior([x['shots_h']+x['shots_a'] for x in rows]); assert math.isclose(mbar,22.832589285714285,abs_tol=1e-9); model_l1.set_m_bar(mbar); result=[]; pred=[]
    reg=ShotsRegressionStore(rows,[LAM]); naive=NaiveTracker(); base=BaseRateTracker(); trail=TrailingR(200.0); layer=LevelLayer([(120.0,0.5,50.0)]); rec={a:{s:[] for s in SCORED} for a in ('A','B','C')}; br={s:[] for s in SCORED}
    for r in rows:
        eh,ea=reg.predict(r['home_id'],r['away_id'],r['day'],LAM); rh,ra=reg.league_mu(r['day'],LAM); nh,na=naive.predict(r['home_id'],r['away_id'],rh,ra); total=eh+ea; nt=nh+na; rr=trail.value(r['day']); vals={'A':(total,200.0),'B':(total,200.0),'C':(total,rr)}
        factor=layer.factor(0,r['day'])
        if r['season'] in SCORED:
            for arm,(mu,sz) in vals.items():
                if arm=='B': mu*=factor
                ps={L:(.5*nb_over(mu,sz,L)+.5*nb_over(nt,sz,L)) for L in LINES}; rec[arm][r['season']].append((r,ps)); pred.append({'arm':arm,'season':r['season'],'match_id':r['match_id'],'date':r['date'],'home_team':r['home'],'away_team':r['away'],'actual_total_shots':r['shots_h']+r['shots_a'],'exp_shots_total':mu,'p_over_22.5':ps[22.5],'p_over_21.5':ps[21.5],'p_over_23.5':ps[23.5]})
                if arm=='A': pred.append({'arm':'baseline_naive','season':r['season'],'match_id':r['match_id'],'date':r['date'],'home_team':r['home'],'away_team':r['away'],'actual_total_shots':r['shots_h']+r['shots_a'],'exp_shots_total':nt,'p_over_22.5':nb_over(nt,200.,22.5),'p_over_21.5':nb_over(nt,200.,21.5),'p_over_23.5':nb_over(nt,200.,23.5)})
        naive.update(r['home_id'],r['away_id'],r['shots_h'],r['shots_a']); base.update(r['day'],r['shots_h'],r['shots_a']); trail.update(r['day'],r['shots_h']+r['shots_a']); layer.update(0,r['day'],r['shots_h']+r['shots_a'],total); reg._ensure(r['day'])
    for arm in rec:
        pairs=sum((rec[arm][s] for s in SCORED),[]); ys=[int(r['shots_h']+r['shots_a']>22.5) for r,p in pairs]; result.append({'arm':arm,'season':'pooled','kind':'model','n':len(ys),'ll_22.5':sum(log_loss(p[22.5],y) for (r,p),y in zip(pairs,ys))/len(ys)})
        for s in SCORED:
            q=rec[arm][s]; yy=[int(r['shots_h']+r['shots_a']>22.5) for r,p in q]; result.append({'arm':arm,'season':s,'kind':'model','n':len(yy),'ll_22.5':sum(log_loss(p[22.5],y) for (r,p),y in zip(q,yy))/len(yy)})
    for s in SCORED:
        prior=[x for x in rows if x['season']<s]; rate=sum(x['shots_h']+x['shots_a']>22.5 for x in prior)/len(prior); tgt=[x for x in rows if x['season']==s]
        for r in tgt: pred.append({'arm':'baseline_league','season':s,'match_id':r['match_id'],'date':r['date'],'home_team':r['home'],'away_team':r['away'],'actual_total_shots':r['shots_h']+r['shots_a'],'exp_shots_total':'','p_over_22.5':rate,'p_over_21.5':'','p_over_23.5':''})
        yy=[int(x['shots_h']+x['shots_a']>22.5) for x in tgt]; result.append({'arm':'baseline_league','season':s,'kind':'baseline','n':len(yy),'ll_22.5':sum(log_loss(rate,y) for y in yy)/len(yy)})
    pool_y=[int(x['shots_h']+x['shots_a']>22.5) for x in rows if x['season'] in SCORED]; pool_p=[]
    for s in SCORED:
        prior=[x for x in rows if x['season']<s]; pool_p += [sum(x['shots_h']+x['shots_a']>22.5 for x in prior)/len(prior)]*112
    result.append({'arm':'baseline_league','season':'pooled','kind':'baseline','n':len(pool_y),'ll_22.5':sum(log_loss(p,y) for p,y in zip(pool_p,pool_y))/len(pool_y)})
    for s in list(SCORED)+['pooled']:
        sel=[x for x in pred if x['arm']=='baseline_naive' and (s=='pooled' or x['season']==s)]; yy=[int(x['actual_total_shots']>22.5) for x in sel]; result.append({'arm':'baseline_naive','season':s,'kind':'baseline','n':len(yy),'ll_22.5':sum(log_loss(x['p_over_22.5'],y) for x,y in zip(sel,yy))/len(yy)})
    output={'protocol':{'warmup':'2021','scored':list(SCORED),'rows_loaded':len(rows),'M_BAR':mbar,'primary_line':22.5,'ladder':list(LINES),'shipped_M_BAR':24.15,'candidate':'L1-T-CA'},'results':result}
    (HERE/'results_dev_l1.json').write_text(json.dumps(output,indent=2)+'\n')
    with (HERE/'predictions_dev_l1.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=sorted(pred[0])); w.writeheader(); w.writerows(pred)
    print(json.dumps(output,indent=2))

if __name__=='__main__': run_dev()
