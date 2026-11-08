#!/usr/bin/env python
"""Total shots model — experiment (design and gate: PREREG.md).

Target: total shots per match (HS + AS), the statistic behind the
bookmaker market "Shots Towards The Goal". Architecture mirrors SOT
v5 step 1 applied to shots: per-division jointly fitted log-linear
Poisson ratings (ridge), line probabilities from a negative binomial
whose size is estimated from pre-test walk-forward residuals, and an
optional 50/50 ensemble with the naive trailing-10 means — the
ensemble is adopted only if it clearly wins on the TUNING season.

Everything frozen is frozen on pre-2023/24 data only:
  - ridge lambda tuned on 2022/23 over {3, 10, 30, 100, 300}
    (line-25.5 log loss of regression+Poisson; ties toward larger);
  - NB size r by method of moments from regression residuals over
    2019/20–2022/23 at the tuned lambda;
  - candidate choice (a) regression+NB vs (b) + naive ensemble, on
    2022/23 line-25.5 log loss: (b) only if better by >= 0.0005.

Baselines (house definitions from the SOT base experiment):
  (a) division base rate — decayed league means, Poisson;
  (b) naive trailing-10 — plain for/against means, Poisson.

Test: walk-forward 2023/24–2025/26, all divisions with shot stats;
gate clauses on pooled + top-5 divisions (see PREREG.md).

Run:  .venv/bin/python experiments/shots_model/run_shots_experiment.py
Writes only RESULTS.md next to itself. No production code touched.
"""

import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "sot_model"))

from run_sot_v2 import (BASE_HL, BASE_K, NaiveTracker, Ratings,  # noqa: E402
                        TEST_SEASONS, TOP5, load_matches, logloss,
                        nb_over, poisson_over)

OUT = os.path.join(HERE, "RESULTS.md")
TUNE_SEASON = "2022/23"
RESID_SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23"]
GRID_LAM = [3.0, 10.0, 30.0, 100.0, 300.0]
REFIT_DAYS = 7
MAIN_LINE = 25.5
LINES = [22.5, 23.5, 24.5, 25.5, 26.5, 27.5, 28.5]
ENS_MARGIN = 0.0005
ETA_LO, ETA_HI = -6.0, 4.0
EPS = 1e-6
METHODS = ["candidate", "base_league", "base_naive"]
LABELS = {"candidate": "Candidate (chosen on tuning)",
          "base_league": "Baseline (a) division base rate",
          "base_naive": "Baseline (b) naive trailing-10"}


# ------------------------------------------- joint regression on shots
class ShotsRegressionStore:
    """run_sot_v5.RegressionStore with the target switched to total
    shots (HS/AS) and shot-scale fallback intercepts. Fit set for a
    refit at day D: the division's matches with day < D, sample
    weights 0.5 ** ((D - day) / 365). Lazy per-division refits every
    REFIT_DAYS of match dates; warm starts carry theta across refits.
    The team index spans all of the division's matches (indexing
    only — a team with no prior matches keeps A = D = 0)."""

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
                "yh": np.array([m["hs"] for m in ms], dtype=float),
                "ya": np.array([m["as"] for m in ms], dtype=float),
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
                theta[0], theta[1] = math.log(13.0), math.log(11.0)
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


# ------------------------------------------------- pass W: tune lambda
def pass_warmup(matches):
    """Chronological pass over pre-2023/24 data: per-lambda line-25.5
    log loss on TUNE_SEASON (regression+Poisson) and per-lambda
    residual moment sums over RESID_SEASONS.
    Returns (tune_ll, resid) with resid[lam] = (s_lam2, s_res2, s_lam, n).
    """
    reg = ShotsRegressionStore(matches, GRID_LAM)
    tune = {lam: [0, 0.0] for lam in GRID_LAM}
    resid = {lam: [0.0, 0.0, 0.0, 0] for lam in GRID_LAM}

    for m in matches:
        if m["season"] in TEST_SEASONS:
            break  # warm-up only; matches are chronological
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        total = m["hs"] + m["as"]
        is_tune = m["season"] == TUNE_SEASON
        is_resid = m["season"] in RESID_SEASONS
        if is_tune or is_resid:
            y = 1.0 if total > MAIN_LINE else 0.0
            for lam in GRID_LAM:
                eh, ea = reg.predict(div, home, away, day, lam)
                lt = eh + ea
                if is_resid:
                    rr = resid[lam]
                    rr[0] += lt * lt
                    rr[1] += (total - lt) ** 2
                    rr[2] += lt
                    rr[3] += 1
                if is_tune:
                    tune[lam][0] += 1
                    tune[lam][1] += logloss(poisson_over(lt, MAIN_LINE), y)
    tune_ll = {lam: s / n for lam, (n, s) in tune.items()}
    return tune_ll, resid


def mom_r(resid_entry):
    s_lam2, s_res2, s_lam, n = resid_entry
    denom = s_res2 - s_lam
    r = s_lam2 / denom if denom > 0 else 1e6
    return min(max(r, 1.0), 1e6), n, (s_lam / n if n else float("nan")), \
        (s_res2 / s_lam if s_lam else float("nan"))


# ------------------------------------------- pass W2: candidate choice
def pass_select(matches, best_lam, nb_r):
    """Score variants A (reg+Poisson), B (reg+NB), C (B + 50/50 naive
    ensemble) on TUNE_SEASON only. Returns {variant: mean LL@25.5}."""
    reg = ShotsRegressionStore(matches, [best_lam])
    naive = NaiveTracker()
    acc = {v: [0, 0.0] for v in ("A", "B", "C")}
    for m in matches:
        if m["season"] in TEST_SEASONS:
            break
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]
        if m["season"] == TUNE_SEASON:
            total = m["hs"] + m["as"]
            y = 1.0 if total > MAIN_LINE else 0.0
            eh, ea = reg.predict(div, home, away, day, best_lam)
            lt = eh + ea
            mu_h, mu_a = reg.league_mu(div, day, best_lam)
            nh, na = naive.predict(div, home, away, mu_h, mu_a)
            lt_n = nh + na
            probs = {"A": poisson_over(lt, MAIN_LINE),
                     "B": nb_over(lt, nb_r, MAIN_LINE),
                     "C": 0.5 * nb_over(lt, nb_r, MAIN_LINE)
                          + 0.5 * nb_over(lt_n, nb_r, MAIN_LINE)}
            for v, p in probs.items():
                acc[v][0] += 1
                acc[v][1] += logloss(p, y)
        naive.update(div, home, away, m["hs"], m["as"])
    return {v: s / n for v, (n, s) in acc.items()}


# ------------------------------------------------------------- pass E
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
            "calib_signed": (sp - sy) / n * 100,
            "pred": 100 * sp / n, "act": 100 * sy / n}


def pass_eval(matches, best_lam, nb_r, use_ensemble):
    reg = ShotsRegressionStore(matches, [best_lam])
    naive = NaiveTracker()
    shots_rt = Ratings(BASE_HL, BASE_K, "shots")

    pooled = {v: new_acc(LINES) for v in METHODS}
    season_acc = {v: {s: new_acc([MAIN_LINE]) for s in TEST_SEASONS}
                  for v in METHODS}
    div_acc = {v: {d: new_acc([MAIN_LINE]) for d in TOP5}
               for v in METHODS}
    mae = {v: [0, 0.0] for v in METHODS}
    mae_season = {s: [0, 0.0] for s in TEST_SEASONS}
    n_eval = 0

    for m in matches:
        day, div = m["day"], m["div"]
        home, away = m["home"], m["away"]

        if m["season"] in TEST_SEASONS:
            total = m["hs"] + m["as"]
            ys = {L: (1.0 if total > L else 0.0) for L in LINES}

            eh, ea = reg.predict(div, home, away, day, best_lam)
            lt = eh + ea
            rmu_h, rmu_a = reg.league_mu(div, day, best_lam)
            nh_r, na_r = naive.predict(div, home, away, rmu_h, rmu_a)
            lt_nr = nh_r + na_r

            mu_h, mu_a, _, _ = shots_rt.league_mu(div, day)
            lt_base = mu_h + mu_a
            nh, na = naive.predict(div, home, away, mu_h, mu_a)
            lt_nb = nh + na

            if use_ensemble:
                cand = {L: 0.5 * nb_over(lt, nb_r, L)
                        + 0.5 * nb_over(lt_nr, nb_r, L) for L in LINES}
            else:
                cand = {L: nb_over(lt, nb_r, L) for L in LINES}
            probs = {"candidate": cand,
                     "base_league": {L: poisson_over(lt_base, L)
                                     for L in LINES},
                     "base_naive": {L: poisson_over(lt_nb, L)
                                    for L in LINES}}
            lam_pt = {"candidate": lt, "base_league": lt_base,
                      "base_naive": lt_nb}

            n_eval += 1
            mae_season[m["season"]][0] += 1
            mae_season[m["season"]][1] += abs(lt - total)
            for v in METHODS:
                mae[v][0] += 1
                mae[v][1] += abs(lam_pt[v] - total)
                for L in LINES:
                    add(pooled[v], L, probs[v][L], ys[L])
                add(season_acc[v][m["season"]], MAIN_LINE,
                    probs[v][MAIN_LINE], ys[MAIN_LINE])
                if div in TOP5:
                    add(div_acc[v][div], MAIN_LINE,
                        probs[v][MAIN_LINE], ys[MAIN_LINE])

        shots_rt.update(div, home, away, day, m["hs"], m["as"])
        naive.update(div, home, away, m["hs"], m["as"])

    return pooled, season_acc, div_acc, mae, mae_season, n_eval


# ------------------------------------------------------------------- main
def main():
    t0 = time.time()
    matches = load_matches()
    tune_ll, resid = pass_warmup(matches)
    # ties break toward MORE regularization (larger lambda)
    best_lam = min(GRID_LAM, key=lambda l: (tune_ll[l], -l))
    nb_r, n_res, mean_lam, var_ratio = mom_r(resid[best_lam])

    sel = pass_select(matches, best_lam, nb_r)
    use_ensemble = sel["C"] <= sel["B"] - ENS_MARGIN
    cand_name = ("(b) regression + NB + naive ensemble" if use_ensemble
                 else "(a) regression + NB")

    pooled, season_acc, div_acc, mae, mae_season, n_eval = pass_eval(
        matches, best_lam, nb_r, use_ensemble)
    runtime = time.time() - t0

    cand = stats(pooled["candidate"])
    bl = stats(pooled["base_league"])
    bn = stats(pooled["base_naive"])
    best_base_ll = min(bl["ll"], bn["ll"])
    margin = best_base_ll - cand["ll"]
    gate1 = margin >= 0.001
    gate2 = abs(cand["calib_signed"]) <= 1.0
    div_rows = {}
    worst_div_excess = -1e9
    for d in TOP5:
        dc = stats(div_acc["candidate"][d])
        db = min(stats(div_acc["base_league"][d])["ll"],
                 stats(div_acc["base_naive"][d])["ll"])
        div_rows[d] = (dc, db)
        worst_div_excess = max(worst_div_excess, dc["ll"] - db)
    gate3 = worst_div_excess <= 0.0003
    passed = gate1 and gate2 and gate3

    out = []
    out.append("# Total Shots Model — Experiment Results")
    out.append("")
    out.append("Script: `run_shots_experiment.py`. Design and gate: "
               "`PREREG.md` (committed before this run). Target: total "
               "shots per match (HS + AS), walk-forward test seasons "
               "2023/24–2025/26, headline line 25.5.")
    out.append("")
    out.append(f"Evaluated matches: {n_eval:,}")
    out.append("")
    out.append("## Frozen choices (pre-2023/24 data only)")
    out.append("")
    out.append("- Ridge lambda (2022/23 line-25.5 log loss, "
               "regression+Poisson): " + ", ".join(
                   f"lam={l:g}: {tune_ll[l]:.4f}" for l in GRID_LAM)
               + f" → chosen **lam = {best_lam:g}**.")
    out.append(f"- NB size: **r = {nb_r:.2f}** from {n_res:,} regression "
               f"walk-forward residuals (2019/20–2022/23; mean predicted "
               f"total {mean_lam:.2f}, residual variance / mean ratio "
               f"{var_ratio:.3f} — Poisson would be 1.000).")
    out.append(f"- Candidate selection on 2022/23 (LL@25.5): "
               f"A reg+Poisson {sel['A']:.4f} · B reg+NB {sel['B']:.4f} "
               f"· C B+ensemble {sel['C']:.4f} → chosen **{cand_name}** "
               f"(ensemble requires a ≥ {ENS_MARGIN} win on tuning).")
    out.append("")
    out.append("## Headline — pooled, line 25.5")
    out.append("")
    out.append("| Method | LogLoss | Brier | Pred Over% | Actual Over% | Calib (pp, signed) | MAE |")
    out.append("|---|---|---|---|---|---|---|")
    for v in METHODS:
        s = stats(pooled[v])
        m = mae[v][1] / mae[v][0]
        out.append(f"| {LABELS[v]} | {s['ll']:.4f} | {s['brier']:.4f} | "
                   f"{s['pred']:.1f} | {s['act']:.1f} | "
                   f"{s['calib_signed']:+.2f} | {m:.2f} |")
    out.append("")
    out.append("## All lines — pooled log loss")
    out.append("")
    out.append("| Method | " + " | ".join(f"{L}" for L in LINES) + " |")
    out.append("|---|" + "---|" * len(LINES))
    for v in METHODS:
        cells = " | ".join(f"{stats(pooled[v], L)['ll']:.4f}" for L in LINES)
        out.append(f"| {LABELS[v]} | {cells} |")
    out.append("")
    out.append("## By season — line 25.5 log loss")
    out.append("")
    out.append("| Season | n | Candidate | Base (a) | Base (b) | Candidate calib (pp) | Candidate MAE |")
    out.append("|---|---|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        sc = stats(season_acc["candidate"][sname])
        sa = stats(season_acc["base_league"][sname])
        sb = stats(season_acc["base_naive"][sname])
        ms = mae_season[sname]
        out.append(f"| {sname} | {sc['n']:,} | {sc['ll']:.4f} | "
                   f"{sa['ll']:.4f} | {sb['ll']:.4f} | "
                   f"{sc['calib_signed']:+.2f} | "
                   f"{ms[1] / ms[0]:.2f} |")
    out.append("")
    out.append("## By division (top-5) — line 25.5 log loss")
    out.append("")
    out.append("| Div | n | Candidate | Best baseline | Δ (cand − best base) |")
    out.append("|---|---|---|---|---|")
    for d in TOP5:
        dc, db = div_rows[d]
        out.append(f"| {d} | {dc['n']:,} | {dc['ll']:.4f} | {db:.4f} | "
                   f"{dc['ll'] - db:+.4f} |")
    out.append("")
    out.append("## Gate verdict (PREREG.md, fixed before the run)")
    out.append("")
    out.append(f"1. Pooled LL@25.5 beats best baseline by ≥ 0.001: "
               f"margin {margin:+.4f} → **{'PASS' if gate1 else 'FAIL'}**.")
    out.append(f"2. Calibration @25.5 within ±1.0pp: "
               f"{cand['calib_signed']:+.2f}pp → "
               f"**{'PASS' if gate2 else 'FAIL'}**.")
    out.append(f"3. Worst top-5 division excess over its best baseline "
               f"≤ 0.0003: {worst_div_excess:+.4f} → "
               f"**{'PASS' if gate3 else 'FAIL'}**.")
    out.append("")
    out.append(f"**VERDICT: {'PASS — proceed to production build (Phase 2)' if passed else 'FAIL — production stays untouched; this market remains unmodelled'}.**")
    out.append("")
    out.append("## Method notes and caveats")
    out.append("")
    out.append("- The candidate's edge over the baselines includes the "
               "NB dispersion (the baselines are Poisson, the house "
               "definition since the SOT base experiment); the tuning "
               "table above separates the regression's own contribution "
               "(variant A vs baselines would show it) — variant A/B/C "
               "are tuning-season numbers, not test numbers.")
    out.append("- Provider disagreement on total shots is larger than "
               "for SOT (O/U flip 1.43–2.04% across the ladder, "
               "PREREG.md): the model is trained and graded on the "
               "spine's count; bookmaker settlement on another count "
               "is a pricing-side risk, not a model error.")
    out.append("- No odds anywhere: predictive accuracy/calibration "
               "only, not betting value (no total-shots odds in our "
               "data).")
    out.append(f"- Script runtime (this run, incl. data load): "
               f"{runtime:.0f}s.")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")

    print(f"tuned: ridge lam={best_lam:g}  NB r={nb_r:.2f}  "
          f"candidate={cand_name}")
    print("  lam grid: " + ", ".join(f"{l:g}:{tune_ll[l]:.4f}"
                                     for l in GRID_LAM))
    print(f"  select: A={sel['A']:.4f} B={sel['B']:.4f} C={sel['C']:.4f}")
    print(f"evaluated n = {n_eval:,}")
    print(f"{'method':34s} {'LL@25.5':>8s} {'Brier':>7s} {'calib':>7s} {'MAE':>5s}")
    for v in METHODS:
        s = stats(pooled[v])
        m = mae[v][1] / mae[v][0]
        print(f"{v:34s} {s['ll']:8.4f} {s['brier']:7.4f} "
              f"{s['calib_signed']:+6.2f}p {m:5.2f}")
    print(f"gate: margin {margin:+.4f} ({gate1}), calib "
          f"{cand['calib_signed']:+.2f}pp ({gate2}), worst div "
          f"{worst_div_excess:+.4f} ({gate3}) -> "
          f"{'PASS' if passed else 'FAIL'}")
    print(f"runtime: {runtime:.0f}s")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
