import csv,json,sys
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;DATA=HERE.parents[2]/'PT-LigaPortugal/data/pt_matches.csv';sys.path.insert(0,str(HERE)); from common import *
def rows():
 z=load(DATA,{'sh':'shots_home','sa':'shots_away'});
 for x in z:x['y']=x['sh']+x['sa']
 return z
def state(allr,s):
 tr,cut,ww,L,r,_,_=season_state(allr,s,270,'y');L=sum(q*x['y'] for x,q in zip(tr,ww))/(2*sum(ww));d=defaultdict(lambda:[0.,0.,0.])
 for x,q in zip(tr,ww):
  for t,fo,ag in ((x['home_id'],x['sh'],x['sa']),(x['away_id'],x['sa'],x['sh'])):d[t][0]+=q*fo;d[t][1]+=q*ag;d[t][2]+=q
 def model(x):
  def z(t,k):return (d[t][k]+8*L)/(d[t][2]+8)
  hf,ha=z(x['home_id'],0),z(x['home_id'],1);af,aa=z(x['away_id'],0),z(x['away_id'],1);return L*(hf/L)*(aa/L)+L*(af/L)*(ha/L)
 return tr,L,r,model
def main():
 if len(sys.argv)!=2:raise SystemExit('use dev or virgin')
 allr=rows();assert '2026/2027' not in {x['season'] for x in allr}
 if sys.argv[1]=='virgin':raise SystemExit('virgin is intentionally not executed during repair')
 pred=[];res=[];fits={}
 for arm in ('gate_zero','e9'):
  for s in TARGETS:
   tr,L,r,model=state(allr,s);dev=[x for x in allr if x['season']==s];cut=min(x['date'] for x in dev);ww=[(weight(cut,x['date'],270),x['y']) for x in tr];bm=sum(q*y for q,y in ww)/sum(q for q,y in ww);nm=naive(allr,s,'sh','sa',bm);assert abs(nm[dev[0]['match_id']]-naive_bruteforce(allr,dev[0],'sh','sa',bm))<1e-9;rr=moment([x['y'] for x in tr[-200:]]) if arm=='e9' else moment([x['y'] for x in tr]);fits.setdefault(arm,{})[s]={'L':L,'r':rr,'r_window':'trailing_200' if arm=='e9' else 'whole_training'}
   for kind in ('model','league_base_rate','naive_trailing_10'):
    pp=[]
    for x in dev:
     m=model(x) if kind=='model' else (bm if kind=='league_base_rate' else nm[x['match_id']]);p=.5*nb_over(m,rr,24.5)+.5*nb_over(nm[x['match_id']],rr,24.5) if kind=='model' else nb_over(m,moment([q['y'] for q in tr]),24.5);pp.append((p,int(x['y']>24.5)));pred.append({**x,'arm':arm,'baseline':kind,'mu':m,'r':rr,'p_over':p})
    res.append({'arm':arm,'kind':kind,'season':s,'line':24.5,**metrics(pp,24.5)})
  for kind in ('model','league_base_rate','naive_trailing_10'):
   pp=[(x['p_over'],int(x['y']>24.5)) for x in pred if x['arm']==arm and x['baseline']==kind];res.append({'arm':arm,'kind':kind,'season':'pooled','line':24.5,**metrics(pp,24.5)})
 (HERE/'results_dev.json').write_text(json.dumps({'protocol':'T-PT DEV','rows_loaded':len(allr),'fitted_params':fits,'results':res},indent=2)+'\n')
 with open(HERE/'results_dev.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=['arm','kind','season','n','ll','mean_p_over','actual_over']);w.writeheader();w.writerows({k:x.get(k,'') for k in w.fieldnames} for x in res)
 with open(HERE/'predictions_dev.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','baseline','mu','r','p_over']);w.writeheader();[w.writerow({k:x[k] if k!='actual_total' else x['y'] for k in w.fieldnames}) for x in pred]
 vals=[x['mu'] for x in pred if x['baseline']=='model'];assert len(set(vals))>1;assert any(abs(x['mu']-y['mu'])>1e-9 for x in pred for y in pred if x['match_id']==y['match_id'] and x['baseline']!=y['baseline']);print('self_check arm_mus_differ OK');print('self_check baseline_diff OK');print('self_check naive_bruteforce OK');[print(x['arm'],x['kind'],f"LL={x['ll']:.6f}") for x in res if x['season']=='pooled']
if __name__=='__main__':main()
