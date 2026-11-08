"""Frozen shots-on-target model for QA-SecondDivision."""
import csv, math
from collections import defaultdict, deque
from datetime import date
import numpy as np

HL=365.0; K_PRIOR=8.0; NB_R=79.94; REFIT_DAYS=7; RIDGE_LAM=100.0
LINES=(7.5,8.5,9.5); ETA_LO,ETA_HI=-6.0,4.0

def nb_over(lam,r,line):
    kmax=int(math.floor(line)); q=lam/(r+lam); term=(r/(r+lam))**r; cdf=term
    for k in range(1,kmax+1): term*=(k-1+r)/k*q; cdf+=term
    return min(max(1-cdf,0),1)

class Decayed:
    def __init__(self): self.s=self.w=0.; self.last=None
    def at(self,d):
        if self.last is not None and d>self.last:
            f=.5**((d-self.last)/HL); self.s*=f; self.w*=f
        self.last=d; return self.s,self.w
    def add(self,d,x): self.at(d); self.s+=x; self.w+=1

class Ratings:
    def __init__(self):
        self.lh,self.la=defaultdict(Decayed),defaultdict(Decayed)
        self.ah,self.dh=defaultdict(Decayed),defaultdict(Decayed)
        self.aa,self.da=defaultdict(Decayed),defaultdict(Decayed)
        self.sh,self.sa=defaultdict(Decayed),defaultdict(Decayed)
        self.lsh,self.lsa=defaultdict(Decayed),defaultdict(Decayed)
    def mean(self,div,d):
        h,wh=self.lh[div].at(d); a,wa=self.la[div].at(d)
        return h/wh if wh else 13., a/wa if wa else 11.
    def shr(self,x,d,mu): s,w=x.at(d); return (s+K_PRIOR*mu)/(w+K_PRIOR)
    def predict(self,div,h,a,d):
        mh,ma=self.mean(div,d)
        return mh*self.shr(self.ah[div,h],d,mh)/mh*self.shr(self.da[div,a],d,mh)/mh, ma*self.shr(self.aa[div,a],d,ma)/ma*self.shr(self.dh[div,h],d,ma)/ma
    def ratio(self,div,t,venue,d,prior):
        if venue=='h': sh,so,ls,lo=self.ah[div,t],self.sh[div,t],self.lh[div],self.lsh[div]; fb=4.5/13
        else: sh,so,ls,lo=self.aa[div,t],self.sa[div,t],self.la[div],self.lsa[div]; fb=3.5/11
        ss,_=sh.at(d); s,_=so.at(d); lss,_=ls.at(d); lso,_=lo.at(d); rho=lso/lss if lss else fb
        return (s+prior*rho)/(ss+prior)
    def update(self,m):
        d=m['day']; div,h,a=m['div'],m['home'],m['away']
        self.ah[div,h].add(d,m['shots_h']); self.dh[div,h].add(d,m['shots_a']); self.aa[div,a].add(d,m['shots_a']); self.da[div,a].add(d,m['shots_h'])
        self.lh[div].add(d,m['shots_h']); self.la[div].add(d,m['shots_a']); self.sh[div,h].add(d,m['sot_h']); self.sa[div,a].add(d,m['sot_a']); self.lsh[div].add(d,m['sot_h']); self.lsa[div].add(d,m['sot_a'])

class Regression:
    def __init__(self,ms):
        self.d={}
        for div in sorted({m['div'] for m in ms}):
            z=[m for m in ms if m['div']==div]; teams=sorted({m['home'] for m in z}|{m['away'] for m in z}); ix={t:i for i,t in enumerate(teams)}; T=len(teams)
            self.d[div]={'teams':teams,'ix':ix,'T':T,'day':np.array([m['day'] for m in z],float),'hi':np.array([ix[m['home']] for m in z]),'ai':np.array([ix[m['away']] for m in z]),'yh':np.array([m['sot_h'] for m in z]),'ya':np.array([m['sot_a'] for m in z]),'theta':None,'next':None}
    def fit(self,x,d):
        day,hi,ai,yh,ya,T=x['day'],x['hi'],x['ai'],x['yh'],x['ya'],x['T']; cut=int(np.searchsorted(day,d,'left')); P=2+2*T; th=x['theta']
        if th is None:
            th=np.zeros(P); th[:2]=math.log(max(np.mean(yh[:cut]) if cut else 4.5,1e-3)),math.log(max(np.mean(ya[:cut]) if cut else 3.5,1e-3))
        if not cut: x['theta']=th; return
        w0=.5**((d-day[:cut])/HL); y=np.r_[yh[:cut],ya[:cut]]; b=np.r_[np.zeros(cut,int),np.ones(cut,int)]; aa=np.r_[hi[:cut],ai[:cut]]+2; dd=np.r_[ai[:cut],hi[:cut]]+2+T; w=np.r_[w0,w0]
        def obj(t):
            e=np.clip(t[b]+t[aa]+t[dd],ETA_LO,ETA_HI); return float(np.sum(w*(y*e-np.exp(e)))-.5*RIDGE_LAM*np.sum(t[2:]**2))
        cur=obj(th)
        for _ in range(60):
            e=np.clip(th[b]+th[aa]+th[dd],ETA_LO,ETA_HI); mu=np.exp(e); r=w*(y-mu); g=np.zeros(P)
            for q in (b,aa,dd): np.add.at(g,q,r)
            g[2:]-=RIDGE_LAM*th[2:]; W=w*mu; H=np.zeros((P,P))
            for q,z in ((b,b),(b,aa),(b,dd),(aa,b),(aa,aa),(aa,dd),(dd,b),(dd,aa),(dd,dd)): np.add.at(H,(q,z),W)
            H[np.arange(2,P),np.arange(2,P)]+=RIDGE_LAM; H[np.arange(P),np.arange(P)]+=1e-10
            try: step=np.linalg.solve(H,g)
            except np.linalg.LinAlgError: break
            t=1.
            for _ in range(25):
                cand=th+t*step
                if obj(cand)>=cur-1e-12: th,cur=cand,obj(cand); break
                t*=.5
            else: break
            if np.max(np.abs(t*step))<1e-6: break
        x['theta']=th
    def ensure(self,div,d):
        x=self.d[div]
        if x['next'] is None or d>=x['next']: self.fit(x,d); x['next']=d+REFIT_DAYS
        return x
    def predict(self,div,h,a,d):
        x=self.ensure(div,d); t=x['theta']; T,ix=x['T'],x['ix']; ih,ia=ix.get(h),ix.get(a); ah=t[2+ih] if ih is not None else 0; aa=t[2+ia] if ia is not None else 0; dh=t[2+T+ih] if ih is not None else 0; da=t[2+T+ia] if ia is not None else 0
        return math.exp(np.clip(t[0]+ah+da,ETA_LO,ETA_HI)),math.exp(np.clip(t[1]+aa+dh,ETA_LO,ETA_HI))
    def means(self,div,d): t=self.ensure(div,d)['theta']; return math.exp(t[0]),math.exp(t[1])

class Engine:
    def __init__(self,ms,arm): self.arm=arm; self.reg=Regression(ms); self.r=Ratings(); self.n=defaultdict(lambda:deque(maxlen=10))
    def predict(self,m):
        d,div,h,a=m['day'],m['div'],m['home'],m['away']; rh,ra=self.reg.predict(div,h,a,d); sh,sa=self.r.predict(div,h,a,d); prior=20000. if self.arm=='RS' else 200.; eh=.5*(rh+sh*self.r.ratio(div,h,'h',d,prior)); ea=.5*(ra+sa*self.r.ratio(div,a,'a',d,prior)); mh,ma=self.reg.means(div,d); hh,aa=self.n[div,h],self.n[div,a]
        if hh and aa:
            hf,ha=np.mean(hh,axis=0); af,ah=np.mean(aa,axis=0); nh,na=(hf+ah)/2,(af+ha)/2
        else: nh,na=mh,ma
        return {'exp_h':eh,'exp_a':ea,'probs':{L:.5*nb_over(eh+ea,NB_R,L)+.5*nb_over(nh+na,NB_R,L) for L in LINES},'naive_probs':{L:nb_over(nh+na,NB_R,L) for L in LINES}}
    def update(self,m): self.r.update(m); self.n[m['div'],m['home']].append((m['sot_h'],m['sot_a'])); self.n[m['div'],m['away']].append((m['sot_a'],m['sot_h']))

def load_matches(path,seasons):
    out=[]
    with open(path,newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['season'] not in seasons or r['phase']!='regular' or r.get('awarded','0')!='0': continue
            if any(r[k] == '' for k in ('total_shots_home','total_shots_away','ShotsOnTarget_home','ShotsOnTarget_away')): continue
            def n(k): return float(r[k])
            dt=date.fromisoformat(r['date']); out.append({'match_id':r['match_id'],'date':dt,'day':dt.toordinal(),'season':r['season'],'round':int(r['round']),'div':r['league'],'home':r['home_team'],'away':r['away_team'],'shots_h':n('total_shots_home'),'shots_a':n('total_shots_away'),'sot_h':n('ShotsOnTarget_home'),'sot_a':n('ShotsOnTarget_away')})
    return sorted(out,key=lambda m:(m['date'],m['match_id']))
