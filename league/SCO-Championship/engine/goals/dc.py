"""Self-contained Dixon-Coles fit and score probabilities for G-RU."""
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
        self.team_names = {}

    def fit(self, games, cutoff):
        """Fit on records with hi, ai, yh, ya, date, xgh, xga, names."""
        self.team_names = {}
        for g in games:
            self.team_names[g["hi"]] = g["home"]
            self.team_names[g["ai"]] = g["away"]
        obs = []
        weighted_goals = weighted_matches = 0.0
        for g in games:
            dt = (cutoff - g["date"]).days
            w = 0.5 ** (dt / HALF_LIFE)
            weighted_goals += w * (g["yh"] + g["ya"])
            weighted_matches += w
            if g.get("xgh") is not None and g.get("xga") is not None:
                oh = 0.5 * g["yh"] + 0.5 * g["xgh"]
                oa = 0.5 * g["ya"] + 0.5 * g["xga"]
            else:
                oh, oa = float(g["yh"]), float(g["ya"])
            obs.append((g, oh, oa, w))
        self.mu = weighted_goals / (2.0 * weighted_matches)
        for _ in range(14):
            oa = defaultdict(float); ea = defaultdict(float)
            od = defaultdict(float); ed = defaultdict(float)
            so = se = 0.0
            for g, oh, oa_obs, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                oa[g["hi"]] += w * oh; ea[g["hi"]] += w * lh
                oa[g["ai"]] += w * oa_obs; ea[g["ai"]] += w * la
                od[g["ai"]] += w * oh; ed[g["ai"]] += w * lh
                od[g["hi"]] += w * oa_obs; ed[g["hi"]] += w * la
                so += w * oh
                se += w * lh
            for t in set(oa) | set(ea):
                self.a[t] += 0.7 * math.log((oa[t] + 0.25) / (ea[t] + 0.25))
            for t in set(od) | set(ed):
                self.d[t] += 0.7 * math.log((od[t] + 0.25) / (ed[t] + 0.25))
            self.h += 0.7 * math.log((so + 0.25) / (se + 0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, _, _, w in obs:
                if g["yh"] <= 1 or g["ya"] <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"])
                    t = tau(g["yh"], g["ya"], lh, la, rho)
                    if t > 0:
                        ll += w * math.log(t)
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
        s = sum(sum(row) for row in m)
        return m, s

    def probs(self, lh, la, rho=None):
        m, s = self.matrix(lh, la, rho)
        ph = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / s
        pd = sum(m[x][x] for x in range(MAXG + 1)) / s
        over = lambda line: sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x + y > line) / s
        p0h = sum(m[0][y] for y in range(MAXG + 1)) / s
        p0a = sum(m[x][0] for x in range(MAXG + 1)) / s
        return {"ph": ph, "pd": pd, "pa": 1.0 - ph - pd,
                "over15": over(1.5), "over25": over(2.5), "over35": over(3.5),
                "btts": 1.0 - p0h - p0a + m[0][0] / s}

    def over(self, lh, la, line, rho=None):
        m, s = self.matrix(lh, la, rho)
        return sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                   if x + y > line) / s
