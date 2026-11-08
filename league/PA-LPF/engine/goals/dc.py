"""Self-contained production-pattern Dixon-Coles fit for G-PA-LPF."""
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
        self.team_names = {}
        obs = []
        weighted_goals = weighted_matches = 0.0
        for g in games:
            self.team_names[g["hi"]] = g["home"]
            self.team_names[g["ai"]] = g["away"]
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            weighted_goals += w * (g["yh"] + g["ya"])
            weighted_matches += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        if not obs:
            raise ValueError("cannot fit Dixon-Coles on empty history")
        self.mu = weighted_goals / (2.0 * weighted_matches)
        for _ in range(14):
            oh = defaultdict(float); eh = defaultdict(float)
            od = defaultdict(float); ed = defaultdict(float)
            total_obs = total_exp = 0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                oh[g["hi"]] += w * yh; eh[g["hi"]] += w * lh
                oh[g["ai"]] += w * ya; eh[g["ai"]] += w * la
                od[g["ai"]] += w * yh; ed[g["ai"]] += w * lh
                od[g["hi"]] += w * ya; ed[g["hi"]] += w * la
                total_obs += w * yh; total_exp += w * lh
            for t in set(oh) | set(eh):
                self.a[t] += 0.7 * math.log((oh[t] + 0.25) / (eh[t] + 0.25))
            for t in set(od) | set(ed):
                self.d[t] += 0.7 * math.log((od[t] + 0.25) / (ed[t] + 0.25))
            self.h += 0.7 * math.log((total_obs + 0.25) / (total_exp + 0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, yh, ya, w in obs:
                if yh <= 1 or ya <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"])
                    correction = tau(int(yh), int(ya), lh, la, rho)
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
        matrix = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho)
                   for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        return matrix, sum(sum(row) for row in matrix)

    def probs(self, lh, la, rho=None):
        matrix, total = self.matrix(lh, la, rho)
        ph = sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / total
        pd = sum(matrix[x][x] for x in range(MAXG + 1)) / total
        over = lambda line: sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x + y > line) / total
        p0h = sum(matrix[0][y] for y in range(MAXG + 1)) / total
        p0a = sum(matrix[x][0] for x in range(MAXG + 1)) / total
        return {"ph": ph, "pd": pd, "pa": 1.0 - ph - pd,
                "over15": over(1.5), "over25": over(2.5), "over35": over(3.5),
                "btts": 1.0 - p0h - p0a + matrix[0][0] / total}

    def over(self, lh, la, line, rho=None):
        matrix, total = self.matrix(lh, la, rho)
        return sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                   if x + y > line) / total
