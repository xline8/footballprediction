"""Goals-only Dixon-Coles fit used by the Lithuania Toplyga engine."""
import math
from collections import defaultdict

MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE = 270.0
SMOOTH = 0.25
DAMPING = 0.7


def poisson_logpmf(k, lam):
    return -lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1)


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
        self.mean_a = 0.0
        self.mean_d = 0.0

    def fit(self, games, cutoff):
        """Fit only FT goals; ``games`` must already obey the cutoff."""
        assert all(g["date"] < cutoff for g in games)
        observations = []
        weighted_goals = weighted_matches = 0.0
        for g in games:
            age = (cutoff - g["date"]).days
            w = 0.5 ** (age / HALF_LIFE)
            weighted_goals += w * (g["yh"] + g["ya"])
            weighted_matches += w
            observations.append((g, float(g["yh"]), float(g["ya"]), w))
            self.team_names[g["hi"]] = g["home"]
            self.team_names[g["ai"]] = g["away"]
        if not observations:
            raise ValueError("cannot fit Dixon-Coles model with no training matches")
        self.mu = weighted_goals / (2.0 * weighted_matches)

        for _ in range(14):
            observed_for = defaultdict(float); expected_for = defaultdict(float)
            observed_against = defaultdict(float); expected_against = defaultdict(float)
            total_observed = total_expected = 0.0
            for g, yh, ya, w in observations:
                lh, la = self.lambdas(g["hi"], g["ai"])
                observed_for[g["hi"]] += w * yh; expected_for[g["hi"]] += w * lh
                observed_for[g["ai"]] += w * ya; expected_for[g["ai"]] += w * la
                observed_against[g["ai"]] += w * yh; expected_against[g["ai"]] += w * lh
                observed_against[g["hi"]] += w * ya; expected_against[g["hi"]] += w * la
                total_observed += w * yh
                total_expected += w * lh
            for team in set(observed_for) | set(expected_for):
                self.a[team] += DAMPING * math.log(
                    (observed_for[team] + SMOOTH) / (expected_for[team] + SMOOTH))
            for team in set(observed_against) | set(expected_against):
                self.d[team] += DAMPING * math.log(
                    (observed_against[team] + SMOOTH) / (expected_against[team] + SMOOTH))
            self.h += DAMPING * math.log((total_observed + SMOOTH) / (total_expected + SMOOTH))

        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g, yh, ya, w in observations:
                lh, la = self.lambdas(g["hi"], g["ai"])
                correction = tau(int(yh), int(ya), lh, la, rho)
                ll += w * (poisson_logpmf(int(yh), lh) + poisson_logpmf(int(ya), la)
                            + math.log(max(correction, 1e-300)))
            if best is None or ll > best[0]:
                best = (ll, rho)
        self.rho = best[1]
        teams = set(self.a) | set(self.d)
        self.mean_a = sum(self.a[t] for t in teams) / len(teams)
        self.mean_d = sum(self.d[t] for t in teams) / len(teams)
        return self

    def lambdas(self, home, away):
        return (math.exp(self.a[home] + self.d[away] + self.h),
                math.exp(self.a[away] + self.d[home]))

    def matrix(self, lh, la, rho=None):
        rho = self.rho if rho is None else rho
        matrix = [[math.exp(poisson_logpmf(x, lh) + poisson_logpmf(y, la))
                   * tau(x, y, lh, la, rho) for y in range(MAXG + 1)]
                  for x in range(MAXG + 1)]
        return matrix, sum(sum(row) for row in matrix)

    def probs(self, lh, la, rho=None):
        matrix, total = self.matrix(lh, la, rho)
        ph = sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / total
        pd = sum(matrix[x][x] for x in range(MAXG + 1)) / total
        over = lambda line: sum(matrix[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                                 if x + y > line) / total
        p0h = sum(matrix[0][y] for y in range(MAXG + 1)) / total
        p0a = sum(matrix[x][0] for x in range(MAXG + 1)) / total
        return {"ph": ph, "pd": pd, "pa": 1.0 - ph - pd,
                "over15": over(1.5), "over25": over(2.5), "over35": over(3.5),
                "btts": 1.0 - p0h - p0a + matrix[0][0] / total}
