import csv,json,math,sys
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent; DATA=HERE.parents[2]/'PT-LigaPortugal/data/pt_matches.csv'
sys.path.insert(0,str(HERE)); from common import *
def rows():
 z=load(DATA,{'yh':'yellow_home','ya':'yellow_away'})
 for x in z:x['y']=x['yh']+x['ya']
 return z
def state(allr,s):
 tr,cut,ww,mu,r,_,_=season_state(allr,s,270,'y'); per=defaultdict(lambda:[0.,0.,0.])
 for x,q in zip(tr,ww):
  for t,fo,ag in ((x['home_id'],x['yh'],x['ya']),(x['away_id'],x['ya'],x['yh'])):
   a=per[t];a[0]+=q*fo;a[1]+=q*ag;a[2]+=q
 def rate(t,k):return (per[t][k]+8*mu/2)/(per[t][2]+8)
 # Coordinator fix: season_state's mu is the PER-MATCH total; the
 # prereg's mu_L is the PER-TEAM mean (mu/2). Codex's model used mu
 # as the per-side base, double-counting (mu ~ 11 for yellows).
 def model(x):return rate(x['home_id'],0)*rate(x['away_id'],1)/(mu/2)+rate(x['away_id'],0)*rate(x['home_id'],1)/(mu/2)
 return tr,mu,r,model
def main():
 if len(sys.argv)!=2:raise SystemExit('use dev or virgin')
 allr=rows();assert '2026/2027' not in {x['season'] for x in allr}
 if sys.argv[1]=='virgin':return virgin(allr)
 preds=[];result=[];fits={}
 for s in TARGETS:
  tr,mu,r,model=state(allr,s);dev=[x for x in allr if x['season']==s];refs=defaultdict(lambda:[0.,0.])
  for x in tr:refs[x['referee']][0]+=x['y'];refs[x['referee']][1]+=1
  cutoff=min(x['date'] for x in dev);ww=[(weight(cutoff,x['date'],270),x['y']) for x in tr];base_mu=sum(q*y for q,y in ww)/sum(q for q,y in ww);nm=naive(allr,s,'yh','ya',base_mu);assert abs(nm[dev[0]['match_id']]-naive_bruteforce(allr,dev[0],'yh','ya',base_mu))<1e-9
  for arm in ('gate_zero','x8'):
   fits.setdefault(arm,{})[s]={'r':r,'mu_L':mu}
   for kind in ('model','league_base_rate','naive_trailing_10'):
    pp=[]
    for x in dev:
     m=model(x) if kind=='model' else (base_mu if kind=='league_base_rate' else nm[x['match_id']]);mult=1
     if arm=='x8' and kind=='model' and x['referee'] and refs[x['referee']][1]>0:mult=clamp((refs[x['referee']][0]+8*mu)/(refs[x['referee']][1]+8)/mu,.75,1.33);m*=mult
     p=nb_over(m,r,4.5);pp.append((p,int(x['y']>4.5)));preds.append({**x,'arm':arm,'baseline':kind,'mu':m,'r':r,'p_over':p})
    result.append({'arm':arm,'kind':kind,'season':s,'line':4.5,**metrics(pp,4.5)})
 for arm in ('gate_zero','x8'):
  for kind in ('model','league_base_rate','naive_trailing_10'):
   pp=[(x['p_over'],int(x['y']>4.5)) for x in preds if x['arm']==arm and x['baseline']==kind];result.append({'arm':arm,'kind':kind,'season':'pooled','line':4.5,**metrics(pp,4.5)})
 write(preds,result,fits)
def write(preds,result,fits):
 (HERE/'results_dev.json').write_text(json.dumps({'protocol':'K-PT DEV','rows_loaded':len(preds)//6,'fitted_params':fits,'results':result},indent=2)+'\n')
 with open(HERE/'results_dev.csv','w',newline='') as f:wri=csv.DictWriter(f,fieldnames=['arm','kind','season','n','ll','mean_p_over','actual_over']);wri.writeheader();wri.writerows({k:x.get(k,'') for k in wri.fieldnames} for x in result)
 with open(HERE/'predictions_dev.csv','w',newline='') as f:
  wri=csv.DictWriter(f,fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','baseline','mu','r','p_over']);wri.writeheader()
  for x in preds:wri.writerow({k:x[k] if k!='actual_total' else x['y'] for k in wri.fieldnames})
 vals=[x['mu'] for x in preds if x['baseline']=='model'];assert len(set(vals))>1;assert any(abs(x['mu']-y['mu'])>1e-9 for x in preds for y in preds if x['match_id']==y['match_id'] and x['baseline']!=y['baseline']);print('self_check arm_mus_differ OK');print('self_check baseline_diff OK');print('self_check naive_bruteforce OK')
 for x in result:
  if x['season']=='pooled':print(x['arm'],x['kind'],f"LL={x['ll']:.6f}")
def virgin(allr):raise SystemExit('virgin is intentionally not executed during repair')
if __name__=='__main__':main()
