"""P3 Gate Zero — variance-component SOT (counting-stat family).

The shipped SOT Gate Zero (v5 pattern, identical template in
LV-Virsliga and SA-FirstDivision) asserts four constants:
  RIDGE_LAM = 100.0   (joint Poisson ridge on attack/defence ratings)
  K_PRIOR   = 8.0     (decayed shots-mean shrinkage strength)
  ratio prior = 200   (Beta-Binomial strength for on-target ratio, GZ arm)
  NB_R      = 79.94   (Negative-Binomial size for total SOT)

This module re-implements that engine on ONE code path with a mode
switch. mode="gz" uses the asserted constants and must reproduce
the shipped engine's dev LL (validation). mode="vc" replaces every
asserted constant with a variance component estimated from data
available at that moment of the walk (never future data):

  ridge:  Laplace-EM per refit — tau_att^2 / tau_def^2 from the
          fitted ratings plus their Laplace posterior variances;
          lambda = 1 / tau^2 per group.
  K:      Gamma-Poisson method of moments across teams in each
          rating group: tau_m^2 = Var(team decayed means)
          - mean(mu / w_t);  K = mu / tau_m^2.
  ratio:  Beta-Binomial method of moments across teams:
          tau_rho^2 = Var(team ratios) - mean(rho(1-rho)/n_t);
          prior strength m = rho(1-rho)/tau_rho^2 - 1.
  NB r:   method of moments on match totals seen so far:
          r = mu^2 / (var - mu).
  era:    single-season dev panels cannot identify a season-level
          variance; the month-level variance of league totals is
          estimated and reported (era_report) but, as with a new
          season in the goals model, an unobserved period's effect
          is predicted as 0.

Everything else is identical to the shipped pipeline: HL=365 decay,
7-day refits, date-grouped predict-then-update walk, warmups, the
0.5 regression / 0.5 ratings blend, the 0.5 model / 0.5 naive
probability blend, lines and scoring. Only DEV data is loaded:
LV season "2025" up to 2025-11-09; SA season "2025/2026" only.
The sealed seasons (LV 2026, SA 2026/2027) are never loaded.
"""
import importlib.util
import math
from collections import defaultdict, deque
from datetime import date
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
HL = 365.0
REFIT_DAYS = 7
ETA_LO, ETA_HI = -6.0, 4.0
NAIVE_N = 10

GZ_CONSTANTS = {"ridge": 100.0, "K": 8.0, "ratio_prior": 200.0, "nb_r": 79.94}


def nb_over(lam, r, line):
    kmax = int(math.floor(line))
    q = lam / (r + lam)
    term = (r / (r + lam)) ** r
    cdf = term
    for k in range(1, kmax + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


class Decayed:
    def __init__(self):
        self.s = self.w = 0.0
        self.last = None

    def decay(self, day):
        if self.last is not None and day > self.last:
            f = 0.5 ** ((day - self.last) / HL)
            self.s *= f
            self.w *= f
        self.last = day

    def value(self, day):
        self.decay(day)
        return self.s, self.w

    def add(self, day, value):
        self.decay(day)
        self.s += value
        self.w += 1.0


def estimate_K(objects, day, mu_pool_hint=None):
    """Gamma-Poisson MoM shrinkage strength for one rating group."""
    sw = []
    for obj in objects:
        s, w = obj.value(day)
        if w > 0:
            sw.append((s, w))
    if len(sw) < 3:
        return 8.0, None  # immaterial: with no data the shrunk value is mu for any K
    S = sum(s for s, _ in sw)
    W = sum(w for _, w in sw)
    mu = S / W
    means = np.array([s / w for s, w in sw])
    var_obs = float(np.var(means))
    noise = float(np.mean([mu / w for _, w in sw]))
    tau2 = max(var_obs - noise, 1e-4)
    K = min(max(mu / tau2, 0.5), 200.0)
    return K, {"mu": mu, "tau_m": math.sqrt(tau2), "n_teams": len(sw)}


def estimate_ratio_prior(shots_store, sot_store, div, teams_keys):
    """Beta-Binomial MoM prior strength for the on-target ratio."""
    rhos, ns = [], []
    S = SS = 0.0
    for key in teams_keys:
        ss, _ = shots_store[key].value_current()
        so, _ = sot_store[key].value_current()
        if ss >= 5:
            rhos.append(so / ss)
            ns.append(ss)
        S += so
        SS += ss
    if len(rhos) < 3 or SS == 0:
        return 200.0, None  # immaterial for teams with no shots (ratio = league rho)
    rho_bar = S / SS
    var_obs = float(np.var(rhos))
    noise = float(np.mean([rho_bar * (1 - rho_bar) / n for n in ns]))
    tau2 = var_obs - noise
    if tau2 <= 1e-5:
        return 5000.0, {"rho_bar": rho_bar, "tau_rho": 0.0, "n_teams": len(rhos)}
    m = rho_bar * (1 - rho_bar) / tau2 - 1.0
    return min(max(m, 5.0), 5000.0), {"rho_bar": rho_bar,
                                      "tau_rho": math.sqrt(tau2),
                                      "n_teams": len(rhos)}


class RatingsVC:
    def __init__(self, mode):
        self.mode = mode
        self.lg_h, self.lg_a = defaultdict(Decayed), defaultdict(Decayed)
        self.att_h, self.def_h = defaultdict(Decayed), defaultdict(Decayed)
        self.att_a, self.def_a = defaultdict(Decayed), defaultdict(Decayed)
        self.sot_h, self.sot_a = defaultdict(Decayed), defaultdict(Decayed)
        self.lg_sot_h, self.lg_sot_a = defaultdict(Decayed), defaultdict(Decayed)
        self.last_K = {}
        self.last_ratio = {}

    def league_mu(self, div, day):
        sh, wh = self.lg_h[div].value(day)
        sa, wa = self.lg_a[div].value(day)
        return (sh / wh if wh else 13.0, sa / wa if wa else 11.0)

    def _shrunk(self, group, obj, day, mu):
        s, w = obj.value(day)
        if self.mode == "gz":
            K = GZ_CONSTANTS["K"]
        else:
            K, info = estimate_K(list(group.values()), day)
            self.last_K[id(group)] = (K, info)
        return (s + K * mu) / (w + K)

    def predict(self, div, home, away, day):
        mh, ma = self.league_mu(div, day)
        eh = (self._shrunk(self.att_h, self.att_h[(div, home)], day, mh)
              * self._shrunk(self.def_a, self.def_a[(div, away)], day, mh) / mh)
        ea = (self._shrunk(self.att_a, self.att_a[(div, away)], day, ma)
              * self._shrunk(self.def_h, self.def_h[(div, home)], day, ma) / ma)
        return eh, ea

    def ratio(self, div, team, venue, day, prior):
        if venue == "h":
            shots, sot = self.att_h, self.sot_h
            lgshots, lgsot = self.lg_h[div], self.lg_sot_h[div]
            fallback = 4.5 / 13.0
        else:
            shots, sot = self.att_a, self.sot_a
            lgshots, lgsot = self.lg_a[div], self.lg_sot_a[div]
            fallback = 3.5 / 11.0
        ss, _ = shots[(div, team)].value(day)
        so, _ = sot[(div, team)].value(day)
        ls, _ = lgshots.value(day)
        lo, _ = lgsot.value(day)
        rho = lo / ls if ls > 0 else fallback
        if self.mode == "vc":
            # decay all group objects to `day` first (deterministic, past-only)
            for store in (shots, sot):
                for obj in store.values():
                    obj.value(day)
            keys = [k for k in shots.keys() if k[0] == div]
            # value_current: Decayed objects already decayed to `day`
            def vc(store):
                class _W:
                    def __init__(self, o):
                        self.o = o

                    def value_current(self):
                        return self.o.s, self.o.w
                return {k: _W(store[k]) for k in keys}
            prior, info = estimate_ratio_prior(vc(shots), vc(sot), div, keys)
            self.last_ratio[venue] = (prior, info)
        return (so + prior * rho) / (ss + prior)

    def update(self, m):
        d = m["day"]
        div, h, a = m["div"], m["home"], m["away"]
        self.att_h[(div, h)].add(d, m["shots_h"])
        self.def_h[(div, h)].add(d, m["shots_a"])
        self.att_a[(div, a)].add(d, m["shots_a"])
        self.def_a[(div, a)].add(d, m["shots_h"])
        self.lg_h[div].add(d, m["shots_h"])
        self.lg_a[div].add(d, m["shots_a"])
        self.sot_h[(div, h)].add(d, m["sot_h"])
        self.sot_a[(div, a)].add(d, m["sot_a"])
        self.lg_sot_h[div].add(d, m["sot_h"])
        self.lg_sot_a[div].add(d, m["sot_a"])


class RegressionVC:
    """Copy of the shipped RegressionStore._fit with a penalty vector;
    in vc mode the two group penalties are Laplace-EM estimates."""

    def __init__(self, matches, mode):
        self.mode = mode
        self.divs = {}
        self.refit_log = []
        for div in sorted({m["div"] for m in matches}):
            ms = [m for m in matches if m["div"] == div]
            teams = sorted({m["home"] for m in ms} | {m["away"] for m in ms})
            tidx = {t: i for i, t in enumerate(teams)}
            T = len(teams)
            self.divs[div] = {"teams": teams, "tidx": tidx, "T": T,
                              "day": np.array([m["day"] for m in ms], float),
                              "hi": np.array([tidx[m["home"]] for m in ms]),
                              "ai": np.array([tidx[m["away"]] for m in ms]),
                              "yh": np.array([m["sot_h"] for m in ms], float),
                              "ya": np.array([m["sot_a"] for m in ms], float),
                              "theta": None, "next_refit": None,
                              "lam_a": GZ_CONSTANTS["ridge"],
                              "lam_d": GZ_CONSTANTS["ridge"]}

    def _fit_once(self, dst, refit_day, pen):
        day, hi, ai, yh, ya, T = dst["day"], dst["hi"], dst["ai"], dst["yh"], dst["ya"], dst["T"]
        cut = int(np.searchsorted(day, refit_day, side="left"))
        P = 2 + 2 * T
        theta = dst["theta"]
        if theta is None:
            theta = np.zeros(P)
            if cut:
                w0 = 0.5 ** ((refit_day - day[:cut]) / HL)
                theta[0] = math.log(max(np.average(yh[:cut], weights=w0), 1e-3))
                theta[1] = math.log(max(np.average(ya[:cut], weights=w0), 1e-3))
            else:
                theta[:2] = math.log(4.5), math.log(3.5)
        if not cut:
            dst["theta"] = theta
            return theta, None
        wm = 0.5 ** ((refit_day - day[:cut]) / HL)
        y = np.r_[yh[:cut], ya[:cut]]
        b = np.r_[np.zeros(cut, int), np.ones(cut, int)]
        a = np.r_[hi[:cut], ai[:cut]] + 2
        d = np.r_[ai[:cut], hi[:cut]] + 2 + T
        w = np.r_[wm, wm]

        def pll(th):
            eta = np.clip(th[b] + th[a] + th[d], ETA_LO, ETA_HI)
            return float(np.sum(w * (y * eta - np.exp(eta))) - .5 * np.sum(pen * th ** 2))

        cur = pll(theta)
        H = None
        for _ in range(60):
            eta = np.clip(theta[b] + theta[a] + theta[d], ETA_LO, ETA_HI)
            mu = np.exp(eta)
            r = w * (y - mu)
            g = np.zeros(P)
            for ix in (b, a, d):
                np.add.at(g, ix, r)
            g -= pen * theta
            W = w * mu
            H = np.zeros((P, P))
            for x, z in ((b, b), (b, a), (b, d), (a, b), (a, a), (a, d),
                         (d, b), (d, a), (d, d)):
                np.add.at(H, (x, z), W)
            H[np.arange(P), np.arange(P)] += pen + 1e-10
            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t = 1.0
            for _ in range(25):
                cand = theta + t * step
                if pll(cand) >= cur - 1e-12:
                    theta, cur = cand, pll(cand)
                    break
                t *= .5
            else:
                break
            if np.max(np.abs(t * step)) < 1e-6:
                break
        dst["theta"] = theta
        return theta, H

    def _fit(self, dst, refit_day):
        T = dst["T"]
        P = 2 + 2 * T
        if self.mode == "gz":
            pen = np.full(P, GZ_CONSTANTS["ridge"])
            pen[:2] = 0.0
            self._fit_once(dst, refit_day, pen)
            return
        # vc: Laplace-EM rounds inside this refit (training slice only)
        for _ in range(3):
            pen = np.zeros(P)
            pen[2:2 + T] = dst["lam_a"]
            pen[2 + T:] = dst["lam_d"]
            theta, H = self._fit_once(dst, refit_day, pen)
            if H is None or theta is None:
                return
            try:
                cov = np.linalg.inv(H)
                post = np.maximum(np.diag(cov), 0.0)
            except np.linalg.LinAlgError:
                return
            tau_a2 = float(np.mean(theta[2:2 + T] ** 2 + post[2:2 + T]))
            tau_d2 = float(np.mean(theta[2 + T:] ** 2 + post[2 + T:]))
            tau_a2 = min(max(tau_a2, 1e-4), 4.0)
            tau_d2 = min(max(tau_d2, 1e-4), 4.0)
            dst["lam_a"] = min(max(1.0 / tau_a2, 1.0), 10000.0)
            dst["lam_d"] = min(max(1.0 / tau_d2, 1.0), 10000.0)
        self.refit_log.append({"refit_day": refit_day,
                               "lam_a": dst["lam_a"], "lam_d": dst["lam_d"],
                               "tau_a": 1.0 / math.sqrt(dst["lam_a"]),
                               "tau_d": 1.0 / math.sqrt(dst["lam_d"])})

    def _ensure(self, div, day):
        dst = self.divs[div]
        if dst["next_refit"] is None or day >= dst["next_refit"]:
            self._fit(dst, day)
            dst["next_refit"] = day + REFIT_DAYS
        return dst

    def predict(self, div, home, away, day):
        dst = self._ensure(div, day)
        th = dst["theta"]
        T, ix = dst["T"], dst["tidx"]
        ih, ia = ix.get(home), ix.get(away)
        ah = th[2 + ih] if ih is not None else 0
        dh = th[2 + T + ih] if ih is not None else 0
        aa = th[2 + ia] if ia is not None else 0
        da = th[2 + T + ia] if ia is not None else 0
        return (math.exp(np.clip(th[0] + ah + da, ETA_LO, ETA_HI)),
                math.exp(np.clip(th[1] + aa + dh, ETA_LO, ETA_HI)))

    def means(self, div, day):
        th = self._ensure(div, day)["theta"]
        return math.exp(th[0]), math.exp(th[1])


class NaiveTracker:
    def __init__(self):
        self.hist = defaultdict(lambda: deque(maxlen=NAIVE_N))

    def predict(self, div, home, away, mh, ma):
        h, a = self.hist[(div, home)], self.hist[(div, away)]
        if h and a:
            hf, ha = np.mean(h, axis=0)
            af, aa = np.mean(a, axis=0)
            return (hf + aa) / 2, (af + ha) / 2
        return mh, ma

    def update(self, m):
        self.hist[(m["div"], m["home"])].append((m["sot_h"], m["sot_a"]))
        self.hist[(m["div"], m["away"])].append((m["sot_a"], m["sot_h"]))


class EngineVC:
    def __init__(self, matches, lines, mode):
        self.mode = mode
        self.lines = lines
        self.reg = RegressionVC(matches, mode)
        self.ratings = RatingsVC(mode)
        self.naive = NaiveTracker()
        self.totals = []          # (date, total SOT) in walk order
        self.nb_r_used = []

    def _nb_r(self):
        if self.mode == "gz":
            return GZ_CONSTANTS["nb_r"]
        vals = np.array([t for _, t in self.totals], float)
        if len(vals) < 15:
            return GZ_CONSTANTS["nb_r"]  # unscored warmup only; see report
        mu = float(vals.mean())
        var = float(vals.var())
        if var <= mu:
            return 500.0
        return min(max(mu * mu / (var - mu), 5.0), 500.0)

    def predict(self, m):
        d, div, h, a = m["day"], m["div"], m["home"], m["away"]
        rh, ra = self.reg.predict(div, h, a, d)
        sh, sa = self.ratings.predict(div, h, a, d)
        prior = GZ_CONSTANTS["ratio_prior"]
        rhoh = self.ratings.ratio(div, h, "h", d, prior)
        rhoa = self.ratings.ratio(div, a, "a", d, prior)
        eh, ea = .5 * (rh + sh * rhoh), .5 * (ra + sa * rhoa)
        mh, ma = self.reg.means(div, d)
        nh, na = self.naive.predict(div, h, a, mh, ma)
        r = self._nb_r()
        self.nb_r_used.append(r)
        total, naive_total = eh + ea, nh + na
        probs = {L: .5 * nb_over(total, r, L) + .5 * nb_over(naive_total, r, L)
                 for L in self.lines}
        return {"exp_h": eh, "exp_a": ea, "probs": probs,
                "naive_probs": {L: nb_over(naive_total, r, L) for L in self.lines}}

    def update(self, m):
        self.ratings.update(m)
        self.naive.update(m)
        self.totals.append((m["date"], m["sot_h"] + m["sot_a"]))

    def era_report(self):
        by_month = defaultdict(list)
        for dt, t in self.totals:
            by_month[(dt.year, dt.month)].append(t)
        if len(by_month) < 3:
            return {"months": len(by_month), "sigma_era_month": None}
        lm = np.array([math.log(np.mean(v)) for v in by_month.values()])
        return {"months": len(by_month),
                "sigma_era_month": float(np.std(lm))}


# ---------------------------------------------------------------- shipped GZ

def import_shipped_model(league):
    sub = {"LV-Virsliga": "LV-Virsliga/engine/sot/model.py",
           "SA-FirstDivision": "SA-FirstDivision/engine/sot/model.py"}[league]
    path = REPO / "league" / sub
    spec = importlib.util.spec_from_file_location(f"shipped_sot_{league}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_league_matches(league):
    mod = import_shipped_model(league)
    if league == "LV-Virsliga":
        data = REPO / "league" / "LV-Virsliga" / "data" / "lv_virsliga_matches.csv"
        ms = [m for m in mod.load_matches(data, {"2025"})
              if date(2025, 3, 5) <= m["date"] <= date(2025, 11, 9)]
        return mod, ms
    data = REPO / "league" / "SA-FirstDivision" / "data" / "safd_matches.csv"
    ms = mod.load_matches(data, {"2025/2026"})
    return mod, ms


def walk_generic(ms, predict_fn, update_fn, score_from):
    """Date-grouped predict-then-update walk; returns scored (m, p) pairs."""
    out = []
    i = 0
    while i < len(ms):
        j = i + 1
        while j < len(ms) and ms[j]["date"] == ms[i]["date"]:
            j += 1
        ps = [(m, predict_fn(m)) for m in ms[i:j]]
        if score_from(ms[i]):
            out.extend(ps)
        for m, _ in ps:
            update_fn(m)
        i = j
    return out


def ll_bin(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def run_sot_league(league):
    mod, ms = load_league_matches(league)
    if league == "LV-Virsliga":
        lines, primary = (8.5, 9.5, 10.5), 9.5
        shipped_ll = 0.682845864332496
        start = date(2025, 5, 1)
        score_from = lambda m: m["date"] >= start
        slice_scored = None
    else:
        lines, primary = (7.5, 8.5, 9.5), 8.5
        shipped_ll = 0.69444695485426
        score_from = lambda m: True
        slice_scored = 90  # harness scores walk rows [90:]

    def finish(out):
        if slice_scored is not None:
            out = out[slice_scored:]
        n = len(out)
        per_line = {str(L): sum(ll_bin(p["probs"][L], int(m["sot_h"] + m["sot_a"] > L))
                                for m, p in out) / n for L in lines}
        return {"n": n, "ll": per_line, "ll_primary": per_line[str(primary)]}

    # 1) shipped engine, shipped walk
    eng = mod.Engine(ms, "GZ")
    out_ship = walk_generic(ms, eng.predict, eng.update, score_from)
    ship = finish(out_ship)

    # 2) my reimplementation in gz mode (must match shipped)
    eng_gz = EngineVC(ms, lines, "gz")
    out_gz = walk_generic(ms, eng_gz.predict, eng_gz.update, score_from)
    gz = finish(out_gz)

    # 3) variance-component mode
    eng_vc = EngineVC(ms, lines, "vc")
    out_vc = walk_generic(ms, eng_vc.predict, eng_vc.update, score_from)
    vc = finish(out_vc)

    # estimated-component summaries (scored window)
    refits = eng_vc.reg.refit_log
    return {"league": league, "market": "sot",
            "bucket": "mid", "stats_seasons": 2,
            "primary_line": primary,
            "shipped": {"ll_primary": shipped_ll},
            "gz_shipped_engine": ship, "gz_replication": gz, "vc": vc,
            "vc_components": {
                "refit_lams": refits,
                "lam_a_final": refits[-1]["lam_a"] if refits else None,
                "lam_d_final": refits[-1]["lam_d"] if refits else None,
                "nb_r_scored_mean": float(np.mean(eng_vc.nb_r_used[-vc["n"]:])) if vc["n"] else None,
                "era_report": eng_vc.era_report(),
            }}


if __name__ == "__main__":
    import json
    import sys
    for lg in sys.argv[1:]:
        o = run_sot_league(lg)
        print(json.dumps(o, indent=2))
