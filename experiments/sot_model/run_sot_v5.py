#!/usr/bin/env python
"""Shots-on-target (SOT) model — v5: three proposal improvements on SLIM.

Every variant starts from the SLIM production recipe (run_sot_v3.py /
RESULTS_V3.md: base ratings + improvement 1 total-shots signal +
improvement 6 naive ensemble; pooled line-9.5 log loss 0.6312, Brier
0.2201, calib err 0.4pp over 21,461 matches, 2023/24-2025/26). This
script first reproduces slim in the same pass — if slim does not
reproduce 0.6312 (tolerance 5e-5), the run is invalid and no adoption
may follow from it.

The three improvements come from an external proposal
(~/workspace/user/files/improvement_model_prediksi_shot_on_goal.md);
only the three testable now are implemented (game-state adjustment is
not — the data has no per-shot event stream):

R. Joint regression ratings. The decayed-weighted-average ratings
   estimator is replaced by a jointly fitted log-linear Poisson model
   per division:
       log(mu_home) = beta_home + A_home + D_away
       log(mu_away) = beta_away + A_away + D_home
   with ridge (L2) penalty (lam/2) * sum(A^2 + D^2) on the team
   parameters (intercepts unpenalized), fitted by Newton/Fisher IRLS
   with backtracking in numpy. Walk-forward: refits are lazy and per
   division — the first prediction request on/after a division's next
   scheduled refit day refits that division on matches strictly before
   that request's date, with the same 365d exponential decay as sample
   weights (age relative to the request date); the next refit is
   scheduled 7 days later. The regression supplies the ratings-based
   expectations; the total-shots component and the naive ensemble stay
   as in slim, except the naive tracker's league-mean fallback (used
   only when a team has no trailing history in the division) comes
   from the regression intercepts exp(beta) instead of the decayed
   ratings. lam is tuned ONLY on 2022/23 over {1, 3, 10, 30, 100}
   (penalty units: weighted-count scale, i.e. lam is comparable to an
   effective number of decayed observations pulling A/D to 0); ties
   break toward the larger lam (more regularization). Frozen after.

NB. Negative binomial on slim. Slim's two expected totals (the blended
    ratings total and the naive total) generate their line
    probabilities from a negative binomial with size r instead of a
    Poisson; the 50/50 ensemble average is unchanged. r is estimated
    by method of moments from the SLIM model's walk-forward residuals
    over the warm-up seasons 2019/20-2022/23 (the same estimator as
    v2's improvement 3), then frozen:
        r = sum(lam^2) / (sum((t - lam)^2) - sum(lam)).

BB. Beta-Binomial-style smoothing of the on-target ratio. The current
    total-shots component already shrinks the team's trailing
    SOT/shots ratio toward the league ratio rho, with prior strength
    K * mu_shots (K = 8 match-equivalents, i.e. ~104 pseudo-shots at
    home, ~88 away — venue-dependent). The proposal's form makes the
    prior strength a fixed pseudo-shot count P for both venues:
        ratio = (S_sot + P * rho) / (S_shots + P)
    with S_sot / S_shots the team's decayed sums at the venue and rho
    the league's decayed ratio at the venue (unchanged). P is tuned
    ONLY on 2022/23 over {20, 50, 100, 200} shots; ties break toward
    the larger P (more smoothing). Frozen after.

VARIANTS: slim (reference), slim+R, slim+NB, slim+BB,
slim+R+NB+BB (combined). Point prediction / MAE: each variant's own
blended expectation lam1 (NB shares slim's, as in v2).

GATE (same as v4): a variant is adoptable only if ALL hold vs slim:
pooled line-9.5 log loss is lower; pooled line-9.5 calibration error
does not worsen by more than 1.5pp; no top-5 division's line-9.5 log
loss worsens by more than 0.003. Preference: the combined variant
when adoptable and best; otherwise the best adoptable single.

Run:  .venv/bin/python experiments/sot_model/run_sot_v5.py
Writes only RESULTS_V5.md next to itself. No production code touched.
"""

import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from run_sot_v2 import (BASE_HL, BASE_K, FALLBACK, LINES, MAIN_LINE,
                        TEST_SEASONS, TOP5, Ratings, NaiveTracker,
                        load_matches, logloss, nb_over, poisson_over)

OUT = os.path.join(HERE, "RESULTS_V5.md")
TUNE_SEASON = "2022/23"
RESID_SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23"]
GRID_LAM = [1.0, 3.0, 10.0, 30.0, 100.0]
GRID_BB = [20.0, 50.0, 100.0, 200.0]
REFIT_DAYS = 7
REF_SLIM_LL = 0.6312            # RESULTS_V3.md, pooled line 9.5
VARIANTS = ["slim", "slim+R", "slim+NB", "slim+BB", "slim+R+NB+BB"]
LABELS = {"slim": "SLIM (production reference)",
          "slim+R": "slim + R (joint regression ratings)",
          "slim+NB": "slim + NB (negative binomial)",
          "slim+BB": "slim + BB (Beta-Binomial ratio)",
          "slim+R+NB+BB": "slim + R + NB + BB (combined)"}
ETA_LO, ETA_HI = -6.0, 4.0      # exp() guards, same in fit and predict


# ------------------------------------------------- joint regression ratings
class RegressionStore:
    """Per-division jointly fitted log-linear Poisson SOT ratings.

    Fit set for a refit at day D: the division's matches with day < D,
    sample weights 0.5 ** ((D - day) / 365). Parameters per division:
    theta = [beta_h, beta_a, A_1..A_T, D_1..D_T] over a fixed team
    index built from all of the division's matches in the data (index
    only — a team with no prior matches keeps A = D = 0 through the
    ridge, so no future information enters any fit). Refits are lazy:
    the first prediction for a division at day >= its next scheduled
    refit day refits (for every registered lambda) with data strictly
    before that day and schedules the next refit REFIT_DAYS later.
    Warm starts carry each (division, lambda)'s theta across refits.
    """

    def __init__(self, matches, lambdas):
        self.lambdas = list(lambdas)
        self.divs = {}
        by_div = {}
        for m in matches:
            by_div.setdefault(m["div"], []).append(m)
        for div, ms in by_div.items():
            teams = sorted({m["home"] for m in ms}
                           | {m["away"] for m in ms})
            tidx = {t: i for i, t in enumerate(teams)}
            self.divs[div] = {
                "teams": teams, "tidx": tidx, "T": len(teams),
                "day": np.array([m["day"] for m in ms], dtype=float),
                "hi": np.array([tidx[m["home"]] for m in ms]),
                "ai": np.array([tidx[m["away"]] for m in ms]),
                "yh": np.array([m["hst"] for m in ms], dtype=float),
                "ya": np.array([m["ast"] for m in ms], dtype=float),
                "theta": {}, "next_refit": None,
            }

    def _fit(self, dst, lam, refit_day):
        day, hi, ai = dst["day"], dst["hi"], dst["ai"]
        yh, ya, T = dst["yh"], dst["ya"], dst["T"]
        cut = int(np.searchsorted(day, refit_day, side="left"))
        P = 2 + 2 * T
        theta = dst["theta"].get(lam)
        if theta is None:
            theta = np.zeros(P)
            if cut > 0:
                wm0 = 0.5 ** ((refit_day - day[:cut]) / BASE_HL)
                theta[0] = math.log(max(np.average(yh[:cut], weights=wm0),
                                        1e-3))
                theta[1] = math.log(max(np.average(ya[:cut], weights=wm0),
                                        1e-3))
            else:
                theta[0], theta[1] = math.log(4.5), math.log(3.5)
            dst["theta"][lam] = theta
        if cut == 0:
            return
        wm = 0.5 ** ((refit_day - day[:cut]) / BASE_HL)
        y = np.concatenate([yh[:cut], ya[:cut]])
        bcol = np.concatenate([np.zeros(cut, dtype=int),
                               np.ones(cut, dtype=int)])
        acol = np.concatenate([hi[:cut], ai[:cut]]) + 2
        dcol = np.concatenate([ai[:cut], hi[:cut]]) + 2 + T
        w = np.concatenate([wm, wm])
        diag = np.arange(P)

        def pll(th):
            eta = np.clip(th[bcol] + th[acol] + th[dcol], ETA_LO, ETA_HI)
            return float(np.sum(w * (y * eta - np.exp(eta)))
                         - 0.5 * lam * np.sum(th[2:] ** 2))

        cur = pll(theta)
        for _ in range(60):
            eta = np.clip(theta[bcol] + theta[acol] + theta[dcol],
                          ETA_LO, ETA_HI)
            mu = np.exp(eta)
            r = w * (y - mu)
            g = np.zeros(P)
            np.add.at(g, bcol, r)
            np.add.at(g, acol, r)
            np.add.at(g, dcol, r)
            g[2:] -= lam * theta[2:]
            W = w * mu
            H = np.zeros((P, P))
            for cc, dd in ((bcol, bcol), (bcol, acol), (bcol, dcol),
                           (acol, bcol), (acol, acol), (acol, dcol),
                           (dcol, bcol), (dcol, acol), (dcol, dcol)):
                np.add.at(H, (cc, dd), W)
            H[diag[2:], diag[2:]] += lam
            H[diag, diag] += 1e-10
            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t, improved = 1.0, False
            for _ in range(25):
                cand = theta + t * step
                v = pll(cand)
                if v >= cur - 1e-12:
                    theta, cur = cand, v
                    improved = True
                    break
                t *= 0.5
            if not improved or np.max(np.abs(t * step)) < 1e-6:
                break
        dst["theta"][lam] = theta

    def _ensure(self, div, day):
        dst = self.divs.get(div)
        if dst is None:
            return None
        if dst["next_refit"] is None or day >= dst["next_refit"]:
            for lam in self.lambdas:
                self._fit(dst, lam, day)
            dst["next_refit"] = day + REFIT_DAYS
        return dst

    def predict(self, div, home, away, day, lam):
        dst = self._ensure(div, day)
        th = dst["theta"][lam]
        T, tidx = dst["T"], dst["tidx"]
        ih, ia = tidx.get(home), tidx.get(away)
        a_h = th[2 + ih] if ih is not None else 0.0
        d_h = th[2 + T + ih] if ih is not None else 0.0
        a_a = th[2 + ia] if ia is not None else 0.0
        d_a = th[2 + T + ia] if ia is not None else 0.0
        eh = math.exp(min(max(th[0] + a_h + d_a, ETA_LO), ETA_HI))
        ea = math.exp(min(max(th[1] + a_a + d_h, ETA_LO), ETA_HI))
        return eh, ea

    def league_mu(self, div, day, lam):
        dst = self._ensure(div, day)
        th = dst["theta"][lam]
        return math.exp(th[0]), math.exp(th[1])


# ------------------------------------------------------------ slim pieces
def slim_components(sot, shots, naive, div, home, away, day):
    """The slim recipe's pieces, in run_sot_v3.pass_slim's exact call
    order/formulas. Returns (eh, ea, seh, sea, imp_h, imp_a, lam1,
    lam_naive)."""
    eh, ea = sot.predict(div, home, away, day)
    seh, sea = shots.predict(div, home, away, day)
    mu_sh_h, mu_sh_a, _, _ = shots.league_mu(div, day)
    imp_h = seh * shots.on_target_ratio(div, home, "h", day, mu_sh_h)
    imp_a = sea * shots.on_target_ratio(div, away, "a", day, mu_sh_a)
    lam1 = 0.5 * (eh + imp_h) + 0.5 * (ea + imp_a)
    mu_h, mu_a, _, _ = sot.league_mu(div, day)
    nh, na = naive.predict(div, home, away, mu_h, mu_a)
    return eh, ea, seh, sea, imp_h, imp_a, lam1, nh + na


def bb_ratio(shots, div, team, venue, day, prior):
    """Proposal BB ratio from the shots system's decayed sums.

    Called only after slim_components has run for the same match/day,
    so every Decayed object read here is already decayed to `day` and
    value_at(day) is a no-op — the slim numbers are untouched.
    """
    if venue == "h":
        s_shots, _ = shots.att_h[(div, team)].value_at(day)
        s_sot, _ = shots.sot_h[(div, team)].value_at(day)
        lg_shot, _ = shots.lg_h[div].value_at(day)
        lg_sot, _ = shots.lg_sot_h[div].value_at(day)
        fb = FALLBACK["sot"][0] / FALLBACK["shots"][0]
    else:
        s_shots, _ = shots.att_a[(div, team)].value_at(day)
        s_sot, _ = shots.sot_a[(div, team)].value_at(day)
        lg_shot, _ = shots.lg_a[div].value_at(day)
        lg_sot, _ = shots.lg_sot_a[div].value_at(day)
        fb = FALLBACK["sot"][1] / FALLBACK["shots"][1]
    rho = lg_sot / lg_shot if lg_shot > 0 else fb
    return (s_sot + prior * rho) / (s_shots + prior)


def update_all(sot, shots, naive, m):
    day, div = m["day"], m["div"]
    sot.update(div, m["home"], m["away"], day, m["hst"], m["ast"])
    shots.update(div, m["home"], m["away"], day, m["hs"], m["as"],
                 sot_h=m["hst"], sot_a=m["ast"])
    naive.update(div, m["home"], m["away"], m["hst"], m["ast"])


# ------------------------------------------------- pass W: tuning + NB size
def pass_warmup(matches):
    """One chronological pass over pre-2023/24 data.

    - scores slim+R (per ridge lambda) and slim+BB (per prior P) by
      line-9.5 log loss on TUNE_SEASON (2022/23) only;
    - accumulates the NB method-of-moments sums from slim residuals
      over RESID_SEASONS.
    Returns (ll_r, ll_bb, nb_r, resid_info).
    """
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, GRID_LAM)
    ll_r = {lam: [0, 0.0] for lam in GRID_LAM}
    ll_bb = {p: [0, 0.0] for p in GRID_BB}
    s_lam2 = s_res2 = s_lam = 0.0
    n_res = 0

    for m in matches:
        if m["season"] in TEST_SEASONS:
            break  # warm-up only; matches are chronological
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        tune = m["season"] == TUNE_SEASON
        resid = m["season"] in RESID_SEASONS
        if tune or resid:
            (eh, ea, seh, sea, imp_h, imp_a, lam1,
             lam_n) = slim_components(sot, shots, naive, div, home, away,
                                      day)
            total = m["hst"] + m["ast"]
            if resid:
                s_lam2 += lam1 * lam1
                s_res2 += (total - lam1) ** 2
                s_lam += lam1
                n_res += 1
            if tune:
                y = 1.0 if total > MAIN_LINE else 0.0
                p_n = poisson_over(lam_n, MAIN_LINE)
                for p_ in GRID_BB:
                    ib_h = seh * bb_ratio(shots, div, home, "h", day, p_)
                    ib_a = sea * bb_ratio(shots, div, away, "a", day, p_)
                    lam1_bb = 0.5 * (eh + ib_h) + 0.5 * (ea + ib_a)
                    p = 0.5 * poisson_over(lam1_bb, MAIN_LINE) + 0.5 * p_n
                    ll_bb[p_][0] += 1
                    ll_bb[p_][1] += logloss(p, y)
                for lam in GRID_LAM:
                    reh, rea = reg.predict(div, home, away, day, lam)
                    lam1_r = 0.5 * (reh + imp_h) + 0.5 * (rea + imp_a)
                    p = 0.5 * poisson_over(lam1_r, MAIN_LINE) + 0.5 * p_n
                    ll_r[lam][0] += 1
                    ll_r[lam][1] += logloss(p, y)
        update_all(sot, shots, naive, m)

    denom = s_res2 - s_lam
    nb_r = s_lam2 / denom if denom > 0 else 1e6
    nb_r = min(max(nb_r, 1.0), 1e6)
    info = {"n": n_res, "mean_lam": s_lam / n_res if n_res else float("nan"),
            "var_ratio": s_res2 / s_lam if s_lam else float("nan")}
    return ll_r, ll_bb, nb_r, info


# ------------------------------------------------------------- pass E: eval
def new_acc(lines):
    return {L: [0, 0.0, 0.0, 0.0, 0.0] for L in lines}


def add(acc, line, p, y):
    a = acc[line]
    a[0] += 1
    a[1] += (p - y) ** 2
    a[2] += logloss(p, y)
    a[3] += p
    a[4] += y


def stats(acc, L=MAIN_LINE):
    n, brier, ll, sp, sy = acc[L]
    return {"n": n, "brier": brier / n, "ll": ll / n,
            "calib": abs(sp - sy) / n * 100, "pred": 100 * sp / n,
            "act": 100 * sy / n}


def pass_eval(matches, best_lam, best_p, nb_r):
    sot = Ratings(BASE_HL, BASE_K, "sot")
    shots = Ratings(BASE_HL, BASE_K, "shots", track_ratio=True)
    naive = NaiveTracker()
    reg = RegressionStore(matches, [best_lam])

    pooled = {v: new_acc(LINES) for v in VARIANTS}
    season_acc = {v: {s: new_acc([MAIN_LINE]) for s in TEST_SEASONS}
                  for v in ("slim", "slim+R+NB+BB")}
    div_acc = {v: {d: new_acc([MAIN_LINE]) for d in TOP5}
               for v in VARIANTS}
    mae = {v: [0, 0.0] for v in VARIANTS}
    n_eval = 0

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]

        if m["season"] in TEST_SEASONS:
            total = m["hst"] + m["ast"]
            ys = {L: (1.0 if total > L else 0.0) for L in LINES}
            (eh, ea, seh, sea, imp_h, imp_a, lam1,
             lam_n) = slim_components(sot, shots, naive, div, home, away,
                                      day)

            ib_h = seh * bb_ratio(shots, div, home, "h", day, best_p)
            ib_a = sea * bb_ratio(shots, div, away, "a", day, best_p)
            lam1_bb = 0.5 * (eh + ib_h) + 0.5 * (ea + ib_a)

            reh, rea = reg.predict(div, home, away, day, best_lam)
            rmu_h, rmu_a = reg.league_mu(div, day, best_lam)
            nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
            lam_n_r = nh_r + na_r
            lam1_r = 0.5 * (reh + imp_h) + 0.5 * (rea + imp_a)
            lam1_rb = 0.5 * (reh + ib_h) + 0.5 * (rea + ib_a)

            def ens(la, lb):
                return {L: 0.5 * poisson_over(la, L)
                        + 0.5 * poisson_over(lb, L) for L in LINES}

            def ens_nb(la, lb):
                return {L: 0.5 * nb_over(la, nb_r, L)
                        + 0.5 * nb_over(lb, nb_r, L) for L in LINES}

            probs = {"slim": ens(lam1, lam_n),
                     "slim+NB": ens_nb(lam1, lam_n),
                     "slim+BB": ens(lam1_bb, lam_n),
                     "slim+R": ens(lam1_r, lam_n_r),
                     "slim+R+NB+BB": ens_nb(lam1_rb, lam_n_r)}
            lam_pt = {"slim": lam1, "slim+NB": lam1, "slim+BB": lam1_bb,
                      "slim+R": lam1_r, "slim+R+NB+BB": lam1_rb}

            n_eval += 1
            for v in VARIANTS:
                mae[v][0] += 1
                mae[v][1] += abs(lam_pt[v] - total)
                for L in LINES:
                    add(pooled[v], L, probs[v][L], ys[L])
                if v in season_acc:
                    add(season_acc[v][m["season"]], MAIN_LINE,
                        probs[v][MAIN_LINE], ys[MAIN_LINE])
                if div in TOP5:
                    add(div_acc[v][div], MAIN_LINE,
                        probs[v][MAIN_LINE], ys[MAIN_LINE])

        update_all(sot, shots, naive, m)

    return pooled, season_acc, div_acc, mae, n_eval


# ------------------------------------------------------------------- gate
def evaluate_gate(pooled, div_acc):
    slim = stats(pooled["slim"])
    res = {}
    for v in VARIANTS[1:]:
        sv = stats(pooled[v])
        deltas = {d: stats(div_acc[v][d])["ll"] - stats(div_acc["slim"][d])["ll"]
                  for d in TOP5}
        worst = max(deltas.values())
        res[v] = {"ll": sv["ll"], "calib": sv["calib"],
                  "beats_ll": sv["ll"] < slim["ll"],
                  "calib_worsen": sv["calib"] - slim["calib"],
                  "calib_ok": sv["calib"] - slim["calib"] <= 1.5,
                  "calib_abs_ok": sv["calib"] <= 1.5,
                  "div_deltas": deltas, "worst_div_delta": worst,
                  "div_ok": worst <= 0.003}
        res[v]["adoptable"] = (res[v]["beats_ll"] and res[v]["calib_ok"]
                               and res[v]["div_ok"])
    adoptable = [v for v in res if res[v]["adoptable"]]
    winner = None
    if adoptable:
        best_ll = min(res[v]["ll"] for v in adoptable)
        if ("slim+R+NB+BB" in adoptable
                and res["slim+R+NB+BB"]["ll"] <= best_ll + 1e-12):
            winner = "slim+R+NB+BB"
        else:
            winner = min(adoptable, key=lambda v: res[v]["ll"])
    return res, winner


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    matches = load_matches()
    ll_r, ll_bb, nb_r, resid = pass_warmup(matches)
    tune_r = {lam: s / n for lam, (n, s) in ll_r.items()}
    tune_bb = {p: s / n for p, (n, s) in ll_bb.items()}
    # ties break toward MORE regularization / smoothing (larger value)
    best_lam = min(GRID_LAM, key=lambda l: (tune_r[l], -l))
    best_p = min(GRID_BB, key=lambda p: (tune_bb[p], -p))

    pooled, season_acc, div_acc, mae, n_eval = pass_eval(
        matches, best_lam, best_p, nb_r)
    runtime = time.time() - t0

    slim95 = stats(pooled["slim"])
    repro_ok = abs(slim95["ll"] - REF_SLIM_LL) < 0.00005
    gate, winner = evaluate_gate(pooled, div_acc) if repro_ok else ({}, None)

    out = []
    out.append("# Shots-on-Target (SOT) Model — v5: Regression Ratings, "
               "Negative Binomial, Beta-Binomial Ratio (on SLIM)")
    out.append("")
    out.append("Script: `run_sot_v5.py` (re-runnable; reuses "
               "`run_sot_v2.py`'s ratings/naive machinery and data loading "
               "unchanged). Reference: slim recipe of `run_sot_v3.py` / "
               "RESULTS_V3.md, which is what production `model_sot.py` "
               "implements. Same walk-forward evaluation (2023/24–2025/26). "
               "The three improvements are items R / 2 / 5A of the external "
               "proposal `improvement_model_prediksi_shot_on_goal.md`.")
    out.append("")
    out.append(f"Evaluated matches: {n_eval:,}")
    out.append("")
    out.append("## Slim reproduction check (validity of this run)")
    out.append("")
    out.append(f"Slim recomputed in this pass: pooled line-9.5 log loss "
               f"**{slim95['ll']:.4f}**, Brier {slim95['brier']:.4f}, calib "
               f"err {slim95['calib']:.1f}pp, MAE "
               f"{mae['slim'][1] / mae['slim'][0]:.2f} — RESULTS_V3.md: "
               f"0.6312 / 0.2201 / 0.4 / 2.45 → "
               f"**{'MATCH' if repro_ok else 'MISMATCH — RUN INVALID, NO ADOPTION'}**.")
    out.append("")
    out.append("## Frozen choices (all made on pre-2023/24 data only)")
    out.append("")
    out.append(f"- R ridge lambda (tuned on 2022/23 only, slim+R line-9.5 "
               f"log loss): " + ", ".join(
                   f"lam={l:g}: {tune_r[l]:.4f}" for l in GRID_LAM)
               + f" → chosen **lam = {best_lam:g}**. Refits: lazy per "
               f"division, every {REFIT_DAYS} days of match dates, data "
               f"strictly before the prediction date, 365d decay sample "
               f"weights, warm-started Newton/Fisher IRLS.")
    out.append(f"- BB prior strength P (tuned on 2022/23 only, slim+BB "
               f"line-9.5 log loss): " + ", ".join(
                   f"P={p:g}: {tune_bb[p]:.4f}" for p in GRID_BB)
               + f" → chosen **P = {best_p:g} shots**. (Slim's built-in "
               f"prior is K*mu_shots ≈ 104 shots home / 88 away.)")
    out.append(f"- NB size: **r = {nb_r:.2f}** from {resid['n']:,} slim "
               f"walk-forward residuals (2019/20–2022/23; mean predicted "
               f"total {resid['mean_lam']:.2f}, residual variance / mean "
               f"ratio {resid['var_ratio']:.3f} — Poisson would be 1.000).")
    out.append("")
    out.append("## Headline — pooled, main line 9.5")
    out.append("")
    out.append("| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs slim |")
    out.append("|---|---|---|---|---|---|")
    for v in VARIANTS:
        s = stats(pooled[v])
        m = mae[v][1] / mae[v][0]
        out.append(f"| {LABELS[v]} | {s['ll']:.4f} | {s['brier']:.4f} | "
                   f"{s['calib']:.1f} | {m:.2f} | {s['ll'] - slim95['ll']:+.4f} |")
    out.append("")
    out.append("## Every variant at every line (pooled log loss)")
    out.append("")
    out.append("| Variant | 7.5 | 8.5 | 9.5 | 10.5 |")
    out.append("|---|---|---|---|---|")
    for v in VARIANTS:
        cells = " | ".join(f"{stats(pooled[v], L)['ll']:.4f}" for L in LINES)
        out.append(f"| {LABELS[v]} | {cells} |")
    out.append("")
    out.append("## By division (top-5) — line 9.5 log loss (slim alongside)")
    out.append("")
    report_divs = ["slim", "slim+R+NB+BB"] + [
        v for v in ("slim+R", "slim+NB", "slim+BB")
        if v in gate and gate[v]["adoptable"]]
    out.append("| Div | n | " + " | ".join(LABELS[v] for v in report_divs) + " |")
    out.append("|---|" + "---|" * (len(report_divs) + 1))
    for d in TOP5:
        cells = " | ".join(f"{stats(div_acc[v][d])['ll']:.4f}"
                           for v in report_divs)
        out.append(f"| {d} | {stats(div_acc['slim'][d])['n']:,} | {cells} |")
    out.append("")
    out.append("## Combined by season — line 9.5 (slim alongside)")
    out.append("")
    out.append("| Season | n | Combined LogLoss | Combined Brier | Combined calib (pp) | Slim LogLoss |")
    out.append("|---|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        sa = stats(season_acc["slim+R+NB+BB"][sname])
        sb = stats(season_acc["slim"][sname])
        out.append(f"| {sname} | {sa['n']:,} | {sa['ll']:.4f} | "
                   f"{sa['brier']:.4f} | {sa['calib']:.1f} | {sb['ll']:.4f} |")
    out.append("")
    out.append("## Gate verdict")
    out.append("")
    if not repro_ok:
        out.append("**RUN INVALID** — slim did not reproduce; no gate was "
                   "evaluated and nothing may be adopted from this run.")
    else:
        for v in VARIANTS[1:]:
            g = gate[v]
            out.append(f"- {LABELS[v]}: ΔLL {g['ll'] - slim95['ll']:+.4f}; "
                       f"calib {g['calib']:.1f}pp (worsening "
                       f"{g['calib_worsen']:+.1f}pp, limit +1.5pp; stricter "
                       f"absolute ≤1.5pp: {'ok' if g['calib_abs_ok'] else 'NO'}); "
                       f"worst top-5 division ΔLL {g['worst_div_delta']:+.4f} "
                       f"(limit +0.003) → "
                       f"**{'ADOPTABLE' if g['adoptable'] else 'not adoptable'}**.")
        if winner:
            out.append(f"- **Winner: {LABELS[winner]}** "
                       f"(LL {gate[winner]['ll']:.4f} vs slim "
                       f"{slim95['ll']:.4f}).")
        else:
            out.append("- **No variant is adoptable — production stays "
                       "on the slim recipe unchanged.**")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- R changes only the ratings-based expectation (and the "
               "naive tracker's league-mean fallback); the shots system, "
               "the naive history and the 50/50 ensemble are slim's. The "
               "regression team index spans all of a division's matches "
               "(indexing only); a team with no prior matches in the fit "
               "set has A = D = 0 by construction of the ridge.")
    out.append("- BB differs from slim's built-in ratio shrinkage only in "
               "the prior-strength parametrization: a fixed pseudo-shot "
               "count P for both venues (tuned) instead of K * mu_shots "
               "(venue-dependent, ~104 home / ~88 away). The shrinkage "
               "target rho (decayed league ratio per venue) is unchanged.")
    out.append("- NB is applied to both ensemble members' totals with the "
               "single frozen r estimated from slim residuals; the "
               "combined variant uses that same frozen r on top of its "
               "own (R+BB) expectations — interactions are not re-estimated.")
    out.append("- Tuning (lam, P) used 2022/23 only; the NB size used "
               "2019/20–2022/23 residuals only; test seasons untouched "
               "by every choice.")
    out.append("- No odds anywhere: predictive accuracy/calibration "
               "only, not betting value (no SOT odds in our data).")
    out.append(f"- Script runtime (this run, incl. data load): "
               f"{runtime:.0f}s.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"tuned: ridge lam={best_lam:g}  BB P={best_p:g}  NB r={nb_r:.2f}")
    print(f"  lam grid: " + ", ".join(f"{l:g}:{tune_r[l]:.4f}"
                                     for l in GRID_LAM))
    print(f"  BB grid:  " + ", ".join(f"{p:g}:{tune_bb[p]:.4f}"
                                     for p in GRID_BB))
    print(f"evaluated n = {n_eval:,}")
    print(f"{'variant':28s} {'LL@9.5':>8s} {'Brier':>7s} {'calib':>6s} "
          f"{'MAE':>5s} {'dLL':>8s}")
    for v in VARIANTS:
        s = stats(pooled[v])
        m = mae[v][1] / mae[v][0]
        print(f"{v:28s} {s['ll']:8.4f} {s['brier']:7.4f} {s['calib']:5.1f}p "
              f"{m:5.2f} {s['ll'] - slim95['ll']:+8.4f}")
    print(f"slim reproduction: {'MATCH' if repro_ok else 'MISMATCH'} "
          f"({slim95['ll']:.4f} vs {REF_SLIM_LL})")
    if repro_ok:
        print(f"gate winner: {winner or 'NONE'}")
    print(f"runtime: {runtime:.0f}s")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
