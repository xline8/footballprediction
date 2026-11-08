# G-WAL goals engine

Reads `data/wal_matches.csv`. Eligibility is the frozen `eligible` column,
which excludes playoff matches. Teams are keyed by stable FotMob team ID,
with display names retained separately. 2021/2022 (192); DEV folds are
2022/2023 (192), 2023/2024 (192), and 2024/2025 (192), pooled n=576. DEV
reads only those four seasons; it never reads 2025/2026 or 2026/2027. Run
`python3 run_g_wal.py` from this directory.

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
2025/2026 (192), with a data-derived first-date cutoff; the frozen halves
constants are 0.4444 (1H) and 0.5556 (2H). SHRINK is expected to be a
structural no-op because no target team has 1–5 prior in-league matches.
