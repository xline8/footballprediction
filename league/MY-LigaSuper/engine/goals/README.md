# G-MY goals engine (development only)

This directory contains the Phase B development engine for Malaysia Liga
Super. It reads `../../data/my_ligasuper_matches.csv`, materializes only the
permitted warm-up season `2021` and scored seasons `2022`, `2023`, and
`2024/2025`, and excludes `is_awarded == 1` rows. The loader asserts the exact
season set and counts 132, 132, 182, and 155 (469 scored). Rows from
`2025/2026` and `2026/2027` are never loaded, fitted, scored, or written.

Run from this directory with `python3 run_g_my.py`. The runner recomputes the
fits from the CSV and writes `results_dev.json`, `results_dev.csv`, and
`fitted_params_dev.json`. There is deliberately no virgin runner, virgin
prediction file, or verdict file in this phase.

Gate Zero is the direct goals-only Dixon-Coles fit: weighted Poisson
log-likelihood, scipy L-BFGS, sum-to-zero attack and defence, ridge 1e-3,
home intercept initialized at 0.25, MAXG 10, standard low-score tau, and rho
selected from `(0.0, -0.05, -0.10, -0.15)` by weighted training
log-likelihood. Weights use the frozen 270-day half-life. A fit is made once
per target season using all permitted model rows strictly before that season's
first match date, then the whole target season is scored.

SHRINK scales both attack and defence exponents at prediction time by `n/6`
for teams with fewer than six prior in-league matches; `n >= 6` is unchanged
and `n = 0` uses zero exponents. Counts are strictly pre-season. The synthetic
unit check proves that three prior matches produce factor `0.5`. Actual
`n_0`, `n_1_to_5`, `n_6_to_29`, and `n_30_plus` buckets are recorded in the
JSON, including any discrepancy from the frozen expectations.

Baselines are training-window pooled climatology and the strict pre-match
trailing-10 independent Poisson baseline. Metrics are mean natural-log-loss
for 1X2 and OU2.5 plus RPS with outcome order H/D/A. Probability clipping for
log metrics uses the TN harness epsilon `1e-12`. No xG or blend is used.

The dev gate is mechanical: pooled 1X2 LL, RPS, and OU2.5 LL must each beat
both baselines, separately for each arm. Gate legs and margins are recorded in
`results_dev.json`; this engine does not write the final verdict.

The CSV has exactly one row per scored match (469 plus header), with actual
match fields, Gate Zero/SHRINK/climatology/trailing-10 probabilities, and the
fitted home intercept and rho for the target-season fit. `fitted_params_dev.json`
contains the per-season team attack/defence parameters for independent replay.
