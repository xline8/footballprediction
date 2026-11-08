"""Halves experiment 2: constant-share goal halves + per-half rho correction.

Follow-up to run_halves_goals.py (experiment 1, GATE FAIL for dedicated
per-half DC fits). The product route is decided: FT lambdas thinned by the
frozen constant train shares (1H share home 0.4419, away 0.4440). The one
known defect of that baseline: it understates half Over 1.5 by ~2-4pp
(1H calib -2.26pp, 2H -3.56pp in experiment 1), because the FT Dixon-Coles
rho is applied at thinned scale, where it misprices the low-score cells
that decide P(total <= 1).

Correction under test (ONE family, two named forms — the brief allows
"a per-half rho or an equivalent overdispersion adjustment"; both are
fitted ONLY on the tuning window, judged by the same gate below):

Form A — per-half rho, pooled across divisions, fitted on the tuning
window (train < 2023-08-01) by maximising the decay-weighted
full-scoreline log-likelihood of the observed half scores under the
thinned FT lambdas (same weighting scheme DC.fit itself uses for its
rho: w = 0.5**((cutoff - date)/HL), HL=365).

Form B — overdispersion: the half TOTAL goals are distributed Negative
Binomial with mean = thinned match total lambda and a per-half size
r_half, fitted on the tuning window by maximising the likelihood of the
observed half totals. (Same production pattern as the SOT models:
per-team expectations stay thinned lambdas; only the total's
distribution is adjusted.) Motivation checked on TUNING data only:
form A's fitted rhos come out ~0.00/+0.03 yet the Over-1.5
understatement survives essentially intact even at rho = 0 — the
residual defect is tail thinness (overdispersion), not the tau cells.

The DC fits and the shares are exactly those of experiment 1.

Gate (pre-registered):
- pooled per-half O/U log loss across lines 0.5/1.5/2.5 must NOT worsen
  vs the uncorrected baseline by more than 0.0005 (per half), AND
- per-half Over-1.5 calibration error must improve to within ~1pp
  (|err| <= 1.0pp) on the test window 2023/24-2025/26.
Both halves must pass for the product to ship.
"""
import math
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from model_v2 import DC  # noqa: E402
from football_etl import pois, tau  # noqa: E402

TOP5 = ["E0", "SP1", "I1", "D1", "F1"]
HL = 365
EPS = 1e-12
LINES = (0.5, 1.5, 2.5)
RHO_GRID = [round(-0.30 + 0.01 * i, 2) for i in range(51)]  # -0.30..+0.20


def games_of(df, yh, ya):
    return [(r.HomeTeam, r.AwayTeam, int(getattr(r, yh)),
             int(getattr(r, ya)), r.Date) for r in df.itertuples()]


def ll_bin(p, y):
    p = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def low_cells(lh, la):
    """Poisson products for the four tau-affected cells + truncated mass.

    Returns (p00, p01, p10, p11, s0) where s0 is the full score-matrix
    mass with tau == 1 (truncation at 10 goals/side, as in DC.probs;
    the missing tail mass is ~1e-9 at half lambdas)."""
    p00 = pois(0, lh) * pois(0, la)
    p01 = pois(0, lh) * pois(1, la)
    p10 = pois(1, lh) * pois(0, la)
    p11 = pois(1, lh) * pois(1, la)
    fh = sum(pois(x, lh) for x in range(11))
    fa = sum(pois(y, la) for y in range(11))
    return p00, p01, p10, p11, fh * fa


def smass(cells, lh, la, rho):
    """Normalising mass of the DC matrix at a given rho."""
    p00, p01, p10, p11, s0 = cells
    return (s0 + p00 * (tau(0, 0, lh, la, rho) - 1.0)
            + p01 * (tau(0, 1, lh, la, rho) - 1.0)
            + p10 * (tau(1, 0, lh, la, rho) - 1.0)
            + p11 * (tau(1, 1, lh, la, rho) - 1.0))


def cell_prob(cells, lh, la, rho, x, y):
    base = pois(x, lh) * pois(y, la)
    return base * tau(x, y, lh, la, rho) / smass(cells, lh, la, rho)


def nb_logpmf(k, mu, r):
    return (math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1)
            + r * math.log(r / (r + mu)) + k * math.log(mu / (r + mu)))


def nb_over(mu, r):
    """P(total > line) for lines 0.5/1.5/2.5 under NB(mu, r)."""
    cdf = [0.0, 0.0, 0.0]
    for k in range(3):
        p = math.exp(nb_logpmf(k, mu, r))
        for i in range(k, 3):
            cdf[i] += p
    return {0.5: 1.0 - cdf[0], 1.5: 1.0 - cdf[1], 2.5: 1.0 - cdf[2]}


def over_probs(cells, lh, la, rho):
    """P(total > line) for lines 0.5/1.5/2.5 under (thinned) DC matrix."""
    s = smass(cells, lh, la, rho)
    p00, p01, p10, p11, _ = cells
    t00 = p00 * tau(0, 0, lh, la, rho)
    t01 = p01 * tau(0, 1, lh, la, rho)
    t10 = p10 * tau(1, 0, lh, la, rho)
    t11 = p11 * tau(1, 1, lh, la, rho)
    p02 = pois(0, lh) * pois(2, la)
    p20 = pois(2, lh) * pois(0, la)
    ple0 = t00 / s
    ple1 = (t00 + t01 + t10) / s
    ple2 = (t00 + t01 + t10 + p02 + t11 + p20) / s
    return {0.5: 1.0 - ple0, 1.5: 1.0 - ple1, 2.5: 1.0 - ple2}


def main():
    df = pd.read_csv("all_matches_clean.csv",
                     usecols=["Div", "Date", "HomeTeam", "AwayTeam",
                              "FTHG", "FTAG", "HTHG", "HTAG"],
                     parse_dates=["Date"])
    df = df[df.Div.isin(TOP5)].dropna(subset=["HTHG", "HTAG"])
    df["H2HG"] = df.FTHG - df.HTHG
    df["H2AG"] = df.FTAG - df.HTAG
    train = df[df.Date < "2023-08-01"]
    test = df[(df.Date >= "2023-08-01") & (df.Date < "2026-07-01")]
    print(f"train rows {len(train)}  test rows {len(test)}")

    s1_h = train.HTHG.sum() / train.FTHG.sum()
    s1_a = train.HTAG.sum() / train.FTAG.sum()
    print(f"train 1H goal share: home {s1_h:.4f}  away {s1_a:.4f}")
    shares = {"1H": (s1_h, s1_a), "2H": (1 - s1_h, 1 - s1_a)}

    # Per-division FT fits (goals only, exactly as experiment 1).
    fits = {}
    for div in TOP5:
        tr = train[train.Div == div].sort_values("Date")
        m = DC()
        m.fit(games_of(tr, "FTHG", "FTAG"), tr.Date.max(), HL)
        fits[div] = (m, tr.Date.max())
        print(f"{div}: FT fit rho {m.rho:+.2f} on {len(tr)} train rows")

    # ---- Fit per-half rho on the TUNING window only (pooled) ----
    # Precompute per train match: thinned lambdas, low cells, observed
    # half score, decay weight (cutoff = that division's train max date).
    tune = {"1H": [], "2H": []}
    for div in TOP5:
        m, cutoff = fits[div]
        tr = train[train.Div == div]
        for r in tr.itertuples():
            lh_ft, la_ft = m._lam(r.HomeTeam, r.AwayTeam)
            w = 0.5 ** ((cutoff - r.Date).days / HL)
            for half, yh, ya in (("1H", r.HTHG, r.HTAG),
                                 ("2H", r.H2HG, r.H2AG)):
                sh, sa = shares[half]
                lh, la = lh_ft * sh, la_ft * sa
                tune[half].append((lh, la, low_cells(lh, la),
                                   int(yh), int(ya), w))
    rho_half = {}
    for half in ("1H", "2H"):
        best_rho, best_ll = None, None
        for rho in RHO_GRID:
            ll = 0.0
            for lh, la, cells, yh, ya, w in tune[half]:
                p = cell_prob(cells, lh, la, rho, yh, ya)
                ll += w * math.log(max(p, EPS))
            if best_ll is None or ll > best_ll:
                best_ll, best_rho = ll, rho
        rho_half[half] = best_rho
        print(f"{half}: rho_half fitted on tuning window = {best_rho:+.2f} "
              f"(n={len(tune[half])})")

    # ---- Fit NB size per half on the TUNING window only (form B) ----
    r_grid = [3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 32, 40, 50, 65, 80,
              100, 130, 170, 220, 300, 450, 700, 1200]
    r_half = {}
    for half in ("1H", "2H"):
        pairs = [(lh + la, yh + ya)
                 for lh, la, cells, yh, ya, w in tune[half]]
        best_r, best_ll = None, None
        for r in r_grid:
            ll = sum(nb_logpmf(t, mu, float(r)) for mu, t in pairs)
            if best_ll is None or ll > best_ll:
                best_ll, best_r = ll, r
        r_half[half] = float(best_r)
        print(f"{half}: NB r_half fitted on tuning window = {best_r} "
              f"(n={len(pairs)})")

    # ---- Walk-forward evaluation on the test window ----
    agg = {h: {"ll_b": [], "ll_a": [], "ll_nb": [], "cal_b": [],
               "cal_a": [], "cal_nb": [], "act": []} for h in ("1H", "2H")}
    for div in TOP5:
        m, _ = fits[div]
        te = test[test.Div == div]
        for r in te.itertuples():
            lh_ft, la_ft = m._lam(r.HomeTeam, r.AwayTeam)
            for half, yh, ya in (("1H", r.HTHG, r.HTAG),
                                 ("2H", r.H2HG, r.H2AG)):
                sh, sa = shares[half]
                lh, la = lh_ft * sh, la_ft * sa
                cells = low_cells(lh, la)
                pb = over_probs(cells, lh, la, m.rho)
                pa = over_probs(cells, lh, la, rho_half[half])
                pnb = nb_over(lh + la, r_half[half])
                tot = int(yh) + int(ya)
                a = agg[half]
                for L in LINES:
                    y = 1.0 if tot > L else 0.0
                    a["ll_b"].append(ll_bin(pb[L], y))
                    a["ll_a"].append(ll_bin(pa[L], y))
                    a["ll_nb"].append(ll_bin(pnb[L], y))
                a["cal_b"].append(pb[1.5])
                a["cal_a"].append(pa[1.5])
                a["cal_nb"].append(pnb[1.5])
                a["act"].append(1.0 if tot > 1 else 0.0)
        print(f"{div}: test {len(te)} scored")

    print()
    verdict = {}
    for form, llk, calk in (("A rho", "ll_a", "cal_a"),
                            ("B NB-overdispersion", "ll_nb", "cal_nb")):
        ok = True
        print(f"--- correction form {form} ---")
        for half in ("1H", "2H"):
            a = agg[half]
            n = len(a["act"])
            llb = sum(a["ll_b"]) / len(a["ll_b"])
            llc = sum(a[llk]) / len(a[llk])
            calb = (sum(a["cal_b"]) / n - sum(a["act"]) / n) * 100
            calc = (sum(a[calk]) / n - sum(a["act"]) / n) * 100
            print(f"{half} n={n}  pooled OU(0.5/1.5/2.5) LL base "
                  f"{llb:.4f} vs corr {llc:.4f}  (delta {llc - llb:+.4f}, "
                  f"limit +0.0005)")
            print(f"{half}      Over-1.5 calib base {calb:+.2f}pp vs "
                  f"corr {calc:+.2f}pp  (must be within ~1pp)")
            if llc - llb > 0.0005 or abs(calc) > 1.0:
                ok = False
        verdict[form] = ok
        print(f"form {form}: {'PASS' if ok else 'FAIL'}")
    print()
    win = [f for f, ok in verdict.items() if ok]
    print("GATE:", f"PASS via form {win[0]}" if win else
          "FAIL - neither correction form clears the pre-registered "
          "gate; no production change")


if __name__ == "__main__":
    main()
