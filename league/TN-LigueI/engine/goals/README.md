# G-TN goals engine

Development-only Tunisia Ligue I goals engine. It reads
`../../data/tn_matches.csv`, uses all-phase model matches excluding awarded
rows from warm-up 2021/2022 and scored seasons 2022/2023–2024/2025, and
hard-checks the frozen counts (156 warm-up and 195/170/237 scored, 602 pooled).
Virgin 2025/2026 and reserve 2026/2027 rows are excluded from every fit,
baseline, and metric.

Run from this directory:

```sh
python3 run_g_tn.py
```

The engine follows the frozen preregistration: weighted direct Poisson
Dixon-Coles fits, 270-day decay, rho grid, MAXG=10, Gate Zero and SHRINK,
pooled climatology, and strict pre-date bounded trailing-10 means. Outputs
are `results_dev.json` (summary), `results_dev.csv` (602 per-match rows), and
`fitted_params_dev.json`.
