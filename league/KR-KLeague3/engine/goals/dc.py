"""Self-contained Dixon-Coles fit for G-KR3."""
import math
from collections import defaultdict

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE = 270.0


def pois(k, lam):
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))


def tau(x, y, lh, la, rho):
    if x == 0 and y == 0:
        return max(0, 1 - lh * la * rho)
    if x == 0 and y == 1:
        return max(0, 1 + lh * rho)
    if x == 1 and y == 0:
        return max(0, 1 + la * rho)
    if x == 1 and y == 1:
        return max(0, 1 - rho)
    return 1.0


class DC:
    def __init__(self):
        self.a = defaultdict(float)
        self.d = defaultdict(float)
        self.h = 0.28
        self.rho = 0.0
        self.mu = 0.0

    def fit(self, games, cutoff):
        obs = []
        wg = wm = 0.0
        for g in games:
            w = 0.5 ** (((cutoff - g['date']).days) / HALF_LIFE)
            wg += w * (g['yh'] + g['ya'])
            wm += w
            obs.append((g, float(g['yh']), float(g['ya']), w))
        self.mu = wg / (2 * wm)
        for _ in range(14):
            of = defaultdict(float); ef = defaultdict(float)
            od = defaultdict(float); ed = defaultdict(float)
            so = se = 0.0
            for g, oh, oa, w in obs:
                lh, la = self.lambdas(g['hi'], g['ai'])
                of[g['hi']] += w * oh; ef[g['hi']] += w * lh
                of[g['ai']] += w * oa; ef[g['ai']] += w * la
                od[g['ai']] += w * oh; ed[g['ai']] += w * lh
                od[g['hi']] += w * oa; ed[g['hi']] += w * la
                so += w * oh; se += w * lh
            for t in set(of) | set(ef):
                self.a[t] += 0.7 * math.log((of[t] + 0.25) / (ef[t] + 0.25))
            for t in set(od) | set(ed):
                self.d[t] += 0.7 * math.log((od[t] + 0.25) / (ed[t] + 0.25))
            self.h += 0.7 * math.log((so + 0.25) / (se + 0.25))
        scores = []
        for rho in RHO_GRID:
            z = sum(w * math.log(max(tau(g['yh'], g['ya'],
                self.lambdas(g['hi'], g['ai'])[0], self.lambdas(g['hi'], g['ai'])[1], rho), 1e-12))
                     for g, _, _, w in obs if g['yh'] <= 1 or g['ya'] <= 1)
            scores.append((z, rho))
        self.rho = max(scores, key=lambda x: x[0])[1]
        return self

    def lambdas(self, home, away):
        return (math.exp(self.a[home] + self.d[away] + self.h),
                math.exp(self.a[away] + self.d[home]))

    def matrix(self, lh, la, rho=None):
        rho = self.rho if rho is None else rho
        m = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho)
              for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        return m, sum(map(sum, m))

    def probs(self, lh, la, rho=None):
        m, s = self.matrix(lh, la, rho)
        ph = sum(m[x][y] for x in range(11) for y in range(11) if x > y) / s
        pd = sum(m[x][x] for x in range(11)) / s
        over = lambda line: sum(m[x][y] for x in range(11) for y in range(11)
                                if x + y > line) / s
        p0h = sum(m[0][y] for y in range(11)) / s
        p0a = sum(m[x][0] for x in range(11)) / s
        return {'ph': ph, 'pd': pd, 'pa': 1 - ph - pd,
                'over15': over(1.5), 'over25': over(2.5), 'over35': over(3.5),
                'btts': 1 - p0h - p0a + m[0][0] / s}
