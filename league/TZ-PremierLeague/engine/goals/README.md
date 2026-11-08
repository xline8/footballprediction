# G-TZ goals engine

Reads `data/tz_matches.csv`. Eligibility is the frozen `eligible` column,
which excludes awarded matches. 2021/2022 (239); DEV folds are 2022/2023
(240), 2023/2024 (240), and 2024/2025 (240), pooled n=720. DEV reads only
those four seasons; it never reads 2025/2026 or 2026/2027. Run
`python3 run_g_tz.py` from this directory.

Gate Zero is the copied Dixon-Coles fit (14 sweeps, damping .7, smoothing
.25, fitted h initialized at .28, rho grid, MAXG=10, half-life 270). SHRINK is
its only variant:
for teams with 1–5 prior matches in the fit, attack and defence are multiplied
by n/6. The naive comparison uses each team's trailing ten matches; if either
team has fewer than six, the league mean is used. Dev gates require pooled
1X2 LL and RPS to beat climatology and OU2.5 LL to beat the base-rate model.

Outputs are `results_dev.json`, `results_dev.csv`, and `predictions_dev.csv`.
`virgin()` is a separate coordinator-controlled step gated on the dev result
and is not invoked by this runner. If later authorized, its virgin season is
2025/2026 (239), with a data-derived first-date cutoff; the frozen halves
constants are 0.4867818118 (1H) and 0.5132181882 (2H).
