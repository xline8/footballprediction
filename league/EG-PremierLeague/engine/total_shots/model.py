"""Self-contained mechanics for the preregistered T-EG total-shots model."""
import math
from collections import defaultdict, deque

import numpy as np

BASE_HL = 365.0
REFIT_DAYS = 7
ETA_LO, ETA_HI = -6.0, 4.0
M_BAR = 24.9


def logloss(p, y):
    p = min(max(float(p), 1e-15), 1.0 - 1e-15)
    return -(y * math.log(p) + (1.0 - y) * math.log1p(-p))


def poisson_over(mu, line):
    kmax = int(math.floor(line))
    term = math.exp(-max(float(mu), 0.0))
    cdf = term
    for k in range(1, kmax + 1):
        term *= mu / k
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


def nb_over(mu, r, line):
    # NB parameterization with mean mu and size r.
    mu = max(float(mu), 1e-12)
    r = max(float(r), 1e-12)
    kmax = int(math.floor(line))
    q = mu / (r + mu)
    term = (r / (r + mu)) ** r
    cdf = term
    for k in range(1, kmax + 1):
        term *= (k - 1.0 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


class ShotsRegressionStore:
    """Joint home/away log-linear Poisson ratings for one division."""

    def __init__(self, matches, lambdas):
        self.lambdas = [float(x) for x in lambdas]
        self.teams = sorted({m["home_id"] for m in matches} |
                            {m["away_id"] for m in matches})
        self.tidx = {t: i for i, t in enumerate(self.teams)}
        self.t = len(self.teams)
        self.days = np.array([m["day"] for m in matches], dtype=float)
        self.hi = np.array([self.tidx[m["home_id"]] for m in matches])
        self.ai = np.array([self.tidx[m["away_id"]] for m in matches])
        self.yh = np.array([m["shots_h"] for m in matches], dtype=float)
        self.ya = np.array([m["shots_a"] for m in matches], dtype=float)
        self.theta = {}
        self.next_refit = None

    def _fit(self, lam, refit_day):
        cut = int(np.searchsorted(self.days, refit_day, side="left"))
        p = 2 + 2 * self.t
        theta = self.theta.get(lam)
        if theta is None:
            theta = np.zeros(p)
            if cut:
                w0 = 0.5 ** ((refit_day - self.days[:cut]) / BASE_HL)
                theta[0] = math.log(max(np.average(self.yh[:cut], weights=w0), 1e-3))
                theta[1] = math.log(max(np.average(self.ya[:cut], weights=w0), 1e-3))
            else:
                theta[0], theta[1] = math.log(13.0), math.log(11.0)
            self.theta[lam] = theta
        if not cut:
            return
        w0 = 0.5 ** ((refit_day - self.days[:cut]) / BASE_HL)
        y = np.concatenate((self.yh[:cut], self.ya[:cut]))
        bcol = np.concatenate((np.zeros(cut, dtype=int), np.ones(cut, dtype=int)))
        acol = np.concatenate((self.hi[:cut], self.ai[:cut])) + 2
        dcol = np.concatenate((self.ai[:cut], self.hi[:cut])) + 2 + self.t
        w = np.concatenate((w0, w0))
        diag = np.arange(p)

        def objective(th):
            eta = np.clip(th[bcol] + th[acol] + th[dcol], ETA_LO, ETA_HI)
            return float(np.sum(w * (y * eta - np.exp(eta))) -
                         0.5 * lam * np.sum(th[2:] ** 2))

        cur = objective(theta)
        for _ in range(60):
            eta = np.clip(theta[bcol] + theta[acol] + theta[dcol], ETA_LO, ETA_HI)
            mu = np.exp(eta)
            residual = w * (y - mu)
            g = np.zeros(p)
            np.add.at(g, bcol, residual); np.add.at(g, acol, residual); np.add.at(g, dcol, residual)
            g[2:] -= lam * theta[2:]
            W = w * mu
            H = np.zeros((p, p))
            for a, b in ((bcol, bcol), (bcol, acol), (bcol, dcol),
                         (acol, bcol), (acol, acol), (acol, dcol),
                         (dcol, bcol), (dcol, acol), (dcol, dcol)):
                np.add.at(H, (a, b), W)
            H[diag[2:], diag[2:]] += lam
            H[diag, diag] += 1e-10
            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            scale, improved = 1.0, False
            for _ in range(25):
                candidate = theta + scale * step
                value = objective(candidate)
                if value >= cur - 1e-12:
                    theta, cur, improved = candidate, value, True
                    break
                scale *= 0.5
            if not improved or np.max(np.abs(scale * step)) < 1e-6:
                break
        self.theta[lam] = theta

    def _ensure(self, day):
        if self.next_refit is None or day >= self.next_refit:
            for lam in self.lambdas:
                self._fit(lam, day)
            self.next_refit = day + REFIT_DAYS

    def predict(self, home_id, away_id, day, lam):
        self._ensure(day)
        th = self.theta[float(lam)]
        h, a = self.tidx.get(home_id), self.tidx.get(away_id)
        ah = th[2 + h] if h is not None else 0.0
        dh = th[2 + self.t + h] if h is not None else 0.0
        aa = th[2 + a] if a is not None else 0.0
        da = th[2 + self.t + a] if a is not None else 0.0
        mh = math.exp(np.clip(th[0] + ah + da, ETA_LO, ETA_HI))
        ma = math.exp(np.clip(th[1] + aa + dh, ETA_LO, ETA_HI))
        return mh, ma

    def league_mu(self, day, lam):
        self._ensure(day)
        th = self.theta[float(lam)]
        return math.exp(np.clip(th[0], ETA_LO, ETA_HI)), math.exp(np.clip(th[1], ETA_LO, ETA_HI))


class NaiveTracker:
    def __init__(self):
        self.history = defaultdict(lambda: deque(maxlen=10))

    def predict(self, home, away, league_h, league_a):
        hh, aa = self.history[home], self.history[away]
        if not hh or not aa:
            return league_h, league_a
        hf = sum(x[0] for x in hh) / len(hh); hag = sum(x[1] for x in hh) / len(hh)
        af = sum(x[0] for x in aa) / len(aa); aag = sum(x[1] for x in aa) / len(aa)
        return (hf + aag) / 2.0, (af + hag) / 2.0

    def update(self, home, away, shots_h, shots_a):
        self.history[home].append((shots_h, shots_a))
        self.history[away].append((shots_a, shots_h))


class BaseRateTracker:
    def __init__(self):
        self.home = [0.0, 0.0, None]
        self.away = [0.0, 0.0, None]

    def _at(self, st, day):
        if st[2] is not None and day > st[2]:
            f = 0.5 ** ((day - st[2]) / BASE_HL)
            st[0] *= f; st[1] *= f
        st[2] = day
        return st

    def predict(self, day):
        h, a = self._at(self.home, day), self._at(self.away, day)
        return (h[0] / h[1] if h[1] else 13.0,
                a[0] / a[1] if a[1] else 11.0)

    def update(self, day, shots_h, shots_a):
        h, a = self._at(self.home, day), self._at(self.away, day)
        h[0] += shots_h; h[1] += 1.0; a[0] += shots_a; a[1] += 1.0


class LevelLayer:
    def __init__(self, cells):
        self.cells = list(cells)
        self.state = [[0.0, 0.0, None] for _ in self.cells]

    def _at(self, ci, day):
        st = self.state[ci]
        if st[2] is not None and day > st[2]:
            f = 0.5 ** ((day - st[2]) / self.cells[ci][0])
            st[0] *= f; st[1] *= f
        st[2] = day
        return st

    def factor(self, ci, day):
        st = self._at(ci, day); _, s, k = self.cells[ci]
        if st[2] is None or st[0] == 0.0 and st[1] == 0.0:
            return 1.0
        ratio = (st[0] + k * M_BAR) / (st[1] + k * M_BAR)
        return min(1.10, max(0.90, 1.0 + s * (ratio - 1.0)))

    def update(self, ci, day, actual, prediction):
        st = self._at(ci, day); st[0] += actual; st[1] += prediction


class TrailingR:
    def __init__(self, r_a, k=200):
        self.r_a, self.k, self.values = r_a, k, deque()

    def value(self, day):
        values = [v for d, v in self.values if d < day][-self.k:]
        n = len(values)
        m = (sum(values) + self.k * M_BAR) / (n + self.k)
        s2 = (sum(v * v for v in values) + self.k *
              (M_BAR + M_BAR * M_BAR / self.r_a + M_BAR * M_BAR)) / (n + self.k)
        variance = max(0.0, s2 - m * m)
        return min(400.0, max(20.0, m * m / max(variance - m, 1e-9)))

    def update(self, day, total):
        self.values.append((day, float(total)))
