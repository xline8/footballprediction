import csv,json,math,sys
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;DATA=HERE.parents[2]/'PT-LigaPortugal/data/pt_matches.csv';sys.path.insert(0,str(HERE)); from common import *
def rows():
 z=load(DATA,{'sh':'shots_home','sa':'shots_away','oh':'sot_home','oa':'sot_away','xh':'xg_home','xa':'xg_away','xh6':'xgot_home','xa6':'xgot_away'})
 for x in z:x['y']=x['oh']+x['oa'];x['th']=x['sh'];x['ta']=x['sa']
 return z
def state(allr,s,arm):
 tr,cut,ww,L,r,_,_=season_state(allr,s,365,'y'); denom=sum(ww); shots=sum(q*(x['sh']+x['sa']) for x,q in zip(tr,ww));L=shots/(2*denom); ratio=sum(q*x['y'] for x,q in zip(tr,ww))/shots; d=defaultdict(lambda:[0.]*9)
 for x,q in zip(tr,ww):
  # Coordinator fix: Codex never accumulated shots AGAINST (it used
  # SOT-for as the against rate). a[8] = weighted shots conceded.
  for t,sh,ag,so,xg,xgot in ((x['home_id'],x['sh'],x['sa'],x['oh'],x['xh'],x['xh6']),(x['away_id'],x['sa'],x['sh'],x['oa'],x['xa'],x['xa6'])):
   a=d[t];xg=xg or 0;xgot=xgot or 0;a[0]+=q*sh;a[1]+=q*so;a[2]+=q*xg;a[3]+=q*xgot;a[4]+=q;a[5]+=1 if x['season'] in ('2024/2025','2025/2026') else 0;a[6]+=q*sh if x['season'] in ('2024/2025','2025/2026') else 0;a[7]+=q*xgot if x['season'] in ('2024/2025','2025/2026') else 0;a[8]+=q*ag
 def tilt(a,k):
  if arm=='gate_zero':return 1
  if arm=='x6' and a[5]<8:return 1
  den=a[0] if arm=='x4' else a[6];num=a[2] if arm=='x4' else a[7]; league=(sum(q*(x['xh'] or 0) for x,q in zip(tr,ww))/shots if arm=='x4' else sum(q*(x['xh6'] or 0) for x,q in zip(tr,ww))/shots);return clamp((num/max(den,1e-9)/max(league,1e-9))**.5,.8,1.25)
 def model(x):
  def team(t,fo):
   a=d[t];F=(a[0]+8*L)/(a[4]+8);A=(a[8]+8*L)/(a[4]+8);R=(a[1] + 200*ratio)/(a[0]+200);return F,A,R*tilt(a,fo)
  hf,ha,hr=team(x['home_id'],0);af,aa,ar=team(x['away_id'],0);return L*(hf/L)*(aa/L)*hr+L*(af/L)*(ha/L)*ar
 return tr,L,r,model
def main():
 if len(sys.argv)!=2:raise SystemExit('use dev or virgin')
 allr=rows();assert '2026/2027' not in {x['season'] for x in allr}
 if sys.argv[1]=='virgin':raise SystemExit('virgin is intentionally not executed during repair')
 preds=[];res=[];fits={}
 for arm in ('gate_zero','x4','x6'):
  for s in TARGETS:
   tr,L,r,model=state(allr,s,arm);dev=[x for x in allr if x['season']==s];cut=min(x['date'] for x in dev);ww=[(weight(cut,x['date'],270),x['y']) for x in tr];bm=sum(q*y for q,y in ww)/sum(q for q,y in ww);nm=naive(allr,s,'oh','oa',bm);assert abs(nm[dev[0]['match_id']]-naive_bruteforce(allr,dev[0],'oh','oa',bm))<1e-9;fits.setdefault(arm,{})[s]={'L':L,'r':r,'baseline_hl':270}
   for kind in ('model','league_base_rate','naive_trailing_10'):
    pp=[]
    for x in dev:
     m=model(x) if kind=='model' else (bm if kind=='league_base_rate' else nm[x['match_id']]);p=.5*nb_over(m,r,8.5)+.5*nb_over(nm[x['match_id']],r,8.5) if kind=='model' else nb_over(m,r,8.5);pp.append((p,int(x['y']>8.5)));preds.append({**x,'arm':arm,'baseline':kind,'mu':m,'r':r,'p_over':p})
    res.append({'arm':arm,'kind':kind,'season':s,'line':8.5,**metrics(pp,8.5)})
  for kind in ('model','league_base_rate','naive_trailing_10'):
   pp=[(x['p_over'],int(x['y']>8.5)) for x in preds if x['arm']==arm and x['baseline']==kind];res.append({'arm':arm,'kind':kind,'season':'pooled','line':8.5,**metrics(pp,8.5)})
 write(preds,res,fits)
def write(preds,res,fits):
 (HERE/'results_dev.json').write_text(json.dumps({'protocol':'S-PT DEV','rows_loaded':len(preds)//9,'fitted_params':fits,'results':res},indent=2)+'\n')
 with open(HERE/'results_dev.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=['arm','kind','season','n','ll','mean_p_over','actual_over']);w.writeheader();w.writerows({k:x.get(k,'') for k in w.fieldnames} for x in res)
 with open(HERE/'predictions_dev.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','baseline','mu','r','p_over']);w.writeheader();[w.writerow({k:x[k] if k!='actual_total' else x['y'] for k in w.fieldnames}) for x in preds]
 vals=[x['mu'] for x in preds if x['baseline']=='model'];assert len(set(vals))>1;assert any(abs(x['mu']-y['mu'])>1e-9 for x in preds for y in preds if x['match_id']==y['match_id'] and x['baseline']!=y['baseline']);print('self_check arm_mus_differ OK');print('self_check baseline_diff OK');print('self_check naive_bruteforce OK');[print(x['arm'],x['kind'],f"LL={x['ll']:.6f}") for x in res if x['season']=='pooled']
if __name__=='__main__':main()
