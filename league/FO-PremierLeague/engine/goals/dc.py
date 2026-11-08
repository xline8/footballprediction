"""Frozen FO Dixon-Coles fit and score probabilities."""
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
        obs = []
        wg = wm = 0.0
        for g in games:
            assert g["date"] < cutoff
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            wg += w * (g["yh"] + g["ya"]); wm += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        if not obs: raise ValueError("DC fit has no training matches")
        self.mu = wg / (2.0 * wm)
        for _ in range(14):
            oa, ea, od, ed = (defaultdict(float) for _ in range(4))
            so = se = 0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                oa[g["hi"]] += w*yh; ea[g["hi"]] += w*lh
                oa[g["ai"]] += w*ya; ea[g["ai"]] += w*la
                od[g["ai"]] += w*yh; ed[g["ai"]] += w*lh
                od[g["hi"]] += w*ya; ed[g["hi"]] += w*la
                so += w*yh; se += w*lh
            for t in set(oa) | set(ea): self.a[t] += .7 * math.log((oa[t]+.25)/(ea[t]+.25))
            for t in set(od) | set(ed): self.d[t] += .7 * math.log((od[t]+.25)/(ed[t]+.25))
            self.h += .7 * math.log((so+.25)/(se+.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, yh, ya, w in obs:
                if yh <= 1 or ya <= 1:
                    t = tau(int(yh), int(ya), *self.lambdas(g["hi"], g["ai"]), rho)
                    if t > 0: ll += w * math.log(t)
            if best is None or ll > best[0]: best = (ll, rho)
        self.rho = best[1]
        return self

    def lambdas(self, hi, ai):
        return math.exp(self.a[hi] + self.d[ai] + self.h), math.exp(self.a[ai] + self.d[hi])

    def probs(self, lh, la):
        m = [[pois(x,lh)*pois(y,la)*tau(x,y,lh,la,self.rho) for y in range(MAXG+1)] for x in range(MAXG+1)]
        s = sum(map(sum,m))
        ph = sum(m[x][y] for x in range(11) for y in range(11) if x > y)/s
        pd = sum(m[x][x] for x in range(11))/s
        over = sum(m[x][y] for x in range(11) for y in range(11) if x+y > 2.5)/s
        return {"ph":ph,"pd":pd,"pa":1-ph-pd,"over25":over}
