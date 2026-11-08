# G-NG goals engine

Reads `data/ng_matches.csv`. Eligibility is the frozen `eligible` column:
finished AND NOT awarded AND stage != championship_group (one stale-flag
match, 4765626, is eligible despite `finished=0` — its 5-1 score
reconciles with its Goal events; see analysis/DATA_UNDERSTANDING.md §5).
2021/2022 (379); DEV folds are 2023 (180), 2023/2024 (379), and 2024/2025
(380), pooled n=939. DEV reads only those four seasons; it never reads
2025/2026 or 2026/2027. Run `python3 run_g_ng.py dev` from this directory.

Gate Zero is the copied Dixon-Coles fit (14 sweeps, damping .7, smoothing
.25, h=.28, rho grid, MAXG=10, half-life 270). SHRINK is its only variant:
for teams with 1–5 prior matches in the fit, attack and defence are multiplied
by n/6. The naive comparison uses each team's trailing ten matches; if either
team has fewer than six, the league mean is used. Dev gates require pooled
1X2 LL and RPS to beat climatology and OU2.5 LL to beat the base-rate model.

Outputs are `results_dev.json`, `results_dev.csv`, and `predictions_dev.csv`.
`virgin()` is coordinator-controlled and is not a CLI command. The virgin
season is 2025/2026 (379), with a data-derived first-date cutoff; the frozen
halves presentation constant is 0.4796 (1H .4796 FT, 2H .5204 FT).
