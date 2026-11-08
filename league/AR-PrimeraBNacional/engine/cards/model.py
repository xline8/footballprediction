"""Online decayed BNAC yellow-card state and preregistered X8 factor."""
import math
from collections import defaultdict, deque
from datetime import date as _date
HL=270.0; K_PRIOR=8.0; K_REF=8.0; R=112.39; FB_MU_H=2.15; FB_MU_A=1.95
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
    def __init__(self): self.teams=defaultdict(Team); self.h=Decayed(); self.a=Decayed()
    def means(self,day):
        sh,wh=self.h.at(day); sa,wa=self.a.at(day)
        return (sh/wh if wh and sh > 0 else FB_MU_H),(sa/wa if wa and sa > 0 else FB_MU_A)
    def shrink(self,stat,day,mu):
        s,w=stat.at(day); return (s+K_PRIOR*mu)/(w+K_PRIOR)
    def predict(self,home,away,day):
        mh,ma=self.means(day); th,ta=self.teams[home],self.teams[away]
        if not mh or not ma: return mh,ma
        return mh*(self.shrink(th.att_h,day,mh)/mh)*(self.shrink(ta.def_a,day,mh)/mh), ma*(self.shrink(ta.att_a,day,ma)/ma)*(self.shrink(th.def_h,day,ma)/ma)
    def update(self,row):
        h,a=self.teams[row["home_id"]],self.teams[row["away_id"]]; d=row["day"]
        h.att_h.add(d,row["yh"]); h.def_h.add(d,row["ya"]); a.att_a.add(d,row["ya"]); a.def_a.add(d,row["yh"]); self.h.add(d,row["yh"]); self.a.add(d,row["ya"])
    def snapshot(self, day):
        mh, ma = self.means(day)
        teams = {}
        for tid, team in sorted(self.teams.items(), key=lambda x: str(x[0])):
            teams[str(tid)] = {"att_home": self.shrink(team.att_h, day, mh), "def_home": self.shrink(team.def_h, day, ma), "att_away": self.shrink(team.att_a, day, ma), "def_away": self.shrink(team.def_a, day, mh)}
        return {"league_mean_home": mh, "league_mean_away": ma, "teams": teams}
def nb_over(mu,line):
    kmax=int(math.floor(line)); q=mu/(R+mu); term=(R/(R+mu))**R; cdf=term
    for k in range(1,kmax+1): term *= (k-1+R)/k*q; cdf += term
    return min(max(1-cdf,0),1)
class Online:
    def __init__(self): self.state=State(); self.naive=defaultdict(lambda:deque(maxlen=10)); self.refs=defaultdict(list); self.league=[]
    def prediction(self,row,arm):
        day=row["day"]; eh,ea=self.state.predict(row["home_id"],row["away_id"],day); mh,ma=self.state.means(day)
        h,a=self.naive[row["home_id"]],self.naive[row["away_id"]]
        if h and a:
            hf=sum(x[0] for x in h)/len(h); hc=sum(x[1] for x in h)/len(h); af=sum(x[0] for x in a)/len(a); ac=sum(x[1] for x in a)/len(a); nh,na=(hf+ac)/2,(af+hc)/2
        else: nh,na=mh,ma
        ref=row["referee"]; prior=self.refs[ref] if ref else []; factor=1.0
        if ref and len(prior)>=8:
            # Preregistered X8 (AR form): decayed (HL=270) referee mean,
            # shrunk toward the plain running league mean, K_REF=8,
            # clamped to [0.8, 1.25]. Fewer than 8 priors -> factor 1.0.
            lm=sum(self.league)/len(self.league) if self.league else 0.0
            if lm:
                ws=[0.5**((day-_date.fromisoformat(k[0]).toordinal())/HL) for k,_ in prior]
                rate=(sum(w*y for w,(_,y) in zip(ws,prior))+K_REF*lm)/(sum(ws)+K_REF)
                factor=min(1.25,max(.8,rate/lm))
        if arm=="x8": eh*=factor; ea*=factor
        return {"model":eh+ea,"base":mh+ma,"naive":nh+na,"ref_factor":factor,"ref_prior":len(prior),"eh":eh,"ea":ea}
    def update(self,row):
        self.state.update(row); self.naive[row["home_id"]].append((row["yh"],row["ya"])); self.naive[row["away_id"]].append((row["ya"],row["yh"])); self.league.append(row["y"])
        if row["referee"]: self.refs[row["referee"]].append((row["key"],row["y"]))
