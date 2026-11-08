"""Dixon-Coles fit used by the preregistered BNAC goals dev harness."""
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
        if not obs: raise ValueError("cannot fit DC with no training rows")
        self.mu = wg / (2.0 * wm)
        for _ in range(14):
            of, ef, oc, ec = defaultdict(float), defaultdict(float), defaultdict(float), defaultdict(float)
            so = se = 0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                of[g["hi"]] += w*yh; ef[g["hi"]] += w*lh
                of[g["ai"]] += w*ya; ef[g["ai"]] += w*la
                oc[g["ai"]] += w*yh; ec[g["ai"]] += w*lh
                oc[g["hi"]] += w*ya; ec[g["hi"]] += w*la
                so += w*yh; se += w*lh
            for t in set(of) | set(ef): self.a[t] += 0.7 * math.log((of[t]+0.25)/(ef[t]+0.25))
            for t in set(oc) | set(ec): self.d[t] += 0.7 * math.log((oc[t]+0.25)/(ec[t]+0.25))
            self.h += 0.7 * math.log((so+0.25)/(se+0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, yh, ya, w in obs:
                if yh <= 1 or ya <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"]); t = tau(int(yh), int(ya), lh, la, rho)
                    if t > 0: ll += w * math.log(t)
            if best is None or ll > best[0]: best = (ll, rho)
        self.rho = best[1]
        return self

    def lambdas(self, home, away):
        return math.exp(self.a[home] + self.d[away] + self.h), math.exp(self.a[away] + self.d[home])

    def matrix(self, lh, la):
        m = [[pois(x, lh)*pois(y, la)*tau(x,y,lh,la,self.rho) for y in range(MAXG+1)] for x in range(MAXG+1)]
        return m, sum(map(sum, m))

    def probs(self, lh, la):
        m, z = self.matrix(lh, la)
        ph = sum(m[x][y] for x in range(11) for y in range(11) if x > y)/z
        pd = sum(m[x][x] for x in range(11))/z
        over = lambda line: sum(m[x][y] for x in range(11) for y in range(11) if x+y > line)/z
        p0h, p0a = sum(m[0])/z, sum(m[x][0] for x in range(11))/z
        return {"ph":ph,"pd":pd,"pa":1-ph-pd,"over25":over(2.5),"over15":over(1.5),"over35":over(3.5),"btts":1-p0h-p0a+m[0][0]/z}
