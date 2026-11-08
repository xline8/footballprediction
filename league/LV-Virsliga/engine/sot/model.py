"""League-local S-RU shots-on-target walk-forward model."""
import csv
import math
from collections import defaultdict, deque
from datetime import date

import numpy as np

HL = 365.0
K_PRIOR = 8.0
NAIVE_N = 10
RIDGE_LAM = 100.0
NB_R = 79.94
REFIT_DAYS = 7
ETA_LO, ETA_HI = -6.0, 4.0
LINES = (8.5, 9.5, 10.5)
ERA = date(2025, 1, 1)


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


class Ratings:
    def __init__(self):
        self.lg_h, self.lg_a = defaultdict(Decayed), defaultdict(Decayed)
        self.att_h, self.def_h = defaultdict(Decayed), defaultdict(Decayed)
        self.att_a, self.def_a = defaultdict(Decayed), defaultdict(Decayed)
        self.sot_h, self.sot_a = defaultdict(Decayed), defaultdict(Decayed)
        self.lg_sot_h, self.lg_sot_a = defaultdict(Decayed), defaultdict(Decayed)

    def league_mu(self, div, day):
        sh, wh = self.lg_h[div].value(day); sa, wa = self.lg_a[div].value(day)
        return (sh / wh if wh else 13.0, sa / wa if wa else 11.0)

    def _shrunk(self, obj, day, mu):
        s, w = obj.value(day)
        return (s + K_PRIOR * mu) / (w + K_PRIOR)

    def predict(self, div, home, away, day):
        mh, ma = self.league_mu(div, day)
        eh = mh * self._shrunk(self.att_h[(div, home)], day, mh) / mh * self._shrunk(self.def_a[(div, away)], day, mh) / mh
        ea = ma * self._shrunk(self.att_a[(div, away)], day, ma) / ma * self._shrunk(self.def_h[(div, home)], day, ma) / ma
        return eh, ea

    def update(self, m):
        d = m["day"]; div, h, a = m["div"], m["home"], m["away"]
        self.att_h[(div, h)].add(d, m["shots_h"]); self.def_h[(div, h)].add(d, m["shots_a"])
        self.att_a[(div, a)].add(d, m["shots_a"]); self.def_a[(div, a)].add(d, m["shots_h"])
        self.lg_h[div].add(d, m["shots_h"]); self.lg_a[div].add(d, m["shots_a"])
        self.sot_h[(div, h)].add(d, m["sot_h"]); self.sot_a[(div, a)].add(d, m["sot_a"])
        self.lg_sot_h[div].add(d, m["sot_h"]); self.lg_sot_a[div].add(d, m["sot_a"])

    def ratio(self, div, team, venue, day, prior):
        if venue == "h":
            shots, sot, lgshots, lgsot = self.att_h[(div, team)], self.sot_h[(div, team)], self.lg_h[div], self.lg_sot_h[div]
            fallback = 4.5 / 13.0
        else:
            shots, sot, lgshots, lgsot = self.att_a[(div, team)], self.sot_a[(div, team)], self.lg_a[div], self.lg_sot_a[div]
            fallback = 3.5 / 11.0
        ss, _ = shots.value(day); so, _ = sot.value(day); ls, _ = lgshots.value(day); lo, _ = lgsot.value(day)
        rho = lo / ls if ls > 0 else fallback
        return (so + prior * rho) / (ss + prior)

    def league_rho(self, div, venue, day):
        if venue == "h":
            lgshots, lgsot, fallback = self.lg_h[div], self.lg_sot_h[div], 4.5 / 13.0
        else:
            lgshots, lgsot, fallback = self.lg_a[div], self.lg_sot_a[div], 3.5 / 11.0
        shots, _ = lgshots.value(day); sot, _ = lgsot.value(day)
        return sot / shots if shots > 0 else fallback


class RegressionStore:
    def __init__(self, matches):
        self.divs = {}
        for div in sorted({m["div"] for m in matches}):
            ms = [m for m in matches if m["div"] == div]
            teams = sorted({m["home"] for m in ms} | {m["away"] for m in ms})
            tidx = {t: i for i, t in enumerate(teams)}; T = len(teams)
            self.divs[div] = {"teams": teams, "tidx": tidx, "T": T,
                "day": np.array([m["day"] for m in ms], float),
                "hi": np.array([tidx[m["home"]] for m in ms]), "ai": np.array([tidx[m["away"]] for m in ms]),
                "yh": np.array([m["sot_h"] for m in ms], float), "ya": np.array([m["sot_a"] for m in ms], float),
                "theta": None, "next_refit": None}

    def _fit(self, dst, refit_day):
        day, hi, ai, yh, ya, T = dst["day"], dst["hi"], dst["ai"], dst["yh"], dst["ya"], dst["T"]
        cut = int(np.searchsorted(day, refit_day, side="left")); P = 2 + 2 * T
        theta = dst["theta"]
        if theta is None:
            theta = np.zeros(P)
            if cut:
                w0 = 0.5 ** ((refit_day - day[:cut]) / HL)
                theta[0] = math.log(max(np.average(yh[:cut], weights=w0), 1e-3)); theta[1] = math.log(max(np.average(ya[:cut], weights=w0), 1e-3))
            else: theta[:2] = math.log(4.5), math.log(3.5)
        if not cut:
            dst["theta"] = theta; return
        wm = 0.5 ** ((refit_day - day[:cut]) / HL)
        y = np.r_[yh[:cut], ya[:cut]]; b = np.r_[np.zeros(cut, int), np.ones(cut, int)]
        a = np.r_[hi[:cut], ai[:cut]] + 2; d = np.r_[ai[:cut], hi[:cut]] + 2 + T; w = np.r_[wm, wm]
        def pll(th):
            eta = np.clip(th[b] + th[a] + th[d], ETA_LO, ETA_HI)
            return float(np.sum(w * (y * eta - np.exp(eta))) - .5 * RIDGE_LAM * np.sum(th[2:] ** 2))
        cur = pll(theta)
        for _ in range(60):
            eta = np.clip(theta[b] + theta[a] + theta[d], ETA_LO, ETA_HI); mu = np.exp(eta); r = w * (y - mu); g = np.zeros(P)
            for ix in (b, a, d): np.add.at(g, ix, r)
            g[2:] -= RIDGE_LAM * theta[2:]; W = w * mu; H = np.zeros((P, P))
            for x, z in ((b,b),(b,a),(b,d),(a,b),(a,a),(a,d),(d,b),(d,a),(d,d)): np.add.at(H, (x,z), W)
            H[np.arange(2, P), np.arange(2, P)] += RIDGE_LAM; H[np.arange(P), np.arange(P)] += 1e-10
            try: step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError: break
            t = 1.0
            for _ in range(25):
                cand = theta + t * step
                if pll(cand) >= cur - 1e-12: theta, cur = cand, pll(cand); break
                t *= .5
            else: break
            if np.max(np.abs(t * step)) < 1e-6: break
        dst["theta"] = theta

    def _ensure(self, div, day):
        dst = self.divs[div]
        if dst["next_refit"] is None or day >= dst["next_refit"]:
            self._fit(dst, day); dst["next_refit"] = day + REFIT_DAYS
        return dst

    def predict(self, div, home, away, day):
        dst = self._ensure(div, day); th = dst["theta"]; T, ix = dst["T"], dst["tidx"]
        ih, ia = ix.get(home), ix.get(away)
        ah = th[2+ih] if ih is not None else 0; dh = th[2+T+ih] if ih is not None else 0
        aa = th[2+ia] if ia is not None else 0; da = th[2+T+ia] if ia is not None else 0
        return math.exp(np.clip(th[0] + ah + da, ETA_LO, ETA_HI)), math.exp(np.clip(th[1] + aa + dh, ETA_LO, ETA_HI))

    def means(self, div, day):
        th = self._ensure(div, day)["theta"]
        return math.exp(th[0]), math.exp(th[1])


class NaiveTracker:
    def __init__(self): self.hist = defaultdict(lambda: deque(maxlen=NAIVE_N))
    def predict(self, div, home, away, mh, ma):
        h, a = self.hist[(div, home)], self.hist[(div, away)]
        if h and a:
            hf, ha = np.mean(h, axis=0); af, aa = np.mean(a, axis=0)
            return (hf + aa) / 2, (af + ha) / 2
        return mh, ma
    def update(self, m):
        self.hist[(m["div"], m["home"])].append((m["sot_h"], m["sot_a"]))
        self.hist[(m["div"], m["away"])].append((m["sot_a"], m["sot_h"]))


class QualityHistory:
    def __init__(self): self.q = defaultdict(deque); self.g = defaultdict(deque)
    def update(self, m):
        for team, side in ((m["home"], "home"), (m["away"], "away")):
            xg, shots = m.get("xg_"+side), m.get("smshots_"+side)
            if xg is not None and shots is not None and shots > 0: self.q[team].append((m["date"], xg, shots))
            if m["date"] >= ERA:
                xgot, n = m.get("xgot_"+side), m.get("xgotn_"+side)
                if xgot is not None and n is not None and n > 0: self.g[team].append((m["date"], xgot, n))
    def ratio_x4(self, team, before, rho, fallback):
        rows = [x for x in self.q[team] if x[0] < before][-25:]
        if len(rows) < 8: return fallback
        q = sum(x[1] for x in rows) / sum(x[2] for x in rows)
        return min(max(rho * q / self.league_q(before), .15), .50)
    def league_q(self, before):
        # Set by the engine from all historical rows; this method is replaced per prediction.
        rows = [x for values in self.q.values() for x in values if x[0] < before]
        return sum(x[1] for x in rows) / sum(x[2] for x in rows) if rows and sum(x[2] for x in rows) > 0 else 1.0
    def multiplier(self, team, before, league_g):
        rows = [x for x in self.g[team] if x[0] < before][-25:]
        if len(rows) < 8 or league_g <= 0: return 1.0
        g = sum(x[1] for x in rows) / sum(x[2] for x in rows)
        return min(max(1 + .5 * (g / league_g - 1), .85), 1.15)
    def league_g(self, before):
        rows = [x for values in self.g.values() for x in values if x[0] < before]
        return sum(x[1] for x in rows) / sum(x[2] for x in rows) if rows and sum(x[2] for x in rows) > 0 else 1.0


class Engine:
    def __init__(self, matches, arm, *, ratio_prior=None):
        self.ratio_prior = ratio_prior
        self.arm = arm; self.matches = matches; self.reg = RegressionStore(matches); self.ratings = Ratings(); self.naive = NaiveTracker(); self.quality = QualityHistory()
    def predict(self, m):
        d, div, h, a = m["day"], m["div"], m["home"], m["away"]
        rh, ra = self.reg.predict(div, h, a, d); sh, sa = self.ratings.predict(div, h, a, d)
        prior = self.ratio_prior if self.ratio_prior is not None else (20000.0 if self.arm == "RS" else 200.0)
        rhoh = self.ratings.ratio(div, h, "h", d, prior)
        rhoa = self.ratings.ratio(div, a, "a", d, prior)
        if self.arm == "X4":
            raise ValueError("X4 is disabled by the frozen S-RU preregistration")
        if self.arm == "X6":
            before = m["date"]; lq = self.quality.league_q(before)
            def qratio(team, venue, rho):
                rows = [x for x in self.quality.q[team] if x[0] < before][-25:]
                if len(rows) < 8: return self.ratings.ratio(div, team, venue, d, 200.0)
                q = sum(x[1] for x in rows) / sum(x[2] for x in rows)
                rho_venue = self.ratings.league_rho(div, venue, d)
                return min(max(rho_venue * q / lq, .15), .50)
            rhoh, rhoa = qratio(h, "h", rhoh), qratio(a, "a", rhoa)
        ih, ia = sh * rhoh, sa * rhoa; eh, ea = .5 * (rh + ih), .5 * (ra + ia)
        if self.arm == "X6":
            lg = self.quality.league_g(m["date"]); eh *= self.quality.multiplier(h, m["date"], lg); ea *= self.quality.multiplier(a, m["date"], lg)
        mh, ma = self.reg.means(div, d); nh, na = self.naive.predict(div, h, a, mh, ma)
        total, naive_total = eh + ea, nh + na
        probs = {L: .5 * nb_over(total, NB_R, L) + .5 * nb_over(naive_total, NB_R, L) for L in LINES}
        return {"exp_h": eh, "exp_a": ea, "probs": probs, "naive_probs": {L: nb_over(naive_total, NB_R, L) for L in LINES}}
    def update(self, m): self.ratings.update(m); self.naive.update(m); self.quality.update(m)


def load_matches(path, allowed_seasons=None, include_era_xgot=True):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            season = str(r["season"])
            if allowed_seasons is not None and season not in allowed_seasons: continue
            def num(k):
                v = r.get(k, ""); return None if v in (None, "") else float(v)
            if r.get("has_stats_all") != "1": continue
            if any(num(k) is None for k in ("total_shots_home", "total_shots_away", "ShotsOnTarget_home", "ShotsOnTarget_away")): continue
            dt = date.fromisoformat(r["date"])
            m = {"match_id": r["match_id"], "date": dt, "day": dt.toordinal(), "season": season, "div": r["league"], "home": r["home_team"], "away": r["away_team"], "shots_h": num("total_shots_home"), "shots_a": num("total_shots_away"), "sot_h": num("ShotsOnTarget_home"), "sot_a": num("ShotsOnTarget_away")}
            for side in ("home", "away"):
                m["smshots_"+side] = num("sm_shots_"+side); m["xg_"+side] = num("sm_xg_"+side)
                if include_era_xgot and dt >= ERA:
                    m["xgot_"+side] = num("sm_xgot_"+side); m["xgotn_"+side] = num("sm_xgot_n_"+side)
            out.append(m)
    out.sort(key=lambda m: (m["date"], m["match_id"]))
    return out
