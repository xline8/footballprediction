# G-SV goals engine

Reads `data/sv_matches.csv`. Eligibility is the frozen `eligible`
column AND `stage == "regular"` (playoffs excluded — MX-LigaMX
precedent for split-season leagues). Seed 2021/2022 - Apertura
(132); DEV folds are 2021/2022 - Clausura (132), 2022/2023 -
Apertura (67), 2022/2023 - Clausura (132), 2023/2024 - Apertura
(132), 2023/2024 - Clausura (132), 2024/2025 - Apertura (110) and
2024/2025 - Clausura (110), pooled n=815. DEV reads only those eight
tournaments; it never reads 2025/2026 or 2026/2027. Run
`python3 run_g_sv.py dev` from this directory. Teams are keyed by
FotMob team id.

Gate Zero is the copied Dixon-Coles fit (14 sweeps, damping .7,
smoothing .25, h=.28, rho grid, MAXG=10, half-life 270). SHRINK is
its only variant: for teams with 1–5 prior matches in the fit,
attack and defence are multiplied by n/6. The naive comparison uses
each team's trailing ten matches; if either team has fewer than six,
the league mean is used. Dev gates require pooled 1X2 LL and RPS to
beat climatology and OU2.5 LL to beat the base-rate model.

Outputs are `results_dev.json`, `results_dev.csv`, and
`predictions_dev.csv`. `virgin()` is coordinator-controlled and is
not a CLI command. The virgin window is 2025/2026 Apertura +
Clausura (264), with a data-derived first-date cutoff; the frozen
halves presentation constant is 0.4335 (1H .4335 FT, 2H .5665 FT).
