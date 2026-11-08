"""Self-contained goals-only Dixon-Coles fit for G-BEB."""
import math
from collections import defaultdict

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE = 270.0


def pois(k, lam):
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))


def tau(x, y, lh, la, rho):
    if x == 0 and y == 0:
        return max(0.0, 1.0 - lh * la * rho)
    if x == 0 and y == 1:
        return max(0.0, 1.0 + lh * rho)
    if x == 1 and y == 0:
        return max(0.0, 1.0 + la * rho)
    if x == 1 and y == 1:
        return max(0.0, 1.0 - rho)
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
        weighted_goals = weighted_matches = 0.0
        for g in games:
            dt = (cutoff - g["date"]).days
            w = 0.5 ** (dt / HALF_LIFE)
            weighted_goals += w * (g["yh"] + g["ya"])
            weighted_matches += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        if not obs:
            raise ValueError("cannot fit Dixon-Coles with an empty training window")
        self.mu = weighted_goals / (2.0 * weighted_matches)
        for _ in range(14):
            of = defaultdict(float); ef = defaultdict(float)
            oa = defaultdict(float); ea = defaultdict(float)
            so = se = 0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                of[g["hi"]] += w * yh; ef[g["hi"]] += w * lh
                of[g["ai"]] += w * ya; ef[g["ai"]] += w * la
                oa[g["ai"]] += w * yh; ea[g["ai"]] += w * lh
                oa[g["hi"]] += w * ya; ea[g["hi"]] += w * la
                so += w * yh; se += w * lh
            for t in set(of) | set(ef):
                self.a[t] += 0.7 * math.log((of[t] + 0.25) / (ef[t] + 0.25))
            for t in set(oa) | set(ea):
                self.d[t] += 0.7 * math.log((oa[t] + 0.25) / (ea[t] + 0.25))
            self.h += 0.7 * math.log((so + 0.25) / (se + 0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, _, _, w in obs:
                if g["yh"] <= 1 or g["ya"] <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"])
                    correction = tau(g["yh"], g["ya"], lh, la, rho)
                    if correction > 0:
                        ll += w * math.log(correction)
            if best is None or ll > best[0]:
                best = (ll, rho)
        self.rho = best[1]
        return self

    def lambdas(self, home_id, away_id):
        return (math.exp(self.a[home_id] + self.d[away_id] + self.h),
                math.exp(self.a[away_id] + self.d[home_id]))

    def matrix(self, lh, la, rho=None):
        rho = self.rho if rho is None else rho
        m = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho)
              for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        return m, sum(sum(row) for row in m)

    def probs(self, lh, la, rho=None):
        m, s = self.matrix(lh, la, rho)
        ph = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / s
        pd = sum(m[x][x] for x in range(MAXG + 1)) / s
        over = lambda line: sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                                if x + y > line) / s
        return {"ph": ph, "pd": pd, "pa": 1.0 - ph - pd, "over25": over(2.5)}
