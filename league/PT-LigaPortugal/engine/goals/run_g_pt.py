"""DEV-only G-PT Dixon-Coles runner."""
import csv, json, math, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE=Path(__file__).resolve().parent; DATA=HERE.parents[1]/"data/pt_matches.csv"
TRAIN=("2021/2022","2022/2023","2023/2024","2024/2025","2025/2026")
TARGET=TRAIN[1:]; MAXG=10; RHOS=(0.0,-.05,-.10,-.15)

def load(seasons):
    out=[]
    with open(DATA,newline='',encoding='utf-8') as f:
        for x in csv.DictReader(f):
            if x['season'] not in seasons: continue
            n=lambda k: float(x[k])
            out.append({'id':x['match_id'],'season':x['season'],'date':date.fromisoformat(x['date']),'hi':x['home_id'],'ai':x['away_id'],'yh':n('home_goals'),'ya':n('away_goals'),'xgh':n('xg_home'),'xga':n('xg_away')})
    out.sort(key=lambda z:(z['date'],z['id'])); return out
def pois(k,l): return math.exp(-l+k*math.log(max(l,1e-12))-math.lgamma(k+1))
def tau(x,y,h,a,r):
    if (x,y)==(0,0): return max(0,1-h*a*r)
    if (x,y)==(0,1): return max(0,1+h*r)
    if (x,y)==(1,0): return max(0,1+a*r)
    if (x,y)==(1,1): return max(0,1-r)
    return 1
class DC:
    def __init__(self,shrink=False): self.a=defaultdict(float); self.d=defaultdict(float); self.h=.28; self.rho=0; self.shrink=shrink; self.count=defaultdict(int)
    def fit(self,rows,cut):
        for g in rows: self.count[g['hi']]+=1; self.count[g['ai']]+=1
        obs=[]; sg=sw=0
        for g in rows:
            w=.5**((cut-g['date']).days/270); oh=.5*(g['yh']+g['xgh']); oa=.5*(g['ya']+g['xga']); obs.append((g,oh,oa,w)); sg+=w*(oh+oa); sw+=w
        self.h=.28
        for _ in range(14):
            of=defaultdict(float); ef=defaultdict(float); od=defaultdict(float); ed=defaultdict(float); so=se=0
            for g,oh,oa,w in obs:
                lh,la=self.lam(g['hi'],g['ai']); of[g['hi']]+=w*oh; ef[g['hi']]+=w*lh; of[g['ai']]+=w*oa; ef[g['ai']]+=w*la; od[g['ai']]+=w*oh; ed[g['ai']]+=w*lh; od[g['hi']]+=w*oa; ed[g['hi']]+=w*la; so+=w*oh; se+=w*lh
            for t in set(of)|set(ef): self.a[t]+=.7*math.log((of[t]+.25)/(ef[t]+.25))
            for t in set(od)|set(ed): self.d[t]+=.7*math.log((od[t]+.25)/(ed[t]+.25))
            self.h+=.7*math.log((so+.25)/(se+.25))
        self.rho=max(RHOS,key=lambda r:sum(w*math.log(max(tau(g['yh'],g['ya'],*self.lam(g['hi'],g['ai']),r),1e-12)) for g,_,_,w in obs if g['yh']<=1 or g['ya']<=1))
    def lam(self,h,a):
        # Coordinator fix: prereg SHRINK applies AFTER the Gate Zero
        # fit, by scaling the stored ratings of teams with <15
        # training matches (done in main after fit()). Codex's first
        # version applied the factor inside lam(), distorting the fit
        # itself. (No team qualifies in this corpus — training counts
        # are 0 or >=34 — so the arm is a documented no-op clone.)
        return math.exp(self.a[h]+self.d[a]+self.h),math.exp(self.a[a]+self.d[h])
    def apply_shrink(self):
        if not self.shrink: return
        for t in set(self.a)|set(self.d):
            if self.count[t]<15: self.a[t]*=.5; self.d[t]*=.5
    def over(self,h,a,line):
        m=[[pois(x,h)*pois(y,a)*tau(x,y,h,a,self.rho) for y in range(MAXG+1)] for x in range(MAXG+1)]; z=sum(map(sum,m)); return sum(m[x][y] for x in range(MAXG+1) for y in range(MAXG+1) if x+y>line)/z
    def probs(self,g):
        h,a=self.lam(g['hi'],g['ai']); m=[[pois(x,h)*pois(y,a)*tau(x,y,h,a,self.rho) for y in range(MAXG+1)] for x in range(MAXG+1)]; z=sum(map(sum,m)); ph=sum(m[x][y] for x in range(11) for y in range(11) if x>y)/z; pd=sum(m[x][x] for x in range(11))/z; return ph,pd,1-ph-pd,self.over(h,a,2.5)
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def main():
    if len(sys.argv)!=2 or sys.argv[1]!='dev': raise SystemExit('use: run_g_pt.py dev (virgin is intentionally not executed)')
    rows=load(TRAIN); assert '2026/2027' not in {r['season'] for r in rows}; result=[]; params={}
    for arm in ('gate_zero','shrink'):
      for s in TARGET:
        tr=[r for r in rows if TRAIN.index(r['season'])<TRAIN.index(s)]; te=[r for r in rows if r['season']==s]; dc=DC(arm=='shrink'); dc.fit(tr,min(r['date'] for r in te)); dc.apply_shrink(); params.setdefault(arm,{})[s]={'rho':dc.rho,'team_counts':dict(dc.count)}
        for kind in ('model','climatology'):
          ps=[]
          for g in te:
            if kind=='model': ph,pd,pa,po=dc.probs(g)
            else:
              prior=[r for r in rows if TRAIN.index(r['season'])<TRAIN.index(s)]; hw=sum(r['yh']>r['ya'] for r in prior)/len(prior); dw=sum(r['yh']==r['ya'] for r in prior)/len(prior); po=sum(r['yh']+r['ya']>2.5 for r in prior)/len(prior); ph,pd,pa=hw,dw,1-hw-dw
            ps.append((g,ph,pd,pa,po))
          result.append(metrics(s,arm,kind,ps))
    for arm in ('gate_zero','shrink'):
      for kind in ('model','climatology'):
        ps=[]
        for s in TARGET:
          tr=[r for r in rows if TRAIN.index(r['season'])<TRAIN.index(s)]; te=[r for r in rows if r['season']==s]; dc=DC(arm=='shrink'); dc.fit(tr,min(r['date'] for r in te)); dc.apply_shrink()
          for g in te:
            if kind=='model': ph,pd,pa,po=dc.probs(g)
            else:
              hw=sum(r['yh']>r['ya'] for r in tr)/len(tr); dw=sum(r['yh']==r['ya'] for r in tr)/len(tr); po=sum(r['yh']+r['ya']>2.5 for r in tr)/len(tr); ph,pd,pa=hw,dw,1-hw-dw
            ps.append((g,ph,pd,pa,po))
        result.append(metrics('pooled',arm,kind,ps))
    (HERE/'results_dev.json').write_text(json.dumps({'protocol':'G-PT DEV','rows_loaded':len(rows),'fitted_params':params,'results':result},indent=2)+'\n')
    with open(HERE/'results_dev.csv','w',newline='',encoding='utf-8') as f:
      w=csv.DictWriter(f,fieldnames=['arm','kind','season','n','ll_1x2','rps','ll_ou2_5','mean_p_over','actual_over','home_win_rate']); w.writeheader(); w.writerows(x for x in result)
    for x in result:
      if x['season']=='pooled': print(x['arm'],x['kind'],f"LL1X2={x['ll_1x2']:.6f}",f"OU={x['ll_ou2_5']:.6f}")
def metrics(s,arm,kind,ps):
    n=len(ps); h=[]; r=[]; o=[]; pp=[]; yy=[]
    for g,ph,pd,pa,po in ps:
      y=(1,0,0) if g['yh']>g['ya'] else ((0,1,0) if g['yh']==g['ya'] else (0,0,1)); h.append(-sum(v*math.log(max(p,1e-12)) for v,p in zip(y,(ph,pd,pa)))); r.append(0.5*((ph-y[0])**2+((ph+pd)-(y[0]+y[1]))**2)); yy.append(int(g['yh']+g['ya']>2.5)); pp.append(po); o.append(ll(po,yy[-1]))
    return {'arm':arm,'kind':kind,'season':s,'n':n,'ll_1x2':sum(h)/n,'rps':sum(r)/n,'ll_ou2_5':sum(o)/n,'mean_p_over':sum(pp)/n,'actual_over':sum(yy)/n,'home_win_rate':sum(g['yh']>g['ya'] for g,*_ in ps)/n}
if __name__=='__main__': main()
