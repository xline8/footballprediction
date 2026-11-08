"""Goals-only Dixon-Coles model for G-IL."""
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
            raise ValueError("cannot fit Dixon-Coles model without training games")
        self.mu = weighted_goals / (2.0 * weighted_matches)
        for _ in range(14):
            attack_obs = defaultdict(float); attack_exp = defaultdict(float)
            defence_obs = defaultdict(float); defence_exp = defaultdict(float)
            total_obs = total_exp = 0.0
            for g, oh, oa, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                attack_obs[g["hi"]] += w * oh; attack_exp[g["hi"]] += w * lh
                attack_obs[g["ai"]] += w * oa; attack_exp[g["ai"]] += w * la
                defence_obs[g["ai"]] += w * oh; defence_exp[g["ai"]] += w * lh
                defence_obs[g["hi"]] += w * oa; defence_exp[g["hi"]] += w * la
                total_obs += w * oh; total_exp += w * lh
            for team in set(attack_obs) | set(attack_exp):
                self.a[team] += 0.7 * math.log((attack_obs[team] + 0.25) / (attack_exp[team] + 0.25))
            for team in set(defence_obs) | set(defence_exp):
                self.d[team] += 0.7 * math.log((defence_obs[team] + 0.25) / (defence_exp[team] + 0.25))
            self.h += 0.7 * math.log((total_obs + 0.25) / (total_exp + 0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, _, _, w in obs:
                if g["yh"] <= 1 or g["ya"] <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"])
                    ll += w * math.log(max(tau(g["yh"], g["ya"], lh, la, rho), 1e-300))
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
