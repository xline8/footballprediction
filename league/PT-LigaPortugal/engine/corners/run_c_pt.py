import csv,json,math,sys
from pathlib import Path
from collections import defaultdict,deque
HERE=Path(__file__).resolve().parent;DATA=HERE.parents[2]/'PT-LigaPortugal/data/pt_matches.csv';sys.path.insert(0,str(HERE)); from common import *
GAMMAS=(0,.15,.3,.45,.6,.8);BP=(-.01,-.0075,-.005,-.0025,0,.0025,.005,.0075,.01);BC=(-.1,-.075,-.05,-.025,0,.025,.05,.075,.1);BT=(-.04,-.03,-.02,-.01,0,.01,.02,.03,.04)
def rows():
 z=load(DATA,{'ch':'corners_home','ca':'corners_away','sh':'shots_home','sa':'shots_away','ph':'poss_home','pa':'poss_away','bh':'bigchance_home','ba':'bigchance_away','th':'touches_home','ta':'touches_away'})
 for x in z:x['y']=x['ch']+x['ca']
 return z
def nb_logpmf(k,mu,r):
 if mu<=0: return 0.0 if k==0 else -30.0
 return math.lgamma(k+r)-math.lgamma(r)-math.lgamma(k+1)+r*math.log(r/(r+mu))+k*math.log(mu/(r+mu))
def features(allr):
 out=[];shots=defaultdict(lambda:deque(maxlen=5));hist=defaultdict(lambda:deque(maxlen=10));i=0
 while i<len(allr):
  j=i+1
  while j<len(allr) and allr[j]['date']==allr[i]['date']:j+=1
  prior=allr[:i];cut=allr[i]['date'];ww=[weight(cut,x['date'],270) for x in prior];den=sum(ww);bh=sum(q*x['ch'] for q,x in zip(ww,prior))/den if den else 0;ba=sum(q*x['ca'] for q,x in zip(ww,prior))/den if den else 0;L=sum(q*(x['sh']+x['sa']) for q,x in zip(ww,prior))/(2*den) if den else 1
  for x in allr[i:j]:
   def fac(t,k):return clamp(sum(v[k] for v in shots[t])/len(shots[t])/L,.6,1.7) if shots[t] else 1
   def z(t,k):
    q=[v for v in hist[t] if v[k+'f'] is not None and v[k+'a'] is not None];return sum(v[k+'f']-v[k+'a'] for v in q)/len(q) if len(q)>=8 else None
   vals={k:(z(x['home_id'],k),z(x['away_id'],k)) for k in ('p','b','t')};out.append({**x,'bh0':bh,'ba0':ba,'fhp':fac(x['home_id'],0),'fhc':fac(x['home_id'],1),'fap':fac(x['away_id'],0),'fac':fac(x['away_id'],1),'zp':None if None in vals['p'] else vals['p'][0]-vals['p'][1],'zb':None if None in vals['b'] else vals['b'][0]-vals['b'][1],'zt':None if None in vals['t'] else vals['t'][0]-vals['t'][1],'prior':len(prior)})
  for x in allr[i:j]:
   shots[x['home_id']].append((x['sh'],x['sa']));shots[x['away_id']].append((x['sa'],x['sh']))
   for t,f,a in ((x['home_id'],x['ph'],x['pa']),(x['away_id'],x['pa'],x['ph'])):hist[t].append({'pf':f,'pa':a,'bf':x['bh'] if t==x['home_id'] else x['ba'],'ba':x['ba'] if t==x['home_id'] else x['bh'],'tf':x['th'] if t==x['home_id'] else x['ta'],'ta':x['ta'] if t==x['home_id'] else x['th']})
  i=j
 return out
def main():
 if len(sys.argv)!=2:raise SystemExit('use dev or virgin')
 allr=rows();assert '2026/2027' not in {x['season'] for x in allr}
 if sys.argv[1]=='virgin':raise SystemExit('virgin is intentionally not executed during repair')
 fr=features(allr);pred=[];res=[];fits={}
 for arm in ('gate_zero','x7'):
  for s in TARGETS:
   tr=[x for x in fr if SEASONS.index(x['season'])<SEASONS.index(s) and x['prior']>=10];dev=[x for x in fr if x['season']==s];
   def core(x,g):return x['bh0']*(x['fhp']*x['fac'])**g+x['ba0']*(x['fap']*x['fhc'])**g
   best=None
   for g in GAMMAS:
    ms=[core(x,g) for x in tr];rr=clamp(sum((x['y']-m)**2 for x,m in zip(tr,ms))/max(sum(ms),1e-9),1.02,5);score=sum(-nb_logpmf(x['y'],m,rr) for x,m in zip(tr,ms))/len(tr);cand=(score,g,rr)  # gamma by full-count NB NLL per prereg (coordinator fix)
    if best is None or cand<best:best=cand
   _,g,rr=best;grid=[(a,b) for a in BP for b in BC] if arm=='gate_zero' else [(b,0) for b in BT];bs=min(grid,key=lambda z:(sum(logloss(nb_over(core(x,g)*clamp(math.exp((z[0]*(x['zp'] or 0)+z[1]*(x['zb'] or 0)) if arm=='gate_zero' else z[0]*(x['zt'] or 0)),.7,1.43),rr,9.5),int(x['y']>9.5)) for x in tr),sum(abs(q) for q in z),z));fits.setdefault(arm,{})[s]={'gamma':g,'r':rr,'beta':list(bs)}
   cutoff=min(x['date'] for x in dev);ww=[weight(cutoff,x['date'],270) for x in tr];bm=sum(q*x['y'] for q,x in zip(ww,tr))/sum(ww);r_base=moment([x['y'] for x in tr]);nm=naive(allr,s,'ch','ca',bm);assert abs(nm[dev[0]['match_id']]-naive_bruteforce(allr,dev[0],'ch','ca',bm))<1e-9
   for kind in ('model','league_base_rate','naive_trailing_10'):
    pp=[]
    for x in dev:
     m=core(x,g) if kind=='model' else (bm if kind=='league_base_rate' else nm[x['match_id']]);
     if kind=='model':m*=clamp(math.exp((bs[0]*(x['zp'] or 0)+bs[1]*(x['zb'] or 0)) if arm=='gate_zero' else bs[0]*(x['zt'] or 0)),.7,1.43)
     p=nb_over(m,rr if kind=='model' else r_base,9.5);pp.append((p,int(x['y']>9.5)));pred.append({**x,'arm':arm,'baseline':kind,'mu':m,'r':rr,'p_over':p})
    res.append({'arm':arm,'kind':kind,'season':s,'line':9.5,**metrics(pp,9.5)})
  for kind in ('model','league_base_rate','naive_trailing_10'):
   pp=[(x['p_over'],int(x['y']>9.5)) for x in pred if x['arm']==arm and x['baseline']==kind];res.append({'arm':arm,'kind':kind,'season':'pooled','line':9.5,**metrics(pp,9.5)})
 (HERE/'results_dev.json').write_text(json.dumps({'protocol':'C-PT DEV','rows_loaded':len(allr),'fitted_params':fits,'results':res},indent=2)+'\n')
 with open(HERE/'results_dev.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=['arm','kind','season','n','ll','mean_p_over','actual_over']);w.writeheader();w.writerows({k:x.get(k,'') for k in w.fieldnames} for x in res)
 with open(HERE/'predictions_dev.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['match_id','season','date','home_id','away_id','actual_total','arm','baseline','mu','r','p_over']);w.writeheader();[w.writerow({k:x[k] if k!='actual_total' else x['y'] for k in w.fieldnames}) for x in pred]
 vals=[x['mu'] for x in pred if x['baseline']=='model'];assert len(set(vals))>1;assert any(abs(x['mu']-y['mu'])>1e-9 for x in pred for y in pred if x['match_id']==y['match_id'] and x['baseline']!=y['baseline']);print('self_check arm_mus_differ OK');print('self_check baseline_diff OK');print('self_check naive_bruteforce OK');[print(x['arm'],x['kind'],f"LL={x['ll']:.6f}") for x in res if x['season']=='pooled']
if __name__=='__main__':main()
