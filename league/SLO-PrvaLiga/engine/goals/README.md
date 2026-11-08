# G-SLO goals engine (development only)

This directory contains the Phase B development engine for Slovenia
Prva Liga. It reads `../../data/slo_prva_liga_matches.csv`, materializes only
the permitted warm-up season 2021/2022 and scored seasons 2022/2023,
2023/2024, and 2024/2025, and excludes `is_awarded == 1` rows. The loader
asserts the exact four-season set and the frozen counts (180, 180, 178, 180;
538 scored). Rows outside this scope are not loaded, fitted, scored, or written.

Run from this directory with `/usr/bin/python3 run_g_slo.py`. The runner writes
`results_dev.json`, `results_dev.csv`, and `fitted_params_dev.json`.

Gate Zero is the direct goals-only Dixon-Coles fit: weighted Poisson
log-likelihood, scipy L-BFGS, sum-to-zero attack and defence, ridge 1e-3,
home intercept initialized at 0.25, MAXG 10, standard low-score tau, and rho
selected from `(0.0, -0.05, -0.10, -0.15)` by weighted training
log-likelihood. Weights use the frozen 270-day half-life. A fit is made once
per target season using all permitted model rows strictly before that season's
first match date, then the whole target season is scored.

SHRINK scales both attack and defence exponents at prediction time by `n/6`
for teams with fewer than six prior training matches; `n >= 6` is unchanged
and `n = 0` uses zero exponents. The synthetic unit check proves that three
prior matches produce factor `0.5`. The real SLO run records the 1-to-5 prior
team counts; the frozen expectation is zero in every scored season, so
SHRINK and Gate Zero should be identical.

Baselines are training-window pooled climatology and the strict pre-match
trailing-10 independent Poisson baseline. Metrics are mean natural-log-loss
for 1X2 and OU2.5 plus RPS with outcome order H/D/A. Probability clipping for
log metrics uses the TN harness epsilon `1e-12`. No xG or blend is used.

The CSV follows the TN wide output shape: one row per scored match, with
actual match fields, Gate Zero/SHRINK/climatology/trailing-10 probabilities,
and the fitted home intercept and rho for that target-season fit. This is a
development artifact only; no other-season runner is present in this phase.
