"""Frozen FO cards state, NB mechanics, and causal online predictions."""
import math
from collections import defaultdict, deque

HL=270.0; FB_MU_H=2.15; FB_MU_A=1.95
class Decayed:
    def __init__(self): self.s=self.w=0.0; self.last=None
    def at(self,day):
        if self.last is not None and day>self.last:
            f=.5**((day-self.last)/HL); self.s*=f; self.w*=f
        self.last=day; return self.s,self.w
    def add(self,day,x): self.at(day); self.s+=x; self.w+=1
class Team:
    def __init__(self): self.att_h=Decayed(); self.def_h=Decayed(); self.att_a=Decayed(); self.def_a=Decayed()
class State:
    def __init__(self,k): self.k=k; self.teams=defaultdict(Team); self.lh=Decayed(); self.la=Decayed()
    def means(self,day):
        sh,wh=self.lh.at(day); sa,wa=self.la.at(day)
        return (sh/wh if wh and sh > 0 else FB_MU_H, sa/wa if wa and sa > 0 else FB_MU_A)
    def shrink(self,stat,day,mu):
        s,w=stat.at(day); return (s+self.k*mu)/(w+self.k)
    def predict(self,h,a,day):
        mh,ma=self.means(day); th,ta=self.teams[h],self.teams[a]
        eh=mh*(self.shrink(th.att_h,day,mh)/mh)*(self.shrink(ta.def_a,day,mh)/mh)
        ea=ma*(self.shrink(ta.att_a,day,ma)/ma)*(self.shrink(th.def_h,day,ma)/ma)
        return eh,ea,mh,ma
    def update(self,h,a,day,yh,ya):
        th,ta=self.teams[h],self.teams[a]; th.att_h.add(day,yh); th.def_h.add(day,ya); ta.att_a.add(day,ya); ta.def_a.add(day,yh); self.lh.add(day,yh); self.la.add(day,ya)
    def snapshot(self,day):
        mh,ma=self.means(day); return {"mu_h":mh,"mu_a":ma,"teams":{str(t):{"att_h":self.shrink(x.att_h,day,mh),"def_h":self.shrink(x.def_h,day,ma),"att_a":self.shrink(x.att_a,day,ma),"def_a":self.shrink(x.def_a,day,mh)} for t,x in self.teams.items()}}
class Online:
    def __init__(self,k): self.state=State(k); self.hist=defaultdict(lambda:deque(maxlen=10)); self.n_updates=0; self.last_key=None
    def predict(self,r):
        key=(r["date"],r["match_id"])
        if self.last_key is not None: assert self.last_key < key, "cards prediction is not strictly before prior update"
        eh,ea,mh,ma=self.state.predict(r["home_id"],r["away_id"],r["day"])
        h=self.hist[r["home_id"]]; a=self.hist[r["away_id"]]
        if h and a:
            hf=sum(x[0] for x in h)/len(h); ha=sum(x[1] for x in h)/len(h); af=sum(x[0] for x in a)/len(a); aa=sum(x[1] for x in a)/len(a); nh,na=(hf+aa)/2,(af+ha)/2
        else: nh,na=mh,ma
        return {"model":eh+ea,"eh":eh,"ea":ea,"base":mh+ma,"naive":nh+na}
    def update(self,r):
        assert self.last_key is None or self.last_key < (r["date"],r["match_id"])
        self.state.update(r["home_id"],r["away_id"],r["day"],r["yh"],r["ya"]); self.hist[r["home_id"]].append((r["yh"],r["ya"])); self.hist[r["away_id"]].append((r["ya"],r["yh"]))
        self.last_key=(r["date"],r["match_id"]); self.n_updates+=1
def nb_over(mu,r,line):
    k=int(math.floor(line)); q=mu/(r+mu); term=(r/(r+mu))**r; cdf=term
    for i in range(1,k+1): term*=(i-1+r)/i*q; cdf+=term
    return min(max(1-cdf,0),1)
def estimate_r(records,key):
    num=sum(x[key]**2 for x in records); den=sum((x["y"]-x[key])**2-x[key] for x in records)
    return 500.0 if den<=0 else min(max(num/den,2.0),500.0)
