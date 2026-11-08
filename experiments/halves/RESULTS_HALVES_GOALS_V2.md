# Halves experiment 2: constant-share goal halves + calibration correction

Date: 2026-11-08. Script: `run_halves_goals_v2.py`. Follow-up to
experiment 1 (`RESULTS_HALVES_GOALS.md`), which decided the product
route — FT lambdas thinned by the frozen constant train shares (1H
share: home 0.4419, away 0.4440) — and flagged one defect to fix first:
the thinned baseline understates half Over 1.5 by ~2–4pp.

## Correction under test

ONE correction family, in the two forms the design brief names, both
fitted ONLY on the tuning window (train < 2023-08-01), both judged by
the same pre-registered gate on 2023/24–2025/26 (top-5, n = 5,255):

- **Form A — per-half rho.** Pooled per-half Dixon-Coles rho, fitted by
  maximising the decay-weighted full-scoreline log-likelihood of the
  observed half scores under the thinned FT lambdas (the same weighting
  DC.fit uses for its own rho). Fitted: 1H rho = 0.00, 2H rho = +0.03.
- **Form B — NB overdispersion.** Half TOTAL goals ~ Negative Binomial,
  mean = thinned match total lambda, per-half size fitted by likelihood
  on the tuning window. Fitted: r = 1200 for both halves — the grid's
  Poisson edge. On tuning data the half totals show no overdispersion
  given the (in-sample) thinned lambdas, so form B collapses to plain
  Poisson.

The baseline replication is exact: Over-1.5 calibration of the
uncorrected baseline reproduces experiment 1 digit for digit
(1H −2.26pp, 2H −3.56pp).

## Gate

Pooled per-half O/U log loss (lines 0.5/1.5/2.5) must not worsen vs the
uncorrected baseline by more than 0.0005, AND per-half Over-1.5
calibration error must improve to within ~1pp.

| Half | Pooled OU LL base | LL form A | LL form B | Calib base | Calib A | Calib B |
|------|-------------------|-----------|-----------|------------|---------|---------|
| 1H   | 0.5394            | 0.5393    | 0.5393    | −2.26pp    | −2.73pp | −2.73pp |
| 2H   | 0.5651            | 0.5649    | 0.5649    | −3.56pp    | −4.42pp | −4.10pp |

**GATE FAIL — both forms, both halves, on the calibration leg.** The
log-loss leg passes trivially (the corrections barely move it), but
neither correction brings Over-1.5 calibration inside 1pp; both move
it the wrong way. Production untouched.

## Diagnosis (measured, not conjectured)

The understatement is NOT a tau/rho artefact and NOT fixable by a
distributional reshaping at fixed means:

- Removing rho entirely (plain independent Poisson) leaves −2.73pp in
  1H: the FT rho was actually *helping* slightly (−2.26 with it). The
  brief's causal story — "the FT rho does not carry into halves" — is
  not what the numbers say.
- At half means (μ ≈ 1.2–1.6), overdispersion at fixed mean *lowers*
  P(total ≥ 2) (mass moves from 1 to 0 and to ≥3), so form B cannot
  repair an Over-1.5 understatement even in principle at these means.
- The real defect is in the MEANS, and it is inherited: the thinned
  lambdas under-predict half goals on the test window by −0.072 (1H)
  and −0.097 (2H) goals per match, because the underlying static
  goals-only DC fit — trained once on ≤2022/23 and evaluated up to
  three seasons out — itself understates FT Over 2.5 on the same test
  window by **−4.73pp** (pred 49.05% vs actual 53.78%; mean FT goals
  rose 2.771 → 2.826 between the windows). The frozen shares barely
  drifted (test 1H share: home 0.4438, away 0.4395 vs frozen
  0.4419/0.4440), so the share is not the problem either.

In other words: the harness's three-season-old static fit drifts low
on totals, and thinning passes that bias straight through. No
correction fitted on the tuning window can repair a bias that only
exists out-of-window — a tuning-fitted mean offset comes out ≈ 1.0 by
construction. Production refits weekly, so this specific bias is
largely a harness artefact; but under the pre-registered comparison
(same static-fit framework as experiment 1, which is where the 2–4pp
figure came from), the gate fails and that is the verdict.

## What would change the answer

A NEW pre-registered experiment with a production-faithful harness —
refit the FT model per test season (as production does weekly) before
thinning — would remove most of the inherited mean bias and isolate
the true half-level calibration. That is a different experiment, not a
continuation of this one, and it needs its own gate.

Production untouched. No predictions_goals_halves_upcoming.csv built.
