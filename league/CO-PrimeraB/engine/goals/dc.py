"""Goals-only Dixon-Coles fit and score probabilities for G-CO."""
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
        self.a = defaultdict(float); self.d = defaultdict(float); self.h = 0.28
        self.rho = 0.0; self.mu = 0.0; self.team_names = {}

    def fit(self, games, cutoff):
        self.team_names = {}; obs = []; weighted_goals = weighted_matches = 0.0
        for g in games:
            self.team_names[g["hi"]] = g["home"]; self.team_names[g["ai"]] = g["away"]
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            weighted_goals += w * (g["yh"] + g["ya"]); weighted_matches += w
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
        if not obs: raise ValueError("cannot fit Dixon-Coles model with no training matches")
        self.mu = weighted_goals / (2.0 * weighted_matches)
        for _ in range(14):
            goals_for = defaultdict(float); expected_for = defaultdict(float)
            goals_against = defaultdict(float); expected_against = defaultdict(float)
            observed_total = expected_total = 0.0
            for g, yh, ya, w in obs:
                lh, la = self.lambdas(g["hi"], g["ai"])
                goals_for[g["hi"]] += w * yh; expected_for[g["hi"]] += w * lh
                goals_for[g["ai"]] += w * ya; expected_for[g["ai"]] += w * la
                goals_against[g["ai"]] += w * yh; expected_against[g["ai"]] += w * lh
                goals_against[g["hi"]] += w * ya; expected_against[g["hi"]] += w * la
                observed_total += w * yh; expected_total += w * lh
            for team in set(goals_for) | set(expected_for):
                self.a[team] += 0.7 * math.log((goals_for[team] + 0.25) / (expected_for[team] + 0.25))
            for team in set(goals_against) | set(expected_against):
                self.d[team] += 0.7 * math.log((goals_against[team] + 0.25) / (expected_against[team] + 0.25))
            self.h += 0.7 * math.log((observed_total + 0.25) / (expected_total + 0.25))
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, _, _, w in obs:
                if g["yh"] <= 1 or g["ya"] <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"]); correction = tau(g["yh"], g["ya"], lh, la, rho)
                    if correction > 0: ll += w * math.log(correction)
            if best is None or ll > best[0]: best = (ll, rho)
        self.rho = best[1]; return self

    def lambdas(self, home_id, away_id):
        return (math.exp(self.a[home_id] + self.d[away_id] + self.h), math.exp(self.a[away_id] + self.d[home_id]))

    def matrix(self, lh, la, rho=None):
        rho = self.rho if rho is None else rho
        matrix = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho) for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        return matrix, sum(sum(row) for row in matrix)

    def probs(self, lh, la, rho=None):
        matrix, total = self.matrix(lh, la, rho)
        home = sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / total
        draw = sum(matrix[x][x] for x in range(MAXG + 1)) / total
        over = lambda line: sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x + y > line) / total
        p0h = sum(matrix[0][y] for y in range(MAXG + 1)) / total; p0a = sum(matrix[x][0] for x in range(MAXG + 1)) / total
        return {"ph": home, "pd": draw, "pa": 1.0 - home - draw, "over15": over(1.5), "over25": over(2.5), "over35": over(3.5), "btts": 1.0 - p0h - p0a + matrix[0][0] / total}

    def over(self, lh, la, line, rho=None):
        matrix, total = self.matrix(lh, la, rho)
        return sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x + y > line) / total
