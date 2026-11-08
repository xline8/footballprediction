# G-LU goals engine

This is the development-only Luxembourg National Division goals engine. It
reads `../../data/lu_matches.csv`, keeps only the warm-up season
`2021/2022` and scored dev seasons `2022/2023`–`2024/2025`, and sorts matches
by `(date, match_id)`. Virgin `2025/2026` and reserve `2026/2027` rows are
never used for fitting, metrics, or calibration; there is deliberately no
virgin code path here.

Run from this directory:

```sh
python3 run_g_lu.py
```

The implementation follows the frozen design in
`../../prereg/PREREG_G_LU.md`, `../../analysis/MODEL_DESIGN.md`, and
`../../analysis/EDA.md`: weighted direct Poisson Dixon–Coles fits, 270-day
decay, the frozen rho grid and MAXG=10, Gate Zero and SHRINK only, pooled
climatology, and bounded trailing-10 goals means. Team identity is always
`home_id`/`away_id`.

Outputs are `results_dev.json` (summary only: pooled and per-season
1X2 log-loss, RPS, OU2.5 log-loss, Gate Zero diagnostics),
`results_dev.csv` (one row per scored match, including both arms and
both baselines — the only per-match record), and
`fitted_params_dev.json`.
