"""Frozen K-SA state and probability mechanics."""
import math
from collections import defaultdict, deque

HL, K_PRIOR, K_REF = 270.0, 8.0, 8.0
FB_MU_H, FB_MU_A = 2.15, 1.95

class Decayed:
    __slots__ = ("s", "w", "last")
    def __init__(self): self.s = self.w = 0.0; self.last = None
    def at(self, day):
        if self.last is not None and day > self.last:
            f = 0.5 ** ((day - self.last) / HL); self.s *= f; self.w *= f
        self.last = day; return self.s, self.w
    def add(self, day, x):
        self.at(day); self.s += x; self.w += 1.0

class Team:
    __slots__ = ("att_h", "def_h", "att_a", "def_a")
    def __init__(self): self.att_h=Decayed(); self.def_h=Decayed(); self.att_a=Decayed(); self.def_a=Decayed()

class State:
    def __init__(self): self.teams = defaultdict(Team); self.h = Decayed(); self.a = Decayed()
    def means(self, day):
        sh, wh = self.h.at(day); sa, wa = self.a.at(day)
        # A zero-card opening observation makes the multiplicative ratio
        # undefined; treat it as the frozen pre-history fallback.
        return (sh / wh if wh and sh > 0 else FB_MU_H, sa / wa if wa and sa > 0 else FB_MU_A)
    @staticmethod
    def shrink(stat, day, mu):
        s, w = stat.at(day); return (s + K_PRIOR * mu) / (w + K_PRIOR)
    def predict(self, home, away, day):
        mh, ma = self.means(day); th, ta = self.teams[home], self.teams[away]
        eh = mh * (self.shrink(th.att_h, day, mh) / mh) * (self.shrink(ta.def_a, day, mh) / mh)
        ea = ma * (self.shrink(ta.att_a, day, ma) / ma) * (self.shrink(th.def_h, day, ma) / ma)
        return eh, ea
    def update(self, home, away, day, yh, ya):
        th, ta = self.teams[home], self.teams[away]
        th.att_h.add(day,yh); th.def_h.add(day,ya); ta.att_a.add(day,ya); ta.def_a.add(day,yh)
        self.h.add(day,yh); self.a.add(day,ya)
    def snapshot(self, day):
        mh, ma = self.means(day); teams = {}
        for team, t in self.teams.items():
            teams[str(team)] = {
                "att_home": self.shrink(t.att_h, day, mh), "def_home": self.shrink(t.def_h, day, ma),
                "att_away": self.shrink(t.att_a, day, ma), "def_away": self.shrink(t.def_a, day, mh),
            }
        return {"league_mean_home": mh, "league_mean_away": ma, "teams": teams}

def nb_over(mu, r, line):
    kmax=int(math.floor(line)); q=mu/(r+mu); term=(r/(r+mu))**r; cdf=term
    for k in range(1,kmax+1): term *= (k-1+r)/k*q; cdf += term
    return min(max(1.0-cdf, 0.0), 1.0)

def estimate_r(records, key):
    num=sum(x[key]**2 for x in records)
    den=sum((x["y"]-x[key])**2-x[key] for x in records)
    return 500.0 if den <= 0 else min(max(num/den, 2.0), 500.0)

class Online:
    def __init__(self):
        self.state=State(); self.naive=defaultdict(lambda: deque(maxlen=10)); self.refs=defaultdict(list); self.league_n=0; self.league_sum=0.0
    def prediction(self, row, arm):
        day=row["day"]; eh,ea=self.state.predict(row["home_id"],row["away_id"],day); mh,ma=self.state.means(day)
        hh, ha = self.naive[row["home_id"]], self.naive[row["away_id"]]
        if hh and ha:
            hf=sum(x[0] for x in hh)/len(hh); hag=sum(x[1] for x in hh)/len(hh); af=sum(x[0] for x in ha)/len(ha); aag=sum(x[1] for x in ha)/len(ha)
            nh,na=(hf+aag)/2,(af+hag)/2
        else: nh,na=mh,ma
        ref=row.get("referee",""); prior=[x for x in self.refs[ref] if x[0] < row["kickoff_utc"]] if ref else []
        reason=""; mult=1.0
        if not ref: reason="unknown_identity"
        elif len(prior)<8: reason="thin_history"
        else:
            assert prior[-1][0] < row["kickoff_utc"]
            lm=self.league_sum/self.league_n if self.league_n else 0.0
            rate=(sum(x[1] for x in prior)+K_REF*lm)/(len(prior)+K_REF); mult=min(1.50,max(0.67,rate/lm)) if lm else 1.0
        if arm == "x8" and not reason: eh*=mult; ea*=mult
        return {"model":eh+ea, "base":mh+ma, "naive":nh+na, "eh":eh, "ea":ea,
                "referee":ref, "n_prior":len(prior), "multiplier":mult if arm=="x8" and not reason else 1.0,
                "fallback":bool(reason), "fallback_reason":reason}
    def update(self,row):
        self.state.update(row["home_id"],row["away_id"],row["day"],row["yh"],row["ya"])
        self.naive[row["home_id"]].append((row["yh"],row["ya"])); self.naive[row["away_id"]].append((row["ya"],row["yh"]))
        self.league_sum += row["y"]; self.league_n += 1
        if row.get("referee"): self.refs[row["referee"]].append((row["kickoff_utc"],row["y"]))
