"""Online venue-split yellow-card state and negative-binomial mechanics."""
import math
from collections import defaultdict, deque
HL,K_PRIOR=270.0,8.0
FB_MU_H,FB_MU_A=2.15,1.95
class Decayed:
    __slots__=("s","w","last")
    def __init__(self): self.s=self.w=0.; self.last=None
    def at(self,day):
        if self.last is not None and day>self.last:
            f=.5**((day-self.last)/HL); self.s*=f; self.w*=f
        self.last=day; return self.s,self.w
    def add(self,day,x): self.at(day); self.s+=x; self.w+=1
class Team:
    __slots__=("att_h","def_h","att_a","def_a")
    def __init__(self): self.att_h=Decayed(); self.def_h=Decayed(); self.att_a=Decayed(); self.def_a=Decayed()
class State:
    def __init__(self): self.teams=defaultdict(Team); self.h=Decayed(); self.a=Decayed()
    def means(self,day):
        sh,wh=self.h.at(day); sa,wa=self.a.at(day)
        return sh/wh if wh and sh>0 else FB_MU_H, sa/wa if wa and sa>0 else FB_MU_A
    @staticmethod
    def shrink(stat,day,mu):
        s,w=stat.at(day); return (s+K_PRIOR*mu)/(w+K_PRIOR)
    def predict(self,home,away,day):
        mh,ma=self.means(day); th,ta=self.teams[home],self.teams[away]
        return mh*self.shrink(th.att_h,day,mh)/mh*self.shrink(ta.def_a,day,mh)/mh, ma*self.shrink(ta.att_a,day,ma)/ma*self.shrink(th.def_h,day,ma)/ma
    def update(self,home,away,day,yh,ya):
        th,ta=self.teams[home],self.teams[away]; th.att_h.add(day,yh); th.def_h.add(day,ya); ta.att_a.add(day,ya); ta.def_a.add(day,yh); self.h.add(day,yh); self.a.add(day,ya)
def nb_over(mu,r,line):
    kmax=int(math.floor(line)); q=mu/(r+mu); term=(r/(r+mu))**r; cdf=term
    for k in range(1,kmax+1): term*=(k-1+r)/k*q; cdf+=term
    return min(max(1-cdf,0),1)
def estimate_r(records,key):
    num=sum(x[key]**2 for x in records); den=sum((x["y"]-x[key])**2-x[key] for x in records)
    return 500. if den<=0 else min(max(num/den,2.),500.)
class Online:
    def __init__(self): self.state=State(); self.naive=defaultdict(lambda:deque(maxlen=10)); self.n=0; self.total=0.
    def prediction(self,row):
        day=row["day"]; eh,ea=self.state.predict(row["home_id"],row["away_id"],day); mh,ma=self.state.means(day)
        hh,ha=self.naive[row["home_id"]],self.naive[row["away_id"]]
        if hh and ha:
            nh=(sum(x[0] for x in hh)/len(hh)+sum(x[1] for x in ha)/len(ha))/2; na=(sum(x[0] for x in ha)/len(ha)+sum(x[1] for x in hh)/len(hh))/2
        else: nh,na=mh,ma
        assert row.get("referee","")==""
        return {"model":eh+ea,"base":mh+ma,"naive":nh+na,"referee_applied":False}
    def update(self,row):
        self.state.update(row["home_id"],row["away_id"],row["day"],row["yh"],row["ya"]); self.naive[row["home_id"]].append((row["yh"],row["ya"])); self.naive[row["away_id"]].append((row["ya"],row["yh"])); self.n+=1; self.total+=row["y"]
