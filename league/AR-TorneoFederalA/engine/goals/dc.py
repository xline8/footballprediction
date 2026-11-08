"""Goals-only Dixon-Coles model for G-FEDA."""
import math
from collections import defaultdict

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE = 270.0

def pois(k, lam):
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))

def tau(x, y, lh, la, rho):
    if x == 0 and y == 0: return max(0.0, 1.0 - lh * la * rho)
    if x == 0 and y == 1: return max(0.0, 1.0 + lh * rho)
    if x == 1 and y == 0: return max(0.0, 1.0 + la * rho)
    if x == 1 and y == 1: return max(0.0, 1.0 - rho)
    return 1.0

class DC:
    def __init__(self):
        self.a, self.d = defaultdict(float), defaultdict(float)
        self.h, self.rho, self.mu = 0.28, 0.0, 0.0

    def fit(self, games, cutoff):
        obs, wg, wm = [], 0.0, 0.0
        for g in games:
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            wg += w * (g["yh"] + g["ya"]); wm += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        if not obs: raise ValueError("empty training set")
        self.mu = wg / (2.0 * wm)
        for _ in range(14):
            oa=defaultdict(float); ea=defaultdict(float); od=defaultdict(float); ed=defaultdict(float); so=se=0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                oa[g["hi"]] += w*yh; ea[g["hi"]] += w*lh; oa[g["ai"]] += w*ya; ea[g["ai"]] += w*la
                od[g["ai"]] += w*yh; ed[g["ai"]] += w*lh; od[g["hi"]] += w*ya; ed[g["hi"]] += w*la
                so += w*yh; se += w*lh
            for t in set(oa) | set(ea): self.a[t] += 0.7 * math.log((oa[t]+0.25)/(ea[t]+0.25))
            for t in set(od) | set(ed): self.d[t] += 0.7 * math.log((od[t]+0.25)/(ed[t]+0.25))
            self.h += 0.7 * math.log((so+0.25)/(se+0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, yh, ya, w in obs:
                if yh <= 1 or ya <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"]); z = tau(int(yh), int(ya), lh, la, rho)
                    if z > 0: ll += w * math.log(z)
            if best is None or ll > best[0]: best = (ll, rho)
        self.rho = best[1]
        return self

    def lambdas(self, home, away):
        return (math.exp(self.a[home] + self.d[away] + self.h), math.exp(self.a[away] + self.d[home]))

    def matrix(self, lh, la):
        m = [[pois(x, lh)*pois(y, la)*tau(x,y,lh,la,self.rho) for y in range(MAXG+1)] for x in range(MAXG+1)]
        return m, sum(map(sum, m))

    def probs(self, lh, la):
        m,s = self.matrix(lh,la)
        ph=sum(m[x][y] for x in range(MAXG+1) for y in range(MAXG+1) if x>y)/s
        pd=sum(m[x][x] for x in range(MAXG+1))/s
        over=lambda line: sum(m[x][y] for x in range(MAXG+1) for y in range(MAXG+1) if x+y>line)/s
        p0h=sum(m[0][y] for y in range(MAXG+1))/s; p0a=sum(m[x][0] for x in range(MAXG+1))/s
        return {"ph":ph,"pd":pd,"pa":1-ph-pd,"over25":over(2.5),"over15":over(1.5),"over35":over(3.5),"btts":1-p0h-p0a+m[0][0]/s}
