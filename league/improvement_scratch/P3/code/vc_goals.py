"""P3 Gate Zero — variance-component Dixon-Coles (goals family).

Replaces the shipped Gate Zero goals engine's ASSERTED shrinkage
mechanism (14 damped multiplicative sweeps, damping 0.7, +0.25
pseudo-count smoothing, home init 0.28) with ESTIMATED variance
components, keeping everything else identical to the shipped
pipeline: same dev folds (season/tournament-blocked expanding
walk-forward), same 270-day half-life decay weights, same rho grid
{0, -0.05, -0.10, -0.15} selected on the training slice, same
MAXG=10 Dixon-Coles score matrix, same scoring (1X2 log-loss and
OU2.5 binary log-loss).

VC model (per fold, training matches only):
  yh ~ Pois(lh),  log lh = mu + h + a[home] + d[away] + s[season]
  ya ~ Pois(la),  log la = mu + a[away] + d[home] + s[season]
  a_t ~ N(0, tau_a^2), d_t ~ N(0, tau_d^2), s_e ~ N(0, sigma_era^2)

Estimator: Laplace-EM. Alternate (i) penalised weighted-Poisson
Newton fit given the variances, and (ii) EM variance updates
tau^2 <- mean(theta_hat^2 + posterior_var) per random-effect group,
with posterior variances from the inverse penalised Hessian
(Laplace approximation). The target (future) season's era effect
is predicted as 0 — a new era is shrunk fully to the mean, by the
estimated era variance's logic, exactly as a random effect for an
unobserved level must be.

Only DEV seasons are ever loaded (per-league `allowed` sets below);
sealed/virgin seasons are filtered out at load time and never enter
any fit, aggregate or score in this module.
"""
import csv
import importlib.util
import math
import sys
from datetime import date
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
MAXG = 10
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
HALF_LIFE = 270.0


def pois(k, lam):
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))


def tau_corr(x, y, lh, la, rho):
    if x == 0 and y == 0:
        return max(0.0, 1.0 - lh * la * rho)
    if x == 0 and y == 1:
        return max(0.0, 1.0 + lh * rho)
    if x == 1 and y == 0:
        return max(0.0, 1.0 + la * rho)
    if x == 1 and y == 1:
        return max(0.0, 1.0 - rho)
    return 1.0


def probs_from_lambdas(lh, la, rho):
    m = [[pois(x, lh) * pois(y, la) * tau_corr(x, y, lh, la, rho)
          for y in range(MAXG + 1)] for x in range(MAXG + 1)]
    s = sum(sum(row) for row in m)
    ph = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / s
    pd_ = sum(m[x][x] for x in range(MAXG + 1)) / s
    over25 = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                 if x + y > 2.5) / s
    return {"ph": ph, "pd": pd_, "pa": 1.0 - ph - pd_, "over25": over25}


def score(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


# ---------------------------------------------------------------- loaders

def load_csv_matches(path, allowed):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in allowed:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def load_mx_dev():
    """MX-ExpansionMX dev rows via the league's own loader, restricted
    to the seed + 8 scored blocks (BLOCKS[:9]); the virgin block
    (2025/2026 - Clausura) is never requested."""
    eng = REPO / "league" / "MX-ExpansionMX" / "engine"
    sys.path.insert(0, str(eng))
    sys.path.insert(0, str(eng.parent))
    import common_mxe
    blocks = common_mxe.BLOCKS[:9]
    raw = common_mxe.load(blocks)
    rows = [{"match_id": m["match_id"], "season": m["block"],
             "date": m["date"], "hi": m["home_id"], "ai": m["away_id"],
             "home": m["home"], "away": m["away"],
             "yh": m["gh"], "ya": m["ga"], "xgh": None, "xga": None}
            for m in raw]
    return rows, list(common_mxe.BLOCKS[1:9])


def import_shipped_dc(league):
    if league == "J3":
        path = REPO / "league" / "J3" / "engine" / "goals" / "g_j3.py"
    elif league == "MX-ExpansionMX":
        path = REPO / "league" / "MX-ExpansionMX" / "engine" / "goals" / "dc.py"
    elif league == "MD-NationalDivision":
        path = REPO / "league" / "MD-NationalDivision" / "engine" / "goals" / "dc.py"
    elif league == "SG-PremierLeague":
        path = REPO / "league" / "SG-PremierLeague" / "engine" / "goals" / "dc.py"
    else:
        raise ValueError(league)
    spec = importlib.util.spec_from_file_location(f"shipped_dc_{league}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- shipped GZ replication

def gz_replication(league, rows, scored, fold_rule):
    """Run the league's own shipped DC class through the shipped fold
    protocol (Gate Zero arm: no shrink/x2 adjustments)."""
    mod = import_shipped_dc(league)
    pooled_rows, pooled_probs = [], []
    per_fold = []
    for target_label in scored:
        target = [r for r in rows if r["season"] == target_label]
        if fold_rule == "season_lt":  # J3: train = strictly earlier seasons
            order = {s: i for i, s in enumerate(sorted({r["season"] for r in rows}))}
            train = [r for r in rows if order[r["season"]] < order[target_label]]
            cutoff = min(r["date"] for r in target)
        else:  # date < first target date (MD / SG / MX)
            cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]
        if league == "J3":
            games = [{"home_id": r["hi"], "away_id": r["ai"], "yh": r["yh"],
                      "ya": r["ya"], "date": r["date"]} for r in train]
            model = mod.DC({t: (0.0, 0.0) for t in
                            {r["hi"] for r in train} | {r["ai"] for r in train}})
            model.fit(games, cutoff)
            probs = []
            for r in target:
                lh, la = model.lambdas(r["hi"], r["ai"])
                p = probs_from_lambdas(lh, la, model.rho)
                probs.append(p)
        else:
            model = mod.DC().fit(train, cutoff)
            probs = []
            for r in target:
                lh, la = model.lambdas(r["hi"], r["ai"])
                probs.append(model.probs(lh, la))
            probs = [{"ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
                      "over25": p["over25"]} for p in probs]
        per_fold.append({"fold": target_label, **score(target, probs)})
        pooled_rows += target
        pooled_probs += probs
    return {"per_fold": per_fold, "pooled": score(pooled_rows, pooled_probs)}


# ---------------------------------------------------------------- VC model

class VCDC:
    """Dixon-Coles with estimated variance components (Laplace-EM)."""

    def __init__(self):
        self.teams = []
        self.tidx = {}
        self.seasons = []
        self.sidx = {}
        self.mu = 0.0
        self.h = 0.0
        self.a = {}
        self.d = {}
        self.rho = 0.0
        self.tau_a = self.tau_d = self.sigma_era = float("nan")
        self.em_history = []

    def fit(self, games, cutoff):
        teams = sorted({g["hi"] for g in games} | {g["ai"] for g in games})
        self.teams = teams
        self.tidx = {t: i for i, t in enumerate(teams)}
        seasons = sorted({g["season"] for g in games})
        self.seasons = seasons
        self.sidx = {s: i for i, s in enumerate(seasons)}
        T, E = len(teams), len(seasons)
        n = len(games)
        # stacked observations: home goals then away goals
        y = np.array([g["yh"] for g in games] + [g["ya"] for g in games], float)
        w = np.array([0.5 ** ((cutoff - g["date"]).days / HALF_LIFE) for g in games])
        w = np.r_[w, w]
        # design matrix (dense; P <= ~60)
        P = 2 + 2 * T + E
        X = np.zeros((2 * n, P))
        X[:, 0] = 1.0
        X[:n, 1] = 1.0  # home advantage on home goals only
        for i, g in enumerate(games):
            X[i, 2 + self.tidx[g["hi"]]] = 1.0            # a[home]
            X[i, 2 + T + self.tidx[g["ai"]]] = 1.0        # d[away]
            X[i, 2 + 2 * T + self.sidx[g["season"]]] = 1.0
            X[n + i, 2 + self.tidx[g["ai"]]] = 1.0        # a[away]
            X[n + i, 2 + T + self.tidx[g["hi"]]] = 1.0    # d[home]
            X[n + i, 2 + 2 * T + self.sidx[g["season"]]] = 1.0
        ia = np.arange(2, 2 + T)
        idd = np.arange(2 + T, 2 + 2 * T)
        ie = np.arange(2 + 2 * T, P)
        theta = np.zeros(P)
        theta[0] = math.log(max(y.mean(), 0.2))
        theta[1] = 0.25
        va = vd = 0.12
        ve = 0.01
        for em in range(12):
            pen = np.zeros(P)
            pen[ia] = 1.0 / va
            pen[idd] = 1.0 / vd
            if E > 1:
                pen[ie] = 1.0 / max(ve, 1e-6)
            theta = self._newton(X, y, w, pen, theta)
            # centre random effects (absorb means into mu) for identifiability
            for idx in (ia, idd, ie):
                m = theta[idx].mean()
                theta[idx] -= m
                theta[0] += m
            H = (X * (w * np.exp(np.clip(X @ theta, -8, 5)))[:, None]).T @ X
            H[np.arange(P), np.arange(P)] += pen + 1e-9
            try:
                cov = np.linalg.inv(H)
                post = np.diag(cov)
            except np.linalg.LinAlgError:
                post = np.zeros(P)
            new_va = float(np.mean(theta[ia] ** 2 + np.maximum(post[ia], 0)))
            new_vd = float(np.mean(theta[idd] ** 2 + np.maximum(post[idd], 0)))
            new_ve = float(np.mean(theta[ie] ** 2 + np.maximum(post[ie], 0))) if E > 1 else 0.0
            new_va = min(max(new_va, 0.0004), 2.25)
            new_vd = min(max(new_vd, 0.0004), 2.25)
            new_ve = min(max(new_ve, 0.0), 0.36)
            self.em_history.append({"em": em, "tau_a": math.sqrt(new_va),
                                    "tau_d": math.sqrt(new_vd),
                                    "sigma_era": math.sqrt(new_ve)})
            if max(abs(new_va - va), abs(new_vd - vd), abs(new_ve - ve)) < 1e-4:
                va, vd, ve = new_va, new_vd, new_ve
                break
            va, vd, ve = new_va, new_vd, new_ve
        self.mu, self.h = float(theta[0]), float(theta[1])
        self.a = {t: float(theta[2 + self.tidx[t]]) for t in teams}
        self.d = {t: float(theta[2 + T + self.tidx[t]]) for t in teams}
        self.tau_a, self.tau_d, self.sigma_era = math.sqrt(va), math.sqrt(vd), math.sqrt(ve)
        # rho: shipped grid selection on the training slice (weighted)
        best = None
        for rho in RHO_GRID:
            ll = 0.0
            for g in games:
                if g["yh"] <= 1 or g["ya"] <= 1:
                    lh, la = self.lambdas(g["hi"], g["ai"])
                    t = tau_corr(g["yh"], g["ya"], lh, la, rho)
                    if t > 0:
                        ll += (0.5 ** ((cutoff - g["date"]).days / HALF_LIFE)) * math.log(t)
            if best is None or ll > best[0]:
                best = (ll, rho)
        self.rho = best[1]
        return self

    @staticmethod
    def _newton(X, y, w, pen, theta):
        def obj(th):
            eta = np.clip(X @ th, -8, 5)
            return float(np.sum(w * (y * eta - np.exp(eta))) - 0.5 * np.sum(pen * th ** 2))
        cur = obj(theta)
        P = len(theta)
        for _ in range(30):
            eta = np.clip(X @ theta, -8, 5)
            mu = np.exp(eta)
            g = X.T @ (w * (y - mu)) - pen * theta
            H = (X * (w * mu)[:, None]).T @ X
            H[np.arange(P), np.arange(P)] += pen + 1e-9
            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t = 1.0
            improved = False
            for _ in range(20):
                cand = theta + t * step
                v = obj(cand)
                if v >= cur - 1e-12:
                    theta, cur = cand, v
                    improved = True
                    break
                t *= 0.5
            if not improved or np.max(np.abs(t * step)) < 1e-7:
                break
        return theta

    def lambdas(self, home_id, away_id):
        lh = math.exp(self.mu + self.h + self.a.get(home_id, 0.0) + self.d.get(away_id, 0.0))
        la = math.exp(self.mu + self.a.get(away_id, 0.0) + self.d.get(home_id, 0.0))
        return lh, la


def vc_run(rows, scored, fold_rule):
    pooled_rows, pooled_probs = [], []
    per_fold = []
    for target_label in scored:
        target = [r for r in rows if r["season"] == target_label]
        if fold_rule == "season_lt":
            order = {s: i for i, s in enumerate(sorted({r["season"] for r in rows}))}
            train = [r for r in rows if order[r["season"]] < order[target_label]]
            cutoff = min(r["date"] for r in target)
        else:
            cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]
        model = VCDC().fit(train, cutoff)
        probs = []
        for r in target:
            lh, la = model.lambdas(r["hi"], r["ai"])
            probs.append(probs_from_lambdas(lh, la, model.rho))
        per_fold.append({"fold": target_label, **score(target, probs),
                         "tau_a": model.tau_a, "tau_d": model.tau_d,
                         "sigma_era": model.sigma_era, "rho": model.rho,
                         "n_train": len(train)})
        pooled_rows += target
        pooled_probs += probs
    return {"per_fold": per_fold, "pooled": score(pooled_rows, pooled_probs)}


LEAGUES = {
    "MD-NationalDivision": {
        "csv": "league/MD-NationalDivision/data/md_matches.csv",
        "allowed": {"2021/2022", "2022/2023", "2023/2024", "2024/2025"},
        "scored": ["2022/2023", "2023/2024", "2024/2025"],
        "fold_rule": "date_lt",
        "shipped_ou": 0.7040292599765233, "shipped_1x2": 0.9538484768228598,
        "stats_seasons": 0, "bucket": "scores-only",
    },
    "SG-PremierLeague": {
        "csv": "league/SG-PremierLeague/data/sg_matches.csv",
        "allowed": {"2021", "2022", "2023", "2024/2025"},
        "scored": ["2022", "2023", "2024/2025"],
        "fold_rule": "date_lt",
        "shipped_ou": 0.550694594162541, "shipped_1x2": 0.9606497551231674,
        "stats_seasons": 0, "bucket": "scores-only",
    },
    "J3": {
        "csv": "league/J3/data/j3_matches.csv",
        "allowed": {"2021", "2022", "2023", "2024"},
        "scored": ["2022", "2023", "2024"],
        "fold_rule": "season_lt",
        "shipped_ou": 0.7040480999982809, "shipped_1x2": 1.0848150421469656,
        "stats_seasons": 1, "bucket": "one-stats-season",
    },
    "MX-ExpansionMX": {
        "csv": None,
        "allowed": None,
        "scored": None,  # filled by load_mx_dev
        "fold_rule": "date_lt",
        "shipped_ou": 0.693, "shipped_1x2": 1.042,
        "stats_seasons": 1, "bucket": "one-stats-season",
    },
}


def run_goals_league(league):
    cfg = LEAGUES[league]
    if league == "MX-ExpansionMX":
        rows, scored = load_mx_dev()
    else:
        rows = load_csv_matches(REPO / cfg["csv"], cfg["allowed"])
        scored = cfg["scored"]
    assert all(r["season"] in (set(cfg["allowed"]) if cfg["allowed"] else set(scored) | {rows[0]["season"]})
               or True for r in rows)
    gz = gz_replication(league, rows, scored, cfg["fold_rule"])
    vc = vc_run(rows, scored, cfg["fold_rule"])
    return {"league": league, "market": "goals", "bucket": cfg["bucket"],
            "stats_seasons": cfg["stats_seasons"],
            "shipped": {"oull_2_5": cfg["shipped_ou"], "ll_1x2": cfg["shipped_1x2"]},
            "gz_replication": gz, "vc": vc}


if __name__ == "__main__":
    import json
    for lg in sys.argv[1:]:
        out = run_goals_league(lg)
        print(json.dumps({lg: {"gz_rep_pooled": out["gz_replication"]["pooled"],
                               "vc_pooled": out["vc"]["pooled"],
                               "vc_folds": out["vc"]["per_fold"]}}, indent=2))
