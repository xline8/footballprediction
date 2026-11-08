# goals — Dixon-Coles engine (Gate Zero + ENTRANT), see dc.py, arms.py and PREREG_G_IL.md

- Fit: Poisson log-likelihood (scipy L-BFGS, sum-to-zero, ridge 1e-3); rho from grid (0, −0.05, −0.10, −0.15) by training LL; MAXG = 10.
- Dev: warm-up 2021/2022, scored 2022/2023–2024/2025 (n = 720), season-blocked expanding fit. Baselines: climatology + naive trailing-10.
- Virgin: 2025/2026 (n = 240), read once, only for dev-passing arms. Run with `IL_DEV_ONLY=1` for dev only.
- Run: `python3 run_g_ec.py` from this directory. Outputs: `results_dev.json`, `results_dev.csv`, `results_virgin.json`, `virgin_rows_<arm>.csv`, `fitted_params_virgin.json`.
