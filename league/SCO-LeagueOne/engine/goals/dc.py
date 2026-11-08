"""Goals-only Dixon-Coles fit used by the development harness."""
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
        obs = []; wg = wm = 0.0
        for g in games:
            assert g["xgh"] is None and g["xga"] is None, "xG must not be used"
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            wg += w * (g["yh"] + g["ya"]); wm += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        self.mu = wg / (2 * wm) if wm else 1.0
        for _ in range(14):
            ho=defaultdict(float); he=defaultdict(float); do=defaultdict(float); de=defaultdict(float); so=se=0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                ho[g["hi"]] += w*yh; he[g["hi"]] += w*lh
                ho[g["ai"]] += w*ya; he[g["ai"]] += w*la
                do[g["ai"]] += w*yh; de[g["ai"]] += w*lh
                do[g["hi"]] += w*ya; de[g["hi"]] += w*la
                so += w*yh; se += w*lh
            for t in set(ho)|set(he): self.a[t] += .7*math.log((ho[t]+.25)/(he[t]+.25))
            for t in set(do)|set(de): self.d[t] += .7*math.log((do[t]+.25)/(de[t]+.25))
            self.h += .7*math.log((so+.25)/(se+.25))
        best = max(((sum(w*math.log(tau(g["yh"],g["ya"],*self.lambdas(g["hi"],g["ai"]),rho))
                         for g, _, _, w in obs if g["yh"] <= 1 or g["ya"] <= 1), rho) for rho in RHO_GRID), key=lambda x:x[0])
        self.rho = best[1]
        return self

    def lambdas(self, home, away):
        return math.exp(self.a[home]+self.d[away]+self.h), math.exp(self.a[away]+self.d[home])

    def matrix(self, lh, la, rho=None):
        rho = self.rho if rho is None else rho
        m = [[pois(x,lh)*pois(y,la)*tau(x,y,lh,la,rho) for y in range(MAXG+1)] for x in range(MAXG+1)]
        return m, sum(map(sum,m))

    def probs(self, lh, la, rho=None):
        m,s=self.matrix(lh,la,rho)
        ph=sum(m[x][y] for x in range(11) for y in range(11) if x>y)/s
        pd=sum(m[x][x] for x in range(11))/s
        over=lambda line: sum(m[x][y] for x in range(11) for y in range(11) if x+y>line)/s
        return {"ph":ph,"pd":pd,"pa":1-ph-pd,"over25":over(2.5)}
