"""Goals-only Dixon--Coles fit for EE-Meistriliiga Phase B."""
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
        self.n_trained = 0
        self.max_train_date = None

    def lambdas(self, home, away, attack=None, defence=None):
        attack = self.a if attack is None else attack
        defence = self.d if defence is None else defence
        return (math.exp(attack[home] + defence[away] + self.h),
                math.exp(attack[away] + defence[home]))

    def fit(self, games, cutoff):
        assert all(g["date"] < cutoff for g in games)
        self.n_trained = len(games)
        self.max_train_date = max((g["date"] for g in games), default=None)
        obs = []
        sw = sg = 0.0
        for g in games:
            w = 0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)
            obs.append((g, float(g["yh"]), float(g["ya"]), w))
            sw += w
            sg += w * (g["yh"] + g["ya"])
        self.mu = sg / (2.0 * sw) if sw else 0.0
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
                so += w * oh; se += w * lh
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
                    correction = tau(g["yh"], g["ya"], lh, la, rho)
                    if correction > 0:
                        ll += w * math.log(correction)
            if best is None or ll > best[0]:
                best = (ll, rho)
        self.rho = best[1] if best else 0.0
        return self

    def matrix(self, lh, la):
        matrix = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, self.rho)
                   for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        total = sum(sum(row) for row in matrix)
        assert total > 0.0
        normalized = [[v / total for v in row] for row in matrix]
        for row in normalized:
            assert all(math.isfinite(v) and v >= 0.0 for v in row)
        assert abs(sum(sum(row) for row in normalized) - 1.0) < 1e-12
        return normalized

    def probs(self, lh, la):
        m = self.matrix(lh, la)
        ph = sum(m[x][y] for x in range(11) for y in range(11) if x > y)
        pd = sum(m[x][x] for x in range(11))
        return {"ph": ph, "pd": pd, "pa": 1.0 - ph - pd,
                "over25": sum(m[x][y] for x in range(11) for y in range(11) if x + y > 2)}
